"""
auth_ui.py — FINCAP GUARD Authentication UI
============================================
Beautiful Sign In / Sign Up page with:
  - Matching FINCAP GUARD design language (dark card, cream canvas)
  - Sign Up tab with live password-strength meter
  - Password confirmation validation
  - Strong-password enforcement via backend AuthService
"""

import streamlit as st
from frontend.theme import (
    BG_CARD, TEXT_PRIMARY, TEXT_MUTED,
    SIDEBAR_ACCENT, ACCENT_PURPLE,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
)
from backend.services.auth_service import validate_password_strength


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _hide_sidebar_css():
    st.markdown("""
    <style>
        section[data-testid="stSidebar"],
        button[data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }
        /* Auth page — slightly tighter block container */
        .main .block-container {
            padding-top: 3.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)


def _brand_header():
    st.markdown(f"""
    <div style="text-align:center; padding: 0 0 28px 0;">
        <div style="font-size:3.4rem; margin-bottom:8px; filter:drop-shadow(0 4px 12px rgba(0,0,0,0.12));">
            🛡️
        </div>
        <div style="font-family:'Outfit','Inter',sans-serif; font-size:2rem;
                    font-weight:800; color:{TEXT_PRIMARY}; letter-spacing:-0.6px;">
            FINCAP GUARD
        </div>
        <div style="font-size:0.88rem; color:{TEXT_MUTED}; margin-top:6px; letter-spacing:0.01em;">
            Institutional Risk, Control Safeguards &amp; Decision Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)


