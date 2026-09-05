import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

from backend.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    TRADING_DAYS_PER_YEAR,
    MARKET_DATA_START_DATE,
    MARKET_DATA_END_DATE,
)

class MarketDataService:
    """
    Handles ingestion, generation, date-alignment, returns, and volatility 
    calculations for NIFTY 50 and Gold historical datasets.
    """
    def __init__(self):
        self.nifty_raw_path = RAW_DATA_DIR / "nifty50.csv"
        self.gold_raw_path = RAW_DATA_DIR / "gold.csv"
        self.crisis_raw_path = RAW_DATA_DIR / "financial_crisis.csv"
        
        self.nifty_returns_path = PROCESSED_DATA_DIR / "nifty_returns.csv"
        self.gold_returns_path = PROCESSED_DATA_DIR / "gold_returns.csv"
        self.aligned_returns_path = PROCESSED_DATA_DIR / "aligned_returns.csv"
        self.market_features_path = PROCESSED_DATA_DIR / "market_features.csv"

    def ensure_datasets_exist(self):
        """Ensure the generated market sources cover the configured analysis window."""
        if not self.nifty_raw_path.exists() or not self._covers_analysis_window(self.nifty_raw_path):
            self._generate_synthetic_nifty()
        if not self.gold_raw_path.exists() or not self._covers_analysis_window(self.gold_raw_path):
            self._generate_synthetic_gold()
        if not self.crisis_raw_path.exists():
            self._generate_synthetic_crisis_dataset()

    @staticmethod
    def _covers_analysis_window(file_path):
        dates = pd.read_csv(file_path, usecols=["Date"], parse_dates=["Date"])["Date"]
        return dates.min() <= pd.Timestamp(MARKET_DATA_START_DATE) and dates.max() >= pd.Timestamp(MARKET_DATA_END_DATE)

    def _generate_synthetic_nifty(self):
        """Generates realistic NIFTY 50 OHLCV data from 2000 to early 2026."""
        np.random.seed(42)
        dates = pd.date_range(start="2000-01-03", end="2026-03-01", freq="B")
        n_days = len(dates)
        
        # Drift and volatility parameters for Indian Equities
        mu = 0.12 / TRADING_DAYS_PER_YEAR
        sigma = 0.20 / np.sqrt(TRADING_DAYS_PER_YEAR)
        
        daily_returns = np.random.normal(mu, sigma, n_days)
        # Inject historical shocks (2008 Lehman, 2020 Covid)
        for i, dt in enumerate(dates):
            if dt.year == 2008 and dt.month in [9, 10]:
                daily_returns[i] -= 0.015
            elif dt.year == 2020 and dt.month == 3:
                daily_returns[i] -= 0.02
        
        price_series = 1400.0 * np.exp(np.cumsum(daily_returns))
        
        high = price_series * (1 + np.abs(np.random.normal(0, 0.008, n_days)))
        low = price_series * (1 - np.abs(np.random.normal(0, 0.008, n_days)))
        open_p = price_series * (1 + np.random.normal(0, 0.004, n_days))
        volume = np.random.randint(50000000, 300000000, n_days)
        
        df = pd.DataFrame({
            "Date": dates.strftime("%Y-%m-%d"),
            "Open": np.round(open_p, 2),
            "High": np.round(high, 2),
            "Low": np.round(low, 2),
            "Close": np.round(price_series, 2),
            "Volume": volume
        })
        df.to_csv(self.nifty_raw_path, index=False)

    def _generate_synthetic_gold(self):
        """Generates synthetic Gold Price data covering the configured analysis window."""
        np.random.seed(101)
        dates = pd.date_range(start="2014-01-01", end=MARKET_DATA_END_DATE, freq="B")
        n_days = len(dates)
        
        mu = 0.09 / TRADING_DAYS_PER_YEAR
        sigma = 0.14 / np.sqrt(TRADING_DAYS_PER_YEAR)
        
        daily_returns = np.random.normal(mu, sigma, n_days)
        # Gold tends to spike during 2020 crisis
        for i, dt in enumerate(dates):
            if dt.year == 2020 and dt.month in [3, 4, 5]:
                daily_returns[i] += 0.005
                
        price_series = 28000.0 * np.exp(np.cumsum(daily_returns))
        
        df = pd.DataFrame({
            "Date": dates.strftime("%Y-%m-%d"),
            "Price": np.round(price_series, 2),
            "Open": np.round(price_series * (1 + np.random.normal(0, 0.003, n_days)), 2),
            "High": np.round(price_series * (1 + np.abs(np.random.normal(0, 0.005, n_days))), 2),
            "Low": np.round(price_series * (1 - np.abs(np.random.normal(0, 0.005, n_days))), 2),
        })
        df.to_csv(self.gold_raw_path, index=False)

    def _generate_synthetic_crisis_dataset(self):
        """
        Generates simulated Multi-Market Financial Crisis dataset matching Ziya07 Kaggle spec:
        ~3000 rows, stock, bond, FX indicators, volatility, VIX, and Crisis_Label.
        """
        np.random.seed(777)
        n_records = 3000
        
        # Simulate market regimes: 0 = Normal (75%), 1 = Crisis (25%)
        regimes = np.random.choice([0, 1], size=n_records, p=[0.78, 0.22])
        
        stock_returns = []
        stock_vols = []
        bond_yields = []
        bond_vols = []
        fx_returns = []
        fx_vols = []
        vix_values = []
        
        for r in regimes:
            if r == 0:  # Normal regime
                stock_returns.append(np.random.normal(0.0005, 0.009))
                stock_vols.append(np.random.uniform(0.10, 0.18))
                bond_yields.append(np.random.normal(0.045, 0.008))
                bond_vols.append(np.random.uniform(0.03, 0.07))
                fx_returns.append(np.random.normal(0.0001, 0.004))
                fx_vols.append(np.random.uniform(0.04, 0.09))
                vix_values.append(np.random.uniform(11.0, 22.0))
            else:  # Crisis regime
                stock_returns.append(np.random.normal(-0.003, 0.025))
                stock_vols.append(np.random.uniform(0.24, 0.65))
                bond_yields.append(np.random.normal(0.075, 0.020))
                bond_vols.append(np.random.uniform(0.09, 0.22))
                fx_returns.append(np.random.normal(-0.002, 0.015))
                fx_vols.append(np.random.uniform(0.12, 0.32))
                vix_values.append(np.random.uniform(28.0, 68.0))
                
        df = pd.DataFrame({
            "Stock_Return": np.round(stock_returns, 5),
            "Stock_Volatility": np.round(stock_vols, 4),
            "Bond_Yield": np.round(bond_yields, 4),
            "Bond_Volatility": np.round(bond_vols, 4),
            "FX_Return": np.round(fx_returns, 5),
            "FX_Volatility": np.round(fx_vols, 4),
            "VIX": np.round(vix_values, 2),
            "Crisis_Label": regimes
        })
        df.to_csv(self.crisis_raw_path, index=False)

    def load_and_process_market_data(self):
        """
        Loads NIFTY and Gold, finds common dates, computes returns and stats.
        """
        self.ensure_datasets_exist()
        
        nifty_df = pd.read_csv(self.nifty_raw_path)
        gold_df = pd.read_csv(self.gold_raw_path)
        
        nifty_df["Date"] = pd.to_datetime(nifty_df["Date"])
        gold_df["Date"] = pd.to_datetime(gold_df["Date"])
        
        nifty_df = nifty_df.sort_values("Date").dropna(subset=["Close"])
        gold_df = gold_df.sort_values("Date").dropna(subset=["Price"])

        start_date = pd.Timestamp(MARKET_DATA_START_DATE)
        end_date = pd.Timestamp(MARKET_DATA_END_DATE)
        nifty_df = nifty_df[nifty_df["Date"].between(start_date, end_date)].copy()
        gold_df = gold_df[gold_df["Date"].between(start_date, end_date)].copy()
        
        # Calculate daily returns
        nifty_df["NIFTY_Return"] = nifty_df["Close"].pct_change()
        gold_df["Gold_Return"] = gold_df["Price"].pct_change()
        
        # Save individual returns
        nifty_df[["Date", "Close", "NIFTY_Return"]].dropna().to_csv(self.nifty_returns_path, index=False)
        gold_df[["Date", "Price", "Gold_Return"]].dropna().to_csv(self.gold_returns_path, index=False)
        
        # Inner merge on Date to get aligned master data
        merged_df = pd.merge(
            nifty_df[["Date", "Close", "NIFTY_Return"]],
            gold_df[["Date", "Price", "Gold_Return"]],
            on="Date",
            how="inner"
        ).dropna()
        
        merged_df.to_csv(self.aligned_returns_path, index=False)
        return merged_df

    def get_market_statistics(self):
        """
        Calculates annualized metrics: return, volatility, correlation matrix,
        and covariance matrix for portfolio risk calculations.
        """
        aligned_df = self.load_and_process_market_data()
        
        nifty_ann_return = float(aligned_df["NIFTY_Return"].mean() * TRADING_DAYS_PER_YEAR)
        nifty_ann_vol = float(aligned_df["NIFTY_Return"].std() * np.sqrt(TRADING_DAYS_PER_YEAR))
        
        gold_ann_return = float(aligned_df["Gold_Return"].mean() * TRADING_DAYS_PER_YEAR)
        gold_ann_vol = float(aligned_df["Gold_Return"].std() * np.sqrt(TRADING_DAYS_PER_YEAR))
        
        correlation = float(aligned_df["NIFTY_Return"].corr(aligned_df["Gold_Return"]))
        
        stats = {
            "NIFTY 50": {
                "annualized_return": nifty_ann_return,
                "annualized_volatility": nifty_ann_vol,
                "data_points": len(aligned_df),
                "date_range": (str(aligned_df["Date"].min().date()), str(aligned_df["Date"].max().date()))
            },
            "Gold": {
                "annualized_return": gold_ann_return,
                "annualized_volatility": gold_ann_vol,
                "data_points": len(aligned_df),
                "date_range": (str(aligned_df["Date"].min().date()), str(aligned_df["Date"].max().date()))
            },
            "Govt Bonds": {
                "annualized_return": 0.071,
                "annualized_volatility": 0.045
            },
            "Cash": {
                "annualized_return": 0.045,
                "annualized_volatility": 0.005
            },
            "Corporate Bonds": {
                "annualized_return": 0.082,
                "annualized_volatility": 0.065
            },
            "Private Assets": {
                "annualized_return": 0.125,
                "annualized_volatility": 0.180
            },
            "nifty_gold_correlation": correlation
        }
        return stats

    def get_asset_covariance_matrix(self, assets):
        """
        Constructs an empirical/parametric annualized covariance matrix for requested asset universe.
        """
        stats = self.get_market_statistics()
        n = len(assets)
        cov_matrix = np.zeros((n, n))
        vols = [stats[a]["annualized_volatility"] if a in stats else 0.10 for a in assets]
        
        corr_matrix = np.eye(n)
        for i, a1 in enumerate(assets):
            for j, a2 in enumerate(assets):
                if i == j:
                    corr_matrix[i, j] = 1.0
                elif (a1 == "NIFTY 50" and a2 == "Gold") or (a1 == "Gold" and a2 == "NIFTY 50"):
                    corr_matrix[i, j] = stats["nifty_gold_correlation"]
                elif (a1 == "NIFTY 50" and "Bonds" in a2) or ("Bonds" in a1 and a2 == "NIFTY 50"):
                    corr_matrix[i, j] = 0.10
                elif (a1 == "Cash" or a2 == "Cash"):
                    corr_matrix[i, j] = 0.00
                elif (a1 == "NIFTY 50" and a2 == "Private Assets") or (a1 == "Private Assets" and a2 == "NIFTY 50"):
                    corr_matrix[i, j] = 0.45
                else:
                    corr_matrix[i, j] = 0.15
                    
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = corr_matrix[i, j] * vols[i] * vols[j]
                
        return pd.DataFrame(cov_matrix, index=assets, columns=assets)
