import numpy as np
import pandas as pd
from scipy.optimize import minimize
from backend.config import RISK_LIMITS
from backend.services.market_data_service import MarketDataService

class OptimizationEngine:
    """
    Institutional portfolio optimizer generating 3 distinct corrective action options:
    - Option A: Conservative De-Risking (Max safety & liquidity, High disruption)
    - Option B: Least-Disruptive Safe State (⭐ Recommended: Minimum change to restore compliance)
    - Option C: Return-Preserving Safe State (Maximizes yield within strict safety boundaries)
    """
    def __init__(self, market_service=None):
        self.market_service = market_service or MarketDataService()

    def _get_expected_returns_and_cov(self, assets):
        stats = self.market_service.get_market_statistics()
        cov_df = self.market_service.get_asset_covariance_matrix(assets)
        cov_matrix = cov_df.to_numpy()

        returns = []
        for a in assets:
            if a in stats and "annualized_return" in stats[a]:
                returns.append(stats[a]["annualized_return"])
            elif "NIFTY" in a or "Equity" in a:
                returns.append(0.12)
            elif "Gold" in a:
                returns.append(0.085)
            elif "Bond" in a:
                returns.append(0.071)
            elif "Cash" in a:
                returns.append(0.045)
            else:
                returns.append(0.08)
        return np.array(returns), cov_matrix

    def generate_rebalancing_options(self, portfolio_df: pd.DataFrame) -> dict:
        df = portfolio_df.copy()
        assets = df["Asset"].tolist()
        current_weights = df["Allocation_Pct"].to_numpy()
        total_capital = float(df["Amount_INR"].sum())
        n = len(assets)

        exp_returns, cov_matrix = self._get_expected_returns_and_cov(assets)

        equity_indices = [i for i, a in enumerate(assets) if "NIFTY" in a or "Equity" in a]
        liquid_indices = [i for i, a in enumerate(assets) if "Cash" in a or "Govt Bonds" in a or "NIFTY" in a or "Gold" in a]
        cash_bond_indices = [i for i, a in enumerate(assets) if "Cash" in a or "Bond" in a]

        max_eq = RISK_LIMITS["max_equity_allocation"]
        min_liq = RISK_LIMITS["min_liquidity_ratio"]
        max_vol = RISK_LIMITS["max_annualized_volatility"]

        # Base constraints
        bounds = tuple((0.02, 0.85) for _ in range(n))
        sum_constraint = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

        def equity_constraint(w):
            return max_eq - sum(w[i] for i in equity_indices)

        def vol_constraint(w):
            return max_vol - np.sqrt(max(0.0, w.T @ cov_matrix @ w))

        def liquidity_constraint(w):
            return sum(w[i] for i in liquid_indices) - min_liq

        # -------------------------------------------------------------
        # OPTION B: LEAST-DISRUPTIVE SAFE STATE (CORE INNOVATION ⭐)
        # Objective: min sum((w - w_curr)^2) + minor penalty for risk
        # -------------------------------------------------------------
        def obj_least_disruptive(w):
            turnover_sq = np.sum((w - current_weights) ** 2)
            var_p = w.T @ cov_matrix @ w
            return turnover_sq * 10.0 + var_p * 2.0

        constraints_b = [
            sum_constraint,
            {"type": "ineq", "fun": equity_constraint},
            {"type": "ineq", "fun": vol_constraint},
            {"type": "ineq", "fun": liquidity_constraint}
        ]

        res_b = minimize(
            obj_least_disruptive,
            current_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_b,
            options={"maxiter": 300, "ftol": 1e-6}
        )
        weights_b = res_b.x if res_b.success else self._fallback_rebalance(current_weights, equity_indices, cash_bond_indices, max_eq)

        # -------------------------------------------------------------
        # OPTION A: CONSERVATIVE DE-RISKING
        # Objective: minimize portfolio variance + heavy cash/bond tilt
        # -------------------------------------------------------------
        def obj_conservative(w):
            var_p = w.T @ cov_matrix @ w
            return var_p - 0.02 * np.sum(w[cash_bond_indices])

        def strict_equity_constraint(w):
            return 0.28 - sum(w[i] for i in equity_indices)

        constraints_a = [
            sum_constraint,
            {"type": "ineq", "fun": strict_equity_constraint},
            {"type": "ineq", "fun": vol_constraint},
            {"type": "ineq", "fun": lambda w: sum(w[i] for i in liquid_indices) - 0.35}
        ]

        res_a = minimize(
            obj_conservative,
            np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_a,
            options={"maxiter": 300, "ftol": 1e-6}
        )
        weights_a = res_a.x if res_a.success else weights_b

        # -------------------------------------------------------------
        # OPTION C: RETURN-PRESERVING SAFE STATE
        # Objective: maximize expected return subject to safe boundary
        # -------------------------------------------------------------
        def obj_return_preserving(w):
            ret_p = exp_returns @ w
            var_p = w.T @ cov_matrix @ w
            return -ret_p + 1.5 * var_p

        constraints_c = [
            sum_constraint,
            {"type": "ineq", "fun": equity_constraint},
            {"type": "ineq", "fun": vol_constraint},
            {"type": "ineq", "fun": liquidity_constraint}
        ]

        res_c = minimize(
            obj_return_preserving,
            current_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_c,
            options={"maxiter": 300, "ftol": 1e-6}
        )
        weights_c = res_c.x if res_c.success else weights_b

        # Normalize weights to exactly 1.0
        weights_a = np.maximum(0, weights_a) / np.sum(np.maximum(0, weights_a))
        weights_b = np.maximum(0, weights_b) / np.sum(np.maximum(0, weights_b))
        weights_c = np.maximum(0, weights_c) / np.sum(np.maximum(0, weights_c))

        opt_a = self._package_option("Option A", "Conservative De-Risking", weights_a, current_weights, assets, total_capital, exp_returns, cov_matrix, liquid_indices)
        opt_b = self._package_option("Option B", "Least-Disruptive Safe State (⭐ Recommended)", weights_b, current_weights, assets, total_capital, exp_returns, cov_matrix, liquid_indices, is_recommended=True)
        opt_c = self._package_option("Option C", "Return-Preserving Rebalance", weights_c, current_weights, assets, total_capital, exp_returns, cov_matrix, liquid_indices)

        return {
            "current_state": {
                "expected_return": float(exp_returns @ current_weights),
                "volatility": float(np.sqrt(max(0.0, current_weights.T @ cov_matrix @ current_weights))),
                "liquidity_ratio": float(sum(current_weights[i] for i in liquid_indices)),
                "weights": dict(zip(assets, [round(float(w), 4) for w in current_weights]))
            },
            "options": {
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c
            }
        }

    def _fallback_rebalance(self, current_weights, equity_indices, cash_bond_indices, max_eq):
        weights = current_weights.copy()
        current_eq = sum(weights[i] for i in equity_indices)
        if current_eq > max_eq:
            excess = current_eq - max_eq
            for i in equity_indices:
                weights[i] -= excess * (weights[i] / current_eq)
            for i in cash_bond_indices:
                weights[i] += excess / len(cash_bond_indices)
        return weights / np.sum(weights)

    def _package_option(self, code, name, new_weights, curr_weights, assets, total_capital, exp_returns, cov_matrix, liquid_indices, is_recommended=False):
        exp_ret = float(exp_returns @ new_weights)
        vol = float(np.sqrt(max(0.0, new_weights.T @ cov_matrix @ new_weights)))
        liq_ratio = float(sum(new_weights[i] for i in liquid_indices))
        turnover = float(0.5 * np.sum(np.abs(new_weights - curr_weights)))

        if turnover <= 0.10:
            impact_level = "LOW"
            impact_color = "#10B981"
        elif turnover <= 0.22:
            impact_level = "MEDIUM"
            impact_color = "#F59E0B"
        else:
            impact_level = "HIGH"
            impact_color = "#EF4444"

        trades = []
        for i, a in enumerate(assets):
            curr_amt = curr_weights[i] * total_capital
            target_amt = new_weights[i] * total_capital
            delta = target_amt - curr_amt
            if abs(delta) >= 1000:
                action = "BUY" if delta > 0 else "SELL"
                trades.append({
                    "asset": a,
                    "action": action,
                    "amount_inr": abs(round(delta, 2)),
                    "from_weight_pct": round(curr_weights[i] * 100, 1),
                    "to_weight_pct": round(new_weights[i] * 100, 1),
                    "trade_statement": f"{action} ₹{abs(delta):,.0f} of {a} ({curr_weights[i]*100:.1f}% → {new_weights[i]*100:.1f}%)"
                })

        return {
            "code": code,
            "name": name,
            "is_recommended": is_recommended,
            "expected_return": round(exp_ret * 100, 2),
            "volatility": round(vol * 100, 2),
            "liquidity_ratio": round(liq_ratio * 100, 1),
            "turnover_pct": round(turnover * 100, 1),
            "impact_level": impact_level,
            "impact_color": impact_color,
            "weights": dict(zip(assets, [round(float(w), 4) for w in new_weights])),
            "target_amounts": dict(zip(assets, [round(float(w * total_capital), 2) for w in new_weights])),
            "trades": trades
        }
