"""Simulate page — pixel-perfect enterprise dashboard (Figma spec)."""
from __future__ import annotations

import html
import re
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from pages_st.Common_Pages.filter_bar import render_context_filter_bar as _render_context_bar

# Design tokens (Figma simulate form)
_PRIMARY = "#011E41"
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
            border-radius: 8px !important;
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_css() -> None:
    """Inject all simulate-page styles (call once per run)."""
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
            border-radius: 8px !important;
            padding: 14px 20px 10px !important;
            min-height: 70px !important;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        }}
        .sim-step-marker {{ display: none !important; }}

        /* ----- Section 3: Main parameter form card — white bg + row borders (Figma) ----- */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stForm"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stNumberInput"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) .stHtml {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) {{
            background: #ffffff !important;
            border: 1px solid {_BORDER} !important;
            border-radius: 12px !important;
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
            border-radius: 10px !important;
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
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stVerticalBlock"]:not(:has(.sim-param-group-wrap)) {{
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

        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) .sim-panel-header-wrap {{
            background: {_PRIMARY} !important;
            margin: 0 !important;
            padding: 0 !important;
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

        /* Fields block — visually inside the same section card */
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]:has(.sim-group-fields-marker) {{
            margin: 0 !important;
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
            border-radius: 6px !important;
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
            border-radius: 6px !important;
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
            border-radius: 8px !important;
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
            display: inline-block !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            line-height: 1 !important;
            flex-shrink: 0 !important;
            padding: 0 6px 0 2px !important;
            margin: 0 !important;
            white-space: nowrap !important;
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
            border-radius: 8px !important;
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
            border-radius: 8px !important;
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

        /* ----- Sidebar cards — white card surface ----- */
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] {{
            gap: 12px !important;
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
        .block-container:has(#simulate-page) [class*="st-key-sim_side_"] {{
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker) {{
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
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker) .stHtml {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        .sim-side-card-marker,
        .sim-side-submit-marker {{ display: none !important; }}

        /* Streamlit container keys (1.39+) — white section cards */
        .block-container:has(#simulate-page) [class*="st-key-sim_grp_"] {{
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 1px solid {_SECTION_BORDER} !important;
            border-radius: 10px !important;
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

            function paintFramedSideCard(wrapper) {
              wrapper.style.setProperty("background-color", white, "important");
              wrapper.style.setProperty("background", white, "important");
              wrapper.style.setProperty("border", "1px solid #DDE2E9", "important");
              wrapper.style.setProperty("border-radius", "8px", "important");
              wrapper.style.setProperty("padding", "0", "important");
              wrapper.style.setProperty("margin", "0", "important");
              wrapper.style.setProperty("overflow", "hidden", "important");
              wrapper.style.setProperty("box-shadow", "none", "important");
              wrapper.querySelectorAll(
                '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"], .stHtml'
              ).forEach((node) => {
                node.style.setProperty("background-color", white, "important");
                node.style.setProperty("background", white, "important");
                node.style.setProperty("padding", "0", "important");
                node.style.setProperty("margin", "0", "important");
              });
            }
            doc.querySelectorAll('[data-testid="stVerticalBlockBorderWrapper"]').forEach((wrapper) => {
              if (!wrapper.querySelector(".sim-side-card-marker") && !wrapper.querySelector(".sim-side-submit-marker")) return;
              paintFramedSideCard(wrapper);
            });
            doc.querySelectorAll('[class*="st-key-sim_side_impact"], [class*="st-key-sim_side_submit_"]').forEach(paintFramedSideCard);

            doc.querySelectorAll('[class*="st-key-sim_grp_"], [data-testid="stVerticalBlockBorderWrapper"]')
              .forEach((wrapper) => {
                if (!wrapper.querySelector(".sim-param-group-wrap")) return;
                wrapper.style.setProperty("background-color", white, "important");
                wrapper.style.setProperty("background", white, "important");
                wrapper.style.setProperty("border", sectionBorder, "important");
                wrapper.style.setProperty("border-radius", "10px", "important");
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
              });

            doc.querySelectorAll(".sim-num-wrap").forEach((marker) => {
              const col = marker.closest('[data-testid="column"]');
              if (!col) return;
              const box = col.querySelector('[data-testid="stVerticalBlock"]');
              if (!box) return;
              box.style.setProperty("display", "inline-flex", "important");
              box.style.setProperty("flex-direction", "row", "important");
              box.style.setProperty("flex-wrap", "nowrap", "important");
              box.style.setProperty("align-items", "center", "important");
              box.style.setProperty("justify-content", "flex-end", "important");
              box.style.setProperty("background-color", inputBg, "important");
              box.style.setProperty("background", inputBg, "important");
              box.style.setProperty("border", inputBorder, "important");
              box.style.setProperty("border-radius", "8px", "important");
              box.style.setProperty("padding", "0 8px 0 10px", "important");
              box.style.setProperty("min-height", "40px", "important");
              box.style.setProperty("width", "fit-content", "important");
              box.style.setProperty("margin-left", "auto", "important");
              col.querySelectorAll('[data-testid="stElementContainer"]').forEach((ec) => {
                ec.style.setProperty("margin", "0", "important");
                ec.style.setProperty("padding", "0", "important");
                ec.style.setProperty("width", "auto", "important");
                ec.style.setProperty("flex", "0 0 auto", "important");
                ec.style.setProperty("background", "transparent", "important");
              });
              col.querySelectorAll(
                '[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"], [data-testid="stNumberInput"] button'
              ).forEach((btn) => {
                btn.style.setProperty("display", "none", "important");
                btn.style.setProperty("visibility", "hidden", "important");
                btn.style.setProperty("width", "0", "important");
                btn.style.setProperty("pointer-events", "none", "important");
              });
            });

            doc.querySelectorAll('[class*="st-key-sim_reset"] button').forEach((btn) => {
              btn.style.setProperty("background", "#ffffff", "important");
              btn.style.setProperty("color", "#011E41", "important");
              btn.style.setProperty("border", "1px solid #E5E7EB", "important");
              btn.style.setProperty("border-radius", "8px", "important");
              btn.style.setProperty("font-weight", "600", "important");
              btn.style.setProperty("opacity", "1", "important");
            });
            doc.querySelectorAll('[class*="st-key-sim_start"] button').forEach((btn) => {
              btn.style.setProperty("background", "#011E41", "important");
              btn.style.setProperty("color", "#ffffff", "important");
              btn.style.setProperty("border", "none", "important");
              btn.style.setProperty("border-radius", "8px", "important");
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
              row.style.setProperty("padding", "10px 20px", "important");
              const parent = row.closest('[data-testid="stElementContainer"]');
              if (parent) {
                parent.style.setProperty("background", white, "important");
                parent.style.setProperty("background-color", white, "important");
                parent.style.setProperty("width", "100%", "important");
                parent.style.setProperty("max-width", "100%", "important");
                parent.style.setProperty("margin-left", "0", "important");
                parent.style.setProperty("margin-right", "0", "important");
                parent.style.setProperty("padding", "0", "important");
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
                wrapper.style.setProperty("border-radius", "8px", "important");
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
            doc.querySelectorAll(".sim-ctx-live").forEach((chip) => {
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("align-items", "center", "important");
              chip.style.setProperty("gap", "8px", "important");
              chip.style.setProperty("padding", "0 14px", "important");
              chip.style.setProperty("background", white, "important");
              chip.style.setProperty("background-color", white, "important");
              chip.style.setProperty("border", "1px solid #e4eaf2", "important");
              chip.style.setProperty("border-radius", "999px", "important");
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
            f'border-radius:4px;padding:1px 6px;font-size:10px;font-weight:700;">'
            f'{html.escape(t["text"])}</span>'
        )
    return "".join(parts)


def _param_count(group: dict[str, Any]) -> str:
    n = len(group.get("fields", []))
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
_STATUS_LABELS = (
    ("DD% (1 field)", 0),
    ("Inflation (4 fields)", 1),
    ("SWC (2 fields)", 2),
    ("Project costs", 3),
)


def _saved_key(index: int) -> str:
    return f"sim_saved_{index}"


def _field_key(group_index: int, field_index: int) -> str:
    return f"sim_f_{group_index}_{field_index}"


def _apply_pending_reset(groups: list[dict[str, Any]]) -> None:
    """Clear widget keys before any inputs render (Streamlit cannot reset after instantiate)."""
    if not st.session_state.pop(_RESET_KEY, False):
        return
    st.session_state[_SIM_RUN_KEY] = False
    st.session_state.pop(_SIM_SNAPSHOT_KEY, None)
    st.session_state.pop(_SIM_HISTORY_KEY, None)
    for i, group in enumerate(groups):
        st.session_state[_saved_key(i)] = False
        st.session_state.pop(f"sim_open_{i}", None)
        for fi, _field in enumerate(group.get("fields", [])):
            key = _field_key(i, fi)
            st.session_state.pop(key, None)
            st.session_state.pop(f"_{key}", None)


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


def _count_saved_fields(groups: list[dict[str, Any]]) -> tuple[int, int]:
    """Return (saved_field_count, total_field_count) across groups with inputs."""
    total = 0
    saved = 0
    for i, group in enumerate(groups):
        fields = group.get("fields", [])
        total += len(fields)
        if _group_is_saved(i):
            saved += len(fields)
    return saved, total


def _compute_progress(groups: list[dict[str, Any]]) -> dict[str, Any]:
    saved_groups = sum(1 for i in range(len(groups)) if _group_is_saved(i))
    total_groups = len(groups)
    saved_fields, total_fields = _count_saved_fields(groups)
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
            n = len(group["fields"])
            rows.append({"name": label, "pill": "partial", "pill_text": f"0 / {n}"})
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
    for fi, field in enumerate(group.get("fields", [])):
        key = _field_key(index, fi)
        fields.append({
            "name": field["name"],
            "value": st.session_state.get(key, field["value"]),
            "suffix": field.get("suffix") or "",
        })
    return {
        "title": group["title"],
        "status_summary": _status_summary(groups),
        "status_rows": build_status_rows(groups),
        "fields": fields,
    }


def _on_save_group(index: int, group: dict[str, Any], groups: list[dict[str, Any]]) -> None:
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
            key = _field_key(i, fi)
            rows.append({
                "group": group["title"],
                "name": field["name"],
                "value": st.session_state.get(key, field["value"]),
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
                f'<div style="width:28px;height:28px;border-radius:50%;background:{_SUCCESS};'
                f'color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;'
                f'font-size:13px;font-weight:700;">✓</div>'
            )
            color = _SUCCESS
        elif st_state == "current":
            circle = (
                f'<div style="width:28px;height:28px;border-radius:50%;background:{_PRIMARY};'
                f'color:#fff;margin:0 auto;display:flex;align-items:center;justify-content:center;'
                f'font-size:12px;font-weight:700;">{i + 1}</div>'
            )
            color = _PRIMARY
        else:
            circle = (
                f'<div style="width:28px;height:28px;border-radius:50%;border:2px solid #d1d5db;'
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
            f'<div style="background:{_SUCCESS};border-radius:8px;color:#fff;font-size:12px;'
            f'font-weight:700;padding:8px 14px;white-space:nowrap;flex-shrink:0;'
            f'display:inline-flex;align-items:center;gap:6px;">'
            f'<span style="font-size:14px;">✓</span> All saved</div>'
        )
    elif saved_g:
        saved_badge = (
            f'<div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);'
            f'border-radius:8px;color:#e2e8f0;font-size:12px;font-weight:600;padding:8px 14px;'
            f'white-space:nowrap;flex-shrink:0;">{saved_g}/{len(groups)} sections saved</div>'
        )
    else:
        saved_badge = (
            f'<div style="background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.3);'
            f'border-radius:8px;color:#e2e8f0;font-size:12px;font-weight:600;padding:8px 14px;'
            f'white-space:nowrap;flex-shrink:0;">Edit parameters freely</div>'
        )
    pills = "".join(
        f'<span style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.22);'
        f'border-radius:6px;padding:6px 12px;font-size:11px;font-weight:600;color:#fff;'
        f'white-space:nowrap;">{html.escape(p)}</span>'
        for p in data["context_pills"]
    )
    _html(
        f"""
        <div class="sim-panel-header-wrap" style="background:{_PRIMARY};padding:22px 20px 18px;
            display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
          <div style="min-width:0;">
            <h2 style="margin:0 0 8px;font-size:22px;font-weight:700;color:#fff;line-height:1.2;">
              {html.escape(data["params_title"])}
            </h2>
            <p style="margin:0 0 14px;font-size:13px;color:rgba(203,213,225,0.95);line-height:1.4;">
              {html.escape(data["params_sub"])}
            </p>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">{pills}</div>
          </div>
          {saved_badge}
        </div>
        """
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
              <div style="width:44px;height:44px;background:{_ICON_BG};border-radius:8px;
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


def render_parameter_group_fields(group: dict[str, Any], index: int) -> None:
    """Parameter rows inside st.form — st.number_input per Figma."""
    if not _group_is_open(index, group):
        return

    st.markdown('<span class="sim-group-fields-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    fields = group.get("fields", [])
    if fields:
        for fi, field in enumerate(fields):
            if fi > 0:
                st.markdown('<hr class="sim-row-divider" aria-hidden="true" />', unsafe_allow_html=True)
            _render_parameter_field(field, index, fi)
    elif "Project" in group.get("title", ""):
        st.markdown('<hr class="sim-row-divider" aria-hidden="true" />', unsafe_allow_html=True)
        st.markdown('<span class="sim-field-row-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="margin:0;padding:20px;font-size:13px;color:#2563eb;font-weight:600;background:#fff;">'
            f'{html.escape(group.get("expander_hint", "+ Show all 16 categories"))}</p>',
            unsafe_allow_html=True,
        )


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
    lock_hint = (
        '<p style="margin:4px 0 0;font-size:10px;color:#16a34a;font-weight:600;">'
        "Locked — click Reset to edit</p>"
        if locked
        else ""
    )
    st.markdown('<span class="sim-field-row-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    col_l, col_r = st.columns([5.2, 1.5], vertical_alignment="center")
    with col_l:
        _html(
            f'<p style="margin:0 0 4px;font-size:13px;font-weight:700;color:{_PRIMARY};">'
            f'{html.escape(field["name"])}{tags}</p>'
            f'<p style="margin:0;font-size:11px;color:{_TEXT_MUTED};line-height:1.4;">{html.escape(field["desc"])}</p>'
            f"{lock_hint}"
        )
    with col_r:
        st.markdown('<span class="sim-num-wrap"></span>', unsafe_allow_html=True)
        suffix = field.get("suffix") or ""
        if field.get("max") is not None and field.get("step") is None:
            kwargs: dict[str, Any] = {
                "min_value": int(field.get("min") or 0),
                "max_value": int(field.get("max") or 100),
                "step": 1,
                "key": key,
                "label_visibility": "collapsed",
                "disabled": locked,
            }
            if key not in st.session_state:
                kwargs["value"] = int(field["value"])
            st.number_input("v", **kwargs)
        else:
            kwargs = {
                "step": float(field.get("step") or 0.1),
                "format": "%.1f",
                "key": key,
                "label_visibility": "collapsed",
                "disabled": locked,
            }
            if key not in st.session_state:
                kwargs["value"] = float(field["value"])
            st.number_input("v", **kwargs)
        if suffix:
            st.markdown(
                f'<span class="sim-pct-suffix" aria-hidden="true">{html.escape(suffix)}</span>',
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
                  <div style="height:10px;background:{_BORDER};border-radius:999px;overflow:hidden;">
                    <div style="height:100%;width:{pct}%;background:{_PRIMARY};border-radius:999px;"></div>
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

def _side_card(inner_html: str, *, card_key: str = "sim_side_card", submit: bool = False) -> None:
    try:
        box = st.container(key=card_key)
    except TypeError:
        box = st.container()
    with box:
        markers = (
            '<span class="sim-side-submit-marker" aria-hidden="true"></span>'
            if submit
            else '<span class="sim-side-card-marker" aria-hidden="true"></span>'
        )
        st.markdown(markers, unsafe_allow_html=True)
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
            <span style="width:8px;height:8px;border-radius:2px;background:{_SQ.get(r["sq"], "#94a3b8")};"></span>
            {html.escape(r["name"])}
          </span>
          <span style="font-weight:700;color:{_VAL.get(r.get("value_class","neutral"), _TEXT)};">
            {html.escape(r["value"])}
          </span>
        </div>
        """
        for r in impact["rows"]
    )


def render_live_impact_card(data: dict[str, Any]) -> None:
    """Top sidebar card — live totals for Direct Delivery, inflation, etc."""
    impact = data["impact"]
    note = html.escape(impact.get("note", ""))
    sub = impact.get("sub", "")
    sub_color = _SUCCESS if sub.strip().startswith("+") else _TEXT_MUTED
    _side_card(
        f"""
        <div style="display:flex;align-items:center;justify-content:space-between;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Live impact preview</span>
          <span style="display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:999px;
            font-size:10px;font-weight:700;background:#fef3c7;color:#b45309;">✦ Real-time</span>
        </div>
        <div style="padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;">
          <div style="background:#f8fafc;border-radius:8px;padding:14px 12px;">
            <div style="font-size:32px;font-weight:800;color:{_DANGER};margin:0 0 6px;line-height:1.1;">
              {html.escape(impact["headline"])}
            </div>
            <div style="font-size:11px;font-weight:600;color:{sub_color};margin:0 0 10px;">
              {html.escape(sub)}
            </div>
            <div style="font-size:10px;color:#9ca3af;line-height:1.45;">{note}</div>
          </div>
        </div>
        {_impact_breakdown_html(impact, sectioned=True)}
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
            font-size:11px;font-weight:700;padding:3px 10px;border-radius:999px;">
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


def render_submission_history_cards() -> None:
    """Stack a card below live impact for each section Save."""
    history: list[dict[str, Any]] = st.session_state.get(_SIM_HISTORY_KEY) or []
    for index, entry in enumerate(history):
        render_section_submission_card(entry, index)


def render_simulate_sidebar(data: dict[str, Any], groups: list[dict[str, Any]]) -> None:
    """Right column — live impact on top, submitted section cards below."""
    st.markdown('<span class="sim-sidebar-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    render_live_impact_card(data)
    render_submission_history_cards()


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
            <span style="width:8px;height:8px;border-radius:2px;background:{_SQ.get(r["sq"], "#94a3b8")};"></span>
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
          <span style="display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:999px;
            font-size:10px;font-weight:700;background:#ecfdf5;color:#065f46;">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></span>Submitted
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
          <span style="display:inline-flex;align-items:center;gap:6px;padding:2px 10px;border-radius:999px;
            font-size:10px;font-weight:700;background:#ecfdf5;color:#065f46;">
            <span style="width:6px;height:6px;border-radius:50%;background:#22c55e;"></span>Live
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
