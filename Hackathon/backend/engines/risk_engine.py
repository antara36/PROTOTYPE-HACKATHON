import pandas as pd
import numpy as np
from pathlib import Path
from backend.config import RISK_LIMITS, RISK_SCORE_WEIGHTS
from backend.services.market_data_service import MarketDataService
from backend.engines.liquidity_engine import LiquidityEngine

class RiskEngine:
    """
    Multi-factor risk assessment engine calculating concentration risk,
    historical volatility, maximum drawdown, liquidity risk, stress loss,
    and composite 0-100 risk score with automated breach detection.
    """
    def __init__(self, market_service=None, liquidity_engine=None):
        self.market_service = market_service or MarketDataService()
        self.liquidity_engine = liquidity_engine or LiquidityEngine()

    def calculate_concentration_risk(self, portfolio_df: pd.DataFrame) -> dict:
        """
        Assesses concentration risk per asset and per asset class against limits.
        """
        df = portfolio_df.copy()
        total_val = df["Amount_INR"].sum()
        if total_val <= 0:
            return {"breaches": [], "equity_exposure": 0.0, "status": "SAFE"}

        # Calculate asset-class aggregates
        equity_mask = df["Asset_Class"] == "Equity"
        equity_exposure = float(df.loc[equity_mask, "Allocation_Pct"].sum())
        
        gold_mask = df["Asset"].str.contains("Gold", case=False, na=False)
        gold_exposure = float(df.loc[gold_mask, "Allocation_Pct"].sum())
        
        breaches = []
        max_eq = RISK_LIMITS["max_equity_allocation"]
        max_gold = RISK_LIMITS["max_gold_allocation"]

        if equity_exposure > max_eq:
            breaches.append({
                "type": "CONCENTRATION_EQUITY",
                "asset_category": "Equity",
                "actual_value": equity_exposure,
                "limit_value": max_eq,
                "severity": "CRITICAL",
                "message": f"Equity exposure is {equity_exposure*100:.1f}%, exceeding the configured {max_eq*100:.0f}% policy cap."
            })

        if gold_exposure > max_gold:
            breaches.append({
                "type": "CONCENTRATION_GOLD",
                "asset_category": "Commodity (Gold)",
                "actual_value": gold_exposure,
                "limit_value": max_gold,
                "severity": "WARNING",
                "message": f"Gold exposure is {gold_exposure*100:.1f}%, exceeding the {max_gold*100:.0f}% cap."
            })

        # Single company asset concentration (> 35% single non-index asset)
        for _, row in df.iterrows():
            if row["Allocation_Pct"] > 0.35 and row["Asset"] not in ["Govt Bonds", "Cash", "NIFTY 50"]:
                breaches.append({
                    "type": "SINGLE_ASSET_CONCENTRATION",
                    "asset_category": row["Asset"],
                    "actual_value": float(row["Allocation_Pct"]),
                    "limit_value": 0.35,
                    "severity": "WARNING",
                    "message": f"Single-asset concentration in {row['Asset']} is {row['Allocation_Pct']*100:.1f}% (Policy guideline: 35%)."
                })

        return {
            "equity_exposure": equity_exposure,
            "gold_exposure": gold_exposure,
            "breaches": breaches,
            "status": "CRITICAL" if any(b["severity"] == "CRITICAL" for b in breaches) else ("WARNING" if breaches else "SAFE")
        }

    def calculate_volatility(self, portfolio_df: pd.DataFrame) -> dict:
        """
        Calculates annualized portfolio volatility using historical covariance matrix.
        sigma_p = sqrt(w.T * Sigma * w)
        """
        df = portfolio_df.copy()
        assets = df["Asset"].tolist()
        weights = df["Allocation_Pct"].to_numpy()

        cov_df = self.market_service.get_asset_covariance_matrix(assets)
        cov_matrix = cov_df.to_numpy()

        var_p = float(weights.T @ cov_matrix @ weights)
        vol_p = float(np.sqrt(max(0.0, var_p)))

        limit_vol = RISK_LIMITS["max_annualized_volatility"]
        is_breach = vol_p > limit_vol

        breaches = []
        if is_breach:
            breaches.append({
                "type": "PORTFOLIO_VOLATILITY",
                "actual_value": vol_p,
                "limit_value": limit_vol,
                "severity": "WARNING" if vol_p <= limit_vol * 1.2 else "CRITICAL",
                "message": f"Portfolio volatility is {vol_p*100:.2f}%, exceeding policy threshold ({limit_vol*100:.0f}%)."
            })

        return {
            "annualized_volatility": vol_p,
            "annualized_variance": var_p,
            "limit_volatility": limit_vol,
            "is_breach": is_breach,
            "breaches": breaches
        }

    def calculate_drawdown(self, portfolio_df: pd.DataFrame) -> dict:
        """
        Estimates historical peak-to-trough max drawdown from aligned historical returns.
        """
        aligned_df = self.market_service.load_and_process_market_data()
        
        # Portfolio daily returns proxy
        w_eq = float(portfolio_df[portfolio_df["Asset_Class"] == "Equity"]["Allocation_Pct"].sum())
        w_gold = float(portfolio_df[portfolio_df["Asset"].str.contains("Gold", case=False, na=False)]["Allocation_Pct"].sum())
        w_other = max(0.0, 1.0 - w_eq - w_gold)
        
        # Daily return series
        daily_ret = (
            w_eq * aligned_df["NIFTY_Return"] +
            w_gold * aligned_df["Gold_Return"] +
            w_other * (0.065 / 252.0)
        )
        
        cum_ret = (1 + daily_ret).cumprod()
        running_max = cum_ret.cummax()
        drawdown = (cum_ret - running_max) / running_max
        max_dd = float(abs(drawdown.min()))
        current_dd = float(abs(drawdown.iloc[-1])) if not drawdown.empty else 0.0

        limit_dd = RISK_LIMITS["max_drawdown"]
        is_breach = max_dd > limit_dd

        breaches = []
        if is_breach:
            breaches.append({
                "type": "MAX_DRAWDOWN",
                "actual_value": max_dd,
                "limit_value": limit_dd,
                "severity": "WARNING",
                "message": f"Estimated historical drawdown is {max_dd*100:.1f}%, exceeding policy limit ({limit_dd*100:.0f}%)."
            })

        return {
            "max_drawdown": max_dd,
            "current_drawdown": current_dd,
            "limit_drawdown": limit_dd,
            "is_breach": is_breach,
            "breaches": breaches,
            "drawdown_series": pd.DataFrame({"Date": aligned_df["Date"], "Drawdown": drawdown}).tail(500).to_dict(orient="records")
        }

    def calculate_composite_risk_score(self, concentration_data: dict, vol_data: dict, 
                                      liquidity_data: dict, stress_loss_pct: float = 0.09) -> dict:
        """
        Computes composite 0-100 prototype risk score:
        Risk Score = 30% concentration + 25% volatility + 20% liquidity + 25% stress loss
        """
        # 1. Concentration sub-score (0-100)
        eq_exp = concentration_data.get("equity_exposure", 0.40)
        # 0.20 or lower -> 10, 0.40 -> 50, 0.60+ -> 100
        score_conc = np.clip(((eq_exp - 0.20) / (0.60 - 0.20)) * 90 + 10, 5, 100)

        # 2. Volatility sub-score (0-100)
        vol = vol_data.get("annualized_volatility", 0.12)
        # 0.06 -> 20, 0.15 -> 60, 0.25+ -> 100
        score_vol = np.clip(((vol - 0.06) / (0.24 - 0.06)) * 80 + 20, 5, 100)

        # 3. Liquidity sub-score (0-100, higher means higher risk / lower liquidity)
        lar = liquidity_data.get("liquid_asset_ratio", 0.30)
        # lar >= 0.50 -> 10, lar == 0.20 -> 60, lar <= 0.05 -> 100
        score_liq = np.clip(((0.50 - lar) / (0.50 - 0.05)) * 90 + 10, 5, 100)

        # 4. Stress loss sub-score (0-100)
        loss = abs(stress_loss_pct)
        # loss 0.02 -> 15, loss 0.10 -> 65, loss 0.20+ -> 100
        score_stress = np.clip(((loss - 0.02) / (0.20 - 0.02)) * 85 + 15, 5, 100)

        weights = RISK_SCORE_WEIGHTS
        composite_score = float(
            weights["concentration"] * score_conc +
            weights["volatility"] * score_vol +
            weights["liquidity"] * score_liq +
            weights["stress_loss"] * score_stress
        )

        composite_score = round(float(np.clip(composite_score, 0, 100)), 1)

        if composite_score >= 65:
            rating = "HIGH RISK"
            badge = "CRITICAL 🔴"
            color = "#EF4444"
        elif composite_score >= 40:
            rating = "MODERATE RISK"
            badge = "WARNING 🟡"
            color = "#F59E0B"
        else:
            rating = "LOW RISK"
            badge = "SAFE 🟢"
            color = "#10B981"

        return {
            "composite_score": composite_score,
            "rating": rating,
            "badge": badge,
            "color": color,
            "sub_scores": {
                "concentration": round(float(score_conc), 1),
                "volatility": round(float(score_vol), 1),
                "liquidity": round(float(score_liq), 1),
                "stress_loss": round(float(score_stress), 1)
            },
            "weights": weights
        }

    def evaluate_portfolio(self, portfolio_df: pd.DataFrame, stress_loss_pct: float = 0.09) -> dict:
        """
        Master risk assessment combining all risk dimensions and compiling breach reports.
        """
        conc_data = self.calculate_concentration_risk(portfolio_df)
        vol_data = self.calculate_volatility(portfolio_df)
        dd_data = self.calculate_drawdown(portfolio_df)
        liq_data = self.liquidity_engine.assess_liquidity(portfolio_df)
        score_data = self.calculate_composite_risk_score(conc_data, vol_data, liq_data, stress_loss_pct)

        all_breaches = []
        all_breaches.extend(conc_data.get("breaches", []))
        all_breaches.extend(vol_data.get("breaches", []))
        all_breaches.extend(dd_data.get("breaches", []))
        if liq_data.get("status") in ["BREACH", "WARNING"]:
            all_breaches.append({
                "type": "LIQUIDITY_LIMIT",
                "actual_value": liq_data["liquid_asset_ratio"],
                "limit_value": liq_data["min_required_ratio"],
                "severity": "CRITICAL" if liq_data["status"] == "BREACH" else "WARNING",
                "message": liq_data["message"]
            })

        has_critical_breach = any(b["severity"] == "CRITICAL" for b in all_breaches)
        has_warning = any(b["severity"] == "WARNING" for b in all_breaches)

        if has_critical_breach:
            system_status = "BREACH"
        elif has_warning:
            system_status = "WARNING"
        else:
            system_status = "SAFE"

        return {
            "system_status": system_status,
            "breach_count": len(all_breaches),
            "breaches": all_breaches,
            "composite_score": score_data,
            "concentration": conc_data,
            "volatility": vol_data,
            "drawdown": dd_data,
            "liquidity": liq_data
        }
