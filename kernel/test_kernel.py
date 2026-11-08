import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from kernel import budget, research


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.now = dt.datetime(2026, 11, 9, 12, tzinfo=dt.timezone.utc)
        self.empty = {"version": 1, "months": {}, "days": {}}

    def test_daily_cap_and_rerun(self):
        ledger = self.empty
        for run in range(1, 5):
            ledger = budget.reserve(ledger, self.now, str(run))
        self.assertEqual(ledger["months"]["2026-11"], 40)
        for run in ("5", "1"):
            with self.assertRaises(ValueError):
                budget.reserve(ledger, self.now, run)
        self.assertEqual(self.empty["months"], {})

    def test_month_cap_31_days_and_rollover(self):
        ledger = self.empty
        start = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
        for day in range(30):
            for run in range(4):
                ledger = budget.reserve(ledger, start + dt.timedelta(days=day), str(day * 4 + run))
        with self.assertRaisesRegex(ValueError, "exhausted"):
            budget.reserve(ledger, start + dt.timedelta(days=30), "120")
        ledger = budget.reserve(ledger, self.now, "121")
        self.assertEqual(ledger["months"], {"2026-10": 1200, "2026-11": 10})
        self.assertLessEqual(len(ledger["days"]), 40)

    def test_fail_closed_and_utc(self):
        for ledger in ({}, {"version": True, "months": {}, "days": {}},
                       {"version": 1, "months": {"2026-11": -10}, "days": {}},
                       {"version": 1, "months": {"2026-12": 10}, "days": {}}):
            with self.assertRaises(ValueError):
                budget.reserve(ledger, self.now, "1")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "budget.json"
            with self.assertRaises(FileNotFoundError):
                budget.load(path)
            path.write_text('{"version":1,"version":1,"months":{},"days":{}}')
            with self.assertRaises(ValueError):
                budget.load(path)
        local = dt.datetime(2026, 12, 1, 1, tzinfo=dt.timezone(dt.timedelta(hours=3)))
        self.assertIn("2026-11-30", budget.reserve(self.empty, local, "1")["days"])
        with self.assertRaises(ValueError):
            budget.reserve(self.empty, self.now.replace(tzinfo=None), "1")

    def test_compact_retention_sparse_years(self):
        ledger = self.empty
        for year in range(2020, 2034):
            ledger = budget.reserve(ledger, self.now.replace(year=year), str(year))
        self.assertEqual(len(ledger["months"]), 12)
        self.assertEqual(len(ledger["days"]), 12)

    def test_science_and_meaningful_memory(self):
        result = research.science()
        self.assertTrue(all(3.9 < ratio < 4.1 for ratio in result["ratios"]))
        report = {"topic": "science", "utc_day": "2026-11-09", "method": "kernel-v1",
                  "source_commit": "offline-test", "sources": research.SOURCES["science"], "result": result}
        with tempfile.TemporaryDirectory() as temp, patch.object(research, "ROOT", Path(temp)):
            folder = Path(temp) / "kernel"
            folder.mkdir()
            (folder / "findings.json").write_text('{}')
            research.record(report)
            initial = (folder / "findings.json").read_bytes()
            report["utc_day"] = "2026-11-10"
            research.record(report)
            self.assertEqual(initial, (folder / "findings.json").read_bytes())
            self.assertIn("3.9", str(json.loads(initial)["science"]["result"]["hypothesis"]))
