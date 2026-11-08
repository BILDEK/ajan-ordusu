"""Fail-closed UTC reservation ledger. Never initialize or refund at runtime."""
import datetime as dt
import json
import os
from pathlib import Path
import re

RESERVATION, DAILY, MONTHLY, MAX_RUNS = 10, 40, 1200, 4


def positive(value, cap):
    return type(value) is int and 0 < value <= cap and value % RESERVATION == 0


def reserve(ledger, now, run_id):
    if now.tzinfo is None or not re.fullmatch(r"[0-9]+", run_id):
        raise ValueError("UTC-aware time and numeric run ID required")
    day = now.astimezone(dt.timezone.utc).date().isoformat()
    month = day[:7]
    if (not isinstance(ledger, dict) or set(ledger) != {"version", "months", "days"}
            or type(ledger["version"]) is not int or ledger["version"] != 1
            or not isinstance(ledger["months"], dict) or not isinstance(ledger["days"], dict)):
        raise ValueError("Malformed ledger; manual review required")
    months, days = ledger["months"], ledger["days"]
    if len(months) > 12 or len(days) > 40:
        raise ValueError("Retention exceeded")
    for key, minutes in months.items():
        if (not re.fullmatch(r"[0-9]{4}-[0-9]{2}", key)
                or dt.date.fromisoformat(key + "-01").isoformat()[:7] != key
                or key > month or not positive(minutes, MONTHLY)):
            raise ValueError("Invalid month reservation")
    seen, sums = set(), {}
    for key, entry in days.items():
        if dt.date.fromisoformat(key).isoformat() != key or key > day:
            raise ValueError("Invalid/future day")
        if (not isinstance(entry, dict) or set(entry) != {"reserved_minutes", "runs"}
                or not positive(entry["reserved_minutes"], DAILY)
                or not isinstance(entry["runs"], list)
                or not 1 <= len(entry["runs"]) <= MAX_RUNS
                or entry["reserved_minutes"] != len(entry["runs"]) * RESERVATION):
            raise ValueError("Invalid daily reservation")
        for previous in entry["runs"]:
            if not isinstance(previous, str) or not re.fullmatch(r"[0-9]+", previous) or previous in seen:
                raise ValueError("Invalid/duplicate run ID")
            seen.add(previous)
        sums[key[:7]] = sums.get(key[:7], 0) + entry["reserved_minutes"]
    if any(total > months.get(key, 0) for key, total in sums.items()):
        raise ValueError("Month/day totals disagree")
    if run_id in seen:
        raise ValueError("Already reserved; reruns denied")
    entry = days.get(day, {"reserved_minutes": 0, "runs": []})
    if (len(entry["runs"]) >= MAX_RUNS or entry["reserved_minutes"] + RESERVATION > DAILY
            or months.get(month, 0) + RESERVATION > MONTHLY):
        raise ValueError("Research budget exhausted")
    # Copy before mutation: rejection cannot partially change callers' ledger.
    result = json.loads(json.dumps(ledger))
    result["months"][month] = months.get(month, 0) + RESERVATION
    result["days"][day] = {"reserved_minutes": entry["reserved_minutes"] + RESERVATION,
                           "runs": entry["runs"] + [run_id]}
    result["months"] = dict(sorted(result["months"].items())[-12:])
    result["days"] = dict(sorted((key, value) for key, value in result["days"].items()
                                if key[:7] in result["months"])[-40:])
    return result


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


if __name__ == "__main__":
    path = Path("kernel/budget.json")  # Missing/malformed is fatal, NOT a reset.
    ledger = reserve(load(path), dt.datetime.now(dt.timezone.utc), os.environ["GITHUB_RUN_ID"])
    path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print("Reserved 10 research runner-minutes; approval requires successful git push.")
