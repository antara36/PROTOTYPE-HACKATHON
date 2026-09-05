import streamlit as st
import pandas as pd
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_GREEN, FILL_GREEN, BORDER_GREEN, COLOR_SUCCESS
)


def render_recommendation_card(decision_data: dict, on_apply_callback=None):
    rec           = decision_data["recommended_option"]
    justification = decision_data.get("justification", "")
    trades        = decision_data.get("trades", [])

    st.markdown(f"""
    <div class="fincap-card" style="background:{FILL_GREEN};
         border:1.5px solid {BORDER_GREEN}; border-radius:20px;
         padding:24px 28px; margin-bottom:20px;
         box-shadow:0 4px 16px rgba(16,185,129,0.06);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;
                    flex-wrap:wrap; gap:10px; margin-bottom:14px;">
            <span style="background:{COLOR_SUCCESS}; color:#fff; font-weight:800;
                         font-size:0.72rem; padding:5px 14px; border-radius:9999px;
                         letter-spacing:0.06em; text-transform:uppercase;">
                ⭐ Best Institutional Recommendation
            </span>
            <span style="background:{BG_CARD}; color:{TEXT_PRIMARY}; font-weight:600;
                         font-size:0.8rem; padding:5px 14px; border-radius:9999px;
                         border:1px solid {BORDER_GREEN};">
                Disruption: {rec['impact_level']} &nbsp;·&nbsp; Turnover: {rec['turnover_pct']}%
            </span>
        </div>
        <div style="font-size:1.25rem; font-weight:800; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:8px;">{rec['name']}</div>
        <div style="font-size:0.9rem; color:{TEXT_MUTED}; line-height:1.65;">{justification}</div>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics of recommended option
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Target Risk Volatility",  f"{rec['volatility']:.1f}%",      "-3.2% vs Current")
    with m2:
        st.metric("Expected Return",         f"{rec['expected_return']:.1f}%",  "-0.4% (Yield Preserved)")
    with m3:
        st.metric("Liquid Asset Ratio",      f"{rec['liquidity_ratio']:.1f}%",  "+5.0% Buffer")
    with m4:
        st.metric("Rebalancing Turnover",    f"{rec['turnover_pct']:.1f}%",     "Minimal Friction",
                  delta_color="inverse")

    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                margin:24px 0 12px 0; font-family:{FONT_FAMILY};">
        📋 Recommended Trade Orders
    </div>
    """, unsafe_allow_html=True)

    if trades:
        trade_rows = []
        for t in trades:
            trade_rows.append({
                "Action":           t["action"],
                "Asset":            t["asset"],
                "Trade Amount":     f"₹{t['amount_inr']:,.0f}",
                "Allocation Shift": f"{t['from_weight_pct']:.1f}% ➔ {t['to_weight_pct']:.1f}%",
                "Instruction":      t["trade_statement"]
            })
        st.dataframe(pd.DataFrame(trade_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio already matches target safe weights.")
