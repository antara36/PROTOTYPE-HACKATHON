import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import pandas as pd
from backend.main import FincapGuardSystem
from frontend.pages.dashboard import show_dashboard
from frontend.pages.portfolio import show_portfolio
from frontend.pages.risk_analysis import show_risk_analysis
from frontend.pages.stress_testing import show_stress_testing
from frontend.pages.optimization import show_optimization
from frontend.pages.recommendations import show_recommendations
from frontend.pages.compliance_rag import show_compliance_rag
from frontend.theme import (
    inject_theme,
    BG_SIDEBAR, TEXT_SIDEBAR, TEXT_SIDEBAR_MUTED,
    SIDEBAR_ACCENT, SIDEBAR_ACTIVE_BG,
    COLOR_SUCCESS, BG_CARD, TEXT_PRIMARY, TEXT_MUTED,
    ACCENT_PURPLE, FILL_PURPLE
)

# Page configuration
st.set_page_config(
    page_title="FINCAP GUARD — Institutional Control System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject global theme (font, background, component overrides)
inject_theme()

# ---------------------------------------------------------------------------
# Initialize Backend Orchestrator in Session State
# ---------------------------------------------------------------------------
if "system" not in st.session_state:
    with st.spinner("Initializing FINCAP GUARD Institutional Engine..."):
        st.session_state["system"] = FincapGuardSystem()

system = st.session_state["system"]

# Authentication State
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

# ---------------------------------------------------------------------------
# LOGIN SCREEN
# ---------------------------------------------------------------------------
def render_login_screen():
    # Hide the sidebar on the login page
    st.markdown("""
    <style>
        section[data-testid="stSidebar"],
        button[data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        st.markdown(f"""
        <div class="fincap-card" style="background:{BG_CARD}; border-radius:24px;
             padding:40px 36px; box-shadow:0 8px 40px rgba(0,0,0,0.12);
             text-align:center; border-top:5px solid {SIDEBAR_ACCENT};">
            <div style="font-size:3.2rem; margin-bottom:8px;">🛡️</div>
            <div style="font-family:'Inter',sans-serif; font-size:1.8rem;
                        font-weight:800; color:{TEXT_PRIMARY}; letter-spacing:-0.5px;">
                FINCAP GUARD
            </div>
            <div style="font-size:0.9rem; color:{TEXT_MUTED}; margin-top:6px; margin-bottom:28px;">
                Institutional Risk, Control Safeguards &amp; Decision Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            email    = st.text_input("📧 Institutional Email", value="risk.officer@fincap.com")
            password = st.text_input("🔐 Password", type="password", value="FincapGuard2026!")
            submit   = st.form_submit_button(
                "Sign In to Control Terminal",
                use_container_width=True,
                type="primary"
            )
            if submit:
                res = system.auth_service.login(email, password)
                if res["authenticated"]:
                    st.session_state["auth_user"] = res
                    st.success("Authentication successful! Loading control dashboard...")
                    st.rerun()
                else:
                    st.error(res.get("error", "Authentication failed."))

        st.caption("Demo Access: `risk.officer@fincap.com` / `FincapGuard2026!` (or click Sign In)")

# ---------------------------------------------------------------------------
# Auth Gate
# ---------------------------------------------------------------------------
if not st.session_state["auth_user"]:
    render_login_screen()
    st.stop()

# ---------------------------------------------------------------------------
# LOGGED-IN APPLICATION
# ---------------------------------------------------------------------------
user = st.session_state["auth_user"]

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand logo
    st.markdown(f"""
    <div style="padding:24px 20px 16px 20px;">
        <div style="display:flex; align-items:center; gap:12px;">
            <div style="background:linear-gradient(135deg,{SIDEBAR_ACCENT} 0%,#8B5CF6 100%);
                        width:40px; height:40px; border-radius:12px;
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.3rem; flex-shrink:0;">🛡️</div>
            <div>
                <div style="font-family:'Inter',sans-serif; font-weight:800;
                            font-size:1.05rem; color:#FFFFFF; letter-spacing:-0.3px;">
                    FINCAP GUARD
                </div>
                <div style="font-size:0.68rem; color:{COLOR_SUCCESS}; font-weight:700;
                            letter-spacing:0.08em; margin-top:1px;">
                    ● SAFEGUARD ENGINE ACTIVE
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # User Profile Card
    st.markdown(f"""
    <div style="margin:0 12px 20px 12px; background:rgba(255,255,255,0.07);
                border-radius:14px; padding:14px 16px;
                border:1px solid rgba(255,255,255,0.1);">
        <div style="display:flex; align-items:center; gap:10px;">
            <div style="width:36px;height:36px;border-radius:50%;
                        background:linear-gradient(135deg,{ACCENT_PURPLE} 0%,{SIDEBAR_ACCENT} 100%);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;font-weight:800;color:#fff;flex-shrink:0;">
                {user['name'][0].upper()}
            </div>
            <div>
                <div style="font-size:0.85rem;font-weight:700;color:#FFFFFF;">
                    {user['name']}
                </div>
                <div style="font-size:0.73rem;color:{TEXT_SIDEBAR_MUTED};">{user['role']}</div>
                <div style="font-size:0.7rem;color:#7DE8D8;margin-top:1px;">{user['institution']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="padding:0 12px 6px 12px; font-size:0.68rem; font-weight:700;
                color:{TEXT_SIDEBAR_MUTED}; letter-spacing:0.12em; text-transform:uppercase;">
        Navigation
    </div>
    """, unsafe_allow_html=True)

    nav_choice = st.radio(
        "Navigation",
        [
            "🛡️ Executive Dashboard",
            "💼 Portfolio Holdings",
            "📊 Risk & Liquidity Engine",
            "⚡ Stress Testing",
            "🎯 Optimization (3 Options)",
            "⚖️ Recommendations & Rebalance",
            "🤖 Policy RAG Assistant"
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()

# ---------------------------------------------------------------------------
# Load real-time system state
# ---------------------------------------------------------------------------
dashboard_state = system.get_full_dashboard_state()

# ---------------------------------------------------------------------------
# Route Pages
# ---------------------------------------------------------------------------
if "Executive Dashboard" in nav_choice:
    show_dashboard(system, dashboard_state)
elif "Portfolio Holdings" in nav_choice:
    show_portfolio(system, dashboard_state)
elif "Risk & Liquidity" in nav_choice:
    show_risk_analysis(system, dashboard_state)
elif "Stress Testing" in nav_choice:
    show_stress_testing(system, dashboard_state)
elif "Optimization" in nav_choice:
    show_optimization(system, dashboard_state)
elif "Recommendations" in nav_choice:
    show_recommendations(system, dashboard_state)
elif "Policy RAG" in nav_choice:
    show_compliance_rag(system, dashboard_state)
