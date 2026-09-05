import streamlit as st
import pandas as pd

def render_recommendation_card(decision_data: dict, on_apply_callback=None):
    rec = decision_data["recommended_option"]
    justification = decision_data.get("justification", "")
    trades = decision_data.get("trades", [])

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(30, 41, 59, 0.7) 100%); 
                border: 2px solid #10B981; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="background: #10B981; color: #0F172A; font-weight: 800; font-size: 0.8rem; padding: 4px 10px; border-radius: 6px;">
                BEST INSTITUTIONAL RECOMMENDATION
            </span>
            <span style="color: #10B981; font-weight: 700;">Disruption Impact: {rec['impact_level']} (Turnover: {rec['turnover_pct']}%)</span>
        </div>
        <h3 style="color: #F8FAFC; margin-top: 10px; margin-bottom: 6px;">{rec['name']}</h3>
        <p style="color: #CBD5E1; font-size: 0.95rem; line-height: 1.5;">{justification}</p>
    </div>
    """, unsafe_allow_html=True)

    # Key Metrics of Option B
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Target Risk Volatility", f"{rec['volatility']:.1f}%", "-3.2% vs Current")
    with m2:
        st.metric("Expected Return", f"{rec['expected_return']:.1f}%", "-0.4% (Yield Preserved)")
    with m3:
        st.metric("Liquid Asset Ratio", f"{rec['liquidity_ratio']:.1f}%", "+5.0% Buffer")
    with m4:
        st.metric("Rebalancing Turnover", f"{rec['turnover_pct']:.1f}%", "Minimal Friction", delta_color="inverse")

    st.markdown("#### 📋 Recommended Trade Orders")
    if trades:
        trade_rows = []
        for t in trades:
            trade_rows.append({
                "Action": t["action"],
                "Asset": t["asset"],
                "Trade Amount": f"₹{t['amount_inr']:,.0f}",
                "Allocation Shift": f"{t['from_weight_pct']:.1f}% ➔ {t['to_weight_pct']:.1f}%",
                "Instruction": t["trade_statement"]
            })
        st.dataframe(pd.DataFrame(trade_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Portfolio already matches target safe weights.")
