import streamlit as st
import pandas as pd
from backend.utils.calculations import format_currency_inr
from frontend.components.charts import plot_stress_impact_bars

def show_stress_testing(system, state):
    st.title("⚡ Stress Testing & Market Shock Simulation")
    st.caption("Simulate severe macroeconomic and market dislocations against portfolio capital resilience.")

    summary = state["portfolio_summary"]
    port_df = pd.DataFrame(summary["holdings"])
    scenarios = system.stress_engine.get_available_scenarios()

    col_select, col_ml = st.columns([2, 1])
    with col_select:
        selected_scenario = st.selectbox("Select Macroeconomic Stress Scenario:", scenarios, index=0)
    with col_ml:
        ml = state["ml_prediction"]
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 10px;">
            <div style="font-size: 0.75rem; color: #94A3B8;">ML Model Regime</div>
            <div style="font-weight: 700; color: {ml['regime_color']};">{ml['regime_badge']} ({ml['crisis_probability_pct']}%)</div>
        </div>
        """, unsafe_allow_html=True)

    # Run selected test
    res = system.stress_engine.run_stress_test(port_df, selected_scenario)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Pre-Shock Portfolio", format_currency_inr(res["original_total"]))
    with s2:
        st.metric("Post-Shock Portfolio", format_currency_inr(res["stressed_total"]))
    with s3:
        st.metric("Projected Capital Loss", format_currency_inr(res["total_loss_inr"]), delta=f"{res['loss_pct']*100:.1f}%", delta_color="inverse")
    with s4:
        breach_badge = "BREACH 🔴" if res["is_stress_breach"] else "TOLERABLE 🟢"
        st.metric("Policy Limit Check", breach_badge, "Max Loss Cap: 12.0%")

    st.markdown(f"**Scenario Description**: *{res['description']}*")
    st.markdown("---")

    # Impact Chart
    st.plotly_chart(plot_stress_impact_bars(res["asset_breakdown"]), use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Comprehensive 4-Scenario Stress Matrix")
    all_res = system.stress_engine.run_all_scenarios(port_df)
    matrix_rows = []
    for r in all_res:
        matrix_rows.append({
            "Scenario": r["scenario"],
            "Description": r["description"],
            "Stressed Valuation": format_currency_inr(r["stressed_total"]),
            "Loss Amount": format_currency_inr(r["total_loss_inr"]),
            "Loss (%)": f"{r['loss_pct']*100:.2f}%",
            "Stress Tolerance": "BREACH 🔴" if r["is_stress_breach"] else "PASS 🟢"
        })
    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
