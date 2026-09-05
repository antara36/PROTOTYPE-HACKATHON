import streamlit as st
import pandas as pd
from backend.utils.calculations import format_currency_inr
from frontend.components.charts import plot_stress_impact_bars
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_YELLOW, FILL_YELLOW, BORDER_YELLOW, COLOR_DANGER, COLOR_SUCCESS,
    FILL_GREEN, SIDEBAR_ACCENT
)


def show_stress_testing(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            ⚡ Stress Testing &amp; Market Shock Simulation
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            Simulate severe macroeconomic and market dislocations against portfolio capital resilience.
        </div>
    </div>
    """, unsafe_allow_html=True)

    summary  = state["portfolio_summary"]
    port_df  = pd.DataFrame(summary["holdings"])
    scenarios = system.stress_engine.get_available_scenarios()

    col_select, col_ml = st.columns([2, 1])
    with col_select:
        selected_scenario = st.selectbox("Select Macroeconomic Stress Scenario:", scenarios, index=0)
    with col_ml:
        ml = state["ml_prediction"]
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_YELLOW}; border:1.5px solid {BORDER_YELLOW};
             border-radius:18px; padding:16px 20px;
             box-shadow:0 2px 10px rgba(0,0,0,0.03);">
            <div style="font-size:0.72rem; font-weight:700; color:{TEXT_MUTED};
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:4px;">
                🤖 ML Model Regime
            </div>
            <div style="font-weight:800; font-size:1rem; color:{ml['regime_color']};
                        font-family:{FONT_FAMILY};">
                {ml['regime_badge']} &nbsp; <span style="font-size:0.82rem; opacity:0.85;">({ml['crisis_probability_pct']}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Run selected test
    res = system.stress_engine.run_stress_test(port_df, selected_scenario)

    st.markdown("<br>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Pre-Shock Portfolio",   format_currency_inr(res["original_total"]))
    with s2:
        st.metric("Post-Shock Portfolio",  format_currency_inr(res["stressed_total"]))
    with s3:
        st.metric("Projected Capital Loss", format_currency_inr(res["total_loss_inr"]),
                  delta=f"{res['loss_pct']*100:.1f}%", delta_color="inverse")
    with s4:
        breach_badge = "BREACH 🔴" if res["is_stress_breach"] else "TOLERABLE 🟢"
        st.metric("Policy Limit Check", breach_badge, "Max Loss Cap: 12.0%")

    st.markdown(f"""
    <div class="fincap-card" style="background:{FILL_YELLOW}; border-radius:14px; padding:14px 20px;
                font-size:0.9rem; color:{TEXT_PRIMARY}; margin:16px 0;
                border:1px solid {BORDER_YELLOW};">
        <b>Scenario:</b> {res['description']}
    </div>
    """, unsafe_allow_html=True)

    # Impact Chart
    st.markdown(f"""
    <div style="background:{BG_CARD}; border-radius:18px; padding:8px 8px 0 8px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:20px;">
    """, unsafe_allow_html=True)
    st.plotly_chart(plot_stress_impact_bars(res["asset_breakdown"]), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:12px;">
        📋 Comprehensive 4-Scenario Stress Matrix
    </div>
    """, unsafe_allow_html=True)

    all_res     = system.stress_engine.run_all_scenarios(port_df)
    matrix_rows = []
    for r in all_res:
        matrix_rows.append({
            "Scenario":         r["scenario"],
            "Description":      r["description"],
            "Stressed Valuation": format_currency_inr(r["stressed_total"]),
            "Loss Amount":      format_currency_inr(r["total_loss_inr"]),
            "Loss (%)":         f"{r['loss_pct']*100:.2f}%",
            "Stress Tolerance": "BREACH 🔴" if r["is_stress_breach"] else "PASS 🟢"
        })
    st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True, hide_index=True)
