import streamlit as st

def show_compliance_rag(system, state):
    st.title("🤖 Policy & Compliance RAG Assistant")
    st.caption("Grounded retrieval-augmented intelligence explaining risk breaches, regulatory alignment, and institutional controls.")

    risk = state["risk_evaluation"]
    breaches = risk.get("breaches", [])
    rag_explanations = state.get("rag_explanations", [])

    st.subheader("📌 Automated Breach Explanations")
    if rag_explanations:
        for item in rag_explanations:
            with st.expander(f"🔴 Policy Analysis: {item['breach_type']} ({item['category']})", expanded=True):
                st.markdown(item["explanation"])
                st.markdown(f"**Document Citation**: `{item['source_document']}` — *{item['source_section']}* (`{item['source_file']}`)")
                
                if item.get("citations"):
                    with st.expander("📄 View Exact Source Policy Excerpt"):
                        for c in item["citations"]:
                            st.markdown(f"> *{c['content']}*")
                            st.caption(f"Relevance Score: {c.get('similarity_score', 'N/A')}")
    else:
        st.success("✅ No active breaches to explain. Portfolio is 100% compliant with internal policy guidelines.")

    st.markdown("---")
    st.subheader("💬 Ask the Compliance & Policy Co-Pilot")
    st.caption("Ask questions about internal limits, liquidity requirements, stress scenario parameters, or Basel reference guidelines:")

    preset_questions = [
        "What is the maximum allowed allocation to equities?",
        "What assets qualify as Tier 1 High Quality Liquid Assets (HQLA)?",
        "What are the mandatory stress testing scenarios and loss limits?",
        "How is our Liquid Asset Ratio (LAR) related to the Basel III LCR?"
    ]

    selected_q = st.selectbox("Quick-Select Policy Question:", ["-- Choose a question or type below --"] + preset_questions)
    
    user_query = st.text_input("Or enter your custom compliance question:", value=selected_q if selected_q != "-- Choose a question or type below --" else "")

    if st.button("🔍 Query Policy Knowledge Base") and user_query:
        with st.spinner("Retrieving authoritative policy clauses..."):
            ans_data = system.rag_engine.answer_governance_query(user_query)
            st.markdown("### Answer")
            st.markdown(ans_data["answer"])

            if ans_data.get("citations"):
                st.markdown("#### Retrieved Citations & Passages")
                for c in ans_data["citations"]:
                    st.markdown(f"**From `{c['doc_title']}` ({c['section']})** — *Similarity: {c.get('similarity_score')}*")
                    st.markdown(f"> {c['content']}")
