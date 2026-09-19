# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status: KILLED (2026-09-17)

This repo is a closed research record. It tested one hypothesis: after a BTC EMA 9/21 bearish cross, short SVXY (an inverse VIX ETP) for 10 sessions. The honest backtest rejected it at step 4 of 6, so step 5 (overfit gate) and step 6 (execution code) were never built. `research/02_backtest_result.md` holds the verdict and the cause: SVXY contango decay, not cost.

Useful work here is reading the record, reproducing it, or porting the tools to a new project. A variant (another instrument, another hold period) is a new hypothesis: it gets its own pre-registration, committed before its backtest runs.

## Research protocol

`README.md` is the single source of truth for the hypothesis, the step order, and the pre-registered parameters.

- **Pre-registered parameters are frozen.** Signal, hold period, entry, exit, and accept criteria were committed before the backtest ran. `HOLD_DAYS`, the EMA spans, and the accept thresholds in the scripts mirror the README and keep their values. Tuning one after seeing results is selection, not discovery.
- **Steps run in cheapest-disqualifier order.** Work on a step starts only after the previous step passed. One failed accept criterion rejects the strategy.
- **`screen()` comes before any backtest code.** Cost is deterministic and gross is a random variable, so the screen requires gross >= 3x cost.
- **Every return series goes through `honesty()`** and is reported with `format_report()`, so median and drop-top-5% sit next to the mean. Drop-top-5% is the decisive check.

## Commands

There is no build, lint, test framework, or dependency manifest. The scripts need `numpy`, `pandas`, and `yfinance` on the system `python3` (developed on Homebrew Python 3.14, no venv).

```bash
python3 scripts/quant_honesty.py --selftest   # the only test: offline, instant, prints "selftest OK"
python3 scripts/backtest_svxy_short.py        # the full study: needs network (yfinance), prints the verdict
python3 scripts/generate_signals.py           # optional dump of signal dates with VIX/VVIX (--start YYYY-MM-DD)
```

`backtest_svxy_short.py` overwrites `data/svxy_short_trades.csv`, the committed evidence behind the kill verdict (84 trades). A re-run on 2026-09-19 reproduced it exactly. It will drift once a new bearish cross completes its hold, or if Yahoo re-adjusts SVXY history. After a run, check `git diff data/` and restore the file unless changing the evidence is the point of the work.

## Architecture

Three scripts in `scripts/`, one real entry point.

- `backtest_svxy_short.py` is the whole study: screen, downloads, trades, cost, honesty battery, verdict. It imports from the other two scripts through a `sys.path` insert, so it runs from any directory. It downloads BTC-USD, SVXY, and ^IRX live on every run. `data/` is output only: nothing reads it back.
- `generate_signals.py` defines the signal in `ema_cross_signals()`. Its `fetch()` returns a flat Close series (yfinance returns MultiIndex columns, so reuse `fetch()` or drop level 1 the same way). Its own `main()` is a leftover from the parent project's VVIX analysis: it writes `data/btc_signals.csv` and `data/vvix_daily.csv`, which are uncommitted and unused by the backtest.
- `quant_honesty.py` is a portable single file: `screen()`, `honesty()`, `format_report()`. Identical copies live in `../fin-vix-signal` and `../fin-trading-engine`. It stays stdlib + numpy with zero project imports so it remains copyable. "This repo" in its docstring means the repo it was born in.
- The step 5 tool, `backtest_overfit_analysis.py` (PBO + Deflated Sharpe), lives only in `../fin-trading-engine/scripts/`.

### Conventions that span files

- **Two calendars.** BTC trades every day, SVXY only on NYSE sessions. Signal dates come from the BTC calendar. Entry is the open of the first SVXY session strictly after the signal date (a Saturday cross enters on Monday). Exit is the close `HOLD_DAYS` sessions after the entry session. Yahoo's BTC-USD history begins 2014-09-17, so the `2012-01-01` start date is nominal and the first trade is 2014-10-24.
- **Units.** `honesty()` is unit-agnostic, and the backtest feeds it percent. The README accept criteria are written in R. The strategy has no stop, so the backtest defines 1R = 20% (the assumed worst 10-session SVXY move): "all years >= -1.0R" is coded as "worst year mean >= -20%". `screen()` takes `stop_pct` as a fraction (0.20) and raises above 1.
- **Three verdicts.** PASS, REJECT, or UNRESOLVABLE. `honesty()` flags `underpowered` below `min_n=60` trades, and the backtest reports that as "cannot tell", a different state from "no edge". The printed gross/cost ratio uses `abs(mean gross)` and sits outside the verdict, so it shows 7.6x on a losing book.
- **The cost model follows the venue finding.** `research/01_venue_access.md` shows that PRIIPs blocks EU retail accounts from SVXY shares, so the tradeable instrument is the IBKR CFD (ZIVB is unavailable on IBKR and was dropped). Cost is therefore CFD overnight financing, `(^IRX as benchmark proxy + 1.5%) * HOLD_DAYS / 360`, plus commission, with no stock borrow fee. Two known simplifications, both tiny next to the -1.03% mean gross: commission is charged at 3.2 bp although 1.6 bp is already the round-trip figure, and financing covers 10 days although 10 sessions span about 14 calendar nights.
