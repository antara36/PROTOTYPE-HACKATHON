from backend.rag.retriever import PolicyRetriever

class RAGEngine:
    """
    Grounded Policy Compliance Assistant.
    Provides authoritative, cited explanations for detected breaches
    and answers governance questions using the institutional policy vector store.
    """
    def __init__(self, retriever=None):
        self.retriever = retriever or PolicyRetriever()

    def explain_breach(self, breach: dict) -> dict:
        """
        Generates a grounded compliance explanation for a specific breach.
        """
        breach_type = breach.get("type", "UNKNOWN")
        actual_val = breach.get("actual_value", 0.0)
        limit_val = breach.get("limit_value", 0.0)
        category = breach.get("asset_category", breach_type)

        chunks = self.retriever.retrieve_context_for_breach(breach, top_k=2)
        top_chunk = chunks[0] if chunks else None

        source_doc = top_chunk["doc_title"] if top_chunk else "Risk Policy"
        source_section = top_chunk["section"] if top_chunk else "Asset Allocation Limits"
        source_file = top_chunk["source"] if top_chunk else "risk_policy.md"

        if "EQUITY" in breach_type:
            explanation = (
                f"**Equity Concentration Breach**: Current equity exposure is **{actual_val*100:.1f}%**, "
                f"exceeding the configured **{limit_val*100:.0f}%** maximum allocation limit.\n\n"
                f"**Policy Rationale**: Over-concentration in equities amplifies portfolio downside during market drawdowns "
                f"and market crashes. Under *{source_doc}* ({source_section}), equity exposure is capped to ensure broad asset "
                f"diversification across uncorrelated safe-haven instruments (Gold, Sovereign Debt, and Cash).\n\n"
                f"**Mandated Control Action**: The system recommends executing the **least-disruptive rebalancing plan** "
                f"to reduce equity weight to 40.0% or lower and reallocate capital into liquid fixed income."
            )
        elif "GOLD" in breach_type:
            explanation = (
                f"**Gold Allocation Warning**: Gold holding stands at **{actual_val*100:.1f}%**, exceeding the **{limit_val*100:.0f}%** guideline.\n\n"
                f"**Policy Rationale**: While gold offers crisis hedging, excessive gold allocation introduces commodity carry drag and volatility.\n\n"
                f"**Mandated Control Action**: Rebalance excess gold gains into cash or yield-bearing sovereign bonds."
            )
        elif "LIQUIDITY" in breach_type:
            explanation = (
                f"**Liquidity Ratio Breach**: The Liquid Asset Ratio is currently **{actual_val*100:.1f}%**, "
                f"breaching the mandatory **{limit_val*100:.0f}%** minimum liquidity floor.\n\n"
                f"**Policy Rationale**: Portfolios must maintain sufficient Tier 1 High-Quality Liquid Assets (HQLA) "
                f"to satisfy unexpected redemption or collateral requirements without fire-sale discounts.\n\n"
                f"**Mandated Control Action**: Immediate stop on illiquid asset purchases and re-allocation to Cash/G-Secs."
            )
        elif "VOLATILITY" in breach_type:
            explanation = (
                f"**Volatility Limit Breach**: Annualized volatility is **{actual_val*100:.2f}%**, exceeding the **{limit_val*100:.0f}%** ceiling.\n\n"
                f"**Policy Rationale**: Elevated volatility signals dangerous covariance among holdings.\n\n"
                f"**Mandated Control Action**: Shift weights toward low-beta sovereign instruments."
            )
        else:
            explanation = (
                f"**Policy Breach Alert**: Detected {breach_type} with value {actual_val}.\n\n"
                f"**Grounded Clause**: Governed by {source_doc} ({source_section}). Corrective rebalancing required."
            )

        return {
            "breach_type": breach_type,
            "category": category,
            "explanation": explanation,
            "source_document": source_doc,
            "source_section": source_section,
            "source_file": source_file,
            "citations": chunks
        }

    def answer_governance_query(self, query: str) -> dict:
        """
        Allows interactive free-form compliance questions from risk officers.
        """
        if not query or not query.strip():
            return {
                "answer": "Question not related to FINCAP Guard policy, or no question was provided.",
                "citations": [],
                "related": False,
            }

        results = self.retriever.search_policy(query, top_k=3)
        # Do not turn an arbitrary nearest-neighbour match into policy advice.
        if not results or results[0].get("similarity_score", 0.0) < 0.12:
            return {
                "answer": "Question not related to FINCAP Guard policy. Ask about portfolio limits, liquidity, stress testing, or governance controls.",
                "citations": [],
                "related": False,
            }

        top = results[0]
        answer = (
            f"**Policy Guidance from {top['doc_title']} ({top['section']})**:\n\n"
            f"{top['content']}\n\n"
            f"*(Source: `{top['source']}` — Relevance Score: {top['similarity_score']})*"
        )

        return {
            "answer": answer,
            "citations": results,
            "related": True,
        }
