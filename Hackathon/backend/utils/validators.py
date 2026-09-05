import pandas as pd

def validate_portfolio_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validates user portfolio input DataFrame.
    """
    if df is None or df.empty:
        return False, "Portfolio cannot be empty."

    if "Asset" not in df.columns:
        return False, "Missing required column 'Asset'."

    if "Amount_INR" not in df.columns:
        return False, "Missing required column 'Amount_INR'."

    try:
        amounts = pd.to_numeric(df["Amount_INR"], errors="coerce")
        if amounts.isna().any():
            return False, "Amount_INR contains non-numeric values."
        if (amounts < 0).any():
            return False, "Holdings amounts cannot be negative."
        if amounts.sum() <= 0:
            return False, "Total portfolio capital must be strictly greater than 0."
    except Exception as e:
        return False, f"Validation error: {str(e)}"

    return True, "Portfolio input is valid."
