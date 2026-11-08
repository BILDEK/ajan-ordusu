import contextlib
import io
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import arge_ci as ci


class ResearchTests(unittest.TestCase):
    def test_cost_reduces_gross_r(self):
        c = [{"o": 100}, {"o": 100}]
        self.assertAlmostEqual(ci.net_r(c, [1, 1], 0, 1.5, 1, 12), 1.5 - .1209)
        self.assertLess(ci.net_r(c, [1, 1], 0, -1., 1, 12), -1.)

    def test_no_losses_pf_not_infinity(self):
        self.assertIsNone(ci.stats([1, 1])["profit_factor"])

    def test_complete_offline_run(self):
        rows = []
        for i in range(2000):
            o = 100 + 3 * math.sin(i / 20)
            c = 100 + 3 * math.sin((i + 1) / 20)
            rows.append([str(1700000000000 + i * 300000), str(o), str(max(o,c) + .2),
                         str(min(o,c) - .2), str(c), "10", "0", "0", "1"])
        old = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            os.chdir(temp)
            try:
                with patch.object(ci.engine, "load_candles", return_value=rows), patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}), contextlib.redirect_stdout(io.StringIO()):
                    ci.main()
                result = json.loads(Path("last-ci-result.json").read_text())
                self.assertEqual(result["training_candles"], 1400)
                self.assertEqual(result["holdout_candles"], 600)
                self.assertIsNotNone(result["selected_on_training_only"])
            finally:
                os.chdir(old)

    def test_incomplete_data_fails(self):
        with patch.object(ci.engine, "load_candles", return_value=[]):
            with self.assertRaisesRegex(RuntimeError, "Incomplete dataset"):
                ci.main()