def _strength_bar(score: int, label: str):
    """Renders a colour-coded password-strength progress bar."""
    colors   = ["#EF4444", "#F59E0B", "#EAB308", "#10B981", "#059669"]
    widths   = [20, 40, 60, 80, 100]
    bar_col  = colors[min(score, 4)]
    bar_w    = widths[min(score, 4)]
    st.markdown(f"""
    <div style="margin: 6px 0 4px 0;">
        <div style="display:flex; justify-content:space-between;
                    font-size:0.75rem; color:{TEXT_MUTED}; margin-bottom:4px;">
            <span>Password Strength</span>
            <span style="font-weight:700; color:{bar_col};">{label}</span>
        </div>
        <div style="background:#E4E4E7; border-radius:9999px; height:6px; overflow:hidden;">
            <div style="width:{bar_w}%; height:100%; background:{bar_col};
                        border-radius:9999px;
                        transition:width 0.3s ease, background 0.3s ease;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _card_wrap(content_fn):
    """Wraps content in the FINCAP GUARD card style."""
    _, col, _ = st.columns([1, 1.7, 1])
    with col:
        st.markdown(f"""
        <div class="fincap-card" style="
            background:{BG_CARD};
            border-radius:24px;
            padding:40px 36px 32px 36px;
            box-shadow:0 8px 48px rgba(0,0,0,0.10);
            border-top:5px solid {SIDEBAR_ACCENT};
        ">
        """, unsafe_allow_html=True)
        content_fn()
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sign In form
# ---------------------------------------------------------------------------

def _sign_in_form(auth_service):
    with st.form("fincap_signin_form", clear_on_submit=False):
        st.markdown(f"""
        <div style="font-family:'Outfit',sans-serif; font-size:1.35rem;
                    font-weight:800; color:{TEXT_PRIMARY}; margin-bottom:4px;">
            Welcome back
        </div>
        <div style="font-size:0.85rem; color:{TEXT_MUTED}; margin-bottom:24px;">
            Sign in to your institutional control terminal
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("📧 Email address",
                                 placeholder="you@institution.com",
                                 key="si_email")
        password = st.text_input("🔐 Password",
                                 type="password",
                                 placeholder="Your password",
                                 key="si_password")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Sign In →",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating…"):
                    result = auth_service.login(email, password)
                if result["authenticated"]:
                    st.session_state["auth_user"] = result
                    st.query_params["session_user"] = result["email"]
                    st.success("✅ Authentication successful! Loading dashboard…")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Authentication failed.')}")

    # Demo credentials hint
    st.markdown(f"""
    <div style="margin-top:16px; padding:14px 16px; background:#F4F4F5;
                border-radius:14px; border:1px solid #E4E4E7;">
        <div style="font-size:0.76rem; font-weight:700; color:{TEXT_MUTED};
                    text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
            🔑 Demo Credentials
        </div>
        <div style="font-size:0.82rem; color:{TEXT_PRIMARY}; line-height:1.7;">
            <b>Email:</b> risk.officer@fincap.com<br>
            <b>Password:</b> FincapGuard2026!
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sign Up form
# ---------------------------------------------------------------------------

def _sign_up_form(auth_service):
    # Live password strength — stored in session state before form submission
    if "su_pw_live" not in st.session_state:
        st.session_state["su_pw_live"] = ""

    st.markdown(f"""
    <div style="font-family:'Outfit',sans-serif; font-size:1.35rem;
                font-weight:800; color:{TEXT_PRIMARY}; margin-bottom:4px;">
        Create account
    </div>
    <div style="font-size:0.85rem; color:{TEXT_MUTED}; margin-bottom:24px;">
        Join FINCAP GUARD — fill in your institutional details
    </div>
    """, unsafe_allow_html=True)

    with st.form("fincap_signup_form", clear_on_submit=False):
        col_a, col_b = st.columns(2)
        with col_a:
            full_name   = st.text_input("👤 Full Name",
                                        placeholder="Jane Smith",
                                        key="su_name")
        with col_b:
            institution = st.text_input("🏦 Institution",
                                        placeholder="Apex Capital",
                                        key="su_institution")

        email   = st.text_input("📧 Email address",
                                 placeholder="you@institution.com",
                                 key="su_email")
        role    = st.selectbox("🎯 Role",
                               ["Analyst", "Risk Manager", "Portfolio Manager",
                                "Compliance Officer", "Chief Risk Officer",
                                "Quantitative Researcher", "Other"],
                               key="su_role")

        password = st.text_input(
            "🔐 Create Password",
            type="password",
            placeholder="Min 8 chars, upper, lower, digit, special",
            key="su_password",
            help="Must have uppercase, lowercase, digit & special character",
        )
        confirm  = st.text_input("🔐 Confirm Password",
                                  type="password",
                                  placeholder="Re-enter your password",
                                  key="su_confirm")

        # --- Password strength feedback (shown inside form, live-ish via rerun) ---
        if password:
            result = validate_password_strength(password)
            _strength_bar(result["score"], result["strength"])
            if result["errors"]:
                for err in result["errors"]:
                    st.markdown(
                        f'<div style="font-size:0.78rem; color:{COLOR_DANGER}; margin:1px 0;">✗ {err}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    f'<div style="font-size:0.78rem; color:{COLOR_SUCCESS}; margin:2px 0;">✓ Password meets all requirements</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "Create Account →",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            # Client-side checks first
            if not email or not password or not confirm:
                st.error("Email, password, and confirmation are required.")
            elif password != confirm:
                st.error("❌ Passwords do not match.")
            else:
                result = auth_service.register(
                    email=email,
                    password=password,
                    name=full_name,
                    institution=institution,
                    role=role,
                )
                if result["success"]:
                    st.success(
                        f"✅ Account created for **{result['name']}**! "
                        "Switch to **Sign In** to log in."
                    )
                else:
                    if result.get("password_errors"):
                        for err in result["password_errors"]:
                            st.error(f"❌ {err}")
                    else:
                        st.error(f"❌ {result.get('error', 'Registration failed.')}")

    # Password rules reminder
    st.markdown(f"""
    <div style="margin-top:16px; padding:14px 16px; background:#F4F4F5;
                border-radius:14px; border:1px solid #E4E4E7;">
        <div style="font-size:0.76rem; font-weight:700; color:{TEXT_MUTED};
                    text-transform:uppercase; letter-spacing:0.08em; margin-bottom:8px;">
            🛡️ Password Requirements
        </div>
        <div style="font-size:0.82rem; color:{TEXT_PRIMARY}; line-height:1.8;">
            ✓ Minimum <b>8 characters</b><br>
            ✓ At least one <b>uppercase</b> letter<br>
            ✓ At least one <b>lowercase</b> letter<br>
            ✓ At least one <b>digit</b> (0–9)<br>
            ✓ At least one <b>special character</b> (!@#$%^&amp;*…)
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Public entry-point  (called from app.py)
# ---------------------------------------------------------------------------

def show_auth_page(auth_service):
    """
    Renders the full Sign In / Sign Up authentication page.
    Sets st.session_state["auth_user"] on successful sign-in.
    """
    _hide_sidebar_css()

    st.markdown("<br>", unsafe_allow_html=True)

    # Brand header (outside card, above tabs)
    _, hcol, _ = st.columns([1, 1.7, 1])
    with hcol:
        _brand_header()

    # Card with Sign In / Sign Up tabs
    _, col, _ = st.columns([1, 1.7, 1])
    with col:
        st.markdown(f"""
        <div class="fincap-card" style="
            background:{BG_CARD};
            border-radius:24px;
            padding:36px 36px 28px 36px;
            box-shadow:0 8px 48px rgba(0,0,0,0.10);
            border-top:5px solid {SIDEBAR_ACCENT};
        ">
        """, unsafe_allow_html=True)

        tab_signin, tab_signup = st.tabs(["🔑  Sign In", "🆕  Sign Up"])

        with tab_signin:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            _sign_in_form(auth_service)

        with tab_signup:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            _sign_up_form(auth_service)

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    _, fcol, _ = st.columns([1, 1.7, 1])
    with fcol:
        st.markdown(f"""
        <div style="text-align:center; margin-top:20px;
                    font-size:0.78rem; color:{TEXT_MUTED};">
            🛡️ FINCAP GUARD — Institutional-Grade Security &nbsp;|&nbsp;
            All data encrypted at rest
        </div>
        """, unsafe_allow_html=True)
