# FINCAP GUARD — LIQUIDITY MANAGEMENT POLICY
Document ID: POL-LIQ-2026-V1
Classification: Confidential / Internal Liquidity Standard

## Section 1: Liquidity Tiers & High-Quality Liquid Assets (HQLA)
Liquidity risk refers to the inability to meet redemption demands or fund trading obligations without incurring punitive fire-sale haircuts. Assets are classified into three operational liquidity tiers:
- **Tier 1 (High Quality Liquid Assets - HQLA)**: Cash, Treasury Bills, Sovereign Government Bonds (G-Secs), and High-Volume Large-Cap ETFs (e.g., NIFTY 50 ETF). Liquidation horizon is within 0 to 2 business days with haircuts below 2.0%.
- **Tier 2 (Medium Liquidity)**: Investment Grade Corporate Bonds and Liquid Commodities (Physical 24K Gold). Liquidation horizon is 3 to 7 business days with haircuts between 3.0% and 8.0%.
- **Tier 3 (Illiquid / Alternative)**: Private Credit, Real Estate, and Unlisted Venture Assets. Liquidation horizon exceeds 30 business days with anticipated fire-sale haircuts between 20.0% and 35.0%.

## Section 2: Minimum Liquid Asset Ratio (LAR) Requirements
Every portfolio governed by FINCAP Guard must maintain an adequate liquidity buffer:
- **Minimum Mandatory Liquid Asset Ratio**: 20.0% of total portfolio valuation.
- **Target Safe Operating Buffer**: Greater than 30.0%.
- Portfolios with LAR between 20.0% and 30.0% are placed in a **WARNING** state.
- Any portfolio falling below 20.0% LAR constitutes a **CRITICAL LIQUIDITY BREACH**, prohibiting all non-liquid asset purchases.

## Section 3: Weighted Liquidation Days Ceiling
- The weighted average time to liquidate the portfolio must not exceed 5.0 business days under stressed market conditions.

## Section 4: Liquidity Stress Remediation Protocol
In the event of a liquidity breach:
1. Liquidations must prioritize high-haircut reduction or reallocating capital into cash and sovereign debt.
2. The Decision Engine must ensure that post-rebalance liquidity is elevated above the 25.0% stabilization mark.
