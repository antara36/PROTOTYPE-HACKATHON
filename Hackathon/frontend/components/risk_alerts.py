import streamlit as st
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED, FONT_FAMILY,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    FILL_GREEN, FILL_YELLOW, FILL_PINK,
    BORDER_GREEN, BORDER_YELLOW, BORDER_PINK
)


def render_system_status_banner(system_status: str, breach_count: int,
                                composite_score: float):
    if system_status == "BREACH":
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_PINK}; border:1.5px solid {BORDER_PINK};
             border-radius:18px; padding:18px 24px; margin-bottom:20px;
             box-shadow:0 2px 12px rgba(239,68,68,0.08);">
            <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                <span style="font-size:1.6rem;">🚨</span>
                <div>
                    <div style="font-weight:800; font-size:1.02rem; color:#991B1B; font-family:{FONT_FAMILY};">
                        CRITICAL RISK BREACH — {breach_count} Active Breach{'es' if breach_count > 1 else ''}
                    </div>
                    <div style="font-size:0.86rem; color:#7F1D1D; margin-top:3px; font-weight:500;">
                        Portfolio composite risk score is <b>{composite_score}/100</b>.
                        One or more investment limits have been violated. Automated control safeguards recommend immediate rebalancing.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif system_status == "WARNING":
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_YELLOW}; border:1.5px solid {BORDER_YELLOW};
             border-radius:18px; padding:18px 24px; margin-bottom:20px;
             box-shadow:0 2px 12px rgba(245,158,11,0.08);">
            <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                <span style="font-size:1.6rem;">⚠️</span>
                <div>
                    <div style="font-weight:800; font-size:1.02rem; color:#92400E; font-family:{FONT_FAMILY};">
                        PORTFOLIO RISK WARNING — {breach_count} Active Warning{'s' if breach_count > 1 else ''}
                    </div>
                    <div style="font-size:0.86rem; color:#78350F; margin-top:3px; font-weight:500;">
                        Portfolio composite risk score is <b>{composite_score}/100</b>.
                        Exposure is nearing policy threshold limits.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_GREEN}; border:1.5px solid {BORDER_GREEN};
             border-radius:18px; padding:18px 24px; margin-bottom:20px;
             box-shadow:0 2px 12px rgba(16,185,129,0.06);">
            <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                <span style="font-size:1.6rem;">✅</span>
                <div>
                    <div style="font-weight:800; font-size:1.02rem; color:#065F46; font-family:{FONT_FAMILY};">
                        PORTFOLIO IN COMPLIANT SAFE STATE
                    </div>
                    <div style="font-size:0.86rem; color:#047857; margin-top:3px; font-weight:500;">
                        All allocation, liquidity, and volatility limits are satisfied.
                        Composite risk score is <b>{composite_score}/100</b>.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_breach_cards(breaches: list):
    if not breaches:
        st.markdown(f"""
        <div class="fincap-card" style="background:{FILL_GREEN}; border-radius:16px; padding:16px 20px;
                    border:1px solid {BORDER_GREEN}; color:#065F46; font-weight:600; font-size:0.9rem;">
            ✅ &nbsp; No active risk breaches detected. Portfolio is operating within all policy bounds.
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="font-size:1rem; font-weight:800; color:{TEXT_PRIMARY};
                margin-bottom:12px; font-family:{FONT_FAMILY};">
        🔔 Active Breaches &amp; Violations ({len(breaches)})
    </div>
    """, unsafe_allow_html=True)

    for i, breach in enumerate(breaches):
        severity    = breach.get("severity", "WARNING")
        is_critical = (severity == "CRITICAL")
        bg_color    = FILL_PINK if is_critical else FILL_YELLOW
        border_col  = BORDER_PINK if is_critical else BORDER_YELLOW
        text_col    = "#991B1B" if is_critical else "#92400E"
        icon        = "🔴" if is_critical else "🟡"
        actual      = breach.get("actual_value", 0.0)
        limit       = breach.get("limit_value", 0.0)

        st.markdown(f"""
        <div class="fincap-card" style="background:{bg_color}; border:1px solid {border_col};
             border-radius:14px; padding:14px 18px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div style="font-weight:700; font-size:0.9rem; color:{text_col};">
                    {icon} &nbsp;{breach.get('type','BREACH')} — {breach.get('message','')}
                </div>
                <div style="font-size:0.8rem; color:{TEXT_PRIMARY}; font-weight:600; white-space:nowrap; opacity:0.85;">
                    Actual: <b>{actual*100:.1f}%</b> &nbsp;|&nbsp; Cap: <b>{limit*100:.0f}%</b>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
