import streamlit as st

def render_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal", help_text: str = None):
    st.metric(label=title, value=value, delta=delta, delta_color=delta_color, help=help_text)

def render_kpi_row(capital_str: str, risk_score: float, risk_badge: str, risk_color: str,
                   liquidity_pct: float, liq_status: str, exp_return_pct: float, vol_pct: float):
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Total Capital</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #F8FAFC; margin-top: 4px;">{capital_str}</div>
            <div style="font-size: 0.75rem; color: #10B981; margin-top: 4px;">Institutional Valuation</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Composite Risk</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {risk_color}; margin-top: 4px;">{risk_score}/100</div>
            <div style="font-size: 0.75rem; color: {risk_color}; font-weight: 600; margin-top: 4px;">{risk_badge}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        liq_color = "#10B981" if liquidity_pct >= 30 else ("#F59E0B" if liquidity_pct >= 20 else "#EF4444")
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Liquid Asset Ratio</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {liq_color}; margin-top: 4px;">{liquidity_pct:.1f}%</div>
            <div style="font-size: 0.75rem; color: {liq_color}; font-weight: 600; margin-top: 4px;">{liq_status} (Min 20%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Expected Return</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: #38BDF8; margin-top: 4px;">{exp_return_pct:.1f}%</div>
            <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Annualized Yield</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        vol_color = "#EF4444" if vol_pct > 15.0 else "#10B981"
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 16px; text-align: center;">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase; font-weight: 600;">Annualized Volatility</div>
            <div style="font-size: 1.6rem; font-weight: 700; color: {vol_color}; margin-top: 4px;">{vol_pct:.1f}%</div>
            <div style="font-size: 0.75rem; color: {vol_color}; margin-top: 4px;">Limit: 15.0%</div>
        </div>
        """, unsafe_allow_html=True)
