"""Simulate page — pixel-perfect enterprise dashboard (Figma spec)."""
from __future__ import annotations

import html
import json
import re
from typing import Any
from urllib.parse import quote, unquote

import streamlit as st
import streamlit.components.v1 as components

from pages_st.Common_Pages.filter_bar import render_context_filter_bar as _render_context_bar
from pages_st.Common_Pages.filter_select import filter_select

# Design tokens (Figma simulate form)
_PRIMARY = "#011E41"
_PANEL_HEADER_BG = "#042A57"
_SECONDARY = "#143A72"
_PAGE_BG = "#F1F3FB"
_CARD_BG = "#ffffff"
_ICON_BG = "#E8EEF7"
_SUCCESS = "#16A34A"
_DANGER = "#DC2626"
_BORDER = "#E5E7EB"
_SECTION_BORDER = "#C3C3C3"
_SIDE_SUBMIT_BORDER = "#DDE2E9"
_SIDE_CARD_RADIUS = "8px"
_SIDE_CARD_GAP = "12px"
_SIDE_PANEL_W = 330
_MAIN_COL_GAP = "16px"
_SUBMIT_SECTION_PAD = "8px 12px"
_INPUT_BG = "#F9F9F9"
_INPUT_BORDER = "#D4DBE6"
_TEXT = "#111827"
_TEXT_MUTED = "#6B7280"
_SAVE_BTN_BG = "#DCE8F2"
_SAVE_BTN_TEXT = "#000000"
_SAVE_BTN_BORDER = "#D4DBE6"

_SQ = {"red": "#ef4444", "blue": "#3b82f6", "green": "#22c55e", "orange": "#f59e0b"}
_VAL = {"red": _DANGER, "green": _SUCCESS, "yellow": "#ca8a04", "neutral": _TEXT}
_TAG = {
    "stc": ("#fee2e2", "#dc2626"),
    "ptc": ("#dbeafe", "#1d4ed8"),
    "dd": ("#f3f4f6", "#475569"),
    "swc": ("#dcfce7", "#15803d"),
    "fields": ("#f3f4f6", "#64748b"),
    "cat": ("#f3f4f6", "#64748b"),
    "entered": ("#fef3c7", "#b45309"),
}

_CSS_LOADED = False

_PANEL_SCOPE_TREE: dict[str, list[str]] = {
    "BA": ["FR10", "FR20", "EA1", "DE01"],
    "Commercial Area": ["EA1 · 2026", "EA2 · 2026", "EA1 · 2025", "EA2 · 2027"],
    "Country": [
        "🇫🇷 FR10 — France",
        "🇪🇸 ES10 — Spain",
        "🇮🇹 IT16 — Italy",
        "🇵🇹 PT10 — Portugal",
    ],
    "Company": ["FR10", "ES10", "IT16", "PT10"],
}
_PANEL_SCOPE_ROOTS: tuple[str, ...] = tuple(_PANEL_SCOPE_TREE.keys())
_PANEL_CHIP_BG = "#E9EDF5"
_PANEL_CHIP_BORDER = "1px solid #D4DBE6"
_PANEL_CHIP_TEXT = "#4B5563"
_PANEL_CHIP_CHEVRON = "#6B7280"
_PANEL_CHIP_RADIUS = "8px"
_PANEL_CHIP_H = "32px"
_PANEL_CHIP_FONT = "11px"
_SCOPE_ROOT_PLACEHOLDER = "— Select category —"
_SCOPE_DRILL_KEY = "sim_panel_scope_drill"
_SCOPE_VALUE_KEY = "sim_panel_scope_value"
_SCOPE_INIT_KEY = "sim_panel_scope_initialized"
_SCOPE_PICK_QP = "scope_pick"

_PANEL_HEADER_FILTERS: tuple[dict[str, str], ...] = (
    {"label": "Business Area", "key": "sim_panel_business_area", "preset": "Business Area", "default": "Europe"},
    {"label": "Commercial Area", "key": "sim_panel_commercial_area", "preset": "Commercial Area", "default": "ATED"},
    {"label": "Country", "key": "sim_panel_country", "preset": "Panel Country", "default": "Germany"},
    {"label": "Period", "key": "sim_panel_period", "preset": "Panel Period", "default": "Last 6 months"},
    {"label": "Company", "key": "sim_panel_company", "preset": "Panel Company", "default": "FR10"},
)


def _html(fragment: str) -> None:
    st.html(fragment)

def dash_spacer() -> None:
    """24px vertical gap between dashboard sections (works in all Streamlit versions)."""
    st.markdown('<div class="dash-spacer-24" aria-hidden="true"></div>', unsafe_allow_html=True)


