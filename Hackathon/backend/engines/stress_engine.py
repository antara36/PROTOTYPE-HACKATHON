import pandas as pd
import numpy as np
from pathlib import Path
from backend.config import SCENARIOS_DATA_DIR, RISK_LIMITS

class StressEngine:
    """
    Simulates portfolio behavior under severe historical and hypothetical market shocks:
    Market Crash, Inflation Shock, Interest Rate Shock, and Systemic Liquidity Crisis.
    """
    def __init__(self, scenarios_path=None):
        self.scenarios_path = scenarios_path or (SCENARIOS_DATA_DIR / "stress_scenarios.csv")
        self.scenarios_df = self._load_scenarios()

    def _load_scenarios(self) -> pd.DataFrame:
        if self.scenarios_path.exists():
            return pd.read_csv(self.scenarios_path)
        else:
            # Fallback scenario table
            data = [
                {"Scenario": "Market Crash", "NIFTY 50": -0.20, "Gold": 0.05, "Govt Bonds": -0.05, "Cash": 0.00, "Corporate Bonds": -0.08, "Private Assets": -0.15, "Description": "Severe equity crash with flight to safety"},
                {"Scenario": "Inflation Shock", "NIFTY 50": -0.10, "Gold": 0.08, "Govt Bonds": -0.07, "Cash": -0.02, "Corporate Bonds": -0.05, "Private Assets": -0.08, "Description": "Surging inflation causing yield spikes"},
                {"Scenario": "Rate Shock", "NIFTY 50": -0.10, "Gold": -0.02, "Govt Bonds": -0.12, "Cash": 0.00, "Corporate Bonds": -0.10, "Private Assets": -0.05, "Description": "Rapid monetary tightening tightening"},
                {"Scenario": "Liquidity Crisis", "NIFTY 50": -0.15, "Gold": -0.05, "Govt Bonds": -0.10, "Cash": -0.20, "Corporate Bonds": -0.18, "Private Assets": -0.30, "Description": "Systemic funding and redemption crunch"}
            ]
            return pd.DataFrame(data)

    def get_available_scenarios(self) -> list:
        return self.scenarios_df["Scenario"].tolist()

    def run_stress_test(self, portfolio_df: pd.DataFrame, scenario_name: str = "Market Crash") -> dict:
        """
        Applies scenario shocks to current portfolio holdings.
        """
        match = self.scenarios_df[self.scenarios_df["Scenario"] == scenario_name]
        if match.empty:
            match = self.scenarios_df.iloc[[0]]
            scenario_name = match.iloc[0]["Scenario"]

        row = match.iloc[0]
        description = row.get("Description", "")
        
        df = portfolio_df.copy()
        original_total = float(df["Amount_INR"].sum())
        
        shocks = []
        stressed_amounts = []
        impact_amounts = []

        for _, asset_row in df.iterrows():
            asset = asset_row["Asset"]
            amount = float(asset_row["Amount_INR"])
            
            # Lookup shock from scenario row
            if asset in row:
                shock_pct = float(row[asset])
            elif "NIFTY" in asset or "Equity" in asset:
                shock_pct = float(row.get("NIFTY 50", -0.15))
            elif "Gold" in asset:
                shock_pct = float(row.get("Gold", 0.02))
            elif "Govt" in asset or "Bond" in asset:
                shock_pct = float(row.get("Govt Bonds", -0.06))
            elif "Cash" in asset:
                shock_pct = float(row.get("Cash", 0.00))
            else:
                shock_pct = -0.10

            stressed_amt = max(0.0, amount * (1.0 + shock_pct))
            impact_amt = stressed_amt - amount

            shocks.append(shock_pct)
            stressed_amounts.append(stressed_amt)
            impact_amounts.append(impact_amt)

        df["Shock_Pct"] = shocks
        df["Stressed_Amount_INR"] = stressed_amounts
        df["Impact_INR"] = impact_amounts

        stressed_total = float(df["Stressed_Amount_INR"].sum())
        total_loss_inr = stressed_total - original_total
        loss_pct = (total_loss_inr / original_total) if original_total > 0 else 0.0

        if stressed_total > 0:
            df["Stressed_Allocation_Pct"] = df["Stressed_Amount_INR"] / stressed_total
        else:
            df["Stressed_Allocation_Pct"] = 0.0

        # Check limit breach post-stress
        equity_stressed_pct = float(df[df["Asset_Class"] == "Equity"]["Stressed_Allocation_Pct"].sum())
        is_stress_breach = abs(loss_pct) > 0.12 or equity_stressed_pct > RISK_LIMITS["max_equity_allocation"]

        return {
            "scenario": scenario_name,
            "description": description,
            "original_total": original_total,
            "stressed_total": stressed_total,
            "total_loss_inr": total_loss_inr,
            "loss_pct": loss_pct,
            "is_stress_breach": is_stress_breach,
            "asset_breakdown": df[["Asset", "Amount_INR", "Shock_Pct", "Stressed_Amount_INR", "Impact_INR", "Stressed_Allocation_Pct"]].to_dict(orient="records")
        }

    def run_all_scenarios(self, portfolio_df: pd.DataFrame) -> list:
        """
        Runs full matrix of available scenarios for comprehensive risk reporting.
        """
        results = []
        for sc in self.get_available_scenarios():
            results.append(self.run_stress_test(portfolio_df, sc))
        return results
