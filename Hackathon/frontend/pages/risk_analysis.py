import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.config import RISK_LIMITS, RISK_SCORE_WEIGHTS

def show_risk_analysis(system, state):
    st.title("📊 Multi-Factor Risk Assessment Engine")
    st.caption("Deep-dive inspection across Concentration, Volatility, Drawdown, Liquidity, and Composite Scoring.")

    risk = state["risk_evaluation"]
    conc = risk["concentration"]
    vol = risk["volatility"]
    dd = risk["drawdown"]
    liq = risk["liquidity"]
    comp = risk["composite_score"]

    tabs = st.tabs([
        "1. Concentration Risk",
        "2. Volatility Analytics",
        "3. Drawdown Analysis",
        "4. Liquidity Engine",
        "5. Composite Risk Score"
    ])

    # Tab 1: Concentration Risk
    with tabs[0]:
        st.subheader("Asset & Sector Concentration Analysis")
        c1, c2 = st.columns(2)
        with c1:
            eq_val = conc["equity_exposure"] * 100
            eq_cap = RISK_LIMITS["max_equity_allocation"] * 100
            st.metric("Equity Exposure", f"{eq_val:.1f}%", f"Cap: {eq_cap:.0f}%", delta_color="inverse" if eq_val > eq_cap else "normal")
            if eq_val > eq_cap:
                st.error(f"🚨 BREACH: Equity exposure exceeds the institutional policy cap of {eq_cap:.0f}% by {eq_val - eq_cap:.1f}%.")
            else:
                st.success("✅ Equity concentration is within safe boundaries.")

        with c2:
            gold_val = conc["gold_exposure"] * 100
            gold_cap = RISK_LIMITS["max_gold_allocation"] * 100
            st.metric("Gold Exposure", f"{gold_val:.1f}%", f"Cap: {gold_cap:.0f}%")

        st.markdown("---")
        st.write("Concentration Breach Log:")
        if conc.get("breaches"):
            for b in conc["breaches"]:
                st.warning(f"**{b['severity']}**: {b['message']}")
        else:
            st.info("No concentration breaches detected.")

    # Tab 2: Volatility Analytics
    with tabs[1]:
        st.subheader("Historical Market Volatility & Asset Correlation")
        stats = system.market_service.get_market_statistics()
        st.caption("NIFTY 50 and Gold metrics are calculated from aligned daily market returns for the available 2020-2025 period. Fixed-income and private-asset figures below are policy assumptions.")
        
        v1, v2, v3 = st.columns(3)
        with v1:
            st.metric("Portfolio Volatility", f"{vol['annualized_volatility']*100:.2f}%", "Ceiling: 15.0%", delta_color="inverse" if vol["is_breach"] else "normal")
        with v2:
            st.metric("NIFTY 50 Volatility", f"{stats['NIFTY 50']['annualized_volatility']*100:.1f}%", "2020-2025")
        with v3:
            st.metric("Gold / NIFTY Correlation", f"{stats['nifty_gold_correlation']:.2f}", "Diversification Factor")

        st.markdown("---")
        st.write("Empirical Asset Annualized Statistics:")
        stat_rows = []
        for k in ["NIFTY 50", "Gold", "Govt Bonds", "Cash", "Corporate Bonds"]:
            if k in stats:
                stat_rows.append({
                    "Asset": k,
                    "Annualized Return": f"{stats[k]['annualized_return']*100:.1f}%",
                    "Annualized Volatility": f"{stats[k]['annualized_volatility']*100:.1f}%"
                })
        st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)

    # Tab 3: Drawdown Analysis
    with tabs[2]:
        st.subheader("Historical Peak-to-Trough Drawdown Analysis")
        d1, d2 = st.columns(2)
        with d1:
            st.metric("Historical Max Drawdown", f"{dd['max_drawdown']*100:.1f}%", "Policy Limit: 20.0%", delta_color="inverse" if dd["is_breach"] else "normal")
        with d2:
            st.metric("Current Underwater Depth", f"{dd['current_drawdown']*100:.1f}%", "Relative to Peak")

        if "drawdown_series" in dd and dd["drawdown_series"]:
            dd_df = pd.DataFrame(dd["drawdown_series"])
            fig = px.area(dd_df, x="Date", y="Drawdown", title="Historical Underwater Drawdown Profile", color_discrete_sequence=["#EF4444"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#E2E8F0"))
            st.plotly_chart(fig, use_container_width=True)

    # Tab 4: Liquidity Engine
    with tabs[3]:
        st.subheader("Liquid Asset Ratio (LAR) & Liquidation Schedule")
        l1, l2, l3 = st.columns(3)
        with l1:
            st.metric("Liquid Asset Ratio", f"{liq['liquid_asset_ratio']*100:.1f}%", f"Status: {liq['status']}")
        with l2:
            st.metric("Weighted Days to Liquidate", f"{liq['weighted_liquidation_days']} Days", "Target: < 5 Days")
        with l3:
            st.metric("Stressed Haircut Loss", f"{liq['haircut_loss_pct']:.2f}%", "Under Fire-Sale Conditions")

        st.markdown("---")
        st.write("Holdings Liquidity Characteristics:")
        st.dataframe(pd.DataFrame(liq["asset_breakdown"]), use_container_width=True, hide_index=True)

    # Tab 5: Composite Risk Score
    with tabs[4]:
        st.subheader("Composite Risk Score Methodology (0–100)")
        st.markdown(f"""
        **Current Prototype Methodology**:
        $$\\text{{Risk Score}} = 30\\% \\cdot \\text{{Concentration}} + 25\\% \\cdot \\text{{Volatility}} + 20\\% \\cdot \\text{{Liquidity Deficiency}} + 25\\% \\cdot \\text{{Stress Vulnerability}}$$
        """)

        sub = comp["sub_scores"]
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric("Concentration Sub-Score", f"{sub['concentration']}/100", "Weight: 30%")
        with sc2:
            st.metric("Volatility Sub-Score", f"{sub['volatility']}/100", "Weight: 25%")
        with sc3:
            st.metric("Liquidity Sub-Score", f"{sub['liquidity']}/100", "Weight: 20%")
        with sc4:
            st.metric("Stress Sub-Score", f"{sub['stress_loss']}/100", "Weight: 25%")

        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.9); border: 2px solid {comp['color']}; border-radius: 12px; padding: 20px; text-align: center; margin-top: 15px;">
            <div style="font-size: 1.1rem; color: #94A3B8;">Final Weighted Composite Risk Score</div>
            <div style="font-size: 3.2rem; font-weight: 900; color: {comp['color']};">{comp['composite_score']} / 100</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: {comp['color']};">{comp['rating']} — {comp['badge']}</div>
        </div>
        """, unsafe_allow_html=True)
