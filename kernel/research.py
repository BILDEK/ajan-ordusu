"""Bounded alternating tasks; stdlib only, no model training or execution rights."""
import base64
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "science": ["https://dlmf.nist.gov/3.5"],
    "income": ["https://www.okx.com/docs-v5/en/#rest-api-market-data-get-history-candlesticks",
               "https://doi.org/10.1090/noti1105"],
}


def science():
    # Predeclared hypothesis: composite trapezoid error decreases ~4x on halving h.
    errors = []
    for n in (16, 32, 64, 128):
        h = math.pi / n
        estimate = h * (sum(math.sin(i * h) for i in range(1, n)) + math.sin(math.pi) / 2)
        errors.append({"n": n, "estimate": estimate, "absolute_error": abs(estimate - 2)})
    ratios = [a["absolute_error"] / b["absolute_error"] for a, b in zip(errors, errors[1:])]
    if not all(3.9 < ratio < 4.1 for ratio in ratios):
        raise RuntimeError("Predeclared second-order convergence test failed")
    return {"hypothesis": "Trapezoid integral sin(x), [0,pi], exact=2; error ratio in (3.9,4.1)",
            "errors": errors, "ratios": ratios,
            "caveats": ["One smooth integrand, not a general accuracy proof"],
            "next_method": "Human-reviewed extension: non-smooth integrand and roundoff study",
            "product_hypothesis": "Open numerical-method QA/tutorial package; demand unvalidated"}


def run(day):
    topic = "science" if day.toordinal() % 2 == 0 else "income"
    if topic == "science":
        result = science()
    else:
        subprocess.run([sys.executable, "arge_ci.py"], cwd=ROOT, check=True, timeout=360)
        result = json.loads((ROOT / "last-ci-result.json").read_text(encoding="utf-8"))
        result.pop("download_seconds", None)
        result.pop("calculation_seconds", None)
        result.pop("logical_cpus", None)
        result["next_method"] = "Freeze hypotheses, add independent windows and cost sensitivity before claims"
        result["product_hypothesis"] = "Reproducible backtest data-quality report/tool; no signals or trade service"
    report = {"topic": topic, "utc_day": day.isoformat(), "method": "kernel-v1",
              "source_commit": os.environ.get("GITHUB_SHA", "local-uncommitted"),
              "sources": SOURCES[topic], "result": result}
    print(json.dumps(report, indent=2))
    (ROOT / "kernel/latest.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write("## Independent kernel\n```json\n" + json.dumps(report, indent=2) + "\n```\n")
    return report


def record(report):
    path = ROOT / "kernel/findings.json"
    findings = json.loads(path.read_text(encoding="utf-8"))
    topic = report["topic"]
    if topic not in SOURCES or report["sources"] != SOURCES[topic] or report["method"] != "kernel-v1":
        raise ValueError("Unexpected findings schema/topic")
    # Identical reruns are not new learning. Keep only latest meaningful finding per topic.
    digest = hashlib.sha256(json.dumps(report["result"], sort_keys=True).encode()).hexdigest()
    if findings.get(topic, {}).get("result_sha256") == digest:
        return
    report["result_sha256"] = digest
    findings[topic] = report
    path.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    lines = ["# Kernel findings", "", "Latest changed result per topic; no model-weight learning.",
             "Full measurements and reproducibility metadata: `findings.json`."]
    for name, item in sorted(findings.items()):
        result = item["result"]
        lines += ["", f"## {name} — {item['utc_day']}", f"Method: {item['method']}; source: `{item['source_commit']}`."]
        if name == "science":
            lines += [f"Observed convergence ratios: {', '.join(f'{r:.6f}' for r in result['ratios'])}."]
        else:
            lines += ["Training-selected candidate and holdout diagnostics recorded; NOT profitability evidence.",
                      f"Data: {result['first_utc']} to {result['last_utc']}, {result['candles']} candles."]
        lines += ["Limitations: " + "; ".join(result["caveats"]),
                  "Next method (proposal, not automatically adopted): " + result["next_method"],
                  "Product hypothesis (no guaranteed income): " + result["product_hypothesis"],
                  "Sources: " + " | ".join(item["sources"])]
    (ROOT / "kernel/FINDINGS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:] == ["--record"]:
        encoded = os.environ["RESULT_JSON"]
        if len(encoded) > 32000:
            raise ValueError("Oversized report")
        record(json.loads(base64.b64decode(encoded, validate=True)))
    else:
        run(dt.datetime.now(dt.timezone.utc).date())
