import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.config import RISK_LIMITS, RISK_SCORE_WEIGHTS
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_PURPLE, FILL_PURPLE, ACCENT_GREEN, FILL_GREEN,
    COLOR_SUCCESS, COLOR_DANGER, SIDEBAR_ACCENT
)


def show_risk_analysis(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            📊 Multi-Factor Risk Assessment Engine
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            Deep-dive inspection across Concentration, Volatility, Drawdown, Liquidity, and Composite Scoring.
        </div>
    </div>
    """, unsafe_allow_html=True)

    risk = state["risk_evaluation"]
    conc = risk["concentration"]
    vol  = risk["volatility"]
    dd   = risk["drawdown"]
    liq  = risk["liquidity"]
    comp = risk["composite_score"]

    tabs = st.tabs([
        "1. Concentration Risk",
        "2. Volatility Analytics",
        "3. Drawdown Analysis",
        "4. Liquidity Engine",
        "5. Composite Risk Score"
    ])

    # ── Tab 1: Concentration Risk ─────────────────────────────────────────────
    with tabs[0]:
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:16px;">
            Asset &amp; Sector Concentration Analysis
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            eq_val = conc["equity_exposure"] * 100
            eq_cap = RISK_LIMITS["max_equity_allocation"] * 100
            st.metric("Equity Exposure", f"{eq_val:.1f}%",
                      f"Cap: {eq_cap:.0f}%",
                      delta_color="inverse" if eq_val > eq_cap else "normal")
            if eq_val > eq_cap:
                st.error(f"🚨 BREACH: Equity exposure exceeds the institutional policy cap of {eq_cap:.0f}% by {eq_val - eq_cap:.1f}%.")
            else:
                st.success("✅ Equity concentration is within safe boundaries.")

        with c2:
            gold_val = conc["gold_exposure"] * 100
            gold_cap = RISK_LIMITS["max_gold_allocation"] * 100
            st.metric("Gold Exposure", f"{gold_val:.1f}%", f"Cap: {gold_cap:.0f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.85rem; font-weight:600; color:{TEXT_MUTED};
                    margin-bottom:10px;">Concentration Breach Log</div>
        """, unsafe_allow_html=True)
        if conc.get("breaches"):
            for b in conc["breaches"]:
                st.warning(f"**{b['severity']}**: {b['message']}")
        else:
            st.info("No concentration breaches detected.")

    # ── Tab 2: Volatility Analytics ───────────────────────────────────────────
    with tabs[1]:
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:8px;">
            Historical Market Volatility &amp; Asset Correlation
        </div>
        """, unsafe_allow_html=True)
        stats = system.market_service.get_market_statistics()
        st.caption("NIFTY 50 and Gold metrics are calculated from aligned daily market returns for the available 2020-2025 period. Fixed-income and private-asset figures below are policy assumptions.")

        v1, v2, v3 = st.columns(3)
        with v1:
            st.metric("Portfolio Volatility",   f"{vol['annualized_volatility']*100:.2f}%",
                      "Ceiling: 15.0%",
                      delta_color="inverse" if vol["is_breach"] else "normal")
        with v2:
            st.metric("NIFTY 50 Volatility",    f"{stats['NIFTY 50']['annualized_volatility']*100:.1f}%",
                      "2020-2025")
        with v3:
            st.metric("Gold / NIFTY Correlation", f"{stats['nifty_gold_correlation']:.2f}",
                      "Diversification Factor")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.85rem; font-weight:600; color:{TEXT_MUTED};
                    margin-bottom:10px;">Empirical Asset Annualized Statistics</div>
        """, unsafe_allow_html=True)
        stat_rows = []
        for k in ["NIFTY 50", "Gold", "Govt Bonds", "Cash", "Corporate Bonds"]:
            if k in stats:
                stat_rows.append({
                    "Asset":               k,
                    "Annualized Return":   f"{stats[k]['annualized_return']*100:.1f}%",
                    "Annualized Volatility": f"{stats[k]['annualized_volatility']*100:.1f}%"
                })
        st.dataframe(pd.DataFrame(stat_rows), use_container_width=True, hide_index=True)

    # ── Tab 3: Drawdown Analysis ──────────────────────────────────────────────
    with tabs[2]:
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:16px;">
            Historical Peak-to-Trough Drawdown Analysis
        </div>
        """, unsafe_allow_html=True)
        d1, d2 = st.columns(2)
        with d1:
            st.metric("Historical Max Drawdown",   f"{dd['max_drawdown']*100:.1f}%",
                      "Policy Limit: 20.0%",
                      delta_color="inverse" if dd["is_breach"] else "normal")
        with d2:
            st.metric("Current Underwater Depth",  f"{dd['current_drawdown']*100:.1f}%",
                      "Relative to Peak")

        if "drawdown_series" in dd and dd["drawdown_series"]:
            dd_df = pd.DataFrame(dd["drawdown_series"])
            fig = px.area(
                dd_df, x="Date", y="Drawdown",
                title="Historical Underwater Drawdown Profile",
                color_discrete_sequence=["#EF4444"]
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color=TEXT_PRIMARY, family="Inter, sans-serif")
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Tab 4: Liquidity Engine ───────────────────────────────────────────────
    with tabs[3]:
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:16px;">
            Liquid Asset Ratio (LAR) &amp; Liquidation Schedule
        </div>
        """, unsafe_allow_html=True)
        l1, l2, l3 = st.columns(3)
        with l1:
            st.metric("Liquid Asset Ratio",       f"{liq['liquid_asset_ratio']*100:.1f}%",
                      f"Status: {liq['status']}")
        with l2:
            st.metric("Weighted Days to Liquidate", f"{liq['weighted_liquidation_days']} Days",
                      "Target: < 5 Days")
        with l3:
            st.metric("Stressed Haircut Loss",    f"{liq['haircut_loss_pct']:.2f}%",
                      "Under Fire-Sale Conditions")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.85rem; font-weight:600; color:{TEXT_MUTED};
                    margin-bottom:10px;">Holdings Liquidity Characteristics</div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(liq["asset_breakdown"]), use_container_width=True, hide_index=True)

    # ── Tab 5: Composite Risk Score ───────────────────────────────────────────
    with tabs[4]:
        st.markdown(f"""
        <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:16px;">
            Composite Risk Score Methodology (0–100)
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        **Current Prototype Methodology**:
        $$\\text{{Risk Score}} = 30\\% \\cdot \\text{{Concentration}} + 25\\% \\cdot \\text{{Volatility}} + 20\\% \\cdot \\text{{Liquidity Deficiency}} + 25\\% \\cdot \\text{{Stress Vulnerability}}$$
        """)

        sub = comp["sub_scores"]
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.metric("Concentration Sub-Score", f"{sub['concentration']}/100",  "Weight: 30%")
        with sc2:
            st.metric("Volatility Sub-Score",    f"{sub['volatility']}/100",     "Weight: 25%")
        with sc3:
            st.metric("Liquidity Sub-Score",     f"{sub['liquidity']}/100",      "Weight: 20%")
        with sc4:
            st.metric("Stress Sub-Score",        f"{sub['stress_loss']}/100",    "Weight: 25%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="fincap-card" style="background:{BG_CARD}; border:2px solid {comp['color']};
             border-radius:20px; padding:28px 32px; text-align:center;
             box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div style="font-size:0.85rem; color:{TEXT_MUTED}; font-weight:600;
                        text-transform:uppercase; letter-spacing:0.07em; margin-bottom:8px;">
                Final Weighted Composite Risk Score
            </div>
            <div style="font-size:3.8rem; font-weight:900; color:{comp['color']};
                        font-family:{FONT_FAMILY}; line-height:1.1;">
                {comp['composite_score']} <span style="font-size:1.5rem; opacity:0.6;">/ 100</span>
            </div>
            <div style="font-size:1.1rem; font-weight:700; color:{comp['color']}; margin-top:8px;">
                {comp['rating']} — {comp['badge']}
            </div>
        </div>
        """, unsafe_allow_html=True)
