# fin-btc-vol-short

**Verdict: KILLED 2026-09-17.** The backtest rejects this strategy. The mean net trade-return is -1.16%, the median is -2.13%, and the drop-top-5% is -2.60%. The BTC signal is correct, but SVXY contango decrease removes the profit on small VIX moves. Cost was not the problem (0.14% for each trade).

## Idea

A BTC EMA 9/21 bearish cross shows VIX elevation in the subsequent 10 to 21 days. Short SVXY at the cross and close the position after 10 sessions.

This project uses `fin-vix-signal` (killed 2026-09-17) as its starting point. That project found a correct BTC timing signal (mean VVIX at cross dates = 100.6). But VIX call options are not tradeable at the moment the signal fires. IV is elevated at that moment, so the call options are expensive. Shorting an inverse-VIX ETP removes the call option premium and IV-of-VIX risk.

## Why it might work

- The financing cost (CFD overnight at benchmark + 1.5%) does not correlate with signal strength.
- SVXY has daily liquidity and fills are possible.

## Why it might fail

- SVXY has path-dependent decrease. Volatility drag works against short positions in low-vol periods.
- A short SVXY position is a leveraged VIX long with daily rebalancing. Vol-of-vol is important.
- 84 signals in 11 years is less than the 63-trade CI floor, so statistical power is marginal.

## Research protocol

The steps operate in cheapest-disqualifier sequence. One criterion that is not satisfactory rejects the strategy.

1. **Venue access.** Can the user short SVXY from Romania through IBKR? See `research/01_venue_access.md`. The result: YES through CFD (ConId 290657198, PRIIPs-compliant).
2. **Cost data.** Get the actual borrow rates. If borrow is more than 5% annualized in stress periods, the trading edge may not survive.
3. **Pre-registration.** Commit the hypothesis, hold period, and accept/reject criteria before a backtest.
4. **Honest backtest.** Use actual SVXY price data. Apply `honesty()`: median, drop-top-5%, by-year. If a single criterion is not satisfactory, reject the strategy.
5. **Overfit gate.** PBO + Deflated Sharpe.
6. Write execution code only after step 5 is satisfactory.

Steps 5 and 6 were not completed. The backtest rejected the strategy at step 4.

## Pre-registered parameters

- Signal: BTC EMA 9/21 bearish cross
- Hold period: 10 sessions
- Entry: short SVXY at the next open after the signal
- Exit: close the position at the close on day N
- Accept criteria: median R > 0, drop-top-5% R > 0, all years >= -1.0R

These parameters are set. Do not change them after you see results. A change to them after results is selection, not discovery.

## Scripts

```bash
python3 scripts/quant_honesty.py --selftest   # offline selftest, prints "selftest OK"
python3 scripts/backtest_svxy_short.py        # full study, needs network (yfinance)
python3 scripts/generate_signals.py           # optional: dump signal dates with VIX/VVIX
```

`backtest_svxy_short.py` writes to `data/svxy_short_trades.csv` (84 trades, the committed sign of the verdict). After a run, make sure that `git diff data/` shows the expected change. Put the file back unless changing the sign is the purpose of the work.

## Key constraints

- Drop-top-5% is the decisive honesty test. Do not skip it.
- Make sure that gross is >= 3x cost before you operate a backtest.
- To select N variants and pick the best is selection, not discovery.
- A universe-wide parameter increase does not move to a selected book (corr = -0.523).
