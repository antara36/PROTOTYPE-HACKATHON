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

# Page configuration
st.set_page_config(
    page_title="FINCAP GUARD — Institutional Control System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling for institutional terminal appearance
st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
    }
    div[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 800;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    /* Streamlit adds these links to headings; the app does not use anchor navigation. */
    a[href^="#"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Backend Orchestrator in Session State
if "system" not in st.session_state:
    with st.spinner("Initializing FINCAP GUARD Institutional Engine..."):
        st.session_state["system"] = FincapGuardSystem()

system = st.session_state["system"]

# Authentication State
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

def render_login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 32px; text-align: center;">
            <div style="font-size: 3rem;">🛡️</div>
            <h2 style="color: #F8FAFC; margin-bottom: 4px;">FINCAP GUARD</h2>
            <div style="color: #94A3B8; font-size: 0.95rem; margin-bottom: 24px;">Institutional Risk, Control Safeguards & Decision Intelligence</div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Institutional Email", value="risk.officer@fincap.com")
            password = st.text_input("Password", type="password", value="FincapGuard2026!")
            submit = st.form_submit_button("Sign In to Control Terminal", use_container_width=True, type="primary")
            
            if submit:
                res = system.auth_service.login(email, password)
                if res["authenticated"]:
                    st.session_state["auth_user"] = res
                    st.success("Authentication successful! Loading control dashboard...")
                    st.rerun()
                else:
                    st.error(res.get("error", "Authentication failed."))

        st.caption("Demo Access: `risk.officer@fincap.com` / `FincapGuard2026!` (or click Sign In)")

# Check Auth
if not st.session_state["auth_user"]:
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"],
            button[data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    render_login_screen()
    st.stop()

# ----------------- Logged In Application -----------------
user = st.session_state["auth_user"]

# Sidebar Profile & Navigation
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
        <span style="font-size: 2rem;">🛡️</span>
        <div>
            <div style="font-weight: 800; font-size: 1.1rem; color: #F8FAFC;">FINCAP GUARD</div>
            <div style="font-size: 0.75rem; color: #10B981; font-weight: 600;">ACTIVE SAFEGUARD ENGINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 10px; margin-bottom: 20px;">
        <div style="font-size: 0.85rem; font-weight: 700; color: #F8FAFC;">{user['name']}</div>
        <div style="font-size: 0.75rem; color: #94A3B8;">{user['role']}</div>
        <div style="font-size: 0.7rem; color: #38BDF8;">{user['institution']}</div>
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
        index=0
    )

    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["auth_user"] = None
        st.rerun()

# Load real-time system state
dashboard_state = system.get_full_dashboard_state()

# Route Pages
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
