import json
from datetime import datetime
import pandas as pd
from backend.config import PROCESSED_DATA_DIR
from backend.engines.portfolio_engine import PortfolioEngine

class PortfolioService:
    """
    Manages portfolio persistence, audit logs of executed rebalances,
    and user session states.
    """
    def __init__(self, engine=None):
        self.engine = engine or PortfolioEngine()
        self.audit_log_path = PROCESSED_DATA_DIR / "rebalance_audit_log.json"

    def get_current_portfolio(self) -> pd.DataFrame:
        return self.engine.load_portfolio()

    def update_portfolio(self, df: pd.DataFrame):
        self.engine.save_portfolio(df)

    def record_rebalance(self, selected_option: dict, verification_cert: dict):
        """
        Appends an audit trail entry for compliance verification.
        """
        logs = []
        if self.audit_log_path.exists():
            try:
                logs = json.loads(self.audit_log_path.read_text(encoding="utf-8"))
            except Exception:
                logs = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "option_name": selected_option.get("name"),
            "expected_return": selected_option.get("expected_return"),
            "volatility": selected_option.get("volatility"),
            "turnover_pct": selected_option.get("turnover_pct"),
            "status_transition": verification_cert.get("status_transition"),
            "risk_score_transition": verification_cert.get("risk_score_transition"),
            "trades": selected_option.get("trades", [])
        }
        logs.append(entry)
        self.audit_log_path.write_text(json.dumps(logs, indent=2), encoding="utf-8")

    def get_rebalance_history(self) -> list:
        if self.audit_log_path.exists():
            try:
                return json.loads(self.audit_log_path.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []
