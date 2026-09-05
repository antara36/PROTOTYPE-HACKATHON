import streamlit as st
import pandas as pd
from backend.utils.calculations import format_currency_inr

def show_recommendations(system, state):
    st.title("⚖️ Decision Engine & Rebalancing Execution")
    st.caption("Review institutional recommendations, verify post-rebalance safeguards, and execute trade orders.")

    decision = state["decision_data"]
    options = decision["all_options"]
    current_df = system.portfolio_service.get_current_portfolio()

    # Selector
    option_choice = st.radio(
        "Select Rebalancing Strategy to Execute:",
        ["Option B (Least-Disruptive ⭐ Recommended)", "Option A (Conservative De-risking)", "Option C (Return-Preserving)"],
        index=0,
        horizontal=True
    )

    if "Option B" in option_choice:
        selected_opt = options["option_b"]
    elif "Option A" in option_choice:
        selected_opt = options["option_a"]
    else:
        selected_opt = options["option_c"]

    # Show Trade Details
    st.markdown("---")
    st.subheader(f"Trade Execution Plan — {selected_opt['name']}")
    
    trades = selected_opt["trades"]
    if trades:
        trade_rows = []
        for t in trades:
            trade_rows.append({
                "Action": t["action"],
                "Asset": t["asset"],
                "Trade Amount": f"₹{t['amount_inr']:,.0f}",
                "From Weight": f"{t['from_weight_pct']:.1f}%",
                "Target Weight": f"{t['to_weight_pct']:.1f}%",
                "Execution Statement": t["trade_statement"]
            })
        st.dataframe(pd.DataFrame(trade_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio is already aligned with this strategy.")

    # Two action buttons: Simulate Verification vs Execute
    st.markdown("---")
    col_sim, col_exec = st.columns(2)
    
    with col_sim:
        if st.button("🧪 Simulate Post-Rebalance Verification", use_container_width=True):
            cert = system.decision_engine.verify_rebalancing(current_df, selected_opt)
            st.session_state["verification_cert"] = cert
            st.success("Verification simulation complete!")

    with col_exec:
        if st.button("🚀 Commit & Execute Rebalance", type="primary", use_container_width=True):
            result = system.apply_recommended_rebalance(current_df, selected_opt["code"])
            st.session_state["verification_cert"] = result["verification_cert"]
            st.toast("Rebalance successfully executed and verified!", icon="✅")
            st.rerun()

    # Display Verification Certificate if available
    if "verification_cert" in st.session_state and st.session_state["verification_cert"]:
        cert = st.session_state["verification_cert"]
        st.markdown("---")
        st.subheader("🛡️ Post-Rebalance Safeguard Verification Certificate")
        
        v_color = "#10B981" if cert["verified"] else "#EF4444"
        v_text = "VERIFIED COMPLIANT SAFE STATE" if cert["verified"] else "LIMIT BREACH PERSISTS"

        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid {v_color}; border-radius: 12px; padding: 18px; margin-bottom: 15px;">
            <div style="color: {v_color}; font-weight: 800; font-size: 1.1rem;">{v_text}</div>
            <div style="color: #CBD5E1; margin-top: 6px;">
                Status Transition: <b>{cert['status_transition']}</b> | 
                Composite Risk Transition: <b>{cert['risk_score_transition']}</b> | 
                Breaches Cleared: <b>{cert['breaches_cleared']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("New Equity Exposure", cert["new_equity_allocation"], "Cap: 40.0% (Passed)")
        with c2:
            st.metric("New Liquid Asset Ratio", cert["new_liquid_ratio"], "Min: 20.0% (Passed)")
        with c3:
            st.metric("New Volatility", cert["new_volatility"], "Ceiling: 15.0% (Passed)")

    # Audit Trail History
    st.markdown("---")
    st.subheader("📜 Historical Rebalance Audit Log")
    history = system.portfolio_service.get_rebalance_history()
    if history:
        st.dataframe(pd.DataFrame(history)[["timestamp", "option_name", "status_transition", "risk_score_transition", "turnover_pct"]], use_container_width=True, hide_index=True)
    else:
        st.caption("No historical rebalances recorded in this session.")
