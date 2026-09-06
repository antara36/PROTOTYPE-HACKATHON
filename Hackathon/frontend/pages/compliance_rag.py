import streamlit as st
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_PURPLE, FILL_PURPLE, BORDER_PURPLE,
    ACCENT_BLUE, FILL_BLUE, BORDER_BLUE,
    FILL_GREEN, BORDER_GREEN,
    COLOR_SUCCESS, COLOR_DANGER, SIDEBAR_ACCENT
)


def show_compliance_rag(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            🤖 Policy &amp; Compliance RAG Assistant
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            Grounded retrieval-augmented intelligence explaining risk breaches, regulatory alignment,
            and institutional controls.
        </div>
    </div>
    """, unsafe_allow_html=True)

    risk             = state["risk_evaluation"]
    breaches         = risk.get("breaches", [])
    rag_explanations = state.get("rag_explanations", [])

    # ── Automated Breach Explanations ─────────────────────────────────────────
    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:16px;">
        📌 Automated Breach Explanations
    </div>
    """, unsafe_allow_html=True)

    if rag_explanations:
        for item in rag_explanations:
            with st.expander(
                f"🔴 Policy Analysis: {item['breach_type']} ({item['category']})",
                expanded=True
            ):
                st.markdown(item["explanation"])
                st.markdown(
                    f"**Document Citation**: `{item['source_document']}` — "
                    f"*{item['source_section']}* (`{item['source_file']}`)"
                )
                if item.get("citations"):
                    with st.expander("📄 View Exact Source Policy Excerpt"):
                        for c in item["citations"]:
                            st.markdown(f"> *{c['content']}*")
                            st.caption(f"Relevance Score: {c.get('similarity_score', 'N/A')}")
    else:
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_GREEN}; border:1.5px solid {BORDER_GREEN};
             border-radius:18px; padding:16px 22px; color:#065F46; font-weight:600;
             font-size:0.92rem; margin-bottom:16px;">
            ✅ &nbsp; No active breaches to explain. Portfolio is 100% compliant with internal policy guidelines.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Policy Co-Pilot Section ───────────────────────────────────────────────
    llm_active = system.rag_engine.is_llm_enabled()
    engine_badge = (
        f'<span style="background:{COLOR_SUCCESS}; color:#fff; font-size:0.75rem; font-weight:700; '
        f'padding:4px 10px; border-radius:9999px; margin-left:8px;">✨ Gemini AI Co-Pilot Active</span>'
        if llm_active else
        f'<span style="background:{SIDEBAR_ACCENT}; color:#fff; font-size:0.75rem; font-weight:700; '
        f'padding:4px 10px; border-radius:9999px; margin-left:8px;">🛡️ Grounded Policy Knowledge Store Active</span>'
    )

    st.markdown(f"""
    <div class="fincap-card" style="background:{FILL_PURPLE}; border:1.5px solid {BORDER_PURPLE};
         border-radius:20px; padding:22px 26px; margin-bottom:20px;
         box-shadow:0 2px 10px rgba(0,0,0,0.03);">
        <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">
            <div style="font-size:1.05rem; font-weight:800; color:{TEXT_PRIMARY};
                        font-family:{FONT_FAMILY};">
                💬 Compliance &amp; Policy Co-Pilot {engine_badge}
            </div>
        </div>
        <div style="font-size:0.86rem; color:{TEXT_MUTED}; font-weight:500; margin-top:6px;">
            Ask questions about internal limits, liquidity requirements, stress scenario parameters,
            or Basel reference guidelines. Grounded in institutional policies.
        </div>
    </div>
    """, unsafe_allow_html=True)

    preset_questions = [
        "What is the maximum allowed allocation to equities?",
        "What assets qualify as Tier 1 High Quality Liquid Assets (HQLA)?",
        "What are the mandatory stress testing scenarios and loss limits?",
        "How is our Liquid Asset Ratio (LAR) related to the Basel III LCR?"
    ]

    selected_q = st.selectbox(
        "Quick-Select Policy Question:",
        ["-- Choose a question or type below --"] + preset_questions
    )

    user_query = st.text_input(
        "Or enter your custom compliance question:",
        value=selected_q if selected_q != "-- Choose a question or type below --" else ""
    )

    if st.button("🔍 Query Policy Knowledge Base") and user_query:
        with st.spinner("Retrieving authoritative policy clauses..."):
            ans_data = system.rag_engine.answer_governance_query(user_query)

            st.markdown(f"""
            <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                        font-family:{FONT_FAMILY}; margin:16px 0 10px 0;">
                📖 Answer
            </div>
            """, unsafe_allow_html=True)
            st.markdown(ans_data["answer"])

            if ans_data.get("citations"):
                st.markdown(f"""
                <div style="font-size:0.9rem; font-weight:700; color:{TEXT_PRIMARY};
                            font-family:{FONT_FAMILY}; margin:16px 0 10px 0;">
                    📄 Retrieved Citations &amp; Passages
                </div>
                """, unsafe_allow_html=True)
                for c in ans_data["citations"]:
                    st.markdown(
                        f"**From `{c['doc_title']}` ({c['section']})** — "
                        f"*Similarity: {c.get('similarity_score')}*"
                    )
                    st.markdown(f"> {c['content']}")
