# FINCAP GUARD — INSTITUTIONAL RISK & ALLOCATION POLICY
Document ID: POL-RISK-2026-V1
Classification: Confidential / Internal Compliance Standard

## Section 1: Executive Purpose & Scope
This Risk Policy defines the mandatory exposure ceilings, volatility thresholds, and capital safeguarding rules governing all investment portfolios managed under the FINCAP Guard control framework. All portfolio managers and automated execution algorithms must strictly adhere to these limits.

## Section 2: Asset Allocation Limits
To prevent catastrophic drawdowns arising from idiosyncratic shocks or systemic sector downturns, the following exposure caps are strictly enforced:
- **Maximum Equity Allocation**: 40.0% of total portfolio capital. Total exposure across large-cap, mid-cap, indices (such as NIFTY 50), and equities must not exceed this boundary under any normal operating conditions.
- **Maximum Commodity / Gold Allocation**: 25.0% of total capital. Gold serves as a flight-to-safety diversifier but carries carry costs and price volatility.
- **Single-Asset Concentration Cap**: No single equity or corporate security may represent more than 35.0% of total portfolio capital.
- **Fixed Income & Cash Floor**: A minimum combined allocation of 35.0% must be maintained in sovereign debt (Govt Bonds) and cash equivalents.

## Section 3: Portfolio Volatility Limits
Portfolio risk must be evaluated daily using an annualized covariance matrix computed over historical rolling return windows:
- **Maximum Annualized Volatility Ceiling**: 15.0%.
- Portfolios exhibiting annualized standard deviation between 12.0% and 15.0% enter an Elevated Alert state. Any portfolio exceeding 15.0% annualized volatility triggers an immediate Risk Breach alert requiring corrective rebalancing.

## Section 4: Maximum Drawdown Thresholds
- **Maximum Allowable Peak-to-Trough Drawdown**: 20.0%.
- If simulated or historical rolling drawdown exceeds 20.0%, the Investment Committee must be formally notified, and automated de-risking must be enacted.

## Section 5: Breach Remediation & Least-Disruptive Mandate
When a limit breach is detected by the Control Engine:
1. The system must immediately freeze new speculative allocations.
2. The portfolio manager must initiate rebalancing within 24 hours.
3. Remediation should prioritize the **least-disruptive corrective allocation** that achieves compliance with the lowest necessary turnover, avoiding excessive slippage and premature liquidations.
