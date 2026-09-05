import pandas as pd
import numpy as np
from pathlib import Path
from backend.config import PROCESSED_DATA_DIR, SCENARIOS_DATA_DIR

class PortfolioEngine:
    """
    Manages portfolio holdings, capital valuation, asset weights, 
    and asset class categorization.
    """
    def __init__(self, portfolio_path=None):
        self.portfolio_path = portfolio_path or (PROCESSED_DATA_DIR / "portfolio_data.csv")
        self.liquidity_ref_path = SCENARIOS_DATA_DIR / "asset_liquidity.csv"
        self._load_metadata()

    def _load_metadata(self):
        if self.liquidity_ref_path.exists():
            self.metadata_df = pd.read_csv(self.liquidity_ref_path)
        else:
            self.metadata_df = pd.DataFrame()

    def get_asset_class(self, asset_name: str) -> str:
        if not self.metadata_df.empty and "Asset" in self.metadata_df.columns:
            match = self.metadata_df[self.metadata_df["Asset"] == asset_name]
            if not match.empty:
                return match.iloc[0]["Asset_Class"]
        # Fallback heuristic
        if "NIFTY" in asset_name or "Equity" in asset_name:
            return "Equity"
        elif "Gold" in asset_name or "Silver" in asset_name:
            return "Commodity"
        elif "Bond" in asset_name or "G-Sec" in asset_name:
            return "Fixed Income"
        elif "Cash" in asset_name or "Liquid" in asset_name:
            return "Cash"
        else:
            return "Alternative"

    def load_portfolio(self) -> pd.DataFrame:
        if self.portfolio_path.exists():
            df = pd.read_csv(self.portfolio_path)
            return self.calculate_portfolio_state(df)
        else:
            # Default institutional portfolio: ₹1 Cr with Equity breach (48%)
            default_data = [
                {"Asset": "NIFTY 50", "Amount_INR": 4800000.0},
                {"Asset": "Gold", "Amount_INR": 1500000.0},
                {"Asset": "Govt Bonds", "Amount_INR": 2200000.0},
                {"Asset": "Cash", "Amount_INR": 1500000.0},
            ]
            df = pd.DataFrame(default_data)
            return self.calculate_portfolio_state(df)

    def calculate_portfolio_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates amounts, computes weights and asset classes.
        """
        df = df.copy()
        if "Amount_INR" not in df.columns:
            raise ValueError("Portfolio DataFrame must contain 'Amount_INR' column.")
            
        df["Amount_INR"] = pd.to_numeric(df["Amount_INR"], errors="coerce").fillna(0.0)
        total_val = df["Amount_INR"].sum()
        
        if total_val <= 0:
            df["Allocation_Pct"] = 0.0
        else:
            df["Allocation_Pct"] = df["Amount_INR"] / total_val
            
        df["Asset_Class"] = df["Asset"].apply(self.get_asset_class)
        return df

    def get_summary(self, df: pd.DataFrame) -> dict:
        state = self.calculate_portfolio_state(df)
        total_capital = float(state["Amount_INR"].sum())
        
        # Asset class grouping
        class_group = state.groupby("Asset_Class")["Allocation_Pct"].sum().to_dict()
        
        # Format Indian Rupee currency (e.g., ₹1.00 Cr, ₹48.00 Lakhs)
        if total_capital >= 1e7:
            formatted_capital = f"₹{total_capital / 1e7:.2f} Cr"
        elif total_capital >= 1e5:
            formatted_capital = f"₹{total_capital / 1e5:.2f} Lakhs"
        else:
            formatted_capital = f"₹{total_capital:,.2f}"

        return {
            "total_capital": total_capital,
            "formatted_capital": formatted_capital,
            "holdings": state.to_dict(orient="records"),
            "weights": dict(zip(state["Asset"], state["Allocation_Pct"])),
            "asset_class_breakdown": class_group,
            "num_assets": len(state)
        }

    def save_portfolio(self, df: pd.DataFrame):
        state = self.calculate_portfolio_state(df)
        state[["Asset", "Amount_INR", "Allocation_Pct"]].to_csv(self.portfolio_path, index=False)
