# Backtest Result: REJECT

**Date:** 2026-09-17

## The signal does not work on SVXY shorts.

Shorting SVXY on BTC EMA 9/21 bearish cross, holding 10 days, loses money.
The mean net return is **-1.16%** per trade. The median is **-2.13%**.
Drop-top-5% is **-2.60%**. Only 5 of 13 years are positive. Win rate is 42%.

## Why it fails

The BTC bearish cross predicts VIX elevation (confirmed in fin-vix-signal), but
SVXY is not a pure VIX inverse. It tracks short-term VIX futures, which have
daily roll yield (contango decay). In normal markets, SVXY drifts UP because of
this decay. A VIX spike must be large enough to overcome the structural upward
drift of SVXY during the hold period.

Most BTC bearish crosses produce mild VIX elevation (5-15 point moves), not
the 20+ point spikes needed to make a 10-day SVXY short profitable.

## Cost was not the problem

Total cost per trade is only 0.14% (financing + commission). The gross return
is already negative at -1.03%. The edge simply does not exist on this instrument.

## Honesty battery

```
n=84
mean=-1.16%  median=-2.13%  win=42%
drop-top-5%=-2.60%
by-year positive 5/13
```

All three accept criteria fail (median, drop-top-5%). The strategy is rejected
at Step 4. No overfit analysis needed.

## Disposition

**Project killed.** The BTC timing signal is real but the cost geometry of SVXY
shorts does not capture it. The contango decay of the underlying works against
the short during mild volatility, which is what most signals produce.
