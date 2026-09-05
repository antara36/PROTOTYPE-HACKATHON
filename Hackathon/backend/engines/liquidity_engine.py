import pandas as pd
import numpy as np
from pathlib import Path
from backend.config import SCENARIOS_DATA_DIR, RISK_LIMITS, LIQUIDITY_THRESHOLDS

class LiquidityEngine:
    """
    Evaluates portfolio liquidity profile, liquid asset ratios (LAR), 
    weighted days to liquidate, and liquidity risk status against policy thresholds.
    """
    def __init__(self, liquidity_path=None):
        self.liquidity_path = liquidity_path or (SCENARIOS_DATA_DIR / "asset_liquidity.csv")
        self.liquidity_df = self._load_liquidity_data()

    def _load_liquidity_data(self) -> pd.DataFrame:
        if self.liquidity_path.exists():
            return pd.read_csv(self.liquidity_path)
        else:
            # Fallback default table
            data = [
                {"Asset": "NIFTY 50", "Asset_Class": "Equity", "Liquidity_Score": 0.95, "Is_Liquid": "Yes", "Liquidation_Days": 1, "Haircut_Pct": 0.02},
                {"Asset": "Gold", "Asset_Class": "Commodity", "Liquidity_Score": 0.85, "Is_Liquid": "Yes", "Liquidation_Days": 1, "Haircut_Pct": 0.03},
                {"Asset": "Govt Bonds", "Asset_Class": "Fixed Income", "Liquidity_Score": 0.90, "Is_Liquid": "Yes", "Liquidation_Days": 2, "Haircut_Pct": 0.01},
                {"Asset": "Cash", "Asset_Class": "Cash", "Liquidity_Score": 1.00, "Is_Liquid": "Yes", "Liquidation_Days": 0, "Haircut_Pct": 0.00},
                {"Asset": "Corporate Bonds", "Asset_Class": "Fixed Income", "Liquidity_Score": 0.60, "Is_Liquid": "Medium", "Liquidation_Days": 7, "Haircut_Pct": 0.08},
                {"Asset": "Private Assets", "Asset_Class": "Alternative", "Liquidity_Score": 0.10, "Is_Liquid": "No", "Liquidation_Days": 30, "Haircut_Pct": 0.25},
            ]
            return pd.DataFrame(data)

    def assess_liquidity(self, portfolio_df: pd.DataFrame) -> dict:
        """
        Assesses liquidity risk for given portfolio state.
        """
        df = portfolio_df.copy()
        
        # Merge portfolio with liquidity characteristics
        merged = pd.merge(df, self.liquidity_df, on="Asset", how="left")
        
        # Fill missing values with conservative illiquid defaults
        merged["Liquidity_Score"] = merged["Liquidity_Score"].fillna(0.30)
        merged["Is_Liquid"] = merged["Is_Liquid"].fillna("No")
        merged["Liquidation_Days"] = merged["Liquidation_Days"].fillna(15)
        merged["Haircut_Pct"] = merged["Haircut_Pct"].fillna(0.15)
        
        total_val = merged["Amount_INR"].sum()
        if total_val <= 0:
            return {"liquid_asset_ratio": 0.0, "status": "BREACH", "weighted_days": 0.0}

        # Liquid assets are defined as Is_Liquid == 'Yes' (High Quality Liquid Assets - HQLA proxy)
        liquid_assets = merged[merged["Is_Liquid"] == "Yes"]
        liquid_val = liquid_assets["Amount_INR"].sum()
        liquid_ratio = float(liquid_val / total_val)
        
        # Weighted days to fully liquidate portfolio
        weighted_days = float((merged["Allocation_Pct"] * merged["Liquidation_Days"]).sum())
        
        # Average liquidity score (0 to 1)
        weighted_score = float((merged["Allocation_Pct"] * merged["Liquidity_Score"]).sum())
        
        # Stressed liquidation value with haircuts
        stressed_liquid_val = (merged["Amount_INR"] * (1 - merged["Haircut_Pct"])).sum()
        haircut_loss_pct = float((total_val - stressed_liquid_val) / total_val)

        # Threshold tier check
        min_limit = RISK_LIMITS["min_liquidity_ratio"]
        safe_tier = LIQUIDITY_THRESHOLDS["safe"]
        warning_tier = LIQUIDITY_THRESHOLDS["warning"]

        if liquid_ratio >= safe_tier:
            status = "SAFE"
            severity = "info"
            message = f"Portfolio liquidity is healthy at {liquid_ratio*100:.1f}%, exceeding policy threshold (>30%)."
        elif liquid_ratio >= warning_tier:
            status = "WARNING"
            severity = "warning"
            message = f"Portfolio liquidity is in warning zone at {liquid_ratio*100:.1f}% (Policy limit: 20-30%)."
        else:
            status = "BREACH"
            severity = "error"
            message = f"CRITICAL: Liquid Asset Ratio ({liquid_ratio*100:.1f}%) breached minimum policy requirement ({min_limit*100:.0f}%)."

        return {
            "liquid_asset_ratio": liquid_ratio,
            "liquid_asset_value": float(liquid_val),
            "status": status,
            "severity": severity,
            "message": message,
            "min_required_ratio": min_limit,
            "weighted_liquidation_days": round(weighted_days, 1),
            "portfolio_liquidity_score": round(weighted_score, 3),
            "haircut_loss_pct": round(haircut_loss_pct * 100, 2),
            "asset_breakdown": merged[["Asset", "Allocation_Pct", "Is_Liquid", "Liquidity_Score", "Liquidation_Days"]].to_dict(orient="records")
        }
