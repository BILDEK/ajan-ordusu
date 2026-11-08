"""Ajan Ordusu - ajan #1: piyasa gozcusu.

OKX public API (anahtar gerektirmez) uzerinden fonlama orani ve
open interest verilerini ceker, GitHub Actions ozetine yazar.
"""
import os
import requests

COINS = ["BTC", "ETH", "SOL"]
BASE = "https://www.okx.com/api/v5/public"


def get(path, **params):
    r = requests.get(f"{BASE}/{path}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()["data"][0]


def main():
    rows = ["| Coin | Fonlama (%) | Open Interest (coin) |", "|---|---|---|"]
    for coin in COINS:
        inst = f"{coin}-USDT-SWAP"
        try:
            fr = float(get("funding-rate", instId=inst)["fundingRate"]) * 100
            oi = float(get("open-interest", instType="SWAP", instId=inst)["oiCcy"])
            rows.append(f"| {coin} | {fr:.4f} | {oi:,.0f} |")
        except Exception as e:
            rows.append(f"| {coin} | hata | {e} |")

    report = "## Ajan #1 - Piyasa Raporu\n\n" + "\n".join(rows) + "\n"
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report)


if __name__ == "__main__":
    main()
