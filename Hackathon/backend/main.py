import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
from backend.services.market_data_service import MarketDataService
from backend.services.portfolio_service import PortfolioService
from backend.services.auth_service import AuthService
from backend.engines.portfolio_engine import PortfolioEngine
from backend.engines.liquidity_engine import LiquidityEngine
from backend.engines.risk_engine import RiskEngine
from backend.engines.stress_engine import StressEngine
from backend.engines.optimization_engine import OptimizationEngine
from backend.engines.decision_engine import DecisionEngine
from backend.ml.crisis_predictor import CrisisPredictor
from backend.rag.rag_engine import RAGEngine

class FincapGuardSystem:
    """
    Master orchestrator integrating Portfolio, Market Data, Risk, Liquidity,
    Stress Testing, ML Crisis Detection, Least-Disruptive Optimization, Decision Engine,
    and Policy RAG into a unified institutional system.
    """
    def __init__(self):
        self.market_service = MarketDataService()
        self.market_service.ensure_datasets_exist()
        
        self.portfolio_service = PortfolioService()
        self.portfolio_engine = self.portfolio_service.engine
        self.liquidity_engine = LiquidityEngine()
        self.risk_engine = RiskEngine(self.market_service, self.liquidity_engine)
        self.stress_engine = StressEngine()
        self.opt_engine = OptimizationEngine(self.market_service)
        self.decision_engine = DecisionEngine(self.opt_engine, self.risk_engine, self.liquidity_engine)
        self.crisis_predictor = CrisisPredictor()
        self.rag_engine = RAGEngine()
        self.auth_service = AuthService()

    def get_full_dashboard_state(self, portfolio_df: pd.DataFrame = None) -> dict:
        """
        Executes end-to-end institutional workflow:
        Holdings -> Risk & Liquidity Assessment -> ML Crisis Probability ->
        Stress Testing -> Optimization (3 Options) -> Decision Recommendation -> Policy RAG.
        """
        if portfolio_df is None:
            portfolio_df = self.portfolio_service.get_current_portfolio()

        portfolio_summary = self.portfolio_engine.get_summary(portfolio_df)
        
        # 1. Evaluate Risk & Liquidity
        risk_evaluation = self.risk_engine.evaluate_portfolio(portfolio_df)
        
        # 2. ML Market Crisis Prediction
        ml_prediction = self.crisis_predictor.predict()

        # 3. Stress Scenario Analysis
        stress_results = self.stress_engine.run_all_scenarios(portfolio_df)
        primary_stress = self.stress_engine.run_stress_test(portfolio_df, "Market Crash")

        # 4. Generate Corrective Alternatives & Decision
        decision_data = self.decision_engine.evaluate_and_recommend(portfolio_df)

        # 5. RAG Policy Compliance Explanations
        rag_explanations = []
        for breach in risk_evaluation.get("breaches", []):
            rag_explanations.append(self.rag_engine.explain_breach(breach))

        return {
            "portfolio_summary": portfolio_summary,
            "risk_evaluation": risk_evaluation,
            "ml_prediction": ml_prediction,
            "stress_results": stress_results,
            "primary_stress": primary_stress,
            "decision_data": decision_data,
            "rag_explanations": rag_explanations,
            "has_breach": risk_evaluation["system_status"] in ["BREACH", "WARNING"]
        }

    def apply_recommended_rebalance(self, current_df: pd.DataFrame, selected_option_code: str = "Option B") -> dict:
        """
        Applies chosen rebalancing option, runs post-rebalance verification,
        updates active portfolio, and records audit trail.
        """
        decision_data = self.decision_engine.evaluate_and_recommend(current_df)
        options = decision_data["all_options"]
        opt_key = selected_option_code.lower().replace(" ", "_")
        selected_option = options.get(opt_key, options["option_b"])

        # Post-rebalance verification
        verification_cert = self.decision_engine.verify_rebalancing(current_df, selected_option)

        # Update saved portfolio if verified
        if verification_cert["verified"]:
            new_df = pd.DataFrame(verification_cert["simulated_portfolio"])
            self.portfolio_service.update_portfolio(new_df)
            self.portfolio_service.record_rebalance(selected_option, verification_cert)

        return {
            "verification_cert": verification_cert,
            "selected_option": selected_option
        }

if __name__ == "__main__":
    print("Initializing FINCAP GUARD Institutional Brain...")
    system = FincapGuardSystem()
    state = system.get_full_dashboard_state()
    print("System State Initialized Successfully:")
    print(f"Total Capital: {state['portfolio_summary']['formatted_capital']}")
    print(f"Risk Score: {state['risk_evaluation']['composite_score']['composite_score']} ({state['risk_evaluation']['system_status']})")
    print(f"Breaches Count: {state['risk_evaluation']['breach_count']}")
    print(f"ML Crisis Probability: {state['ml_prediction']['crisis_probability_pct']}%")
    print(f"Recommended Action: {state['decision_data']['recommended_code']} - {state['decision_data']['recommended_option']['name']}")