def inject_simulate_layout_css() -> None:
    """Per-run layout — stepper section white surface with 24px inset."""
    st.markdown(
        """
        <style>
        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"] {
            overflow-x: hidden !important;
            max-width: 100% !important;
        }
        .sim-step-section-marker { display: none !important; }

        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-step-section-marker),
        .block-container:has(#simulate-page) [class*="st-key-sim_stepper_section"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            margin: 24px !important;
            padding: 0 !important;
            box-sizing: border-box !important;
            width: auto !important;
            max-width: 100% !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_stepper_section"] [data-testid="stVerticalBlockBorderWrapper"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-step-section-marker) [data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 0 !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        }
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-step-section-marker) [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_stepper_section"] [data-testid="stVerticalBlock"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Section 3 — main form + sidebar: 24px left/right inset (same as stepper) */
        .sim-content-section-marker { display: none !important; }
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-content-section-marker),
        .block-container:has(#simulate-page) [class*="st-key-sim_main_content"] {
            margin-left: 24px !important;
            margin-right: 24px !important;
            margin-top: 0 !important;
            margin-bottom: 24px !important;
            padding: 0 !important;
            box-sizing: border-box !important;
            width: auto !important;
            max-width: 100% !important;
            background: transparent !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_main_content"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-content-section-marker) [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-content-section-marker) [data-testid="stHorizontalBlock"] {
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }

        /* Main two-column layout — left grows, right fixed 330px */
        .block-container:has(#simulate-page) [class*="st-key-sim_main_content"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-content-section-marker) [data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: flex-start !important;
            gap: 16px !important;
            width: 100% !important;
        }
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-sidebar-marker) {
            width: 330px !important;
            min-width: 330px !important;
            max-width: 330px !important;
            flex: 0 0 330px !important;
        }
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-main-panel-marker) {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: auto !important;
            max-width: none !important;
        }
        .sim-main-panel-marker { display: none !important; }

        /* Panel header — bg + padding (keyed container) */
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-panel-header-wrap),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] {
            background: #042A57 !important;
            background-color: #042A57 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] {
            padding: 0 16px 16px 16px !important;
        }

        /* Panel header dropdowns — five equal columns */
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"] {
            justify-content: flex-start !important;
            gap: 12px !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow: visible !important;
            padding: 16px !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] {
            min-width: 0 !important;
            overflow: visible !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] [data-testid="stSelectbox"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] > div {
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-filter-upper-lbl,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-filter-panel-lbl,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl),
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl) p {
            display: block !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        /* Panel scope tree dropdown (hover flyout, no iframe) */
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-panel-scope-tree) {
            overflow: visible !important;
        }
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-panel-scope-tree) > div[data-testid="stVerticalBlock"] {
            overflow: visible !important;
            width: 100% !important;
        }
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.elx-scope-tree),
        .block-container:has(#simulate-page) [data-testid="stMarkdownContainer"]:has(.elx-scope-tree) {
            overflow: visible !important;
            width: 100% !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-scope-trigger,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .elx-scope-trigger {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 28px 0 10px !important;
            border: 1px solid #D4DBE6 !important;
            border-radius: 8px !important;
            background: #E9EDF5 !important;
            background-color: #E9EDF5 !important;
            color: #4B5563 !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            line-height: 1 !important;
            box-shadow: none !important;
            cursor: pointer !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-scope-trigger::after,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .elx-scope-trigger::after {
            color: #6B7280 !important;
            opacity: 1 !important;
            font-size: 10px !important;
        }

        /* Parameter group cards (Delivery Mix, etc.) — 10px internal padding */
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"],
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) {
            padding: 10px !important;
            box-sizing: border-box !important;
        }

        /* Form footer — Parameters completed / Reset / Start Simulation */
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-footer-marker):has([class*="st-key-sim_reset"]),
        .block-container:has(#simulate-page) [class*="st-key-sim_footer"] {
            background: #ffffff !important;
            background-color: #ffffff !important;
            padding: 10px !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_footer"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_footer"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_footer"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_footer"] [data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
            background: #ffffff !important;
            background-color: #ffffff !important;
        }

        /* Parameter value chip — nested columns keep value + % on one row */
        [data-testid="column"]:has(.sim-pct-chip-row) {
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) > div[data-testid="stVerticalBlock"] {
            align-items: flex-end !important;
            width: 100% !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) > div[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.sim-pct-chip-row) {
            display: none !important;
            height: 0 !important;
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stHorizontalBlock"] {
            display: inline-flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: 0 !important;
            background: #F9F9F9 !important;
            border: 1px solid #D4DBE6 !important;
            border-radius: 8px !important;
            padding: 0 12px 0 12px !important;
            min-height: 40px !important;
            height: 40px !important;
            min-width: 108px !important;
            width: fit-content !important;
            max-width: 100% !important;
            margin-left: auto !important;
            box-sizing: border-box !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            width: auto !important;
            min-width: 0 !important;
            flex: 0 0 auto !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stHorizontalBlock"] > [data-testid="column"] > div[data-testid="stVerticalBlock"] {
            gap: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"],
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"] > div {
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"] label,
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stWidgetLabel"] {
            display: none !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"] input {
            text-align: left !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            color: #011E41 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 36px !important;
            height: 36px !important;
            width: 52px !important;
            min-width: 44px !important;
            max-width: 72px !important;
            padding: 0 !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) .sim-pct-chip-suffix,
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stMarkdownContainer"]:has(.sim-pct-chip-suffix) p {
            display: inline-flex !important;
            align-items: center !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 0 0 4px !important;
            user-select: none !important;
            pointer-events: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_css() -> None:
    """Inject all simulate-page styles (call once per session)."""
    global _CSS_LOADED
    if _CSS_LOADED:
        return
    _CSS_LOADED = True
    import pages_st.Common_Pages.filter_select as _fs

    _fs._CSS_INJECTED = False
    _fs._SIM_CTX_CSS_INJECTED = False
    st.markdown(
        f"""
        <style>
        .block-container:has(#simulate-page) {{
            padding: 0 0 16px 0 !important;
            max-width: 100% !important;
            background: {_PAGE_BG} !important;
        }}
        section.main:has(#simulate-page),
        [data-testid="stMainBlockContainer"]:has(#simulate-page),
        [data-testid="stAppViewContainer"]:has(#simulate-page),
        .stApp:has(#simulate-page) {{
            background: {_PAGE_BG} !important;
            background-color: {_PAGE_BG} !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stVerticalBlock"] {{
            background: transparent !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"] {{
            background: transparent !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="column"],
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] [data-testid="column"],
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-step-marker) [data-testid="column"],
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="column"] {{
            background: {_CARD_BG} !important;
        }}
        #simulate-page {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .block-container:has(#simulate-page) {{
            padding-top: 0 !important;
            margin-top: 0 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stVerticalBlock"] {{
            gap: 0 !important;
            row-gap: 0 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stElementContainer"] {{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }}
        .block-container:has(#simulate-page)
        [data-testid="stElementContainer"]:has(#navbar-bar-marker),
        .block-container:has(#simulate-page)
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) {{
            padding-top: 0 !important;
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }}
        .block-container:has(#simulate-page)
        [data-testid="stElementContainer"]:has(#navbar-bar-marker) + [data-testid="stElementContainer"],
        .block-container:has(#simulate-page)
        [data-testid="stElementContainer"]:has(#navbar-bar-marker) + div {{
            margin-top: 0 !important;
            padding-top: 0 !important;
        }}

        .block-container:has(#simulate-page)
        [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:not(:has(.sim-ctx-marker)):not(:has(#navbar-bar-marker)):not(:has(.dash-spacer-24)):not(:has(.sim-step-marker)):not(:has(.sim-step-section-marker)):not(:has(.sim-content-section-marker)) {{
            padding-left: 0 !important;
            padding-right: 0 !important;
            box-sizing: border-box !important;
        }}

        section.main:has(.sim-ctx-marker),
        [data-testid="stAppViewContainer"]:has(.sim-ctx-marker) {{
            overflow-x: visible !important;
        }}

        .block-container:has(#simulate-page) .dash-spacer-24 {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.dash-spacer-24),
        .block-container:has(#simulate-page) [data-testid="stMarkdownContainer"]:has(.dash-spacer-24) {{
            min-height: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.dash-spacer-24) + [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.dash-spacer-24) + div {{
            margin-top: 24px !important;
        }}

        /* ----- Section 2: Stepper ----- */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-step-marker) {{
            background: #ffffff !important;
            border: 1px solid {_BORDER} !important;
            border-radius: 0 !important;
            padding: 14px 20px 10px !important;
            min-height: 70px !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        }}
        .sim-step-marker {{ display: none !important; }}

        /* ----- Section 3: Main parameter form card — white bg + row borders (Figma) ----- */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stVerticalBlock"]:not(:has(.sim-panel-header-marker)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stElementContainer"]:not(:has(.sim-panel-header-marker)):not(:has(.sim-panel-header-wrap)):not([class*="st-key-sim_panel_header_wrap"]),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stHorizontalBlock"]:not(:has(.sim-panel-header-marker)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stMarkdownContainer"]:not(:has(.sim-panel-header-marker)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stNumberInput"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) .stHtml:not(:has(.sim-panel-header-wrap)) {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) {{
            background: #ffffff !important;
            border: 1px solid {_BORDER} !important;
            border-radius: 8px !important;
            padding: 0 !important;
            overflow: hidden !important;
            box-shadow: 0 1px 3px rgba(1, 30, 65, 0.08) !important;
        }}
        .sim-main-marker, .sim-form-marker, .sim-group-fields-marker, .sim-param-group-wrap {{
            display: none !important;
        }}

        /* ----- Per-section accordion card (Delivery Mix, etc.) — pure white ----- */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) > div > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stVerticalBlock"] > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:not(:has(.sim-num-wrap)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) div[data-testid="stMarkdown"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) .stHtml,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:not(:has(.sim-num-wrap)) [class*="st-emotion-cache"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:not(:has(.sim-num-wrap)) [class*="st-emotion-cache"] {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) {{
            --secondary-background-color: #ffffff !important;
            --background-color: #ffffff !important;
            border: 1px solid {_SECTION_BORDER} !important;
            border-radius: 0 !important;
            margin: 0 0 10px !important;
            padding: 10px !important;
            overflow: hidden !important;
            box-shadow: none !important;
            box-sizing: border-box !important;
        }}
        /* Only the numeric input chip keeps #F9F9F9 (not the section body) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:has(.sim-num-wrap) > div[data-testid="stVerticalBlock"] {{
            background-color: {_INPUT_BG} !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stVerticalBlock"] {{
            gap: 0 !important;
            row-gap: 0 !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"] {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        /* Main panel body (behind section cards) stays white */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker):not(:has(.sim-param-group-wrap)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stVerticalBlock"]:not(:has(.sim-param-group-wrap)):not(:has(.sim-panel-header-marker)) {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}

        [data-testid="stForm"]:has(.sim-form-marker) {{
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stForm"] [data-testid="stElementContainer"] {{
            margin: 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }}

        /* Panel header — navy bar with country/year filter_select dropdowns */
        .sim-panel-header-marker {{ display: none !important; }}
        .sim-panel-header-wrap {{
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 16px !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] {{
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
            border: none !important;
            box-shadow: none !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .stHtml,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stSelectbox"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .stHtml,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stSelectbox"],
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"],
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] [data-testid="column"] {{
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            margin: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] {{
            padding: 0 16px 16px 16px !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap),
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) .stHtml {{
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] {{
            justify-content: flex-start !important;
            gap: 12px !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow: visible !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel),
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] [data-testid="column"]:has(.elx-filter-panel),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) {{
            min-width: 0 !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) {{
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            align-self: flex-end !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) [data-testid="stSelectbox"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) [data-testid="stSelectbox"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div {{
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .elx-filter-upper-lbl,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .elx-filter-panel-lbl,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl) p {{
            display: block !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            text-transform: none !important;
            letter-spacing: 0 !important;
            margin: 0 0 4px 2px !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.22) !important;
            border-radius: 4px !important;
            min-height: 32px !important;
            height: 32px !important;
            color: #ffffff !important;
            box-shadow: none !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] > div > div {{
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 0 24px 0 10px !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            overflow: visible !important;
            white-space: nowrap !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] span {{
            overflow: visible !important;
            white-space: nowrap !important;
            text-overflow: clip !important;
            color: #ffffff !important;
            font-size: 11px !important;
            font-weight: 600 !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] input {{
            cursor: pointer !important;
        }}
        .sim-panel-static-pill {{
            display: inline-flex;
            align-items: center;
            background: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 0;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 600;
            color: #fff;
            white-space: nowrap;
        }}

        /* Group header row — inside section card */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-param-group-marker) {{
            border-bottom: none !important;
            margin: 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker)
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) {{
            margin-left: 16px !important;
            margin-right: 16px !important;
            width: calc(100% - 32px) !important;
            max-width: calc(100% - 32px) !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-param-group-marker)
        > [data-testid="stHorizontalBlock"] {{
            padding: 0 !important;
            margin: 0 !important;
            align-items: center !important;
            min-height: 0 !important;
            box-sizing: border-box !important;
            background: #ffffff !important;
        }}

        /* Fields block — gap below section header before first child row */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-group-fields-marker) {{
            margin: 12px 0 0 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
            border-top: 1px solid {_BORDER} !important;
        }}

        /* Explicit row dividers (always visible between header ↔ fields ↔ rows) */
        hr.sim-row-divider,
        div.sim-row-divider {{
            display: block !important;
            width: 100% !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            border-top: 1px solid {_BORDER} !important;
            background: transparent !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-row-divider),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stMarkdownContainer"]:has(.sim-row-divider),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(hr.sim-row-divider) {{
            margin: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) hr.sim-row-divider {{
            margin: 0 !important;
        }}

        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-marker) {{
            margin: 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-marker)
        > [data-testid="stHorizontalBlock"] {{
            padding: 0 !important;
            margin: 0 !important;
            align-items: center !important;
            min-height: 0 !important;
            background: #ffffff !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-marker):last-of-type
        > [data-testid="stHorizontalBlock"] {{
            border-bottom: none !important;
        }}

        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_save_"] button {{
            background: {_SAVE_BTN_BG} !important;
            color: {_SAVE_BTN_TEXT} !important;
            border: 1px solid {_SAVE_BTN_BORDER} !important;
            border-radius: 0 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            min-height: 32px !important;
            height: 32px !important;
            padding: 0 16px !important;
            box-shadow: none !important;
            opacity: 1 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button:hover,
        .block-container:has(#simulate-page) [class*="st-key-sim_save_"] button:hover,
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button:focus,
        .block-container:has(#simulate-page) [class*="st-key-sim_save_"] button:focus {{
            background: {_SAVE_BTN_BG} !important;
            color: {_SAVE_BTN_TEXT} !important;
            border: 1px solid {_SAVE_BTN_BORDER} !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button {{
            background: {_SAVE_BTN_BG} !important;
            color: {_SAVE_BTN_TEXT} !important;
            border: 1px solid {_SAVE_BTN_BORDER} !important;
            border-radius: 0 !important;
            min-height: 32px !important;
            height: 32px !important;
            width: 32px !important;
            min-width: 32px !important;
            font-size: 14px !important;
            padding: 0 !important;
            box-shadow: none !important;
            opacity: 1 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button:hover,
        .block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button:hover {{
            background: #cfe0f0 !important;
            color: {_SAVE_BTN_TEXT} !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-actions-col) {{
            display: flex !important;
            justify-content: flex-end !important;
            gap: 6px !important;
        }}

        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) {{
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) > div[data-testid="stVerticalBlock"] {{
            display: inline-flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0 !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 0 !important;
            padding: 0 8px 0 10px !important;
            min-height: 40px !important;
            height: 40px !important;
            min-width: 96px !important;
            width: fit-content !important;
            max-width: 100% !important;
            margin-left: auto !important;
            box-sizing: border-box !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) > div[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {{
            margin: 0 !important;
            padding: 0 !important;
            width: auto !important;
            flex: 0 0 auto !important;
            background: transparent !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stWidgetLabel"],
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] label {{
            display: none !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] {{
            width: auto !important;
            max-width: none !important;
            flex: 0 0 auto !important;
            background: transparent !important;
            border: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] > div,
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] [data-testid="stNumberInputContainer"] {{
            width: auto !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            gap: 0 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] input {{
            text-align: right !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            border-radius: 0 !important;
            min-height: 36px !important;
            height: 36px !important;
            width: 48px !important;
            min-width: 40px !important;
            max-width: 64px !important;
            background: transparent !important;
            padding: 0 4px !important;
            box-shadow: none !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap)
        [data-testid="stNumberInputStepDown"],
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap)
        [data-testid="stNumberInputStepUp"],
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap)
        [data-testid="stNumberInput"] button {{
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            min-width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stMarkdownContainer"]:has(.sim-pct-suffix),
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-num-wrap) [data-testid="stElementContainer"]:has(.sim-pct-suffix) {{
            margin: 0 !important;
            padding: 0 !important;
            width: auto !important;
            flex: 0 0 auto !important;
            display: flex !important;
            align-items: center !important;
        }}
        .block-container:has(#simulate-page) .sim-pct-suffix {{
            display: none !important;
        }}

        /* Numeric chip — also without #simulate-page (param groups may sit outside ctx marker tree) */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:has(.sim-num-wrap),
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-num-wrap) {{
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:has(.sim-num-wrap) > div[data-testid="stVerticalBlock"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-num-wrap) > div[data-testid="stVerticalBlock"] {{
            display: inline-flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0 !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 0 !important;
            padding: 0 10px 0 10px !important;
            min-height: 40px !important;
            height: 40px !important;
            min-width: 96px !important;
            width: fit-content !important;
            max-width: 100% !important;
            margin-left: auto !important;
            box-sizing: border-box !important;
        }}
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stElementContainer"]:has(.sim-num-wrap) {{
            display: none !important;
        }}
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stElementContainer"]:has(.sim-pct-suffix) {{
            display: none !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="stNumberInputStepDown"],
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="stNumberInputStepUp"],
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="stNumberInput"] button,
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="stNumberInputContainer"] button,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stNumberInputStepDown"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stNumberInputStepUp"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stNumberInput"] button,
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInputStepDown"],
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInputStepUp"],
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] button,
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInputContainer"] button {{
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            min-width: 0 !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }}
        [data-testid="column"]:has(.sim-num-wrap) [data-testid="stNumberInput"] input {{
            text-align: right !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            min-height: 36px !important;
            height: 36px !important;
            width: 48px !important;
            min-width: 40px !important;
            max-width: 64px !important;
            padding: 0 4px !important;
        }}
        [data-testid="column"]:has(.sim-num-wrap) .sim-pct-inline,
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] .sim-pct-inline {{
            display: inline-flex !important;
            align-items: center !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            line-height: 1 !important;
            flex-shrink: 0 !important;
            padding: 0 2px 0 4px !important;
            margin: 0 !important;
            white-space: nowrap !important;
            user-select: none !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {{
            display: inline-flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 0 !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 0 !important;
            padding: 0 10px !important;
            min-height: 40px !important;
            height: 40px !important;
            min-width: 96px !important;
            width: fit-content !important;
            margin-left: auto !important;
            box-sizing: border-box !important;
        }}

        /* ----- Form footer (Figma) — white + top border ----- */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) .sim-footer-divider {{
            border-top: 1px solid {_BORDER} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stElementContainer"]:has(.sim-footer-marker):has([class*="st-key-sim_reset"]),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_footer"] {{
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
            margin: 0 !important;
            padding: 10px !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_footer"] [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_footer"] [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_footer"] [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_footer"] [data-testid="column"] {{
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
            margin: 0 !important;
            padding: 0 !important;
            align-items: center !important;
            box-sizing: border-box !important;
        }}
        .sim-footer-marker {{ display: none !important; }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_reset"] button {{
            background: {_CARD_BG} !important;
            color: {_PRIMARY} !important;
            border: 1px solid {_BORDER} !important;
            border-radius: 0 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            min-height: 42px !important;
            height: 42px !important;
            box-shadow: none !important;
            opacity: 1 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button:hover,
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button:focus,
        .block-container:has(#simulate-page) [class*="st-key-sim_reset"] button:hover,
        .block-container:has(#simulate-page) [class*="st-key-sim_reset"] button:focus {{
            background: #f8fafc !important;
            color: {_PRIMARY} !important;
            border: 1px solid {_BORDER} !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_start"] button {{
            background: {_PRIMARY} !important;
            color: #fff !important;
            border: none !important;
            border-radius: 0 !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            min-height: 42px !important;
            height: 42px !important;
            box-shadow: none !important;
            opacity: 1 !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button:hover,
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button:focus,
        .block-container:has(#simulate-page) [class*="st-key-sim_start"] button:hover,
        .block-container:has(#simulate-page) [class*="st-key-sim_start"] button:focus {{
            background: #013060 !important;
            color: #fff !important;
            border: none !important;
        }}

        /* ----- Main layout — left form grows, right sidebar fixed 330px ----- */
        .block-container:has(#simulate-page) [class*="st-key-sim_main_content"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-content-section-marker) [data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: flex-start !important;
            gap: {_MAIN_COL_GAP} !important;
            width: 100% !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-sidebar-marker) {{
            width: {_SIDE_PANEL_W}px !important;
            min-width: {_SIDE_PANEL_W}px !important;
            max-width: {_SIDE_PANEL_W}px !important;
            flex: 0 0 {_SIDE_PANEL_W}px !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-main-panel-marker) {{
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: auto !important;
            max-width: none !important;
        }}
        .sim-main-panel-marker {{ display: none !important; }}

        /* ----- Sidebar cards — white card surface ----- */
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] {{
            gap: {_SIDE_CARD_GAP} !important;
            row-gap: {_SIDE_CARD_GAP} !important;
        }}
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([class*="st-key-sim_side_submit_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([class*="st-key-sim_side_infl_calc_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_side_submit_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_side_infl_calc_"]) {{
            margin-top: {_SIDE_CARD_GAP} !important;
        }}
        .sim-sidebar-marker {{ display: none !important; }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker) .stHtml,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker) .stHtml,
        .block-container:has(#simulate-page) [class*="st-key-sim_side_"] {{
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-infl-calc-marker) {{
            border: 1px solid {_SIDE_SUBMIT_BORDER} !important;
            border-radius: {_SIDE_CARD_RADIUS} !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
            box-shadow: none !important;
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"] .stHtml,
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"] .stHtml,
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"] .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-infl-calc-marker) .stHtml {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        .sim-side-card-marker,
        .sim-side-submit-marker,
        .sim-side-infl-calc-marker {{ display: none !important; }}
        .sim-side-card-gap,
        [data-testid="stElementContainer"]:has(.sim-side-card-gap),
        [data-testid="stMarkdownContainer"]:has(.sim-side-card-gap),
        .block-container:has(#simulate-page) [class*="st-key-sim_side_gap_"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_gap_"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_gap_"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_gap_"] [data-testid="stVerticalBlockBorderWrapper"] {{
            display: block !important;
            height: {_SIDE_CARD_GAP} !important;
            min-height: {_SIDE_CARD_GAP} !important;
            max-height: {_SIDE_CARD_GAP} !important;
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            overflow: hidden !important;
            line-height: 0 !important;
            box-shadow: none !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"] {{
            margin-top: {_SIDE_CARD_GAP} !important;
        }}

        /* Streamlit container keys (1.39+) — white section cards */
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid {_SECTION_BORDER} !important;
            border-radius: 0 !important;
            padding: 10px !important;
            overflow: hidden !important;
            box-shadow: none !important;
            box-sizing: border-box !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] [data-testid="column"]:not(:has(.sim-num-wrap)) {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_paint_js() -> None:
    """Apply Figma colors when Streamlit theme CSS wins over :has() selectors."""
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent?.document || document;
          function paint() {
            const white = "#ffffff";
            const sectionBorder = "1px solid #C3C3C3";
            const inputBg = "#F9F9F9";
            const inputBorder = "1px solid #D4DBE6";

            const sideCardGap = "12px";
            function paintFramedSideCard(wrapper) {
              wrapper.style.setProperty("background-color", white, "important");
              wrapper.style.setProperty("background", white, "important");
              wrapper.style.setProperty("border", "1px solid #DDE2E9", "important");
              wrapper.style.setProperty("border-radius", "8px", "important");
              wrapper.style.setProperty("padding", "0", "important");
              wrapper.style.setProperty("margin-left", "0", "important");
              wrapper.style.setProperty("margin-right", "0", "important");
              wrapper.style.setProperty("margin-bottom", "0", "important");
              wrapper.style.setProperty("overflow", "hidden", "important");
              wrapper.style.setProperty("box-shadow", "none", "important");
              wrapper.querySelectorAll(
                '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"], .stHtml'
              ).forEach((node) => {
                if (node === wrapper) return;
                node.style.setProperty("background-color", white, "important");
                node.style.setProperty("background", white, "important");
                node.style.setProperty("padding", "0", "important");
                node.style.setProperty("margin", "0", "important");
              });
            }
            doc.querySelectorAll(
              '[class*="st-key-sim_side_impact"], [class*="st-key-sim_side_submit_"], [class*="st-key-sim_side_infl_calc_"]'
            ).forEach((card) => {
              paintFramedSideCard(card);
            });
            function paintSideGap(node) {
              node.style.setProperty("display", "block", "important");
              node.style.setProperty("height", sideCardGap, "important");
              node.style.setProperty("min-height", sideCardGap, "important");
              node.style.setProperty("max-height", sideCardGap, "important");
              node.style.setProperty("margin", "0", "important");
              node.style.setProperty("padding", "0", "important");
              node.style.setProperty("background", "transparent", "important");
              node.style.setProperty("border", "none", "important");
              node.style.setProperty("overflow", "hidden", "important");
            }
            doc.querySelectorAll(".sim-side-card-gap").forEach(paintSideGap);
            doc.querySelectorAll('[class*="st-key-sim_side_gap_"]').forEach((gapBox) => {
              paintSideGap(gapBox);
              gapBox.querySelectorAll(
                '[data-testid="stVerticalBlock"], [data-testid="stElementContainer"], [data-testid="stVerticalBlockBorderWrapper"]'
              ).forEach(paintSideGap);
            });
            doc.querySelectorAll('[class*="st-key-sim_side_infl_calc_"]').forEach((card) => {
              card.style.setProperty("margin-top", sideCardGap, "important");
            });

            doc.querySelectorAll('[class*="st-key-sim_grp_"], [data-testid="stVerticalBlockBorderWrapper"]')
              .forEach((wrapper) => {
                if (!wrapper.querySelector(".sim-param-group-wrap")) return;
                wrapper.style.setProperty("background-color", white, "important");
                wrapper.style.setProperty("background", white, "important");
                wrapper.style.setProperty("border", sectionBorder, "important");
                wrapper.style.setProperty("border-radius", "0", "important");
                wrapper.style.setProperty("padding", "10px", "important");
                wrapper.style.setProperty("box-sizing", "border-box", "important");
                wrapper.style.setProperty("overflow", "hidden", "important");
                wrapper.querySelectorAll(
                  '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"]'
                ).forEach((node) => {
                  if (node.querySelector && node.querySelector(".sim-num-wrap")) return;
                  node.style.setProperty("background-color", white, "important");
                  node.style.setProperty("background", white, "important");
                });
                wrapper.querySelectorAll('[data-testid="stElementContainer"]:has(.sim-group-fields-marker)').forEach((node) => {
                  node.style.setProperty("margin-top", "12px", "important");
                });
              });

            doc.querySelectorAll('[data-testid="column"]:has(.sim-pct-chip-row)').forEach((numCol) => {
              const chip = numCol.querySelector('[data-testid="stHorizontalBlock"]');
              if (!chip) return;
              numCol.style.setProperty("display", "flex", "important");
              numCol.style.setProperty("justify-content", "flex-end", "important");
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("flex-direction", "row", "important");
              chip.style.setProperty("align-items", "center", "important");
              chip.style.setProperty("background-color", inputBg, "important");
              chip.style.setProperty("background", inputBg, "important");
              chip.style.setProperty("border", inputBorder, "important");
              chip.style.setProperty("border-radius", "8px", "important");
              chip.style.setProperty("padding", "0 12px", "important");
              chip.style.setProperty("min-height", "40px", "important");
              chip.style.setProperty("height", "40px", "important");
              chip.style.setProperty("width", "fit-content", "important");
              chip.style.setProperty("margin-left", "auto", "important");
              chip.querySelectorAll('[data-testid="stTextInput"] input').forEach((input) => {
                input.style.setProperty("text-align", "left", "important");
                input.style.setProperty("font-weight", "700", "important");
                input.style.setProperty("border", "none", "important");
                input.style.setProperty("background", "transparent", "important");
                input.style.setProperty("box-shadow", "none", "important");
              });
              chip.querySelectorAll(".sim-pct-chip-suffix").forEach((pct) => {
                pct.style.setProperty("font-size", "13px", "important");
                pct.style.setProperty("font-weight", "600", "important");
                pct.style.setProperty("color", "#64748b", "important");
              });
            });

            doc.querySelectorAll('[class*="st-key-sim_reset"] button').forEach((btn) => {
              btn.style.setProperty("background", "#ffffff", "important");
              btn.style.setProperty("color", "#011E41", "important");
              btn.style.setProperty("border", "1px solid #E5E7EB", "important");
              btn.style.setProperty("border-radius", "0", "important");
              btn.style.setProperty("font-weight", "600", "important");
              btn.style.setProperty("opacity", "1", "important");
            });
            doc.querySelectorAll('[class*="st-key-sim_start"] button').forEach((btn) => {
              btn.style.setProperty("background", "#011E41", "important");
              btn.style.setProperty("color", "#ffffff", "important");
              btn.style.setProperty("border", "none", "important");
              btn.style.setProperty("border-radius", "0", "important");
              btn.style.setProperty("font-weight", "600", "important");
              btn.style.setProperty("opacity", "1", "important");
            });
            function paintFooterRow(row) {
              if (!row) return;
              row.style.setProperty("background", white, "important");
              row.style.setProperty("background-color", white, "important");
              row.style.setProperty("padding", "10px", "important");
              row.style.setProperty("margin", "0", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
              row.querySelectorAll(
                '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"]'
              ).forEach((node) => {
                if (node === row) return;
                node.style.setProperty("padding", "0", "important");
                node.style.setProperty("margin", "0", "important");
                node.style.setProperty("background", white, "important");
                node.style.setProperty("background-color", white, "important");
              });
            }
            doc.querySelectorAll('[class*="st-key-sim_footer"]').forEach((box) => {
              const row = box.matches('[data-testid="stElementContainer"]')
                ? box
                : box.closest('[data-testid="stElementContainer"]');
              paintFooterRow(row);
            });
            doc.querySelectorAll(".sim-footer-marker").forEach((m) => {
              let row = m.closest('[class*="st-key-sim_footer"]');
              row = row && row.matches('[data-testid="stElementContainer"]')
                ? row
                : row?.closest('[data-testid="stElementContainer"]');
              if (!row) {
                let el = m.parentElement;
                while (el) {
                  if (
                    el.matches('[data-testid="stElementContainer"]') &&
                    el.querySelector('[class*="st-key-sim_reset"]')
                  ) {
                    row = el;
                    break;
                  }
                  el = el.parentElement;
                }
              }
              paintFooterRow(row);
            });

            function paintPanelHeaderNode(node, navy) {
              if (!node) return;
              node.style.setProperty("background", navy, "important");
              node.style.setProperty("background-color", navy, "important");
            }
            function paintPanelHeaderDropdowns(root) {
              if (!root) return;
              root.querySelectorAll('[data-testid="column"]').forEach((col) => {
                col.style.setProperty("min-width", "0", "important");
                col.style.setProperty("overflow", "visible", "important");
              });
              root.querySelectorAll(".elx-filter-upper-lbl, .elx-filter-panel-lbl").forEach((lbl) => {
                lbl.style.setProperty("display", "block", "important");
                lbl.style.setProperty("color", "#ffffff", "important");
                lbl.style.setProperty("-webkit-text-fill-color", "#ffffff", "important");
                lbl.style.setProperty("font-size", "11px", "important");
                lbl.style.setProperty("font-weight", "600", "important");
                lbl.style.setProperty("opacity", "1", "important");
                lbl.style.setProperty("visibility", "visible", "important");
                const md = lbl.closest('[data-testid="stMarkdownContainer"]');
                if (md) {
                  md.style.setProperty("color", "#ffffff", "important");
                  md.querySelectorAll("p").forEach((p) => {
                    p.style.setProperty("color", "#ffffff", "important");
                    p.style.setProperty("-webkit-text-fill-color", "#ffffff", "important");
                  });
                }
              });
              root.querySelectorAll('[data-testid="column"] div[data-baseweb="select"]').forEach((sel) => {
                sel.style.setProperty("width", "100%", "important");
                sel.style.setProperty("min-width", "0", "important");
                sel.style.setProperty("max-width", "100%", "important");
                sel.style.setProperty("overflow", "visible", "important");
                sel.style.setProperty("cursor", "pointer", "important");
              });
              root.querySelectorAll('[data-testid="column"] div[data-baseweb="select"] input').forEach((input) => {
                input.setAttribute("readonly", "true");
                input.setAttribute("inputmode", "none");
                input.style.setProperty("cursor", "pointer", "important");
                input.style.setProperty("caret-color", "transparent", "important");
                if (!input.dataset.elxPanelSelectGuard) {
                  input.dataset.elxPanelSelectGuard = "1";
                  input.addEventListener("keydown", (e) => {
                    const nav = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Enter", "Escape", "Tab", "Home", "End"];
                    if (nav.includes(e.key)) return;
                    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) e.preventDefault();
                    if (e.key === "Backspace" || e.key === "Delete") e.preventDefault();
                  });
                }
              });
              root.querySelectorAll('[data-testid="column"] div[data-baseweb="select"] > div').forEach((sel) => {
                sel.style.setProperty("width", "100%", "important");
                sel.style.setProperty("min-width", "0", "important");
                sel.style.setProperty("max-width", "100%", "important");
                sel.style.setProperty("overflow", "visible", "important");
                sel.style.setProperty("cursor", "pointer", "important");
                sel.style.setProperty("background-color", "rgba(255, 255, 255, 0.12)", "important");
                sel.style.setProperty("border", "1px solid rgba(255, 255, 255, 0.22)", "important");
                sel.style.setProperty("border-radius", "4px", "important");
                sel.style.setProperty("min-height", "32px", "important");
                sel.style.setProperty("height", "32px", "important");
                sel.style.setProperty("color", "#ffffff", "important");
              });
              root.querySelectorAll(
                '[data-testid="column"] div[data-baseweb="select"] > div > div, [data-testid="column"] div[data-baseweb="select"] span, [data-testid="column"] div[data-baseweb="select"] p, [data-testid="column"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"]'
              ).forEach((node) => {
                node.style.setProperty("color", "#ffffff", "important");
                node.style.setProperty("overflow", "visible", "important");
                node.style.setProperty("text-overflow", "unset", "important");
                node.style.setProperty("white-space", "nowrap", "important");
                node.style.setProperty("max-width", "none", "important");
              });
              root.querySelectorAll('[data-testid="column"] div[data-baseweb="select"] svg').forEach((node) => {
                node.style.setProperty("color", "#ffffff", "important");
                node.style.setProperty("fill", "#ffffff", "important");
              });
            }
            function paintPanelHeader() {
              const navy = "#042A57";
              doc.querySelectorAll(".sim-panel-header-wrap").forEach((wrap) => {
                wrap.style.setProperty("background", navy, "important");
                wrap.style.setProperty("background-color", navy, "important");
                wrap.style.setProperty("border-radius", "8px 8px 0 0", "important");
                wrap.style.setProperty("padding", "16px", "important");
                wrap.style.setProperty("margin", "0", "important");
              });
              doc.querySelectorAll('[class*="st-key-sim_panel_header_wrap"]').forEach((box) => {
                const root = box.matches('[data-testid="stElementContainer"]')
                  ? box
                  : box.closest('[data-testid="stElementContainer"]');
                if (!root) return;
                paintPanelHeaderNode(root, navy);
                root.style.setProperty("border-radius", "8px 8px 0 0", "important");
                root.style.setProperty("padding", "0", "important");
                root.style.setProperty("margin", "0", "important");
                root.querySelectorAll(
                  '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"], .stHtml, [data-testid="stMarkdownContainer"], [data-testid="stSelectbox"]'
                ).forEach((node) => paintPanelHeaderNode(node, navy));
                const wrap = root.querySelector(".sim-panel-header-wrap");
                const wrapRow = wrap?.closest('[data-testid="stElementContainer"]');
                const pillsRow = wrapRow?.nextElementSibling;
                if (wrapRow) paintPanelHeaderNode(wrapRow, navy);
                if (pillsRow && pillsRow.matches('[data-testid="stElementContainer"]')) {
                  paintPanelHeaderNode(pillsRow, navy);
                  pillsRow.style.setProperty("padding", "0 16px 16px 16px", "important");
                  pillsRow.style.setProperty("margin", "0", "important");
                  const pillBlock = pillsRow.querySelector('[data-testid="stHorizontalBlock"]');
                  if (pillBlock) {
                    pillBlock.style.setProperty("justify-content", "flex-start", "important");
                    pillBlock.style.setProperty("gap", "12px", "important");
                    pillBlock.style.setProperty("width", "100%", "important");
                    pillBlock.style.setProperty("overflow", "visible", "important");
                  }
                  pillsRow.querySelectorAll(
                    '[data-testid="stHorizontalBlock"], [data-testid="column"], [data-testid="stSelectbox"]'
                  ).forEach((node) => paintPanelHeaderNode(node, navy));
                }
                paintPanelHeaderDropdowns(root);
              });
            }
            paintPanelHeader();

            doc.querySelectorAll("#navbar-bar-marker").forEach((marker) => {
              const nav = marker.closest('[data-testid="stElementContainer"]');
              if (!nav) return;
              nav.style.setProperty("margin-bottom", "0", "important");
              nav.style.setProperty("padding-bottom", "0", "important");
              const next = nav.nextElementSibling;
              if (next && next.matches('[data-testid="stElementContainer"]')) {
                next.style.setProperty("margin-top", "0", "important");
                next.style.setProperty("padding-top", "0", "important");
              }
            });
            doc.querySelectorAll(".sim-ctx-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stHorizontalBlock"]');
              if (!row) return;
              row.style.setProperty("background", white, "important");
              row.style.setProperty("background-color", white, "important");
              row.style.setProperty("border-bottom", "1px solid #e4eaf2", "important");
              row.style.setProperty("width", "100%", "important");
              row.style.setProperty("max-width", "100%", "important");
              row.style.setProperty("margin-left", "0", "important");
              row.style.setProperty("margin-right", "0", "important");
              row.style.setProperty("padding", "12px 20px 10px", "important");
              row.style.setProperty("min-height", "58px", "important");
              row.style.setProperty("overflow", "visible", "important");
              row.querySelectorAll('[data-testid="column"]').forEach((col) => {
                col.style.setProperty("overflow", "visible", "important");
              });
              row.querySelectorAll(".elx-filter-upper-lbl").forEach((lbl) => {
                lbl.style.setProperty("display", "block", "important");
                lbl.style.setProperty("overflow", "visible", "important");
                lbl.style.setProperty("line-height", "1.3", "important");
                lbl.style.setProperty("margin-bottom", "4px", "important");
              });
              const parent = row.closest('[data-testid="stElementContainer"]');
              if (parent) {
                parent.style.setProperty("background", white, "important");
                parent.style.setProperty("background-color", white, "important");
                parent.style.setProperty("width", "100%", "important");
                parent.style.setProperty("max-width", "100%", "important");
                parent.style.setProperty("margin-left", "0", "important");
                parent.style.setProperty("margin-right", "0", "important");
                parent.style.setProperty("padding", "0", "important");
                parent.style.setProperty("overflow", "visible", "important");
              }
            });
            doc.querySelectorAll(".sim-step-section-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stElementContainer"]');
              if (!row) return;
              row.style.setProperty("background", white, "important");
              row.style.setProperty("background-color", white, "important");
              row.style.setProperty("margin", "24px", "important");
              row.style.setProperty("padding", "0", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
              const wrapper = row.querySelector('[data-testid="stVerticalBlockBorderWrapper"]');
              if (wrapper) {
                wrapper.style.setProperty("background", white, "important");
                wrapper.style.setProperty("background-color", white, "important");
                wrapper.style.setProperty("border", "1px solid #E5E7EB", "important");
                wrapper.style.setProperty("border-radius", "0", "important");
              }
            });
            doc.querySelectorAll('[class*="st-key-sim_stepper_section"]').forEach((box) => {
              box.style.setProperty("background", white, "important");
              box.style.setProperty("margin", "24px", "important");
            });
            doc.querySelectorAll(".sim-content-section-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stElementContainer"]');
              if (!row) return;
              row.style.setProperty("margin-left", "24px", "important");
              row.style.setProperty("margin-right", "24px", "important");
              row.style.setProperty("margin-bottom", "24px", "important");
              row.style.setProperty("padding", "0", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
            });
            doc.querySelectorAll('[class*="st-key-sim_main_content"]').forEach((box) => {
              box.style.setProperty("margin-left", "24px", "important");
              box.style.setProperty("margin-right", "24px", "important");
              box.style.setProperty("margin-bottom", "24px", "important");
            });
            const sideW = "330px";
            doc.querySelectorAll('[data-testid="column"]:has(.sim-sidebar-marker)').forEach((col) => {
              col.style.setProperty("width", sideW, "important");
              col.style.setProperty("min-width", sideW, "important");
              col.style.setProperty("max-width", sideW, "important");
              col.style.setProperty("flex", `0 0 ${sideW}`, "important");
            });
            doc.querySelectorAll('[data-testid="column"]:has(.sim-main-panel-marker)').forEach((col) => {
              col.style.setProperty("flex", "1 1 0", "important");
              col.style.setProperty("min-width", "0", "important");
              col.style.setProperty("width", "auto", "important");
              col.style.setProperty("max-width", "none", "important");
            });
            doc.querySelectorAll(
              '[class*="st-key-sim_main_content"] [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"]:has(.sim-content-section-marker) [data-testid="stHorizontalBlock"]'
            ).forEach((row) => {
              row.style.setProperty("display", "flex", "important");
              row.style.setProperty("flex-wrap", "nowrap", "important");
              row.style.setProperty("align-items", "flex-start", "important");
              row.style.setProperty("gap", "16px", "important");
              row.style.setProperty("width", "100%", "important");
            });
            doc.querySelectorAll('[data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"]:last-child').forEach((col) => {
              col.style.setProperty("display", "flex", "important");
              col.style.setProperty("justify-content", "flex-end", "important");
              col.style.setProperty("align-items", "center", "important");
              col.style.setProperty("align-self", "center", "important");
              col.style.setProperty("margin-left", "auto", "important");
              const vb = col.querySelector(':scope > [data-testid="stVerticalBlock"]');
              if (vb) {
                vb.style.setProperty("display", "flex", "important");
                vb.style.setProperty("justify-content", "flex-end", "important");
                vb.style.setProperty("align-items", "center", "important");
                vb.style.setProperty("width", "100%", "important");
              }
            });
            doc.querySelectorAll(".sim-ctx-live").forEach((chip) => {
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("align-items", "center", "important");
              chip.style.setProperty("gap", "8px", "important");
              chip.style.setProperty("padding", "0 14px", "important");
              chip.style.setProperty("margin-left", "auto", "important");
              chip.style.setProperty("background", white, "important");
              chip.style.setProperty("background-color", white, "important");
              chip.style.setProperty("border", "1px solid #e4eaf2", "important");
              chip.style.setProperty("border-radius", "0", "important");
              chip.style.setProperty("font-size", "13px", "important");
              chip.style.setProperty("font-weight", "600", "important");
              chip.style.setProperty("color", "#011e41", "important");
            });
          }
          paint();
          let ticks = 0;
          const timer = setInterval(() => {
            paint();
            if (++ticks > 40) clearInterval(timer);
          }, 125);
          const obs = new MutationObserver(paint);
          obs.observe(doc.body, { childList: true, subtree: true });
          setTimeout(() => obs.disconnect(), 12000);
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def _tags_html(tags: list[dict[str, str]]) -> str:
    parts = []
    for t in tags:
        bg, fg = _TAG.get(t.get("class", "fields"), _TAG["fields"])
        parts.append(
            f'<span class="sim-tag" style="background:{bg};color:{fg};margin-left:6px;'
            f'border-radius:0;padding:1px 6px;font-size:10px;font-weight:700;">'
            f'{html.escape(t["text"])}</span>'
        )
    return "".join(parts)


def _is_inflation_calculated_field(field: dict[str, Any]) -> bool:
    return field.get("infl_role") == "calculated" or field.get("name") in _INFLATION_CALCULATED_NAMES


def _is_section_field(field: dict[str, Any]) -> bool:
    return field.get("field_role") == "section"


def _iter_input_fields(group: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    return [
        (fi, field)
        for fi, field in enumerate(group.get("fields", []))
        if not (_is_inflation_rates_group(group) and _is_inflation_calculated_field(field))
        and not _is_section_field(field)
    ]


def _field_has_user_entry(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
    group: dict[str, Any],
) -> bool:
    """True when the user entered a value different from the field default."""
    if _is_inflation_rates_group(group) and _is_inflation_calculated_field(field):
        return False
    key = _field_key(group_index, field_index)
    if _group_is_saved(group_index):
        raw = st.session_state.get(
            _saved_display_key(group_index, field_index),
            st.session_state.get(key, ""),
        )
    else:
        raw = st.session_state.get(key, "")
    parsed = _parse_field_text(field, str(raw))
    if parsed is None:
        return False
    default = field["value"]
    if _field_is_int(field):
        return int(parsed) != int(default)
    return abs(float(parsed) - float(default)) > 1e-9


def _group_entered_field_count(group_index: int, group: dict[str, Any]) -> int:
    return sum(
        1
        for fi, field in _iter_input_fields(group)
        if _field_has_user_entry(group_index, fi, field, group)
    )


def _group_input_field_count(group: dict[str, Any]) -> int:
    return len(_iter_input_fields(group))


def _param_count(group: dict[str, Any]) -> str:
    n = _group_input_field_count(group)
    if n:
        return f"{n} Parameter{'s' if n != 1 else ''}"
    for t in group.get("tags", []):
        txt = t.get("text", "")
        m = re.search(r"\d+", txt)
        if not m:
            continue
        count = int(m.group())
        if any(k in txt.lower() for k in ("entered", "field", "parameter")):
            return f"{count} Parameter{'s' if count != 1 else ''}"
    return "0 Parameters"


# ---------------------------------------------------------------------------
# Simulate form state — per-section Save (lock) / Reset / Start simulation
# ---------------------------------------------------------------------------

_SIM_RUN_KEY = "simulation_run"
_SIM_SNAPSHOT_KEY = "simulation_snapshot"
_SIM_HISTORY_KEY = "sim_submission_history"
_RESET_KEY = "sim_reset_requested"
_SIDE_GAP_GEN_KEY = "sim_side_gap_gen"
_STATUS_LABELS = (
    ("DD% (4 fields)", 0),
    ("Inflation (6 fields)", 1),
    ("Process cost", 2),
)


def _saved_key(index: int) -> str:
    return f"sim_saved_{index}"


def _field_key(group_index: int, field_index: int) -> str:
    return f"sim_f_{group_index}_{field_index}"


def _saved_display_key(group_index: int, field_index: int) -> str:
    return f"sim_saved_display_{group_index}_{field_index}"


def _field_is_int(field: dict[str, Any]) -> bool:
    return field.get("max") is not None and field.get("step") is None


def _field_display_str(field: dict[str, Any], value: Any) -> str:
    if _field_is_int(field):
        return str(int(value))
    return f"{float(value):.1f}"


def _parse_field_text(field: dict[str, Any], raw: str) -> int | float | None:
    text = (raw or "").strip().replace("%", "")
    if not text:
        return None
    try:
        if _field_is_int(field):
            parsed = int(float(text))
            lo = int(field.get("min") or 0)
            hi = int(field.get("max") or 100)
            return max(lo, min(hi, parsed))
        return round(float(text), 1)
    except ValueError:
        return None


_FIELD_WIDGET_VERSION = 9
_DELIVERY_MIX_TITLE = "Direct Delivery"
_INFLATION_RATES_TITLE = "Inflation Rates"
_INFLATION_CALC_TO_IMPACT = {
    "PTC": "PTC impact",
    "STC": "STC impact",
    "SWC var": "SWC var impact",
    "SWC fixed": "SWC fixed impact",
    "SWC Obs. fix.": "SWC Obs. fix. Impact",
}
_INFLATION_CALCULATED_NAMES = frozenset(_INFLATION_CALC_TO_IMPACT.keys())


def _ensure_field_text_state(key: str, field: dict[str, Any]) -> None:
    """Migrate widget keys to text chip strings; resets to field default on version bump."""
    ver_key = f"_{key}_wver"
    if st.session_state.get(ver_key) != _FIELD_WIDGET_VERSION:
        st.session_state.pop(key, None)
        st.session_state[key] = _field_display_str(field, field["value"])
        st.session_state[ver_key] = _FIELD_WIDGET_VERSION
    elif key not in st.session_state:
        st.session_state[key] = _field_display_str(field, field["value"])
    elif isinstance(st.session_state[key], (int, float)):
        st.session_state[key] = _field_display_str(field, st.session_state[key])


def _persist_group_field_displays(index: int, group: dict[str, Any]) -> None:
    """Freeze entered values on Save so locked rows keep what the user typed."""
    for fi, field in enumerate(group.get("fields", [])):
        if _is_inflation_rates_group(group) and _is_inflation_calculated_field(field):
            continue
        key = _field_key(index, fi)
        raw = st.session_state.get(key, "")
        parsed = _parse_field_text(field, str(raw))
        value = parsed if parsed is not None else field["value"]
        display = _field_display_str(field, value)
        st.session_state[_saved_display_key(index, fi)] = display
        st.session_state[key] = display


def _saved_field_display(group_index: int, field_index: int, field: dict[str, Any]) -> str:
    return st.session_state.get(
        _saved_display_key(group_index, field_index),
        _field_display_str(field, field["value"]),
    )


def _field_numeric_value(field: dict[str, Any], key: str, default: Any | None = None) -> int | float:
    fallback = field["value"] if default is None else default
    raw = st.session_state.get(key, _field_display_str(field, fallback))
    if isinstance(raw, (int, float)):
        return int(raw) if _field_is_int(field) else float(raw)
    parsed = _parse_field_text(field, str(raw))
    if parsed is None:
        return int(fallback) if _field_is_int(field) else float(fallback)
    return parsed


def _dm_calc_key(group_index: int) -> str:
    return f"sim_dm_calc_{group_index}"


def _is_delivery_mix_group(group: dict[str, Any]) -> bool:
    return group.get("title") == _DELIVERY_MIX_TITLE


def _delivery_mix_effective_dd(dd_change: int | float, user_input: int | float) -> int:
    """Effective DD% = baseline DD_change + user adjustment (0–100)."""
    return max(0, min(100, int(round(dd_change + user_input))))


def _compute_delivery_mix(group_index: int, group: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fi, field in enumerate(group.get("fields", [])):
        key = _field_key(group_index, fi)
        user_input = _field_numeric_value(field, key)
        dd_change = int(field.get("dd_change", 0))
        rows.append({
            "company": field["name"],
            "dd_change": dd_change,
            "user_input": int(user_input),
            "effective_dd": _delivery_mix_effective_dd(dd_change, user_input),
        })
    return rows


def _delivery_mix_field_value(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
    group: dict[str, Any],
) -> int:
    """Resolved DD% for snapshots — uses saved calculation when available."""
    calc_rows: list[dict[str, Any]] = st.session_state.get(_dm_calc_key(group_index), [])
    if calc_rows and field_index < len(calc_rows):
        return int(calc_rows[field_index]["effective_dd"])
    key = _field_key(group_index, field_index)
    user_input = _field_numeric_value(field, key)
    return _delivery_mix_effective_dd(field.get("dd_change", 0), user_input)


def _infl_calc_key(group_index: int) -> str:
    return f"sim_infl_calc_{group_index}"


def _is_inflation_rates_group(group: dict[str, Any]) -> bool:
    return group.get("title") == _INFLATION_RATES_TITLE


def _inflation_impact_field_index(group: dict[str, Any], impact_name: str) -> int | None:
    for fi, field in enumerate(group.get("fields", [])):
        if field.get("name") == impact_name:
            return fi
    return None


def _inflation_user_input_for_field(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
    group: dict[str, Any],
) -> float:
    if _is_inflation_calculated_field(field):
        impact_name = _INFLATION_CALC_TO_IMPACT.get(field["name"])
        if impact_name:
            impact_idx = _inflation_impact_field_index(group, impact_name)
            if impact_idx is not None:
                impact_field = group["fields"][impact_idx]
                key = _field_key(group_index, impact_idx)
                return float(_field_numeric_value(impact_field, key))
        return 0.0
    key = _field_key(group_index, field_index)
    return float(_field_numeric_value(field, key))


def _inflation_cell_values(inflation_vector: tuple[float, ...], impact: list[int] | tuple[int, ...]) -> list[float]:
    return [round(inflation_vector[i] * impact[i] / 100, 1) for i in range(len(inflation_vector))]


def _inflation_baseline_from_field(field: dict[str, Any]) -> float:
    if "infl_baseline" in field:
        return float(field["infl_baseline"])
    impact = field.get("impact") or ()
    inflation_vector = field.get("inflation_vector") or (2.0, 3.0, 5.0, 2.0, -1.0, 2.0)
    return round(sum(_inflation_cell_values(inflation_vector, impact)), 1)


def _inflation_effective_total(baseline: float, user_input: float) -> float:
    return round(baseline + user_input, 1)


def _compute_inflation_rates(group_index: int, group: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fi, field in enumerate(group.get("fields", [])):
        user_input = _inflation_user_input_for_field(group_index, fi, field, group)
        baseline = _inflation_baseline_from_field(field)
        impact = field.get("impact") or []
        inflation_vector = field.get("inflation_vector") or (2.0, 3.0, 5.0, 2.0, -1.0, 2.0)
        cells = _inflation_cell_values(inflation_vector, impact) if impact else []
        rows.append({
            "name": field["name"],
            "role": field.get("infl_role", "calculated"),
            "infl_baseline": baseline,
            "user_input": round(user_input, 1),
            "cells": cells,
            "effective_total": _inflation_effective_total(baseline, user_input),
        })
    return rows


def _inflation_field_value(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
    group: dict[str, Any],
) -> float:
    """Resolved inflation % for snapshots — uses saved calculation when available."""
    calc_rows: list[dict[str, Any]] = st.session_state.get(_infl_calc_key(group_index), [])
    if calc_rows and field_index < len(calc_rows):
        return float(calc_rows[field_index]["effective_total"])
    user_input = _inflation_user_input_for_field(group_index, field_index, field, group)
    return _inflation_effective_total(_inflation_baseline_from_field(field), user_input)


def _apply_pending_reset(groups: list[dict[str, Any]]) -> None:
    """Clear widget keys before any inputs render (Streamlit cannot reset after instantiate)."""
    if not st.session_state.pop(_RESET_KEY, False):
        return
    st.session_state[_SIM_RUN_KEY] = False
    st.session_state.pop(_SIM_SNAPSHOT_KEY, None)
    st.session_state.pop(_SIM_HISTORY_KEY, None)
    st.session_state[_SIDE_GAP_GEN_KEY] = st.session_state.get(_SIDE_GAP_GEN_KEY, 0) + 1
    for i, group in enumerate(groups):
        st.session_state[_saved_key(i)] = False
        st.session_state.pop(f"sim_open_{i}", None)
        st.session_state.pop(_dm_calc_key(i), None)
        st.session_state.pop(_infl_calc_key(i), None)
        for fi, _field in enumerate(group.get("fields", [])):
            key = _field_key(i, fi)
            st.session_state.pop(key, None)
            st.session_state.pop(_saved_display_key(i, fi), None)
            st.session_state.pop(f"_{key}", None)
            st.session_state.pop(f"_{key}_wver", None)
    for spec in _PANEL_HEADER_FILTERS:
        st.session_state.pop(spec["key"], None)
    for key in (_SCOPE_DRILL_KEY, _SCOPE_VALUE_KEY, _SCOPE_INIT_KEY, "sim_panel_year"):
        st.session_state.pop(key, None)


def _scope_parent_for_leaf(leaf: str) -> str | None:
    clean = leaf.replace("📅 ", "").strip()
    for parent, children in _PANEL_SCOPE_TREE.items():
        for child in children:
            if child == clean or clean in child or child.endswith(clean):
                return parent
    return None


def _init_panel_scope_state(default_leaf: str | None) -> None:
    if st.session_state.get(_SCOPE_INIT_KEY):
        return
    st.session_state[_SCOPE_INIT_KEY] = True
    if not default_leaf:
        return
    clean = default_leaf.replace("📅 ", "").strip()
    parent = _scope_parent_for_leaf(clean)
    if not parent:
        return
    child = next(
        (c for c in _PANEL_SCOPE_TREE[parent] if c == clean or clean in c),
        _PANEL_SCOPE_TREE[parent][0],
    )
    st.session_state[_SCOPE_DRILL_KEY] = parent
    st.session_state[_SCOPE_VALUE_KEY] = child


def _scope_flyout_trigger_label() -> str:
    parent = st.session_state.get(_SCOPE_DRILL_KEY)
    child = st.session_state.get(_SCOPE_VALUE_KEY)
    if parent and child:
        return f"{parent} · {child}"
    return _SCOPE_ROOT_PLACEHOLDER


def _scope_pick_from_query() -> bool:
    """Apply scope selection from ?scope_pick=Parent|Child query param."""
    raw = st.query_params.get(_SCOPE_PICK_QP)
    if not raw:
        return False
    parts = unquote(str(raw)).split("|", 1)
    if len(parts) != 2:
        return False
    parent, child = parts[0], parts[1]
    if parent not in _PANEL_SCOPE_TREE or child not in _PANEL_SCOPE_TREE[parent]:
        return False
    st.session_state[_SCOPE_DRILL_KEY] = parent
    st.session_state[_SCOPE_VALUE_KEY] = child
    del st.query_params[_SCOPE_PICK_QP]
    return True


def _scope_tree_pick_href(parent: str, child: str) -> str:
    return f"?{_SCOPE_PICK_QP}={quote(f'{parent}|{child}', safe='')}"


def _scope_hover_tree_html(trigger_label: str) -> str:
    """Native HTML/CSS hover flyout — categories left, values fly out on hover."""
    parent_rows: list[str] = []
    for parent, children in _PANEL_SCOPE_TREE.items():
        child_links = "".join(
            f'<a class="elx-scope-child" href="{_scope_tree_pick_href(parent, child)}">'
            f"{html.escape(child)}</a>"
            for child in children
        )
        parent_rows.append(
            f'<div class="elx-scope-parent">'
            f'<span class="elx-scope-chev">▸</span>'
            f'<span class="elx-scope-parent-lbl">{html.escape(parent)}</span>'
            f'<div class="elx-scope-submenu">{child_links}</div>'
            f"</div>"
        )
    parents_html = "".join(parent_rows)
    return f"""
<style>
.elx-scope-tree {{
  position: relative; width: 100%; font-family: "Source Sans Pro", sans-serif;
}}
.elx-scope-open {{ display: none; }}
.elx-scope-trigger {{
  display: flex; align-items: center; width: 100%; height: {_PANEL_CHIP_H};
  padding: 0 28px 0 10px; border: {_PANEL_CHIP_BORDER};
  border-radius: {_PANEL_CHIP_RADIUS}; background: {_PANEL_CHIP_BG}; color: {_PANEL_CHIP_TEXT};
  font-size: {_PANEL_CHIP_FONT}; font-weight: 600; cursor: pointer; position: relative;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; box-sizing: border-box;
  box-shadow: none; line-height: 1;
}}
.elx-scope-trigger::after {{
  content: "▾"; position: absolute; right: 10px; top: 50%;
  transform: translateY(-50%); font-size: 10px; color: {_PANEL_CHIP_CHEVRON}; opacity: 1;
}}
.elx-scope-panel {{
  display: none; position: absolute; left: 0; top: calc(100% + 4px);
  z-index: 99999; min-width: 100%; background: #ffffff;
  border: 1px solid #d4dbe6; border-radius: 4px;
  box-shadow: 0 8px 24px rgba(15,23,42,0.14); padding: 4px 0;
}}
.elx-scope-open:checked + .elx-scope-trigger + .elx-scope-panel {{ display: block; }}
.elx-scope-parent {{
  position: relative; display: flex; align-items: center; gap: 6px;
  padding: 8px 12px; font-size: 13px; font-weight: 600; color: #011e41;
  white-space: nowrap; cursor: default;
}}
.elx-scope-parent:hover {{ background: #eef2f7; }}
.elx-scope-chev {{ color: #64748b; font-size: 11px; }}
.elx-scope-submenu {{
  display: none; position: absolute; left: 100%; top: 0;
  min-width: 148px; background: #ffffff; border: 1px solid #d4dbe6;
  border-radius: 4px; box-shadow: 0 6px 18px rgba(15,23,42,0.12);
  padding: 4px 0; z-index: 100000;
}}
.elx-scope-parent:hover .elx-scope-submenu {{ display: block; }}
.elx-scope-child {{
  display: block; padding: 8px 14px; font-size: 13px; font-weight: 600;
  color: #011e41; text-decoration: none; white-space: nowrap;
}}
.elx-scope-child:hover {{ background: #eef2f7; color: #011e41; }}
</style>
<div class="elx-scope-tree">
  <input type="checkbox" id="elx-scope-open" class="elx-scope-open" />
  <label for="elx-scope-open" class="elx-scope-trigger">{html.escape(trigger_label)}</label>
  <div class="elx-scope-panel">{parents_html}</div>
</div>
"""


def _render_panel_scope_tree_dropdown(parent_col, *, default_leaf: str | None = None) -> str:
    """Hover flyout — categories left, child values beside on hover; pick in one step."""
    if _scope_pick_from_query():
        st.rerun()

    _init_panel_scope_state(default_leaf)
    trigger_label = _scope_flyout_trigger_label()
    parent_col.markdown(
        '<span class="elx-filter-panel sim-panel-scope-tree" aria-hidden="true"></span>'
        + _scope_hover_tree_html(trigger_label),
        unsafe_allow_html=True,
    )
    return str(st.session_state.get(_SCOPE_VALUE_KEY, trigger_label))


def init_simulate_state(groups: list[dict[str, Any]]) -> None:
    """Session keys for saved sections, field values, and simulation results."""
    _apply_pending_reset(groups)
    if "sim_state_ready" not in st.session_state:
        st.session_state["sim_state_ready"] = True
        st.session_state[_SIM_RUN_KEY] = False
        for i in range(len(groups)):
            st.session_state.setdefault(_saved_key(i), False)


def _group_is_saved(index: int) -> bool:
    return bool(st.session_state.get(_saved_key(index), False))


def _all_groups_saved(groups: list[dict[str, Any]]) -> bool:
    return all(_group_is_saved(i) for i in range(len(groups)))


def _count_progress_fields(groups: list[dict[str, Any]]) -> tuple[int, int]:
    """Return (entered_field_count, total_field_count) across all input fields."""
    total = 0
    entered = 0
    for i, group in enumerate(groups):
        for fi, field in _iter_input_fields(group):
            total += 1
            if _field_has_user_entry(i, fi, field, group):
                entered += 1
    return entered, total


def _compute_progress(groups: list[dict[str, Any]]) -> dict[str, Any]:
    saved_groups = sum(1 for i in range(len(groups)) if _group_is_saved(i))
    total_groups = len(groups)
    saved_fields, total_fields = _count_progress_fields(groups)
    if total_fields:
        pct = round(saved_fields / total_fields * 100, 1)
        count = f"{saved_fields}/{total_fields}"
        label = "Parameters completed"
    else:
        pct = round(saved_groups / max(total_groups, 1) * 100, 1)
        count = f"{saved_groups}/{total_groups}"
        label = "Sections saved"
    return {"label": label, "count": count, "pct": pct}


def build_status_rows(groups: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Sidebar status rows — reflect which sections are saved."""
    rows: list[dict[str, str]] = []
    for label, idx in _STATUS_LABELS:
        if idx >= len(groups):
            continue
        group = groups[idx]
        if _group_is_saved(idx):
            rows.append({"name": label, "pill": "done", "pill_text": "Done"})
        elif not group.get("fields"):
            rows.append({"name": label, "pill": "partial", "pill_text": "Save section"})
        else:
            n = _group_input_field_count(group)
            entered = _group_entered_field_count(idx, group)
            rows.append({"name": label, "pill": "partial", "pill_text": f"{entered} / {n}"})
    return rows


def _status_summary(groups: list[dict[str, Any]]) -> str:
    saved_g = sum(1 for i in range(len(groups)) if _group_is_saved(i))
    return f"{saved_g}/{len(groups)} done"


def _warn_message(groups: list[dict[str, Any]]) -> str:
    if st.session_state.get(_SIM_RUN_KEY):
        return ""
    saved_g = sum(1 for i in range(len(groups)) if _group_is_saved(i))
    if saved_g:
        return "Optional: save sections to lock values. Start simulation anytime with current inputs."
    return "Fill parameters and click Start simulation when ready."


def _capture_group_submission(
    index: int,
    group: dict[str, Any],
    groups: list[dict[str, Any]],
) -> dict[str, Any]:
    """Snapshot entered values and completion status when a section is saved."""
    fields: list[dict[str, Any]] = []
    calculated_fields: list[dict[str, Any]] = []
    dm_calc: list[dict[str, Any]] = (
        st.session_state.get(_dm_calc_key(index), [])
        if _is_delivery_mix_group(group)
        else []
    )
    infl_calc: list[dict[str, Any]] = (
        st.session_state.get(_infl_calc_key(index), [])
        if _is_inflation_rates_group(group)
        else []
    )
    for fi, field in enumerate(group.get("fields", [])):
        if _is_inflation_rates_group(group) and _is_inflation_calculated_field(field):
            if infl_calc and fi < len(infl_calc):
                calculated_fields.append({
                    "name": field["name"],
                    "name_tags": field.get("name_tags", []),
                    "value": _field_display_str(field, infl_calc[fi]["effective_total"]),
                    "suffix": field.get("suffix") or "%",
                })
            continue
        key = _field_key(index, fi)
        if dm_calc and fi < len(dm_calc):
            value = dm_calc[fi]["effective_dd"]
        elif infl_calc and fi < len(infl_calc):
            value = infl_calc[fi]["effective_total"]
        elif _is_delivery_mix_group(group):
            value = _delivery_mix_field_value(index, fi, field, group)
        elif _is_inflation_rates_group(group):
            value = _inflation_field_value(index, fi, field, group)
        else:
            value = _field_numeric_value(field, key)
        fields.append({
            "name": field["name"],
            "value": value,
            "suffix": field.get("suffix") or "",
        })
    return {
        "title": group["title"],
        "status_summary": _status_summary(groups),
        "status_rows": build_status_rows(groups),
        "fields": fields,
        "calculated_fields": calculated_fields,
    }


def _on_save_group(index: int, group: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    _persist_group_field_displays(index, group)
    if _is_delivery_mix_group(group):
        st.session_state[_dm_calc_key(index)] = _compute_delivery_mix(index, group)
    elif _is_inflation_rates_group(group):
        st.session_state[_infl_calc_key(index)] = _compute_inflation_rates(index, group)
    st.session_state[_saved_key(index)] = True
    st.session_state[_SIM_RUN_KEY] = False
    history = st.session_state.setdefault(_SIM_HISTORY_KEY, [])
    history.append(_capture_group_submission(index, group, groups))


def request_reset_simulate() -> None:
    """Schedule reset on next rerun (must run before widgets are drawn)."""
    st.session_state[_RESET_KEY] = True


def _capture_submission_snapshot(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Store parameter values at Start simulation — right panel shows only this data."""
    rows: list[dict[str, Any]] = []
    for i, group in enumerate(groups):
        for fi, field in enumerate(group.get("fields", [])):
            if _is_delivery_mix_group(group):
                value = _delivery_mix_field_value(i, fi, field, group)
            elif _is_inflation_rates_group(group):
                value = _inflation_field_value(i, fi, field, group)
            else:
                key = _field_key(i, fi)
                value = _field_numeric_value(field, key)
            rows.append({
                "group": group["title"],
                "name": field["name"],
                "value": value,
                "suffix": field.get("suffix") or "",
            })
    return rows


def _on_start_simulation(groups: list[dict[str, Any]]) -> None:
    """Run simulation with whatever values are currently in the form (no fill-all requirement)."""
    st.session_state[_SIM_SNAPSHOT_KEY] = _capture_submission_snapshot(groups)
    st.session_state[_SIM_RUN_KEY] = True


# ---------------------------------------------------------------------------
# Section 1 — Context filter bar (seed: SIMULATE_CONTEXT)
# ---------------------------------------------------------------------------

def render_simulate_context_bar(data: dict[str, Any]) -> None:
    """CONTEXT row — shared filter_bar.render_context_filter_bar (Figma)."""
    _render_context_bar(data, page_marker=True)


# ---------------------------------------------------------------------------
# Section 2 — Progress stepper
# ---------------------------------------------------------------------------

def render_stepper(steps: list[dict[str, str]]) -> None:
    done_n = sum(1 for s in steps if s.get("state") == "done")
    total = max(len(steps) - 1, 1)
    prog = int(done_n / total * 84)
    items = []
    for i, s in enumerate(steps):
        st_state = s.get("state", "")
        if st_state == "done":
            circle = (
                f'<div style="width:28px;height:28px;border-radius:0;background:{_SUCCESS};'
                f'color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;'
                f'font-size:13px;font-weight:700;">✓</div>'
            )
            color = _SUCCESS
        elif st_state == "current":
            circle = (
                f'<div style="width:28px;height:28px;border-radius:0;background:{_PRIMARY};'
                f'color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;'
                f'font-size:12px;font-weight:700;">{i + 1}</div>'
            )
            color = _PRIMARY
        else:
            circle = (
                f'<div style="width:28px;height:28px;border-radius:0;border:2px solid #d1d5db;'
                f'background:#fff;color:#9ca3af;margin:0 auto;display:flex;align-items:center;'
                f'justify-content:center;font-size:12px;font-weight:700;">{i + 1}</div>'
            )
            color = "#9ca3af"
        items.append(
            f'<div style="text-align:center;flex:1;min-width:0;">{circle}'
            f'<div style="margin-top:6px;font-size:11px;font-weight:600;color:{color};">'
            f'{html.escape(s["label"])}</div></div>'
        )
    try:
        box = st.container(border=True, key="sim_stepper_section")
    except TypeError:
        box = st.container(border=True)
    with box:
        st.markdown(
            '<span class="sim-step-section-marker" aria-hidden="true"></span>'
            '<span class="sim-step-marker" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        _html(
            f"""
            <div style="position:relative;padding:4px 0 0;">
              <div style="position:absolute;top:18px;left:8%;right:8%;height:2px;background:{_BORDER};z-index:1;"></div>
              <div style="position:absolute;top:18px;left:8%;width:{prog}%;height:2px;background:{_SUCCESS};z-index:2;"></div>
              <div style="display:flex;justify-content:space-between;position:relative;z-index:3;gap:4px;">
                {"".join(items)}
              </div>
            </div>
            """
        )


# ---------------------------------------------------------------------------
# Section 3 — Left panel header + parameter groups
# ---------------------------------------------------------------------------

def render_parameter_panel_header(data: dict[str, Any], groups: list[dict[str, Any]] | None = None) -> None:
    groups = groups or data.get("param_groups") or []
    saved_g = sum(1 for i in range(len(groups)) if _group_is_saved(i)) if groups else 0
    all_saved = groups and _all_groups_saved(groups)
    if all_saved:
        saved_badge = (
            f'<div style="background:{_SUCCESS};border-radius:0;color:#fff;font-size:12px;'
            f'font-weight:700;padding:8px 14px;white-space:nowrap;flex-shrink:0;'
            f'display:inline-flex;align-items:center;gap:6px;">'
            f'<span style="font-size:14px;">✓</span> All saved</div>'
        )
    elif saved_g:
        saved_badge = (
            f'<div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);'
            f'border-radius:0;color:#e2e8f0;font-size:12px;font-weight:600;padding:8px 14px;'
            f'white-space:nowrap;flex-shrink:0;">{saved_g}/{len(groups)} sections saved</div>'
        )
    else:
        saved_badge = (
            f'<div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);'
            f'border-radius:0;color:#e2e8f0;font-size:12px;font-weight:600;padding:8px 14px;'
            f'white-space:nowrap;flex-shrink:0;">Edit parameters freely</div>'
        )
    try:
        header_wrap = st.container(key="sim_panel_header_wrap")
    except TypeError:
        header_wrap = st.container()
    with header_wrap:
        st.markdown('<span class="sim-panel-header-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        _html(
            f"""
            <div class="sim-panel-header-wrap" style="background:{_PANEL_HEADER_BG};padding:16px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                <div style="min-width:0;flex:1;">
                  <h2 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#fff;line-height:1.2;">
                    {html.escape(data["params_title"])}
                  </h2>
                  <p style="margin:0 0 14px;font-size:13px;color:rgba(203,213,225,0.95);line-height:1.4;">
                    {html.escape(data["params_sub"])}
                  </p>
                </div>
                <div style="flex-shrink:0;">{saved_badge}</div>
              </div>
            </div>
            """
        )
        st.markdown('<span class="sim-panel-filters-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        filter_cols = st.columns(5, gap="small", vertical_alignment="bottom")
        for col, spec in zip(filter_cols, _PANEL_HEADER_FILTERS):
            filter_select(
                spec["label"],
                spec["key"],
                preset=spec["preset"],
                default=spec["default"],
                parent=col,
                panel_header=True,
                label_above=spec["label"],
            )


def _group_is_open(index: int, group: dict[str, Any]) -> bool:
    open_key = f"sim_open_{index}"
    if open_key not in st.session_state:
        st.session_state[open_key] = bool(group.get("expanded"))
    return bool(st.session_state[open_key])


def render_parameter_group_header(
    group: dict[str, Any],
    index: int,
    groups: list[dict[str, Any]],
) -> None:
    """Section header row — Save + chevron outside st.form (Figma)."""
    open_key = f"sim_open_{index}"
    chevron = "▾" if _group_is_open(index, group) else "▸"
    saved = _group_is_saved(index)

    st.markdown('<span class="sim-param-group-marker"></span>', unsafe_allow_html=True)
    top_l, top_m, top_a = st.columns([5.5, 1.0, 1.2], vertical_alignment="center")
    with top_l:
        _html(
            f"""
            <div style="display:flex;align-items:center;gap:14px;">
              <div style="width:44px;height:44px;background:{_ICON_BG};border-radius:0;
                  display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;">
                {html.escape(group["icon"])}
              </div>
              <div style="min-width:0;">
                <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;">
                  <p style="margin:0;font-size:15px;font-weight:700;color:{_PRIMARY};line-height:1.25;">
                    {html.escape(group["title"])}
                  </p>
                  {_tags_html(group.get("tags", []))}
                </div>
                <p style="margin:4px 0 0;font-size:12px;color:{_TEXT_MUTED};line-height:1.4;">
                  {html.escape(group["desc"])}
                </p>
              </div>
            </div>
            """
        )
    with top_m:
        _html(
            f'<p style="margin:0;font-size:12px;color:{_TEXT_MUTED};text-align:right;white-space:nowrap;">'
            f'{html.escape(_param_count(group))}</p>'
        )
    with top_a:
        st.markdown('<span class="sim-actions-col"></span>', unsafe_allow_html=True)
        btn_s, btn_t = st.columns([2.1, 1], gap="small")
        with btn_s:
            st.markdown('<span class="sim-save-col"></span>', unsafe_allow_html=True)
            if saved:
                st.button("✓ Saved", key=f"sim_save_{index}", disabled=True, use_container_width=True)
            elif st.button("Save", key=f"sim_save_{index}", use_container_width=True):
                _on_save_group(index, group, groups)
                st.rerun()
        with btn_t:
            st.markdown('<span class="sim-toggle-col"></span>', unsafe_allow_html=True)
            if st.button(chevron, key=f"sim_toggle_{index}"):
                st.session_state[open_key] = not st.session_state[open_key]
                st.rerun()


def _render_process_section_header(field: dict[str, Any], *, show_divider: bool) -> None:
    if show_divider:
        st.markdown('<hr class="sim-row-divider" aria-hidden="true" />', unsafe_allow_html=True)
    st.markdown('<span class="sim-field-row-marker sim-section-header-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _html(
        f'<p style="margin:0;padding:10px 0 6px;font-size:13px;font-weight:700;color:{_PRIMARY};">'
        f'{html.escape(field["name"])}</p>'
    )


def render_parameter_group_fields(group: dict[str, Any], index: int) -> None:
    """Parameter rows — compact text chip with % suffix (no number_input steppers)."""
    if not _group_is_open(index, group):
        return

    st.markdown('<span class="sim-group-fields-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    fields = group.get("fields", [])
    if not fields:
        return

    content_started = False
    prev_was_section = False
    for fi, field in enumerate(fields):
        if _is_inflation_rates_group(group) and _is_inflation_calculated_field(field):
            continue
        if _is_section_field(field):
            _render_process_section_header(field, show_divider=content_started)
            content_started = True
            prev_was_section = True
            continue
        if content_started and not prev_was_section:
            st.markdown('<hr class="sim-row-divider" aria-hidden="true" />', unsafe_allow_html=True)
        prev_was_section = False
        _render_parameter_field(field, index, fi)
        content_started = True


def render_parameter_group(
    group: dict[str, Any],
    index: int,
    groups: list[dict[str, Any]],
) -> None:
    """One Figma accordion card: header and fields inside the same bordered section."""
    try:
        box = st.container(border=True, key=f"sim_grp_{index}")
    except TypeError:
        box = st.container(border=True)
    with box:
        st.markdown(
            f'<span class="sim-param-group-wrap" data-group="{index}" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        render_parameter_group_header(group, index, groups)
        render_parameter_group_fields(group, index)


def _render_parameter_field(field: dict[str, Any], group_index: int, field_index: int) -> None:
    key = _field_key(group_index, field_index)
    locked = _group_is_saved(group_index)
    tags = _tags_html(field.get("name_tags", []))
    st.markdown('<span class="sim-field-row-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    col_l, col_r = st.columns([5.2, 1.5], vertical_alignment="center")
    with col_l:
        desc_html = (
            f'<p style="margin:0;font-size:11px;color:{_TEXT_MUTED};line-height:1.4;">'
            f'{html.escape(field["desc"])}</p>'
            if field.get("desc")
            else ""
        )
        _html(
            f'<p style="margin:0 0 4px;font-size:13px;font-weight:700;color:{_PRIMARY};">'
            f'{html.escape(field["name"])}{tags}</p>'
            f"{desc_html}"
        )
    with col_r:
        if locked:
            display = _saved_field_display(group_index, field_index, field)
            st.markdown(
                '<span class="sim-pct-chip-row sim-pct-chip-readonly" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
            _html(
                f'<div style="display:inline-flex;align-items:center;justify-content:flex-end;'
                f'gap:4px;width:100%;background:{_INPUT_BG};border:1px solid {_INPUT_BORDER};'
                f'border-radius:8px;padding:0 12px;min-height:40px;height:40px;box-sizing:border-box;">'
                f'<span style="font-size:14px;font-weight:700;color:{_PRIMARY};">'
                f'{html.escape(display)}</span>'
                f'<span style="font-size:13px;font-weight:600;color:#64748b;">%</span></div>'
            )
        else:
            st.markdown('<span class="sim-pct-chip-row" aria-hidden="true"></span>', unsafe_allow_html=True)
            val_c, pct_c = st.columns([1, 0.28], gap="small", vertical_alignment="center")
            with val_c:
                _ensure_field_text_state(key, field)
                st.text_input("\u200b", key=key, label_visibility="collapsed")
            with pct_c:
                st.markdown(
                    '<span class="sim-pct-chip-suffix" aria-hidden="true">%</span>',
                    unsafe_allow_html=True,
                )


def render_action_bar(
    data: dict[str, Any],
    groups: list[dict[str, Any]],
    *,
    in_form: bool = False,
) -> None:
    prog = _compute_progress(groups)
    pct = float(prog.get("pct", 0))
    count = html.escape(prog["count"])
    st.markdown('<hr class="sim-row-divider sim-footer-divider" aria-hidden="true" />', unsafe_allow_html=True)
    try:
        footer = st.container(key="sim_footer")
    except TypeError:
        footer = st.container()
    with footer:
        st.markdown('<span class="sim-footer-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        col_p, col_r, col_s = st.columns([6.2, 1.15, 1.45], vertical_alignment="center")
        with col_p:
            _html(
                f"""
                <p style="margin:0 0 10px;font-size:13px;font-weight:500;color:{_TEXT_MUTED};">
                  {html.escape(prog["label"])}
                </p>
                <div style="position:relative;height:10px;">
                  <div style="height:10px;background:{_BORDER};border-radius:0;overflow:hidden;">
                    <div style="height:100%;width:{pct}%;background:{_PRIMARY};border-radius:0;"></div>
                  </div>
                  <span style="position:absolute;right:0;top:-22px;font-size:14px;font-weight:700;color:{_PRIMARY};">
                    {count}
                  </span>
                </div>
                """
            )
        with col_r:
            st.markdown('<span class="sim-reset-col"></span>', unsafe_allow_html=True)
            if st.button("↺  Reset", key="sim_reset", use_container_width=True):
                request_reset_simulate()
                st.rerun()
        with col_s:
            st.markdown('<span class="sim-start-col"></span>', unsafe_allow_html=True)
            if st.button(
                "▶  Start Simulation",
                type="primary",
                use_container_width=True,
                key="sim_start",
            ):
                _on_start_simulation(groups)
                st.rerun()


# ---------------------------------------------------------------------------
# Section 4 — Right sidebar cards
# ---------------------------------------------------------------------------

def _side_card_spacer(key_suffix: str) -> None:
    """Fixed 12px gap between stacked sidebar cards."""
    gap_gen = st.session_state.get(_SIDE_GAP_GEN_KEY, 0)
    gap_key = f"sim_side_gap_{gap_gen}_{key_suffix}"
    try:
        gap_box = st.container(key=gap_key)
    except TypeError:
        gap_box = st.container()
    with gap_box:
        st.markdown(
            f'<span class="sim-side-card-gap" aria-hidden="true"></span>'
            f'<div style="height:{_SIDE_CARD_GAP};min-height:{_SIDE_CARD_GAP};display:block;"></div>',
            unsafe_allow_html=True,
        )


def _side_card(
    inner_html: str,
    *,
    card_key: str = "sim_side_card",
    submit: bool = False,
    infl_calc: bool = False,
) -> None:
    if infl_calc:
        marker = '<span class="sim-side-infl-calc-marker" aria-hidden="true"></span>'
    elif submit:
        marker = '<span class="sim-side-submit-marker" aria-hidden="true"></span>'
    else:
        marker = '<span class="sim-side-card-marker" aria-hidden="true"></span>'
    try:
        box = st.container(border=True, key=card_key) if infl_calc else st.container(key=card_key)
    except TypeError:
        box = st.container()
    with box:
        st.markdown(marker, unsafe_allow_html=True)
        _html(
            f'<div style="font-family:inherit;background:{_CARD_BG};padding:0;margin:0;">'
            f"{inner_html}</div>"
        )


def _impact_breakdown_html(impact: dict[str, Any], *, sectioned: bool = False) -> str:
    row_pad = _SUBMIT_SECTION_PAD if sectioned else "10px 0"
    section_border = "border-bottom:1px solid #eef2f7;" if sectioned else ""
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{row_pad};{section_border}font-size:12px;">
          <span style="display:flex;align-items:center;gap:8px;color:{_TEXT};font-weight:600;">
            <span style="width:8px;height:8px;border-radius:0;background:{_SQ.get(r["sq"], "#94a3b8")};"></span>
            {html.escape(r["name"])}
          </span>
          <span style="font-weight:700;color:{_VAL.get(r.get("value_class","neutral"), _TEXT)};">
            {html.escape(r["value"])}
          </span>
        </div>
        """
        for r in impact["rows"]
    )


def _summary_rows_html(rows: list[dict[str, Any]]) -> str:
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;font-size:12px;">
          <span style="display:flex;align-items:center;gap:8px;color:{_TEXT_MUTED};font-weight:600;">
            <span style="width:8px;height:8px;border-radius:0;background:{_SQ.get(r["sq"], "#94a3b8")};flex-shrink:0;"></span>
            {html.escape(r["name"])}
          </span>
          <span style="font-weight:700;color:{_VAL.get(r.get("value_class", "neutral"), _TEXT)};">
            {html.escape(r["value"])}
          </span>
        </div>
        """
        for r in rows
    )


def render_live_impact_card(data: dict[str, Any]) -> None:
    """Top sidebar card — Simulation Summary (Figma)."""
    summary = data.get("summary") or {}
    title = html.escape(summary.get("title", "Simulation Summary"))
    badge = html.escape(summary.get("badge", "Real-time"))
    rows = summary.get("rows") or []
    _side_card(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;background:#f8fafc;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">{title}</span>
          <span style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:4px;
            font-size:10px;font-weight:700;background:#fef3c7;color:#b45309;">✦ {badge}</span>
        </div>
        {_summary_rows_html(rows)}
        """,
        card_key="sim_side_impact",
    )


def render_summary_card(data: dict[str, Any]) -> None:
    render_live_impact_card(data)


def _status_rows_html(rows: list[dict[str, Any]], *, warn: str = "", compact: bool = False) -> str:
    row_pad = _SUBMIT_SECTION_PAD if compact else "7px 0"
    section_border = "border-bottom:1px solid #eef2f7;" if compact else ""
    body = "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{row_pad};{section_border}font-size:12px;color:{_TEXT};">
          <span>{html.escape(r["name"])}</span>
          <span style="background:{"#dcfce7" if r["pill"] == "done" else "#fef3c7"};
            color:{"#16a34a" if r["pill"] == "done" else "#b45309"};
            font-size:11px;font-weight:700;padding:3px 10px;border-radius:0;">
            {"✓ " if r["pill"] == "done" else ""}{html.escape(r["pill_text"])}
          </span>
        </div>
        """
        for r in rows
    )
    if warn:
        body += (
            f'<div style="font-size:11px;color:#b45309;margin-top:10px;line-height:1.4;">'
            f'{html.escape(warn)}</div>'
        )
    return body


def render_progress_card(data: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    rows = build_status_rows(groups)
    summary = html.escape(_status_summary(groups))
    warn = _warn_message(groups)
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Parameter Completion</span>
          <span style="font-size:12px;font-weight:700;color:#b45309;">{summary}</span>
        </div>
        {_status_rows_html(rows, warn=warn)}
        """
    )


def _submission_field_rows_html(fields: list[dict[str, Any]], *, compact: bool = False) -> str:
    if not fields:
        return ""
    rows = "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            font-size:12px;{"margin-top:6px;" if compact else "padding:8px 0;border-bottom:1px solid #eef2f7;"}">
          <span style="color:{_TEXT_MUTED};max-width:62%;">{html.escape(f["name"])}</span>
          <span style="font-weight:700;color:{_PRIMARY};">
            {html.escape(str(f["value"]))}{html.escape(f["suffix"])}
          </span>
        </div>
        """
        for f in fields
    )
    if compact:
        return (
            f'<div style="padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;">'
            f'<p style="margin:0;font-size:11px;font-weight:700;color:{_TEXT_MUTED};">Entered values</p>'
            f"{rows}</div>"
        )
    return (
        f'<div style="margin-bottom:10px;padding-bottom:4px;border-bottom:1px solid #eef2f7;">'
        f'<p style="margin:0 0 6px;font-size:11px;font-weight:700;color:{_TEXT_MUTED};">Entered values</p>'
        f"{rows}</div>"
    )


def _inflation_calculated_display_rows(group_index: int, group: dict[str, Any]) -> list[dict[str, Any]]:
    """Build PTC/STC/SWC rows from saved inflation calculation."""
    infl_calc: list[dict[str, Any]] = st.session_state.get(_infl_calc_key(group_index), [])
    rows: list[dict[str, Any]] = []
    for fi, field in enumerate(group.get("fields", [])):
        if not _is_inflation_calculated_field(field):
            continue
        if infl_calc and fi < len(infl_calc):
            rows.append({
                "name": field["name"],
                "name_tags": field.get("name_tags", []),
                "value": _field_display_str(field, infl_calc[fi]["effective_total"]),
                "suffix": field.get("suffix") or "%",
            })
    return rows


def _inflation_calculated_rows_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    parts: list[str] = []
    for i, row in enumerate(rows):
        tags = _tags_html(row.get("name_tags", []))
        border = "border-bottom:1px solid #eef2f7;" if i < len(rows) - 1 else ""
        parts.append(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                padding:{_SUBMIT_SECTION_PAD};{border}font-size:12px;">
              <span style="display:flex;align-items:center;gap:6px;font-weight:700;color:{_PRIMARY};">
                {html.escape(row["name"])}{tags}
              </span>
              <span style="font-weight:700;color:{_PRIMARY};">
                {html.escape(str(row["value"]))}{html.escape(row.get("suffix", "%"))}
              </span>
            </div>
            """
        )
    return "".join(parts)


def render_inflation_calculated_card(rows: list[dict[str, Any]], index: int) -> None:
    """Right sidebar — calculated PTC/STC/SWC rates after inflation Save."""
    if not rows:
        return
    _side_card(
        f"""
        <div style="padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Calculated rates</span>
        </div>
        {_inflation_calculated_rows_html(rows)}
        """,
        card_key=f"sim_side_infl_calc_{index}",
        infl_calc=True,
    )


def render_section_submission_card(entry: dict[str, Any], index: int) -> None:
    """One card per Save — shows submitted section data (Figma status card)."""
    title = html.escape(entry["title"])
    summary = html.escape(entry.get("status_summary", ""))
    field_block = _submission_field_rows_html(entry.get("fields") or [], compact=True)
    status_block = _status_rows_html(entry.get("status_rows") or [], compact=True)
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:baseline;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">{title}</span>
          <span style="font-size:12px;font-weight:700;color:#b45309;">{summary}</span>
        </div>
        {field_block}
        {status_block}
        """,
        card_key=f"sim_side_submit_{index}",
        submit=True,
    )


def render_submission_history_cards(groups: list[dict[str, Any]]) -> None:
    """Stack a card below live impact for each section Save."""
    history: list[dict[str, Any]] = st.session_state.get(_SIM_HISTORY_KEY) or []
    inflation_idx = next(
        (i for i, group in enumerate(groups) if _is_inflation_rates_group(group)),
        None,
    )
    for index, entry in enumerate(history):
        _side_card_spacer(f"before_submit_{index}")
        render_section_submission_card(entry, index)
        calc_rows = entry.get("calculated_fields") or []
        if (
            not calc_rows
            and inflation_idx is not None
            and entry.get("title") == _INFLATION_RATES_TITLE
            and _group_is_saved(inflation_idx)
        ):
            calc_rows = _inflation_calculated_display_rows(inflation_idx, groups[inflation_idx])
        if calc_rows:
            _side_card_spacer(f"before_calc_{index}")
            render_inflation_calculated_card(calc_rows, index)


def render_simulate_sidebar(data: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    """Right column — live impact on top, submitted section cards below."""
    st.markdown('<span class="sim-sidebar-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    render_live_impact_card(data)
    render_submission_history_cards(groups)


def render_simulation_results_card(data: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    """Right sidebar — single card with submitted simulation data only."""
    snapshot: list[dict[str, Any]] = st.session_state.get(_SIM_SNAPSHOT_KEY) or []
    if not snapshot:
        return

    impact = data["impact"]
    impact_rows = "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:8px 0;border-bottom:1px solid #f3f4f6;font-size:12px;">
          <span style="display:flex;align-items:center;gap:8px;color:{_TEXT};">
            <span style="width:8px;height:8px;border-radius:0;background:{_SQ.get(r["sq"], "#94a3b8")};"></span>
            {html.escape(r["name"])}
          </span>
          <span style="font-weight:700;color:{_VAL.get(r.get("value_class","neutral"), _TEXT)};">
            {html.escape(r["value"])}
          </span>
        </div>
        """
        for r in impact["rows"]
    )
    param_rows = "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:7px 0;border-bottom:1px solid #f3f4f6;font-size:12px;">
          <span style="color:{_TEXT_MUTED};max-width:58%;">{html.escape(row["group"])} — {html.escape(row["name"])}</span>
          <span style="font-weight:700;color:{_PRIMARY};">{html.escape(str(row["value"]))}{html.escape(row["suffix"])}</span>
        </div>
        """
        for row in snapshot
    )
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Simulation Results</span>
          <span style="display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:0;
            font-size:10px;font-weight:700;background:#ecfdf5;color:#065f46;">
            <span style="width:6px;height:6px;border-radius:0;background:#22c55e;"></span>Submitted
          </span>
        </div>
        <div style="font-size:28px;font-weight:800;color:{_DANGER};margin:4px 0 6px;line-height:1.1;">
          {html.escape(impact["headline"])}
        </div>
        <div style="font-size:11px;font-weight:600;color:{_SUCCESS};margin:0 0 14px;">
          {html.escape(impact["sub"])}
        </div>
        {impact_rows}
        <div style="margin-top:14px;padding-top:12px;border-top:1px solid #f3f4f6;">
          <p style="margin:0 0 8px;font-size:12px;font-weight:700;color:{_PRIMARY};">Submitted parameters</p>
          {param_rows}
        </div>
        """
    )


def render_inflation_summary_card(data: dict[str, Any]) -> None:
    rows = data["status_rows"][:4]
    summary = html.escape(data.get("status_summary", ""))
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:8px;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Direct Delivery</span>
          <span style="font-size:12px;font-weight:700;color:#b45309;">{summary}</span>
        </div>
        {_status_rows_html(rows)}
        """
    )


def render_context_card(data: dict[str, Any]) -> None:
    groups = data.get("param_groups") or []
    card_title = groups[0]["title"] if groups else "Direct Delivery"
    rows = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:6px 0;font-size:12px;'
        f'border-bottom:1px solid #f3f4f6;">'
        f'<span style="color:{_TEXT_MUTED};">{html.escape(r["label"])}</span>'
        f'<span style="color:{_PRIMARY};font-weight:600;">{html.escape(r["value"])}</span></div>'
        for r in data["ctx_rows"]
    )
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">{html.escape(card_title)}</span>
          <span style="display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:0;
            font-size:10px;font-weight:700;background:#ecfdf5;color:#065f46;">
            <span style="width:6px;height:6px;border-radius:0;background:#22c55e;"></span>Live
          </span>
        </div>
        {rows}
        """
    )


# Backward-compatible aliases
inject_simulate_css = inject_css
render_context_bar = render_simulate_context_bar
render_params_header = render_parameter_panel_header
render_param_group = render_parameter_group
render_progress_footer = render_action_bar
render_impact_card = render_summary_card
render_status_cards = render_progress_card
