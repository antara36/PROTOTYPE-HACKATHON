import streamlit as st
import pandas as pd
from frontend.components.metric_cards import render_kpi_row
from frontend.components.risk_alerts import render_system_status_banner, render_breach_cards
from frontend.components.charts import plot_allocation_donut, plot_asset_class_bars
from frontend.components.recommendation_card import render_recommendation_card

def show_dashboard(system, state):
    st.title("🛡️ Institutional Risk & Control Dashboard")
    st.caption("Real-Time Multi-Factor Portfolio Risk, Control Safeguards & Decision Intelligence")

    summary = state["portfolio_summary"]
    risk = state["risk_evaluation"]
    ml = state["ml_prediction"]
    comp_score = risk["composite_score"]
    decision = state["decision_data"]

    # 1. System Status Alert Banner
    render_system_status_banner(
        risk["system_status"],
        risk["breach_count"],
        comp_score["composite_score"]
    )

    # 2. Executive Metric Row
    render_kpi_row(
        capital_str=summary["formatted_capital"],
        risk_score=comp_score["composite_score"],
        risk_badge=comp_score["badge"],
        risk_color=comp_score["color"],
        liquidity_pct=risk["liquidity"]["liquid_asset_ratio"] * 100,
        liq_status=risk["liquidity"]["status"],
        exp_return_pct=decision["current_state"]["expected_return"] * 100,
        vol_pct=risk["volatility"]["annualized_volatility"] * 100
    )

    st.markdown("---")

    # 3. Market Crisis AI Signal & Breach Overview
    col_ml, col_alerts = st.columns([1, 2])
    with col_ml:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">ML Crisis Intelligence</div>
            <div style="font-size: 1.8rem; font-weight: 800; color: {ml['regime_color']}; margin-top: 4px;">{ml['crisis_probability_pct']}%</div>
            <div style="font-size: 0.85rem; font-weight: 600; color: {ml['regime_color']};">{ml['regime_badge']}</div>
            <div style="font-size: 0.8rem; color: #CBD5E1; margin-top: 8px;">{ml['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_alerts:
        render_breach_cards(risk["breaches"])

    st.markdown("---")

    # 4. Visual Charts Row
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        holdings_df = pd.DataFrame(summary["holdings"])
        st.plotly_chart(plot_allocation_donut(holdings_df), use_container_width=True)
    with chart_col2:
        st.plotly_chart(plot_asset_class_bars(summary["asset_class_breakdown"]), use_container_width=True)

    # 5. Quick Action Decision Card
    st.markdown("---")
    st.subheader("⚡ Automated Control Safeguard")
    render_recommendation_card(decision)
