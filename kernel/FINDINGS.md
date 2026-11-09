# Kernel findings

Latest changed result per topic; no model-weight learning.
Full measurements and reproducibility metadata: `findings.json`.

## income — 2026-11-09
Method: kernel-v1; source: `979e5abca5c017eb0abc91c774f0b94c4f8b0bf9`.
Training-selected candidate and holdout diagnostics recorded; NOT profitability evidence.
Data: 2026-11-02T07:50:00+00:00 to 2026-11-09T06:20:00+00:00, 1999 candles.
Limitations: Small holdout; not evidence of profitability; Selection bias remains in training; No funding/gap fills/market impact; R diagnostics, not portfolio return; No model training or self-improving agent; this is a bounded software/data test; No raw snapshot retained; provider revisions can prevent exact reproduction; Repeated daily holdouts overlap; these are not independent confirmations
Next method (proposal, not automatically adopted): Freeze hypotheses, add independent windows and cost sensitivity before claims
Product hypothesis (no guaranteed income): Reproducible backtest data-quality report/tool; no signals or trade service
Sources: https://www.okx.com/docs-v5/en/#rest-api-market-data-get-history-candlesticks | https://doi.org/10.1090/noti1105

## science — 2026-11-08
Method: kernel-v1; source: `94c41f5dd4eac44ea50bf4c7f7fee6587d9acf8e`.
Observed convergence ratios: 4.001930, 4.000482, 4.000120.
Limitations: One smooth integrand, not a general accuracy proof
Next method (proposal, not automatically adopted): Human-reviewed extension: non-smooth integrand and roundoff study
Product hypothesis (no guaranteed income): Open numerical-method QA/tutorial package; demand unvalidated
Sources: https://dlmf.nist.gov/3.5
