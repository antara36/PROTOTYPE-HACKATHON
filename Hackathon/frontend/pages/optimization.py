import streamlit as st
import pandas as pd
from frontend.components.charts import plot_optimization_comparison
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    ACCENT_GREEN, FILL_GREEN, BORDER_GREEN,
    ACCENT_BLUE, FILL_BLUE, BORDER_BLUE,
    ACCENT_PURPLE, FILL_PURPLE, BORDER_PURPLE,
    COLOR_SUCCESS, SIDEBAR_ACCENT
)


def show_optimization(system, state):
    # ── Page Header ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <h1 style="font-family:{FONT_FAMILY}; font-size:2rem; font-weight:800;
                   color:{TEXT_PRIMARY}; margin:0 0 4px 0;">
            🎯 Portfolio Optimization Engine
        </h1>
        <div style="font-size:0.9rem; color:{TEXT_MUTED};">
            SciPy SLSQP Constrained Optimization generating 3 distinct corrective action alternatives.
        </div>
    </div>
    """, unsafe_allow_html=True)

    decision  = state["decision_data"]
    options   = decision["all_options"]
    current   = decision["current_state"]
    comp_tbl  = decision["comparison_table"]

    st.markdown(f"""
    <div style="font-size:1rem; font-weight:700; color:{TEXT_PRIMARY};
                font-family:{FONT_FAMILY}; margin-bottom:12px;">
        Comparison of Corrective Rebalancing Alternatives
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(comp_tbl), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Allocation Shift Comparison Chart
    st.markdown(f"""
    <div style="background:{BG_CARD}; border-radius:18px; padding:8px 8px 0 8px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:24px;">
    """, unsafe_allow_html=True)
    st.plotly_chart(
        plot_optimization_comparison(options, current["weights"]),
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Innovation Highlight Banner
    st.markdown(f"""
    <div class="fincap-card" style="background:{FILL_GREEN}; border:1.5px solid {BORDER_GREEN};
         border-radius:20px; padding:22px 26px; margin-bottom:24px;
         box-shadow:0 2px 12px rgba(16,185,129,0.06);">
        <div style="font-size:1.05rem; font-weight:800; color:{TEXT_PRIMARY};
                    font-family:{FONT_FAMILY}; margin-bottom:10px;">
            💡 Innovation Highlight: Least-Disruptive Optimization
        </div>
        <div style="font-size:0.88rem; color:{TEXT_MUTED}; line-height:1.65;">
            <b>Why Least-Disruptive Rebalancing Wins:</b> Traditional portfolio optimizers blindly maximize
            return or minimize variance without regard to execution friction, often demanding 50%+ turnover
            that triggers high transaction costs, capital gains taxes, and market slippage.<br><br>
            <b>FINCAP Guard's Objective:</b> Restores <b>100% regulatory compliance</b> while keeping
            turnover to an absolute minimum <b>(Option B: Low Impact)</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(r"""
    $$\min_{w} \sum_{i} (w_i - w_{\text{curr}, i})^2 \quad \text{s.t.} \quad \text{Risk} \le 15\%, \; \text{Liquidity} \ge 20\%, \; \text{Equity} \le 40\%$$
    """)

    # ── Option Cards ──────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        oa = options["option_a"]
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_BLUE}; border:1.5px solid {BORDER_BLUE};
             border-radius:20px; padding:22px 24px;
             box-shadow:0 2px 10px rgba(0,0,0,0.03); height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:{ACCENT_BLUE};
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
                Option A
            </div>
            <div style="font-size:1.1rem; font-weight:800; color:{TEXT_PRIMARY};
                        font-family:{FONT_FAMILY}; margin-bottom:8px;">{oa['name']}</div>
            <div style="font-size:0.82rem; color:{TEXT_MUTED}; margin-bottom:12px; line-height:1.5;">
                Heavily defensive flight to safety.
            </div>
            <div style="font-size:0.86rem; color:{TEXT_PRIMARY}; line-height:2.0;">
                <b>Return:</b> {oa['expected_return']}%<br>
                <b>Volatility:</b> {oa['volatility']}%<br>
                <b>Liquidity:</b> {oa['liquidity_ratio']}%<br>
                <span style="color:{oa['impact_color']};"><b>Turnover:</b> {oa['turnover_pct']}% ({oa['impact_level']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        ob = options["option_b"]
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_GREEN}; border:1.5px solid {BORDER_GREEN};
             border-radius:20px; padding:22px 24px;
             box-shadow:0 4px 16px rgba(16,185,129,0.08); height:100%;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <span style="background:{COLOR_SUCCESS}; color:#fff; font-weight:800;
                             font-size:0.68rem; padding:4px 12px; border-radius:9999px;
                             letter-spacing:0.06em;">⭐ RECOMMENDED</span>
            </div>
            <div style="font-size:1.1rem; font-weight:800; color:{TEXT_PRIMARY};
                        font-family:{FONT_FAMILY}; margin-bottom:8px;">{ob['name']}</div>
            <div style="font-size:0.82rem; color:{TEXT_MUTED}; margin-bottom:12px; line-height:1.5;">
                Smallest change to restore safe state.
            </div>
            <div style="font-size:0.86rem; color:{TEXT_PRIMARY}; line-height:2.0;">
                <b>Return:</b> {ob['expected_return']}%<br>
                <b>Volatility:</b> {ob['volatility']}%<br>
                <b>Liquidity:</b> {ob['liquidity_ratio']}%<br>
                <span style="color:{ob['impact_color']};"><b>Turnover:</b> {ob['turnover_pct']}% ({ob['impact_level']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c:
        oc = options["option_c"]
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_PURPLE}; border:1.5px solid {BORDER_PURPLE};
             border-radius:20px; padding:22px 24px;
             box-shadow:0 2px 10px rgba(0,0,0,0.03); height:100%;">
            <div style="font-size:0.72rem; font-weight:700; color:{ACCENT_PURPLE};
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
                Option C
            </div>
            <div style="font-size:1.1rem; font-weight:800; color:{TEXT_PRIMARY};
                        font-family:{FONT_FAMILY}; margin-bottom:8px;">{oc['name']}</div>
            <div style="font-size:0.82rem; color:{TEXT_MUTED}; margin-bottom:12px; line-height:1.5;">
                Maximizes yield on safe boundary.
            </div>
            <div style="font-size:0.86rem; color:{TEXT_PRIMARY}; line-height:2.0;">
                <b>Return:</b> {oc['expected_return']}%<br>
                <b>Volatility:</b> {oc['volatility']}%<br>
                <b>Liquidity:</b> {oc['liquidity_ratio']}%<br>
                <span style="color:{oc['impact_color']};"><b>Turnover:</b> {oc['turnover_pct']}% ({oc['impact_level']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
