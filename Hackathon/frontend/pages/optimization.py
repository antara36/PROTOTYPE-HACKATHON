import streamlit as st
import pandas as pd
from frontend.components.charts import plot_optimization_comparison

def show_optimization(system, state):
    st.title("🎯 Portfolio Optimization Engine")
    st.caption("SciPy SLSQP Constrained Optimization generating 3 distinct corrective action alternatives.")

    decision = state["decision_data"]
    options = decision["all_options"]
    current = decision["current_state"]
    comp_tbl = decision["comparison_table"]

    st.subheader("Comparison of Corrective Rebalancing Alternatives")
    st.dataframe(pd.DataFrame(comp_tbl), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Allocation Shift Comparison Chart
    st.plotly_chart(
        plot_optimization_comparison(options, current["weights"]),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("💡 Innovation Highlight: Least-Disruptive Optimization")
    st.info("""
    **Why Least-Disruptive Rebalancing Wins**:  
    Traditional portfolio optimizers blindly maximize return or minimize variance without regard to execution friction, 
    often demanding 50%+ turnover that triggers high transaction costs, capital gains taxes, and market slippage.  
    
    **FINCAP Guard's Objective**:  
    $$\\min_{w} \\sum_{i} (w_i - w_{\\text{curr}, i})^2 \\quad \\text{s.t.} \\quad \\text{Risk} \\le 15\\%, \\; \\text{Liquidity} \\ge 20\\%, \\; \\text{Equity} \\le 40\\%$$  
    This restores **100% regulatory compliance** while keeping turnover to an absolute minimum (**Option B: Low Impact**).
    """)

    # Option Cards
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        oa = options["option_a"]
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 15px;">
            <h4>{oa['name']}</h4>
            <p>Heavily defensive flight to safety.</p>
            <p><b>Return:</b> {oa['expected_return']}%</p>
            <p><b>Volatility:</b> {oa['volatility']}%</p>
            <p><b>Liquidity:</b> {oa['liquidity_ratio']}%</p>
            <p style="color: {oa['impact_color']};"><b>Turnover:</b> {oa['turnover_pct']}% ({oa['impact_level']})</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        ob = options["option_b"]
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10B981; border-radius: 10px; padding: 15px;">
            <div style="color: #10B981; font-weight: 800; font-size: 0.75rem;">RECOMMENDED ACTION</div>
            <h4 style="color: #F8FAFC;">{ob['name']}</h4>
            <p>Smallest change to restore safe state.</p>
            <p><b>Return:</b> {ob['expected_return']}%</p>
            <p><b>Volatility:</b> {ob['volatility']}%</p>
            <p><b>Liquidity:</b> {ob['liquidity_ratio']}%</p>
            <p style="color: {ob['impact_color']};"><b>Turnover:</b> {ob['turnover_pct']}% ({ob['impact_level']})</p>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        oc = options["option_c"]
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 15px;">
            <h4>{oc['name']}</h4>
            <p>Maximizes yield on safe boundary.</p>
            <p><b>Return:</b> {oc['expected_return']}%</p>
            <p><b>Volatility:</b> {oc['volatility']}%</p>
            <p><b>Liquidity:</b> {oc['liquidity_ratio']}%</p>
            <p style="color: {oc['impact_color']};"><b>Turnover:</b> {oc['turnover_pct']}% ({oc['impact_level']})</p>
        </div>
        """, unsafe_allow_html=True)
