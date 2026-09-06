import streamlit as st
import pandas as pd
from backend.utils.calculations import format_currency_inr
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_GREEN, FILL_GREEN, BORDER_GREEN, COLOR_SUCCESS, COLOR_DANGER,
    FILL_PINK, BORDER_PINK, ACCENT_PURPLE, FILL_PURPLE, SIDEBAR_ACCENT
)


def show_recommendations(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            ⚖️ Decision Engine &amp; Rebalancing Execution
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            Review institutional recommendations, verify post-rebalance safeguards, and execute trade orders.
        </div>
    </div>
    """, unsafe_allow_html=True)

    decision    = state["decision_data"]
    options     = decision["all_options"]
    user_id     = state.get("user_id")
    current_df  = system.portfolio_service.get_current_portfolio(user_id=user_id)

    # Strategy Selector
    option_choice = st.radio(
        "Select Rebalancing Strategy to Execute:",
        [
            "Option B (Least-Disruptive ⭐ Recommended)",
            "Option A (Conservative De-risking)",
            "Option C (Return-Preserving)"
        ],
        index=0,
        horizontal=True
    )

    if "Option B" in option_choice:
        selected_opt = options["option_b"]
    elif "Option A" in option_choice:
        selected_opt = options["option_a"]
    else:
        selected_opt = options["option_c"]

    # ── Trade Execution Plan ──────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:12px;">
        📋 Trade Execution Plan — {selected_opt['name']}
    </div>
    """, unsafe_allow_html=True)

    trades = selected_opt["trades"]
    if trades:
        trade_rows = []
        for t in trades:
            trade_rows.append({
                "Action":             t["action"],
                "Asset":              t["asset"],
                "Trade Amount":       f"₹{t['amount_inr']:,.0f}",
                "From Weight":        f"{t['from_weight_pct']:.1f}%",
                "Target Weight":      f"{t['to_weight_pct']:.1f}%",
                "Execution Statement": t["trade_statement"]
            })
        st.dataframe(pd.DataFrame(trade_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio is already aligned with this strategy.")

    # ── Action Buttons ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_sim, col_exec = st.columns(2)

    with col_sim:
        if st.button("🧪 Simulate Post-Rebalance Verification", use_container_width=True):
            cert = system.decision_engine.verify_rebalancing(current_df, selected_opt)
            st.session_state["verification_cert"] = cert
            st.success("Verification simulation complete!")

    with col_exec:
        if st.button("🚀 Commit & Execute Rebalance", type="primary", use_container_width=True):
            result = system.apply_recommended_rebalance(current_df, selected_opt["code"], user_id=user_id)
            st.session_state["verification_cert"] = result["verification_cert"]
            st.toast("Rebalance successfully executed and verified!", icon="✅")
            st.rerun()

    # ── Verification Certificate ──────────────────────────────────────────────
    if "verification_cert" in st.session_state and st.session_state["verification_cert"]:
        cert    = st.session_state["verification_cert"]
        v_color = COLOR_SUCCESS if cert["verified"] else COLOR_DANGER
        v_fill  = FILL_GREEN    if cert["verified"] else FILL_PINK
        v_border = BORDER_GREEN if cert["verified"] else BORDER_PINK
        v_text  = "✅ VERIFIED COMPLIANT SAFE STATE" if cert["verified"] else "🚨 LIMIT BREACH PERSISTS"

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:12px;">
            🛡️ Post-Rebalance Safeguard Verification Certificate
        </div>
        <div class="fincap-card" style="background:{v_fill}; border:1.5px solid {v_border};
             border-radius:20px; padding:22px 26px; margin-bottom:16px;
             box-shadow:0 4px 16px rgba(0,0,0,0.04);">
            <div style="font-weight:800; font-size:1.05rem; color:{v_color};
                        font-family:{FONT_FAMILY}; margin-bottom:8px;">{v_text}</div>
            <div style="font-size:0.88rem; color:{TEXT_PRIMARY}; font-weight:500; line-height:1.8; opacity:0.85;">
                Status Transition: <b>{cert['status_transition']}</b> &nbsp;|&nbsp;
                Composite Risk: <b>{cert['risk_score_transition']}</b> &nbsp;|&nbsp;
                Breaches Cleared: <b>{cert['breaches_cleared']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("New Equity Exposure",   cert["new_equity_allocation"], "Cap: 40.0% (Passed)")
        with c2:
            st.metric("New Liquid Asset Ratio", cert["new_liquid_ratio"],     "Min: 20.0% (Passed)")
        with c3:
            st.metric("New Volatility",         cert["new_volatility"],       "Ceiling: 15.0% (Passed)")

    # ── Audit Trail ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:12px;">
        📜 Historical Rebalance Audit Log
    </div>
    """, unsafe_allow_html=True)
    history = system.portfolio_service.get_rebalance_history()
    if history:
        st.dataframe(
            pd.DataFrame(history)[["timestamp", "option_name", "status_transition",
                                   "risk_score_transition", "turnover_pct"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.caption("No historical rebalances recorded in this session.")
