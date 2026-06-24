"""Top navigation bar (Electrolux dark header)."""
from __future__ import annotations

import base64
import html
from pathlib import Path
from typing import Any

import streamlit as st

_PAGES_ST_DIR = Path(__file__).resolve().parent.parent
_ELEX_LOGO_CANDIDATES = (
    _PAGES_ST_DIR / "assets" / "elex_logo.png",
    _PAGES_ST_DIR.parent / "static" / "images" / "elx-icon.png",
)

# Fallback if elex_logo.png is not on disk yet
_ELECTROLUX_ICON_SVG = """
<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="16" cy="16" r="15" stroke="white" stroke-width="1.5"/>
  <path d="M11 10h8.5c2.2 0 3.5 1.1 3.5 2.8 0 1.2-.7 2.1-1.8 2.5 1.4.3 2.3 1.4 2.3 3 0 2.1-1.6 3.2-4.2 3.2H11V10zm3.2 2.4v3.1h4.6c1 0 1.6-.5 1.6-1.3 0-.8-.6-1.3-1.6-1.3h-4.6zm0 5.5v3.4h5.1c1.2 0 1.9-.6 1.9-1.5 0-.9-.7-1.5-1.9-1.5h-5.1z" fill="white"/>
</svg>
""".strip()


def _elex_logo_markup() -> str:
    """Electrolux mark from elex_logo.png (login page asset), else inline SVG."""
    for path in _ELEX_LOGO_CANDIDATES:
        if path.is_file():
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            return (
                f'<img src="data:image/png;base64,{encoded}" '
                f'class="elex-logo" alt="Electrolux" width="32" height="32" />'
            )
    return _ELECTROLUX_ICON_SVG

# Figma navbar inset: 16px top/bottom, 12px left/right
_NAVBAR_PAD_V = 16
_NAVBAR_PAD_H = 12
_CTRL_H = 36
_TOGGLE_BORDER = "#3E526F"
_TOGGLE_RADIUS = "99px"


def _nav_menus(is_admin: bool) -> list[tuple[str, str | None]]:
    menus: list[tuple[str, str | None]] = [
        ("Dashboard", "dashboard"),
        ("Simulate", "simulate"),
    ]
    if is_admin:
        menus.append(("Admin", "admin"))
    menus.extend([
        ("History", None),
        ("Export", None),
        ("Reports", None),
    ])
    return menus


def _active_nav_key(menus: list[tuple[str, str | None]]) -> str | None:
    current = st.session_state.get("page", "dashboard")
    for _label, page_key in menus:
        if page_key == current:
            return page_key
    return None


