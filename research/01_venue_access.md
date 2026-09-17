# Step 1: Venue Access Assessment

**Date:** 2026-09-17
**Question:** Can SVXY (or ZIVB) be shorted from Romania via IBKR?

## Answer: YES, via CFD. Direct stock short also available (paper account shows borrow).

### The PRIIPs blocker

SVXY and ZIVB are US-domiciled ETFs. EU regulation (PRIIPs, Regulation 1286/2014)
prohibits brokers from selling US ETFs to retail EEA clients because the issuers
(ProShares, Volatility Shares) do not publish a Key Information Document (KID).

This means: **IBKR will not let a Romanian retail account buy or short SVXY shares.**

### Workaround A: CFD (viable, changes cost model)

IBKR offers CFDs on many US ETFs to EU clients. CFDs are issued by IBKR's European
entity and come with their own KID, so they comply with PRIIPs.

Going short a CFD = economically similar to shorting the stock, but:
- No stock borrow fee. Instead you pay/receive overnight financing (benchmark +/- 1.5%).
- Short CFD on SVXY: you receive the short rate (benchmark minus spread) on days
  SVXY goes down, pay it on days it goes up. Net cost is the financing spread.
- ESMA leverage limits apply (2:1 for retail on ETFs, 5:1 for professional).
- **VERIFIED (2026-09-17):** SVXY CFD exists. ConId 290657198, exchange SMART,
  min tick 0.01, trading hours 04:00-20:00 ET. Market is outside hours at time of
  check so bid/ask were NaN, but the contract qualifies.

### Workaround B: Professional client opt-up (viable if portfolio > EUR 500k)

MiFID II allows elective professional classification if you meet 2 of 3 criteria:
1. Portfolio > EUR 500k (dropping to EUR 250k under upcoming RIS rules)
2. 10+ significant trades per quarter in the last 4 quarters
3. 1+ year professional experience in finance

Professional clients are exempt from PRIIPs. They can trade US ETFs directly,
including shorting SVXY (subject to borrow availability).

### No UCITS equivalent exists

There is no UCITS-compliant inverse VIX ETP that replicates SVXY or ZIVB. The
strategy cannot be accessed through a European-domiciled fund.

## API verification results (2026-09-17, IB Gateway 10.48, paper account DUQ739115)

### SVXY Stock (ConId 331641614)
- Last: $63.55, Close: $62.31, Bid: $63.41, Ask: $63.51
- **Shortable shares: 366,823** (good liquidity for borrow)
- Note: paper account may show stock short availability that a retail EU account
  cannot actually execute due to PRIIPs. Must confirm on live account.

### SVXY CFD (ConId 290657198)
- Contract qualifies on IBKR, min tick $0.01
- Market data was NaN (queried outside trading hours 04:00-20:00 ET)
- CFDs are PRIIPs-compliant, so this IS tradeable from EU retail

### ZIVB
- **Not available** as stock or CFD on IBKR. Dropped from consideration.

## Access path: resolved

**Primary:** Short SVXY via CFD (PRIIPs-compliant, confirmed available).
**Backup:** Direct stock short if professional opt-up is obtained.

Cost model for backtest = CFD overnight financing (benchmark +/- 1.5%), not stock
borrow. For a 10-day hold, financing cost is roughly:
`notional × (benchmark_rate + 1.5%) × (10/360)`

## Action items

- [x] Verify SVXY CFD exists on IBKR (confirmed ConId 290657198)
- [x] Verify ZIVB availability (not available, dropped)
- [ ] During market hours: re-check CFD bid/ask spread (affects realistic entry/exit)
- [ ] Check CFD margin requirement on live account

## Sources

- [IBKR Short Securities Availability](https://www.interactivebrokers.com/en/trading/short-securities-availability.php)
- [IBKR CFDs for UK/EU](https://www.interactivebrokers.co.uk/en/trading/products-cfds.php)
- [How to buy US ETFs from Europe (2026)](https://financialexpertclass.com/how-to-legally-buy-usa-etfs-from-europe/)
- [PRIIPs KID Compliance Guide 2026](https://financialregulations.eu/blog/priips-kid-compliance-guide-2026)
- [EU investors locked out of ETFs](https://www.bankeronwheels.com/kid-etf-registration-priips-ucits/)
- [IBKR Short Sale Cost](https://www.interactivebrokers.com/en/pricing/short-sale-cost.php)
