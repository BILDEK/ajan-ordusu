"""Bounded public-data regression/research test; no AI API, secrets or trades.
Train-only volatility threshold and chronological holdout; approximate costs.
"""
import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import statistics
import sys
import time

# Standalone engine parses argv at import. Fix this CI workload to one dataset.
sys.argv = ["arge_ci.py", "ETH-USDT-SWAP", "5m", "2000"]
import strateji_backtest as engine


def stats(values):
    wins = sum(x for x in values if x > 0)
    losses = -sum(x for x in values if x < 0)
    return {"n": len(values), "mean_net_R": round(statistics.mean(values), 4) if values else None,
            "profit_factor": round(wins / losses, 3) if losses else None}


def net_r(candles, atrs, i, gross_r, side, cost_bps):
    entry = candles[i + 1]["o"]
    risk = atrs[i] or entry * 0.002
    inferred_exit = entry + side * gross_r * risk
    # Assumption: 10bps round-trip fees + 2bps total slippage; NOT account pricing.
    estimated_cost = (entry + abs(inferred_exit)) * (cost_bps / 2 / 10000)
    return gross_r - estimated_cost / risk


def main():
    start = time.perf_counter()
    raw = engine.load_candles("ETH-USDT-SWAP", "5m", 2000)
    candles = [engine.num(c) for c in raw][-2000:]
    if len(candles) < 1900:
        raise RuntimeError("Incomplete dataset: expected at least 1900 confirmed candles")
    if any(b["ts"] - a["ts"] != 300000 for a, b in zip(candles, candles[1:])):
        raise RuntimeError("Candle gaps: reject incomplete coverage")
    download_seconds = time.perf_counter() - start
    calc_start = time.perf_counter()
    closes = [c["c"] for c in candles]
    atrs = engine.atr(candles)
    cut = int(len(candles) * .7)
    volmed = statistics.median(atrs[i] / closes[i] * 100 for i in range(50, cut))
    sigs = engine.signals(candles, closes, engine.rsi(closes), atrs,
                          engine.ema(closes, 20), engine.ema(closes, 50), engine.bollinger(closes))
    COST_BPS = 12

    def evaluate(name, bucket, begin, end):
        values, busy_until = [], -1
        side = 1 if name.endswith("long") else -1
        for i in sigs[name]:
            if i < max(50, begin) or i + 12 >= end or i < busy_until:
                continue
            trend, volpct = engine.regime(closes, atrs, i)
            vol = "highvol" if volpct > volmed else "lowvol"
            if bucket not in ("ALL", trend, vol):
                continue
            gross_r, hold = engine.simulate(candles, i, side, 1.5, 1., atrs)
            values.append(net_r(candles, atrs, i, gross_r, side, COST_BPS))
            busy_until = i + hold  # no overlapping positions inside this candidate
        return stats(values)

    candidates = []
    for name in sigs:
        for bucket in ("ALL", "up", "down", "range", "highvol", "lowvol"):
            training = evaluate(name, bucket, 0, cut)
            if training["n"] >= 20:
                candidates.append((training["mean_net_R"], name, bucket, training))
    candidates.sort(reverse=True)
    selected = None
    if candidates:
        _, name, bucket, training = candidates[0]
        selected = {"strategy": name, "regime": bucket, "training": training,
                    "holdout": evaluate(name, bucket, cut, len(candles))}
    result = {
        "instrument": "ETH-USDT-SWAP", "bar": "5m", "candles": len(candles),
        "first_utc": dt.datetime.fromtimestamp(candles[0]["ts"] / 1000, dt.timezone.utc).isoformat(),
        "last_utc": dt.datetime.fromtimestamp(candles[-1]["ts"] / 1000, dt.timezone.utc).isoformat(),
        "training_candles": cut, "holdout_candles": len(candles) - cut,
        "round_trip_cost_assumption_bps": COST_BPS, "selected_on_training_only": selected,
        "download_seconds": round(download_seconds, 3),
        "calculation_seconds": round(time.perf_counter() - calc_start, 3),
        "logical_cpus": os.cpu_count(),
        "caveats": ["Small holdout; not evidence of profitability", "Selection bias remains in training",
                    "No funding/gap fills/market impact", "R diagnostics, not portfolio return",
                    "No model training or self-improving agent; this is a bounded software/data test"],
    }
    report = "## Bounded research test\n\n```json\n" + json.dumps(result, indent=2) + "\n```\n"
    print(report)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(report)
    # Tiny result can be retained in workflow logs without billed artifacts/cache.
    Path("last-ci-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