def _navbar_css(active_key: str | None) -> str:
    active_rule = ""
    if active_key:
        active_rule = f"""
        [class*="st-key-nav_{active_key}"] button {{
            background: #1a3d66 !important;
            border: none !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }}
        [class*="st-key-nav_{active_key}"] button:hover {{
            background: #1f4675 !important;
            color: #ffffff !important;
        }}
        """

    return f"""
    <style>
    /* Let navbar break out of Streamlit's centered content gutter */
    section.main:has(#navbar-bar-marker),
    [data-testid="stMainBlockContainer"]:has(#navbar-bar-marker),
    [data-testid="stVerticalBlock"]:has(#navbar-bar-marker) {{
        overflow-x: visible !important;
        max-width: 100% !important;
    }}

    #navbar-bar-marker,
    #navbar-left-marker,
    #navbar-nav-marker,
    #navbar-right-marker,
    .mode-toggle-marker {{
        display: none !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) {{
        background-color: #011e41 !important;
        box-sizing: border-box !important;
        padding: {_NAVBAR_PAD_V}px {_NAVBAR_PAD_H}px !important;
        min-height: calc({_CTRL_H}px + {_NAVBAR_PAD_V * 2}px) !important;
        height: auto !important;
        max-height: none !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
        border-bottom: 1px solid #18365d !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        align-content: center !important;
        justify-content: space-between !important;
        gap: 0 !important;
    }}

    /* Flatten Streamlit wrappers — center children, do not squash bar height */
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stVerticalBlock"] > div {{
        gap: 0 !important;
        row-gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        justify-content: center !important;
        align-items: center !important;
        height: auto !important;
        min-height: unset !important;
        max-height: none !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stElementContainer"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stMarkdownContainer"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) div[data-testid="stMarkdown"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) div[data-testid="stButton"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stWidgetLabel"],
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) [data-testid="stSegmentedControl"] {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        align-self: center !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) .stMarkdown p,
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) .stMarkdown {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) > div[data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        align-self: center !important;
        height: auto !important;
        min-height: unset !important;
        max-height: none !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) > div[data-testid="column"]:first-child {{
        flex: 0 1 auto !important;
        width: auto !important;
        max-width: 75% !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) > div[data-testid="column"]:last-child {{
        flex: 1 1 auto !important;
        justify-content: flex-end !important;
    }}

    /* LEFT: logo + Electrolux + nav links */
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker)
    [data-testid="column"]:has(#navbar-left-marker) {{
        flex: 0 1 auto !important;
        justify-content: flex-start !important;
        align-items: center !important;
        width: auto !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-left-marker) > div[data-testid="stVerticalBlock"] {{
        justify-content: flex-start !important;
        align-items: center !important;
        gap: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-left-marker) > div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 8px !important;
        width: auto !important;
    }}

    [data-testid="column"]:has(#navbar-left-marker) [data-testid="column"] {{
        flex: 0 0 auto !important;
        width: auto !important;
        display: flex !important;
        align-items: center !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) {{
        flex: 0 0 auto !important;
        justify-content: flex-start !important;
        align-items: center !important;
        width: auto !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) {{
        justify-content: flex-start !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) > div[data-testid="stVerticalBlock"] {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        height: auto !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 4px !important;
        width: auto !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) [data-testid="column"] {{
        width: auto !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        height: auto !important;
    }}

    [data-testid="column"]:has(#navbar-nav-marker) div[data-testid="stButton"] {{
        display: flex !important;
        align-items: center !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
    }}

    /* RIGHT: mode, countries, bell, profile */
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker)
    [data-testid="column"]:has(#navbar-right-marker) {{
        margin-left: auto !important;
        flex: 0 0 auto !important;
        justify-content: flex-end !important;
        align-items: center !important;
        width: auto !important;
        min-width: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) > div[data-testid="stVerticalBlock"] {{
        align-items: flex-end !important;
        justify-content: center !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) > div[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 12px !important;
        width: auto !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) [data-testid="column"] {{
        flex: 0 0 auto !important;
        width: auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) > div[data-testid="stVerticalBlock"] {{
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: flex-end !important;
        height: auto !important;
        width: 100% !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) [data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: flex-end !important;
        gap: 12px !important;
        width: auto !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
    }}

    [data-testid="column"]:has(#navbar-right-marker) [data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: auto !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }}

    [class*="st-key-nav_"] button {{
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 0 14px !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
        line-height: {_CTRL_H}px !important;
        border-radius: 8px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
    }}

    [class*="st-key-nav_"] button:hover {{
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
    }}

    [class*="st-key-nav_history"] button,
    [class*="st-key-nav_export"] button,
    [class*="st-key-nav_reports"] button {{
        opacity: 0.92 !important;
        cursor: default !important;
    }}

    {active_rule}

    .logo-wrap {{
        display: flex;
        align-items: center;
        gap: 10px;
        height: {_CTRL_H}px;
        white-space: nowrap;
    }}

    .logo-wrap svg,
    .logo-wrap .elex-logo {{
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        display: block;
        object-fit: contain;
    }}

    .logo-text {{
        color: #ffffff;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}

    .scope-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        height: {_CTRL_H}px;
        padding: 0 14px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.05);
        color: #ffffff;
        font-size: 13px;
        font-weight: 500;
        white-space: nowrap;
    }}

    .scope-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #eab308;
        flex-shrink: 0;
    }}

    /* Mode toggle — clickable pill buttons */
    [data-testid="column"]:has(.mode-toggle-marker) {{
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: unset !important;
        z-index: 5 !important;
        pointer-events: auto !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) > div[data-testid="stVerticalBlock"],
    [data-testid="column"]:has(.mode-toggle-marker) [data-testid="stElementContainer"] {{
        gap: 0 !important;
        align-items: center !important;
        width: auto !important;
        overflow: visible !important;
        pointer-events: auto !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [data-testid="stHorizontalBlock"]:has([class*="st-key-mode_ctrl"]) {{
        display: inline-flex !important;
        flex: 0 0 auto !important;
        width: auto !important;
        align-items: center !important;
        gap: 2px !important;
        margin: 0 !important;
        padding: 3px !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
        box-sizing: border-box !important;
        border: 1px solid {_TOGGLE_BORDER} !important;
        border-radius: {_TOGGLE_RADIUS} !important;
        background: rgba(255, 255, 255, 0.04) !important;
        position: relative !important;
        z-index: 5 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
        flex: 0 0 auto !important;
        width: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        pointer-events: auto !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_ctrl"],
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_mgmt"] {{
        pointer-events: auto !important;
        z-index: 5 !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_ctrl"] [data-testid="stButton"],
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_mgmt"] [data-testid="stButton"] {{
        width: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: auto !important;
        cursor: pointer !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_ctrl"] button,
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_mgmt"] button {{
        opacity: 1 !important;
        visibility: visible !important;
        pointer-events: auto !important;
        color: rgba(198, 210, 225, 0.95) !important;
        background: transparent !important;
        border: none !important;
        border-radius: {_TOGGLE_RADIUS} !important;
        padding: 0 14px !important;
        margin: 0 !important;
        height: 30px !important;
        min-height: 30px !important;
        max-height: 30px !important;
        width: auto !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        line-height: 30px !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        cursor: pointer !important;
    }}

    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_ctrl"] button p,
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_mgmt"] button p,
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_ctrl"] button span,
    [data-testid="column"]:has(.mode-toggle-marker) [class*="st-key-mode_mgmt"] button span {{
        color: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        cursor: pointer !important;
        pointer-events: none !important;
    }}

    [data-testid="column"]:has(.mode-is-controller) [class*="st-key-mode_ctrl"] button {{
        background: #1a3d66 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    [data-testid="column"]:has(.mode-is-management) [class*="st-key-mode_mgmt"] button {{
        background: #1a3d66 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    [data-testid="column"]:has(.mode-is-controller) [class*="st-key-mode_mgmt"] button:hover,
    [data-testid="column"]:has(.mode-is-management) [class*="st-key-mode_ctrl"] button:hover {{
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
    }}

    [data-testid="column"]:has(.mode-is-controller) [class*="st-key-mode_ctrl"] button:hover,
    [data-testid="column"]:has(.mode-is-management) [class*="st-key-mode_mgmt"] button:hover {{
        background: #1f4675 !important;
        color: #ffffff !important;
    }}

    .notification-wrap {{
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: {_CTRL_H}px;
        height: {_CTRL_H}px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }}

    .bell-svg {{
        width: 18px;
        height: 18px;
        color: #ffffff;
    }}

    .bell-badge {{
        position: absolute;
        top: 7px;
        right: 7px;
        width: 6px;
        height: 6px;
        background: #ef4444;
        border-radius: 50%;
    }}

    [data-testid="column"]:has(.notification-wrap) {{
        position: relative !important;
        width: auto !important;
        flex: 0 0 auto !important;
    }}

    [data-testid="column"]:has(.notification-wrap) > div[data-testid="stVerticalBlock"] {{
        position: relative !important;
        flex-direction: row !important;
        align-items: center !important;
        width: {_CTRL_H}px !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
    }}

    [data-testid="column"]:has(.notification-wrap) div[data-testid="stButton"] {{
        position: absolute !important;
        inset: 0 !important;
        width: {_CTRL_H}px !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        z-index: 2 !important;
    }}

    [data-testid="column"]:has(.notification-wrap) button {{
        position: absolute !important;
        inset: 0 !important;
        width: {_CTRL_H}px !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
        opacity: 0 !important;
        z-index: 2 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    .profile-container {{
        display: flex;
        align-items: center;
        gap: 10px;
        height: {_CTRL_H}px;
    }}

    .profile-info {{
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        text-align: right;
    }}

    .profile-name {{
        color: #ffffff;
        font-size: 13px;
        font-weight: 700;
        line-height: 1.2;
        white-space: nowrap;
    }}

    .profile-role {{
        color: rgba(198, 210, 225, 0.95);
        font-size: 11px;
        line-height: 1.2;
        margin-top: 2px;
        white-space: nowrap;
    }}

    .profile-avatar {{
        width: {_CTRL_H}px;
        height: {_CTRL_H}px;
        border-radius: 50%;
        background: #173a63;
        border: 1.5px solid rgba(255, 255, 255, 0.85);
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 700;
        flex-shrink: 0;
    }}

    [data-testid="column"]:has(.profile-container) {{
        position: relative !important;
        flex: 0 0 auto !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }}

    [data-testid="column"]:has(.profile-container) > div[data-testid="stVerticalBlock"] {{
        flex-direction: row !important;
        align-items: center !important;
        height: auto !important;
        min-height: unset !important;
        position: relative !important;
    }}

    [data-testid="column"]:has(.profile-container) div[data-testid="stButton"] {{
        position: absolute !important;
        right: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        width: {_CTRL_H}px !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        z-index: 3 !important;
    }}

    [class*="st-key-nav_signout"] button {{
        position: absolute !important;
        right: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        width: {_CTRL_H}px !important;
        height: {_CTRL_H}px !important;
        min-height: {_CTRL_H}px !important;
        opacity: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        z-index: 3 !important;
        cursor: pointer !important;
    }}

    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) button:focus,
    [data-testid="stHorizontalBlock"]:has(#navbar-bar-marker) button:active {{
        outline: none !important;
        box-shadow: none !important;
    }}

    /* Filter / CONTEXT bar sits flush under navbar */
    [data-testid="stVerticalBlock"]:has([data-testid="stHorizontalBlock"]:has(#navbar-bar-marker)) {{
        margin-bottom: 0 !important;
        gap: 0 !important;
        row-gap: 0 !important;
    }}
    [data-testid="stElementContainer"]:has(#navbar-bar-marker) {{
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }}
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has(.sim-ctx-outer-marker),
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has(.sim-ctx-marker),
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker)),
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(.sim-ctx-marker)),
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has(.dash-filters-marker),
    [data-testid="stElementContainer"]:has(#navbar-bar-marker)
        + [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(.dash-filters-marker)) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    </style>
    """


