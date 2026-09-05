import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SCENARIOS_DATA_DIR = DATA_DIR / "scenarios"
MODELS_DIR = BASE_DIR / "ml" / "models"
DOCUMENTS_DIR = BASE_DIR / "rag" / "documents"

# Ensure runtime directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SCENARIOS_DATA_DIR, MODELS_DIR, DOCUMENTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Risk Policy Limits (Configurable Prototype Thresholds)
RISK_LIMITS = {
    "max_equity_allocation": 0.40,      # 40% maximum allocation to Equities
    "max_gold_allocation": 0.25,        # 25% maximum allocation to Gold
    "min_liquidity_ratio": 0.20,        # 20% minimum Liquid Asset Ratio
    "max_annualized_volatility": 0.15,  # 15% maximum annualized volatility
    "max_drawdown": 0.20,               # 20% maximum peak-to-trough drawdown
    "crisis_probability_trigger": 0.60, # 60% ML crisis detection threshold
}

# Composite Risk Score Calculation Weights (Sum = 1.0)
RISK_SCORE_WEIGHTS = {
    "concentration": 0.30,
    "volatility": 0.25,
    "liquidity": 0.20,
    "stress_loss": 0.25,
}

# Liquidity Tiers (Liquid Asset Ratio)
LIQUIDITY_THRESHOLDS = {
    "safe": 0.30,     # > 30% SAFE
    "warning": 0.20,  # 20% - 30% WARNING
    "breach": 0.20,   # < 20% BREACH
}

# Asset Universe Default Map
DEFAULT_ASSETS = ["NIFTY 50", "Gold", "Govt Bonds", "Cash", "Corporate Bonds", "Private Assets"]

# Annualization Factor for Daily Returns
TRADING_DAYS_PER_YEAR = 252

# Historical window used by the market analytics and crisis model.
MARKET_DATA_START_DATE = "2020-01-01"
MARKET_DATA_END_DATE = "2025-12-31"
ML_FEATURE_COLUMNS = [
    "nifty_return",
    "gold_return",
    "nifty_volatility_20d",
    "gold_volatility_20d",
    "nifty_drawdown_20d",
]
