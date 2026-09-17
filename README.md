# fin-btc-vol-short

**Idea:** BTC EMA 9/21 bearish cross → short inverse VIX ETPs (SVXY / ZIVB)

## Origin

Spin-off from `fin-vix-signal` (killed 2026-09-17). The BTC timing signal is real
(mean VVIX at cross dates = 100.6, VIX spikes reliably after bearish EMA cross) but
VIX call options are untradeable — you buy expensive vol exactly when the signal fires.

**This project tests a different cost geometry:** instead of buying calls, short an
inverse-VIX ETP. SVXY and similar products move inversely to VIX. A VIX spike = SVXY
drops = short profits. No options premium to pay, no IV-of-VIX risk eating the edge.

## Hypothesis

BTC EMA 9/21 bearish cross predicts VIX elevation over the next 10–21 days.
Shorting SVXY at the cross and covering after N days should capture that move
without the options cost trap.

## Why this might work

- Cost is borrow + spread (roughly 1–3% annualized), not a large upfront premium.
- Entry cost does NOT correlate with signal strength (unlike VVIX, which spikes exactly
  when you want to buy calls).
- SVXY has daily liquidity; fills are realistic.

## Why this might fail

- SVXY has path-dependent decay — volatility drag works against shorts in low-vol periods.
- Short SVXY is a leveraged VIX long with daily rebalancing; the vol-of-vol matters.
- Borrow costs can spike during stress (when you most want the short on).
- 84 signals over 11 years is still below the 63-trade CI floor — power is marginal.

## Method (follow cheapest-disqualifier order from parent project)

1. **Venue access:** can SVXY be shorted from Romania via IBKR? Check margin/borrow
   availability before any analysis.
2. **Real cost data:** get actual borrow rates for SVXY (Interactive Brokers stock loan).
   If borrow > 5% annualized during stress periods, the edge may not survive.
3. **Pre-register:** commit hypothesis, hold period, and accept/reject criteria BEFORE
   running any backtest.
4. **Honest backtest:** use real SVXY price data (yfinance: `SVXY`). Apply `honesty()`
   battery — median, drop-top-5%, by-year. Any single criterion failing = reject.
5. **Overfit gate:** PBO + Deflated Sharpe (copy `scripts/backtest_overfit_analysis.py`
   from `fin-trading-engine`).
6. Only then: write execution code.

## Parameters to pre-register (do NOT change after seeing results)

- Signal: BTC EMA 9/21 bearish cross (same definition as `fin-vix-signal`)
- Hold period: **10 days** (best in spike, but treat as fitted — document this)
- Entry: short SVXY at next open after signal
- Exit: cover at close on day N
- Accept criteria: median R > 0, drop-top-5% R > 0, all years ≥ −1.0R

## Portable tools

Copy from `fin-vix-signal` or `fin-trading-engine`:
- `scripts/generate_signals.py` — BTC EMA cross dates (already written)
- `scripts/quant_honesty.py` — `screen()` + `honesty()`
- `scripts/backtest_overfit_analysis.py` — PBO + Deflated Sharpe

## Key constraints (inherited from parent project)

- Drop-top-5% is the decisive honesty check — never skip it.
- Cost is deterministic; gross is a random variable. Require gross ≥ 3× cost.
- Running N variants and picking the best is selection, not discovery.
- A universe-wide parameter gain does not transfer to a selected book (corr = −0.523).

## Status

**Step 1 complete (2026-09-17).** Venue access researched. See `research/01_venue_access.md`.

**Blocker:** SVXY is a US ETF, blocked for EU retail by PRIIPs (no KID).
Two workarounds: (A) short via IBKR CFD if available, (B) professional client opt-up.
Manual check needed: log into IBKR, verify SVXY is in the CFD product list.

**Next:** resolve access path, then Step 2 (real cost data).
