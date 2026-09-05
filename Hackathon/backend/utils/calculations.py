import numpy as np

def format_currency_inr(amount: float) -> str:
    """Formats numeric INR into Indian Rupee denomination string (Crores/Lakhs)."""
    abs_amt = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amt >= 1e7:
        return f"{sign}₹{abs_amt / 1e7:.2f} Cr"
    elif abs_amt >= 1e5:
        return f"{sign}₹{abs_amt / 1e5:.2f} L"
    else:
        return f"{sign}₹{abs_amt:,.2f}"

def format_pct(value: float, decimals: int = 1) -> str:
    """Formats decimal fraction to percentage string."""
    return f"{value * 100:.{decimals}f}%"

def calculate_sharpe_ratio(expected_return: float, volatility: float, risk_free_rate: float = 0.065) -> float:
    """Calculates annualized Sharpe Ratio."""
    if volatility <= 0:
        return 0.0
    return float((expected_return - risk_free_rate) / volatility)

def calculate_parametric_var(portfolio_value: float, volatility: float, confidence_level: float = 0.95, horizon_days: int = 1) -> float:
    """
    Parametric Value at Risk (VaR) assuming normal distribution.
    confidence_level 0.95 -> z = 1.645, 0.99 -> z = 2.326
    """
    from scipy.stats import norm
    z = norm.ppf(confidence_level)
    daily_vol = volatility / np.sqrt(252)
    var_amount = portfolio_value * z * daily_vol * np.sqrt(horizon_days)
    return float(var_amount)
