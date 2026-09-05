import streamlit as st
import pandas as pd
from frontend.components.metric_cards import render_kpi_row
from frontend.components.risk_alerts import render_system_status_banner, render_breach_cards
from frontend.components.charts import plot_allocation_donut, plot_asset_class_bars
from frontend.components.recommendation_card import render_recommendation_card
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_PURPLE, FILL_PURPLE, BORDER_PURPLE, ACCENT_BLUE, FILL_BLUE,
    SIDEBAR_ACCENT
)


def show_dashboard(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            🛡️ Institutional Risk &amp; Control Dashboard
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            Real-Time Multi-Factor Portfolio Risk, Control Safeguards &amp; Decision Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary    = state["portfolio_summary"]
    risk       = state["risk_evaluation"]
    ml         = state["ml_prediction"]
    comp_score = risk["composite_score"]
    decision   = state["decision_data"]

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

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Market Crisis AI Signal & Breach Overview
    col_ml, col_alerts = st.columns([1, 2])
    with col_ml:
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_PURPLE}; border:1.5px solid {BORDER_PURPLE};
             border-radius:20px; padding:22px 24px;
             box-shadow:0 2px 12px rgba(0,0,0,0.04); height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:{TEXT_MUTED};
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
                🤖 ML Crisis Intelligence
            </div>
            <div style="font-size:2.4rem; font-weight:900; color:{ml['regime_color']};
                        font-family:{FONT_FAMILY}; line-height:1.1;">
                {ml['crisis_probability_pct']}%
            </div>
            <div style="font-size:0.88rem; font-weight:700; color:{ml['regime_color']};
                        margin:6px 0;">
                {ml['regime_badge']}
            </div>
            <div style="font-size:0.84rem; color:{TEXT_PRIMARY}; font-weight:500; line-height:1.55; opacity:0.85;">
                {ml['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_alerts:
        render_breach_cards(risk["breaches"])

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Visual Charts Row
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown(f"""
        <div style="background:{BG_CARD}; border-radius:18px; padding:8px 8px 0 8px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);">
        """, unsafe_allow_html=True)
        holdings_df = pd.DataFrame(summary["holdings"])
        st.plotly_chart(plot_allocation_donut(holdings_df), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown(f"""
        <div style="background:{BG_CARD}; border-radius:18px; padding:8px 8px 0 8px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.06);">
        """, unsafe_allow_html=True)
        st.plotly_chart(plot_asset_class_bars(summary["asset_class_breakdown"]),
                        use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Quick Action Decision Card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:1.1rem; font-weight:800; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:12px;">
        ⚡ Automated Control Safeguard
    </div>
    """, unsafe_allow_html=True)
    render_recommendation_card(decision)
