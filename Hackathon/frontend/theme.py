"""
theme.py — FINCAP GUARD Centralized Theme System
================================================
Single source of truth for all design tokens, colors, typography,
and CSS helper functions used across every page and component.

Inspired by clean, modern fintech UI with:
  - Rich dark sidebar (#121214) with crisp white text and pill hover
  - Warm cream canvas (#FAF7F2)
  - Soft, high-contrast pastel cards with crisp dark typography (#18181B)
  - Sleek black pill action buttons (#18181B)
"""

from pathlib import Path
import streamlit as st

# ---------------------------------------------------------------------------
# COLOR TOKENS
# ---------------------------------------------------------------------------

BG_PAGE     = "#FAF7F2"
BG_SIDEBAR  = "#121214"
BG_CARD     = "#FFFFFF"
BG_CARD_ALT = "#F9F9F8"

# High-contrast pastel fills (like reference dashboard)
FILL_YELLOW = "#FEF3C7"
ACCENT_YELLOW = "#F59E0B"
BORDER_YELLOW = "#FDE68A"

FILL_PINK   = "#FCE7F3"
ACCENT_PINK = "#EC4899"
BORDER_PINK = "#FBCFE8"

FILL_GREEN  = "#DCFCE7"
ACCENT_GREEN = "#10B981"
BORDER_GREEN = "#BBF7D0"

FILL_BLUE   = "#E0F2FE"
ACCENT_BLUE = "#0284C7"
BORDER_BLUE = "#BAE6FD"

FILL_PURPLE = "#F3E8FF"
ACCENT_PURPLE = "#8B5CF6"
BORDER_PURPLE = "#E9D5FF"

# Primary text & muted text
TEXT_PRIMARY       = "#18181B"
TEXT_MUTED         = "#71717A"
TEXT_SIDEBAR       = "#F4F4F5"
TEXT_SIDEBAR_MUTED = "#A1A1AA"

COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER  = "#EF4444"
COLOR_INFO    = "#0284C7"

SIDEBAR_ACCENT    = "#18181B"
SIDEBAR_ACTIVE_BG = "#27272A"

CHART_COLORS = [
    "#3B82F6", "#EC4899", "#10B981", "#F59E0B",
    "#8B5CF6", "#06B6D4", "#F97316", "#64748B"
]

FONT_FAMILY = "'Inter', -apple-system, sans-serif"


# ---------------------------------------------------------------------------
# CSS HELPERS
# ---------------------------------------------------------------------------

def card_style(accent: str = ACCENT_BLUE, fill: str = BG_CARD,
               border: bool = False) -> str:
    border_css = (f"border-left: 4px solid {accent};" if border
                  else "border: 1px solid #E4E4E7;")
    return (f"background:{fill}; {border_css} border-radius:18px; "
            f"padding:22px 24px; box-shadow:0 2px 10px rgba(0,0,0,0.04); "
            f"color:{TEXT_PRIMARY}; margin-bottom:12px;")


def badge_html(text: str, color: str = COLOR_SUCCESS,
               text_color: str = "#FFFFFF") -> str:
    return (f'<span style="background:{color};color:{text_color};font-weight:700;'
            f'font-size:0.75rem;padding:4px 12px;border-radius:9999px;'
            f'letter-spacing:0.04em;">{text}</span>')


# ---------------------------------------------------------------------------
# THEME INJECTION
# ---------------------------------------------------------------------------

def inject_theme():
    """
    Injects the global stylesheet via Streamlit's official Path handler.
    st.html(Path(...)) automatically encapsulates the CSS in a <style> tag
    and sends it to the event container, ensuring zero sanitization issues.
    """
    css_path = Path(__file__).resolve().parent / "style.css"
    if css_path.exists():
        st.html(css_path)
