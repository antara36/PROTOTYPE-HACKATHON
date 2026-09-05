import streamlit as st

def render_system_status_banner(system_status: str, breach_count: int, composite_score: float):
    if system_status == "BREACH":
        st.error(f"""
        🚨 **CRITICAL RISK BREACH DETECTED ({breach_count} Active Breach{'es' if breach_count > 1 else ''})**  
        Portfolio composite risk score is **{composite_score}/100**. One or more investment limits have been violated.  
        *Automated control safeguards recommend immediate least-disruptive rebalancing to restore regulatory compliance.*
        """)
    elif system_status == "WARNING":
        st.warning(f"""
        ⚠️ **PORTFOLIO RISK WARNING ({breach_count} Active Warning{'s' if breach_count > 1 else ''})**  
        Portfolio composite risk score is **{composite_score}/100**. Exposure is nearing threshold limits.
        """)
    else:
        st.success(f"""
        ✅ **PORTFOLIO IN COMPLIANT SAFE STATE**  
        All allocation, liquidity, and volatility limits are satisfied. Composite risk score is **{composite_score}/100**.
        """)

def render_breach_cards(breaches: list):
    if not breaches:
        st.info("No active risk breaches detected. Portfolio is operating within all policy bounds.")
        return

    st.subheader(f"Active Breaches & Violations ({len(breaches)})")
    for i, breach in enumerate(breaches):
        severity = breach.get("severity", "WARNING")
        icon = "🔴" if severity == "CRITICAL" else "🟡"
        actual = breach.get("actual_value", 0.0)
        limit = breach.get("limit_value", 0.0)
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{icon} {breach.get('type', 'BREACH')}** — {breach.get('message', '')}")
            with col2:
                st.caption(f"Actual: **{actual*100:.1f}%** | Cap: **{limit*100:.0f}%**")
