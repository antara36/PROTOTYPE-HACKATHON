import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from backend.config import (
    MARKET_DATA_END_DATE,
    MARKET_DATA_START_DATE,
    ML_FEATURE_COLUMNS,
    PROCESSED_DATA_DIR,
    TRADING_DAYS_PER_YEAR,
)


def _load_market_features():
    # Refresh the derived file from the configured raw market sources before
    # training or inference so a stale artifact cannot leak into the dashboard.
    from backend.services.market_data_service import MarketDataService

    MarketDataService().load_and_process_market_data()
    file_path = PROCESSED_DATA_DIR / "aligned_returns.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Processed dataset missing at: {file_path}")

    df = pd.read_csv(file_path, parse_dates=["Date"])
    df = df[df["Date"].between(MARKET_DATA_START_DATE, MARKET_DATA_END_DATE)].copy()
    df = df.sort_values("Date")

    df["nifty_return"] = df["NIFTY_Return"]
    df["gold_return"] = df["Gold_Return"]
    df["nifty_volatility_20d"] = (
        df["nifty_return"].rolling(20).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    )
    df["gold_volatility_20d"] = (
        df["gold_return"].rolling(20).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    )
    df["nifty_drawdown_20d"] = df["Close"] / df["Close"].rolling(20).max() - 1

    # Predict a forward stress event so the target is not copied from the input features.
    df["forward_20d_return"] = df["Close"].shift(-20) / df["Close"] - 1
    df["crisis_event"] = (df["forward_20d_return"] <= -0.10).astype(int)
    return df.dropna(subset=ML_FEATURE_COLUMNS + ["forward_20d_return"])

def load_and_prepare_crisis_data():
    """
    Loads processed market datasets, computes features, and returns scaled splits with fitted scaler.
    """
    df = _load_market_features()
    feature_names = ML_FEATURE_COLUMNS.copy()
    X = df[feature_names]
    y = df["crisis_event"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return {
        "X_train_scaled": X_train_scaled,
        "X_test_scaled": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "scaler": scaler,
        "feature_names": feature_names
    }


def get_latest_market_features():
    """Return the latest real market observation used by the trained model."""
    latest = _load_market_features().iloc[-1]
    return {column: float(latest[column]) for column in ML_FEATURE_COLUMNS}


def get_market_data_period():
    """Return the actual dates represented by the rows used for model training."""
    df = _load_market_features()
    return str(df["Date"].min().date()), str(df["Date"].max().date())

def prepare_inference_features(input_data: dict, scaler, feature_names: list):
    """
    Converts live API payloads into scaled feature arrays matching model training.
    """
    df = pd.DataFrame([input_data])
    
    missing = [col for col in feature_names if col not in df.columns or pd.isna(df[col].values[0])]
    if missing:
        raise ValueError(f"Missing required model features: {', '.join(missing)}")

    df_ordered = df[feature_names]
    return scaler.transform(df_ordered)



# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from backend.config import RAW_DATA_DIR
# from backend.services.market_data_service import MarketDataService

# FEATURE_COLUMNS = [
#     "Stock_Return",
#     "Stock_Volatility",
#     "Bond_Yield",
#     "Bond_Volatility",
#     "FX_Return",
#     "FX_Volatility",
#     "VIX"
# ]
# TARGET_COLUMN = "Crisis_Label"

# def load_and_prepare_crisis_data(test_size=0.2, random_state=42):
#     """
#     Loads simulated Multi-Market Financial Crisis dataset, cleans features,
#     and returns scaled train and test partitions.
#     """
#     market_service = MarketDataService()
#     market_service.ensure_datasets_exist()
    
#     file_path = RAW_DATA_DIR / "financial_crisis.csv"
#     df = pd.read_csv(file_path)
    
#     # Ensure all feature columns exist
#     for col in FEATURE_COLUMNS:
#         if col not in df.columns:
#             df[col] = 0.0
            
#     X = df[FEATURE_COLUMNS].copy()
#     y = df[TARGET_COLUMN].copy()
    
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=test_size, random_state=random_state, stratify=y
#     )
    
#     scaler = StandardScaler()
#     X_train_scaled = scaler.fit_transform(X_train)
#     X_test_scaled = scaler.transform(X_test)
    
#     return {
#         "X_train": X_train,
#         "X_test": X_test,
#         "X_train_scaled": X_train_scaled,
#         "X_test_scaled": X_test_scaled,
#         "y_train": y_train,
#         "y_test": y_test,
#         "scaler": scaler,
#         "feature_names": FEATURE_COLUMNS
#     }