def _set_nav_mode(mode: str) -> None:
    st.session_state.nav_user_mode = mode


def _render_mode_toggle(container: Any) -> None:
    """Controller | Management pill — native Streamlit buttons."""
    if "nav_user_mode" not in st.session_state:
        # Migrate legacy widget key from earlier st.radio experiments
        legacy = st.session_state.get("user_mode", "Controller")
        st.session_state.nav_user_mode = (
            legacy if legacy in ("Controller", "Management") else "Controller"
        )
    mode = str(st.session_state.nav_user_mode)
    mode_class = "mode-is-controller" if mode == "Controller" else "mode-is-management"

    container.markdown(
        f'<span class="mode-toggle-marker {mode_class}"></span>',
        unsafe_allow_html=True,
    )
    hit1, hit2 = container.columns(2, gap="xxsmall")
    with hit1:
        st.button(
            "Controller",
            key="mode_ctrl",
            on_click=_set_nav_mode,
            args=("Controller",),
        )
    with hit2:
        st.button(
            "Management",
            key="mode_mgmt",
            on_click=_set_nav_mode,
            args=("Management",),
        )


def top_navigation(scope_label: str = "All Countries") -> None:
    """Render the full-width top navbar."""
    user: dict[str, Any] = st.session_state.get("user", {})
    is_admin = bool(user.get("is_admin", False))
    menus = _nav_menus(is_admin)
    active_key = _active_nav_key(menus)

    st.markdown(_navbar_css(active_key), unsafe_allow_html=True)

    left_col, right_col = st.columns(2, vertical_alignment="center")

    with left_col:
        st.markdown(
            '<span id="navbar-bar-marker"></span>'
            '<span id="navbar-left-marker"></span>',
            unsafe_allow_html=True,
        )
        brand_col, links_col = st.columns([1.05, 5.5], vertical_alignment="center")
        with brand_col:
            st.markdown(
                f"""
                <div class="logo-wrap">
                    {_elex_logo_markup()}
                    <span class="logo-text">Electrolux</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with links_col:
            st.markdown('<span id="navbar-nav-marker"></span>', unsafe_allow_html=True)
            nav_cols = st.columns(len(menus), vertical_alignment="center")
            for col, (label, page_key) in zip(nav_cols, menus):
                if page_key:
                    if col.button(label, key=f"nav_{page_key}"):
                        st.session_state.page = page_key
                        st.rerun()
                else:
                    col.button(label, key=f"nav_{label.lower()}", disabled=True)

    with right_col:
        st.markdown('<span id="navbar-right-marker"></span>', unsafe_allow_html=True)
        toggle_col, scope_col, bell_col, profile_col = st.columns(
            [1.5, 1.2, 0.38, 1.05],
            gap="small",
            vertical_alignment="center",
        )

        with toggle_col:
            _render_mode_toggle(toggle_col)

        with scope_col:
            safe_scope = html.escape(scope_label)
            st.markdown(
                f"""
                <div class="scope-pill">
                    <span class="scope-dot"></span>
                    <span>{safe_scope}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with bell_col:
            st.markdown(
                """
                <div class="notification-wrap">
                    <svg class="bell-svg" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2"
                         stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    <span class="bell-badge"></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.button(" ", key="notification_btn")

        with profile_col:
            name = html.escape(str(user.get("name", "Harvey Norman")))
            role = html.escape(str(user.get("role", "Controller")))
            parts = str(user.get("name", "Harvey Norman")).split()
            initials = html.escape("".join(p[0] for p in parts[:2]).upper() or "U")
            st.markdown(
                f"""
                <div class="profile-container">
                    <div class="profile-info">
                        <div class="profile-name">{name}</div>
                        <div class="profile-role">{role}</div>
                    </div>
                    <div class="profile-avatar">{initials}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Sign out", key="nav_signout", help="Sign out"):
                st.session_state.pop("user", None)
                st.session_state.pop("page", None)
                st.rerun()
