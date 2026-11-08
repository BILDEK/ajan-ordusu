# Independent research kernel

Separate software/data research area: `kernel/`. It does not control the PC or replace the existing `ajan.yml` analysis/Telegram bot. No secret files, Telegram token, AI API, personal data, account credentials, live trade execution, purchases, paid runners/APIs, artifacts, cache upload, persistent server or large model weights. GitHub's scoped ephemeral `GITHUB_TOKEN` is used only by the two repository-persistence jobs, not by research. Human approval is required for code/method changes; no self-modifying execution.

## Scientific and revenue rules

- Declare the question, hypothesis, test thresholds, sampling assumptions and method before measuring. Include negative results, limitations, source citations, source commit, parameters and reproducibility information. Never promote one selected backtest or synthetic unit test into scientific proof.
- UTC-date parity rotates one task: even ordinal = offline trapezoid integration convergence (`sin`, `[0,pi]`, exact integral2;16/32/64/128 subdivisions; error ratios3.9–4.1); odd = existing bounded ETH research. Four daily runs repeat that day's task, NOT four independent studies.
- The income task uses public confirmed candles, chronological70/30 split, training-only selection, costs and overlap exclusions. Holdout is small; repeated windows overlap. Selection bias, funding/gap fills/market impact remain. No signals, trade orders, recommendations or guaranteed money. Revenue hypotheses mean ethical reusable code/data-quality reports/tutorial products; demand/licensing/accuracy must be validated by a human, without buying anything.
- Market results include UTC range and canonical normalized-candle SHA256 plus API citation. Raw snapshots are not retained: provider revisions can prevent exact reproduction. Do not claim full reproduction from a hash alone. Science tests reproduce fully offline with the stated source commit. Do not invent citations or results.
- `kernel/findings.json` retains the latest changed result per topic; `kernel/FINDINGS.md` summarizes meaningful evidence, caveats and next-method proposals. Identical results do not become new learning. Detailed run logs are diagnostic, not permanent evidence. This is accumulated research memory and reviewed method improvement, NOT neural-model weight learning, autonomous intelligence improvement or an income guarantee. Future method changes require human review and regression tests.

## Fail-closed reservation budget

`kernel/budget.json` is an intentionally tracked version1 ledger, initialized once by this deployment. No runtime initialization/reset/refund. Missing, malformed, duplicate-key, inconsistent/future entries or exhausted budget deny research. Never manually clear active usage; corrections require an auditable human review. Failed/cancelled runs retain their full reservation.

A serialized budget gate fetches/rebases current `main`, reserves **10 positive integer research runner-minutes per run**, commits and pushes ONLY the ledger before setting approval. Failed commit/push produces no approval or research output. No retry loop; a conflicting push fails closed. Manual runs only on `main`; workflow reruns are denied to prevent spending again without a fresh reservation. Research checks that the reserved UTC day has not expired before starting.

Limits: **40 reserved minutes and4 research runs per UTC day;1200 reserved minutes per UTC month**. A31-day month therefore allows at most120 research runs, not124. Monthly totals survive day compaction. Keep last12 used UTC months and last40 used UTC days, compact JSON; sparse days whose month has expired are also dropped. No unused allocation is a target to consume.

`arge.yml`: existing off-peak cron UTC00:17/06:17/12:17/18:17 (delivery can be delayed), manual, and relevant source pushes on `main`; no PR trigger. Ledger/findings-only commits cannot recurse via the source path filter (also use `[skip ci]`). One gate at a time; no fan-out. Gate timeout2min, research timeout8min, small separate findings-publish timeout2min. Research has read-only repository permission and no persisted checkout credentials; only gate/publish have repository write permission. Repository branch protection may deny bot pushes: that denies research safely; do not weaken protection automatically.

**These are self-imposed reservation limits, NOT an official GitHub public-runner minute quota and NOT a guaranteed cap on complete billed/provisioned time.** The10-minute reservation covers the bounded research job envelope; gate, provisioning, cancellation latency and optional publication have overhead (denied manual/source runs can still consume gate time). Existing analysis is outside this research ledger. Public repositories' standard hosted runners have free compute under GitHub terms; larger runners/paid services are forbidden here. No guarantee of scheduling, always-on service or unlimited capacity.

## Local verification / deployment

Run `python -m unittest -v test_arge kernel.test_kernel` offline; tests use synthetic market data and temporary files. No network/API/credential required. Operator inspects, commits and pushes these files; this implementation makes no local git commit/push. After deploy, inspect the reservation commit before the research job and check Findings/Summary. Disabled schedules, missing permissions or failed data validation mean no new evidence, not hidden progress.

Sources:
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.github.com/en/actions/reference/limits
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency
- https://dlmf.nist.gov/3.5
- https://www.okx.com/docs-v5/en/#rest-api-market-data-get-history-candlesticks
- https://doi.org/10.1090/noti1105 (backtest overfitting cautions)
