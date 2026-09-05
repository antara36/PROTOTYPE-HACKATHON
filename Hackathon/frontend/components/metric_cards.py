import streamlit as st
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_PINK, ACCENT_PURPLE,
    FILL_BLUE, FILL_GREEN, FILL_YELLOW, FILL_PINK, FILL_PURPLE,
    BORDER_BLUE, BORDER_GREEN, BORDER_YELLOW, BORDER_PINK, BORDER_PURPLE,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    FONT_FAMILY
)


def render_metric_card(title: str, value: str, delta: str = None,
                       delta_color: str = "normal", help_text: str = None):
    st.metric(label=title, value=value, delta=delta,
              delta_color=delta_color, help=help_text)


def _kpi_card(col, icon, label, value, sub, border_col, fill):
    col.markdown(f"""
    <div class="fincap-card" style="background:{fill}; border:1px solid {border_col};
         border-radius:20px; padding:20px 22px;
         box-shadow:0 2px 10px rgba(0,0,0,0.03); margin-bottom:8px; height:100%;">
        <div style="font-size:1.6rem; margin-bottom:6px;">{icon}</div>
        <div style="font-size:0.72rem; font-weight:700; color:{TEXT_MUTED};
                    text-transform:uppercase; letter-spacing:0.08em;">{label}</div>
        <div style="font-size:1.7rem; font-weight:800; color:{TEXT_PRIMARY};
                    margin:6px 0 4px 0; font-family:{FONT_FAMILY};">{value}</div>
        <div style="font-size:0.8rem; color:{TEXT_PRIMARY}; font-weight:600; opacity:0.85;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(capital_str: str, risk_score: float, risk_badge: str, risk_color: str,
                   liquidity_pct: float, liq_status: str,
                   exp_return_pct: float, vol_pct: float):

    col1, col2, col3, col4, col5 = st.columns(5)

    # 1 — Total Capital (Soft Blue)
    _kpi_card(col1, "💰", "Total Capital", capital_str,
              "Institutional Valuation", BORDER_BLUE, FILL_BLUE)

    # 2 — Composite Risk (Soft Pink)
    _kpi_card(col2, "🎯", "Composite Risk", f"{risk_score}/100",
              risk_badge, BORDER_PINK, FILL_PINK)

    # 3 — Liquid Asset Ratio (Soft Green)
    liq_border = BORDER_GREEN if liquidity_pct >= 30 else (BORDER_YELLOW if liquidity_pct >= 20 else BORDER_PINK)
    liq_fill   = FILL_GREEN if liquidity_pct >= 30 else (FILL_YELLOW if liquidity_pct >= 20 else FILL_PINK)
    _kpi_card(col3, "💧", "Liquid Asset Ratio",
              f"{liquidity_pct:.1f}%",
              f"{liq_status} · Min 20%", liq_border, liq_fill)

    # 4 — Expected Return (Soft Yellow)
    _kpi_card(col4, "📈", "Expected Return",
              f"{exp_return_pct:.1f}%",
              "Annualized Yield", BORDER_YELLOW, FILL_YELLOW)

    # 5 — Volatility (Soft Purple)
    vol_border = BORDER_PINK if vol_pct > 15.0 else BORDER_PURPLE
    vol_fill   = FILL_PINK if vol_pct > 15.0 else FILL_PURPLE
    _kpi_card(col5, "📉", "Annualized Vol",
              f"{vol_pct:.1f}%",
              "Limit: 15.0%", vol_border, vol_fill)
