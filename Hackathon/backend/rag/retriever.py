from backend.rag.vector_store import PolicyVectorStore

class PolicyRetriever:
    """
    Translates risk engine breach events into targeted policy queries
    and retrieves the most relevant regulatory and internal policy clauses.
    """
    def __init__(self, vector_store=None):
        self.vector_store = vector_store or PolicyVectorStore()

    def get_query_for_breach(self, breach_type: str) -> str:
        mapping = {
            "CONCENTRATION_EQUITY": "Maximum Equity Allocation limit 40% concentration ceiling single asset",
            "CONCENTRATION_GOLD": "Maximum Gold Commodity Allocation limit 25% flight to safety",
            "SINGLE_ASSET_CONCENTRATION": "Single Asset Concentration Cap 35% portfolio capital",
            "PORTFOLIO_VOLATILITY": "Maximum Annualized Volatility Ceiling 15% risk alert breach",
            "MAX_DRAWDOWN": "Maximum Allowable Peak to Trough Drawdown 20% committee notification",
            "LIQUIDITY_LIMIT": "Minimum Liquid Asset Ratio LAR 20% liquidity tiers HQLA cash buffer",
            "STRESS_TOLERANCE": "Maximum Tolerated Stress Loss 12% scenario analysis de-risking"
        }
        return mapping.get(breach_type, f"Policy rules governing {breach_type}")

    def retrieve_context_for_breach(self, breach: dict, top_k: int = 2) -> list:
        breach_type = breach.get("type", "")
        query = self.get_query_for_breach(breach_type)
        return self.vector_store.search(query, top_k=top_k)

    def search_policy(self, user_query: str, top_k: int = 3) -> list:
        return self.vector_store.search(user_query, top_k=top_k)
