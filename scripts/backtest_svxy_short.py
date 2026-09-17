#!/usr/bin/env python3
"""Backtest: short SVXY CFD on BTC EMA 9/21 bearish cross, hold N days.

Step 2 (cost model) + Step 4 (honest backtest) combined.

CFD cost model (IBKR EU retail):
  - Commission: 0.5 cents/share each way = ~1.6 bp round-trip at $63
  - Overnight financing: (benchmark + 1.5%) * notional * days/360
    Using Fed Funds as benchmark proxy (yfinance: ^IRX for 3-month T-bill).
    For a SHORT CFD, you PAY the financing spread (benchmark + 1.5%).
  - No stock borrow fee on a CFD.

Pre-registered parameters (from README.md, do NOT change after seeing results):
  - Signal: BTC EMA 9/21 bearish cross
  - Hold: 10 trading days
  - Entry: short SVXY at next open after signal
  - Exit: cover at close on day 10
  - Accept: median R > 0, drop-top-5% R > 0, all years >= -1.0R
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_signals import fetch, ema_cross_signals
from quant_honesty import honesty, format_report, screen

DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

HOLD_DAYS = 10
COMMISSION_BPS = 1.6  # 0.5c/share each way at ~$63
FINANCING_SPREAD = 0.015  # 1.5% above benchmark


def get_fed_funds_proxy(start):
    """Use 3-month T-bill yield as overnight rate proxy."""
    irx = yf.download("^IRX", start=start, auto_adjust=True, progress=False)
    if isinstance(irx.columns, pd.MultiIndex):
        irx.columns = irx.columns.droplevel(1)
    rate = irx["Close"].dropna() / 100  # IRX is in percent
    return rate


def main():
    print("=" * 60)
    print("SVXY SHORT BACKTEST — BTC EMA 9/21 BEARISH CROSS")
    print("=" * 60)

    # --- Step 0: Screen ---
    # For a CFD short with no stop (hold 10 days, accept any outcome),
    # the "stop" is the max adverse move. SVXY can move ~15-20% in 10 days
    # during vol events, so use 20% as the risk unit.
    # Expected gross: unknown, estimate ~3% from VIX spike literature.
    # This is a rough screen, the backtest is the real test.
    print("\n--- VIABILITY SCREEN (rough) ---")
    s = screen(gross_r=0.03 / 0.20, fee_bps=COMMISSION_BPS, slip_bps=2.0, stop_pct=0.20)
    print(f"  Leverage: {s['leverage']:.1f}x")
    print(f"  Cost per trade: {s['cost_r']:.4f} R")
    print(f"  Required gross: {s['required_r']:.4f} R")
    print(f"  Screen: {'PASS' if s['pass'] else 'FAIL'}")
    print(f"  (Using 20% as risk unit, 3% estimated gross)")

    # --- Fetch data ---
    print("\nFetching BTC-USD...")
    btc = fetch("BTC-USD", "2012-01-01")

    print("Fetching SVXY...")
    svxy_raw = yf.download("SVXY", start="2011-10-01", auto_adjust=True, progress=False)
    if isinstance(svxy_raw.columns, pd.MultiIndex):
        svxy_raw.columns = svxy_raw.columns.droplevel(1)
    svxy_open = svxy_raw["Open"].dropna()
    svxy_close = svxy_raw["Close"].dropna()

    print("Fetching Fed Funds proxy (^IRX)...")
    ff_rate = get_fed_funds_proxy("2011-10-01")

    # --- Generate signals ---
    signals = ema_cross_signals(btc)
    bearish = signals[signals["signal"] == "bearish_cross"].copy()
    print(f"\nBearish crosses: {len(bearish)}")
    print(f"Date range: {bearish.index[0].date()} to {bearish.index[-1].date()}")

    # --- Backtest ---
    trades = []
    svxy_dates = svxy_close.index

    for sig_date in bearish.index:
        # Entry: next trading day's open
        future_dates = svxy_dates[svxy_dates > sig_date]
        if len(future_dates) < HOLD_DAYS + 1:
            continue

        entry_date = future_dates[0]
        exit_date = future_dates[HOLD_DAYS]

        if entry_date not in svxy_open.index or exit_date not in svxy_close.index:
            continue

        entry_price = svxy_open.loc[entry_date]
        exit_price = svxy_close.loc[exit_date]

        # Short return: (entry - exit) / entry
        gross_return = (entry_price - exit_price) / entry_price

        # CFD financing cost: (benchmark + 1.5%) * (hold_days / 360)
        # Use the rate on entry date, forward-filled
        ff_aligned = ff_rate.reindex(svxy_dates, method="ffill")
        if entry_date in ff_aligned.index:
            benchmark = float(ff_aligned.loc[entry_date])
        else:
            benchmark = 0.05  # fallback
        financing_cost = (benchmark + FINANCING_SPREAD) * (HOLD_DAYS / 360)

        # Commission cost
        commission_cost = COMMISSION_BPS * 2 * 1e-4  # round-trip in decimal

        total_cost = financing_cost + commission_cost
        net_return = gross_return - total_cost

        trades.append({
            "signal_date": sig_date.date(),
            "entry_date": entry_date.date(),
            "exit_date": exit_date.date(),
            "entry_price": float(entry_price),
            "exit_price": float(exit_price),
            "gross_return": float(gross_return),
            "benchmark_rate": benchmark,
            "financing_cost": financing_cost,
            "commission_cost": commission_cost,
            "total_cost": total_cost,
            "net_return": float(net_return),
            "year": entry_date.year,
        })

    df = pd.DataFrame(trades)
    df.to_csv(DATA / "svxy_short_trades.csv", index=False)
    print(f"\nTrades executed: {len(df)}")
    print(f"Trade date range: {df['entry_date'].iloc[0]} to {df['entry_date'].iloc[-1]}")

    # --- Step 2: Cost summary ---
    print("\n--- COST MODEL (Step 2) ---")
    print(f"  Mean benchmark rate: {df['benchmark_rate'].mean():.3f}")
    print(f"  Mean financing cost per trade: {df['financing_cost'].mean():.4f} ({df['financing_cost'].mean()*100:.2f}%)")
    print(f"  Commission per trade: {df['commission_cost'].iloc[0]:.4f} ({df['commission_cost'].iloc[0]*100:.2f}%)")
    print(f"  Mean total cost per trade: {df['total_cost'].mean():.4f} ({df['total_cost'].mean()*100:.2f}%)")

    # --- Step 4: Honesty battery ---
    print("\n--- GROSS RETURNS ---")
    gross = df["gross_return"].values
    by_year_gross = {y: g["gross_return"].values for y, g in df.groupby("year")}
    h_gross = honesty(gross * 100, by_year={y: v * 100 for y, v in by_year_gross.items()})
    print(format_report(h_gross, unit="%"))

    print("\n--- NET RETURNS (after CFD costs) ---")
    net = df["net_return"].values
    by_year_net = {y: g["net_return"].values for y, g in df.groupby("year")}
    h_net = honesty(net * 100, by_year={y: v * 100 for y, v in by_year_net.items()})
    print(format_report(h_net, unit="%"))

    # --- Accept/reject ---
    print("\n--- ACCEPT/REJECT CRITERIA ---")
    median_ok = h_net["median"] > 0
    drop5_ok = h_net["drop5"] > 0
    # "all years >= -1.0R" — R is the risk unit (20%), so -1R = -20%
    worst_year = min(np.mean(v) for v in by_year_net.values()) * 100 if by_year_net else float("nan")
    years_ok = worst_year >= -20.0  # -1R in percent terms
    underpowered = h_net["underpowered"]

    print(f"  Median net > 0: {median_ok} (median = {h_net['median']:+.2f}%)")
    print(f"  Drop-top-5% net > 0: {drop5_ok} (drop5 = {h_net['drop5']:+.2f}%)")
    print(f"  Worst year mean >= -20%: {years_ok} (worst = {worst_year:+.2f}%)")
    print(f"  Underpowered (n < 60): {underpowered}")
    print(f"  Gross/cost ratio: {abs(h_gross['mean']) / (df['total_cost'].mean() * 100):.1f}x (need >= 3x)")

    all_pass = median_ok and drop5_ok and years_ok
    if underpowered:
        print(f"\n  VERDICT: UNRESOLVABLE — only {h_net['n']} trades, need 60+")
    elif all_pass:
        print("\n  VERDICT: PASS — proceed to Step 5 (overfit gate)")
    else:
        print("\n  VERDICT: REJECT — strategy does not survive honesty battery")

    # --- Per-year breakdown ---
    print("\n--- PER-YEAR BREAKDOWN ---")
    print(f"  {'Year':>6}  {'N':>3}  {'Gross%':>8}  {'Net%':>8}  {'Cost%':>7}")
    for y in sorted(by_year_net.keys()):
        n = len(by_year_net[y])
        gm = np.mean(by_year_gross[y]) * 100
        nm = np.mean(by_year_net[y]) * 100
        cm = np.mean(df[df["year"] == y]["total_cost"]) * 100
        print(f"  {y:>6}  {n:>3}  {gm:>+8.2f}  {nm:>+8.2f}  {cm:>7.3f}")

    print(f"\n  Saved: data/svxy_short_trades.csv ({len(df)} trades)")


if __name__ == "__main__":
    main()
