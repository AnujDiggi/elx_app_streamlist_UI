"""Reusable compact filter dropdown — single styled select (value only)."""
from __future__ import annotations

import html
import inspect
from typing import TYPE_CHECKING

import streamlit as st
import streamlit.components.v1 as components

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

_CSS_INJECTED = False
_JS_INJECTED = False
_SIM_CTX_CSS_INJECTED = False
_CTX_BAR_WIDGET_VERSION = 2
_SELECTBOX_SUPPORTS_FILTER_MODE = "filter_mode" in inspect.signature(st.selectbox).parameters
_FILTER_H = 32
_FILTER_CTX_H = 36
_CTX_FILTER_MIN_W = 50
_CTX_FILTER_W = 65
_PANEL_HEADER_FILTER_GAP = "2px"
PANEL_HEADER_DD_WIDTH = "75%"
PRESET_OPTIONS: dict[str, list[str]] = {
    "Area": ["FR10", "FR20", "EA1", "DE01"],
    "Period": ["Jan", "EA2 · 2026", "EA1 · 2025", "EA2 · 2027"],
    "FADP": ["BC04", "BC03", "BC05"],
    "Category": ["All", "STC", "PTC", "Warehouse"],
    "Bucket": ["All buckets", "Fixed", "Variable"],
    "Scenario": ["Base Case", "Optimistic", "Pessimistic"],
    "Country": [
        "🇫🇷 FR10 — France",
        "🇪🇸 ES10 — Spain",
        "🇮🇹 IT16 — Italy",
        "🇵🇹 PT10 — Portugal",
    ],
    "Year": [
        "📅 EA1 · 2026",
        "📅 EA2 · 2026",
        "📅 EA1 · 2025",
        "📅 EA2 · 2027",
    ],
    "Business Area": ["Europe", "Americas", "APAC", "MEA"],
    "Commercial Area": ["ATED", "EMEA", "NAFTA", "LATAM"],
    "Panel Period": ["BC 202601", "BC 202512", "BC 202511", "BC 202510"],
    "Panel Company": ["FR10", "ES10", "IT16", "PT10"],
}


def inject_filter_select_css() -> None:
    """Inject styles once per session."""
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return
    _CSS_INJECTED = True
    h = _FILTER_H
    st.markdown(
        f"""
        <style>
        /* Dashboard compact row — value only (not simulate labeled filters) */
        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)):not(:has(.elx-filter-panel)) {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: {h}px !important;
            min-height: {h}px !important;
            max-height: {h}px !important;
            overflow: hidden !important;
            align-self: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)):not(:has(.elx-filter-panel)) > div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
            gap: 0 !important;
            justify-content: center !important;
            align-items: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-panel)) [data-testid="stSelectbox"] {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-panel)) div[data-baseweb="select"] {{
            width: 100% !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) {{
            min-width: 0 !important;
            overflow: visible !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) > div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) [data-testid="stSelectbox"],
        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"],
        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div {{
            width: 100% !important;
            min-width: 0 !important;
            max-width: 100% !important;
            overflow: visible !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div {{
            background-color: #E9EDF5 !important;
            border: 1px solid #D4DBE6 !important;
            border-radius: 8px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #4B5563 !important;
            box-shadow: none !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div > div,
        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] span,
        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] p {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            text-align: left !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: none !important;
            min-height: {h}px !important;
            height: {h}px !important;
            padding: 0 28px 0 10px !important;
            color: #4B5563 !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            line-height: 1 !important;
            overflow: visible !important;
            text-overflow: unset !important;
            white-space: nowrap !important;
        }}

        [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] svg {{
            fill: #6B7280 !important;
            color: #6B7280 !important;
        }}

        /* Simulate panel header — labeled navy dropdowns */
        [data-testid="column"]:has(.elx-filter-panel-labeled) > div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
            gap: 4px !important;
        }}
        [data-testid="column"]:has(.elx-filter-panel-labeled) .elx-filter-upper-lbl,
        [class*="st-key-sim_panel_header_wrap"] .elx-filter-upper-lbl,
        [class*="st-key-sim_panel_header_wrap"] .elx-filter-panel-lbl,
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl),
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stMarkdownContainer"]:has(.elx-filter-upper-lbl) p {{
            display: block !important;
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            letter-spacing: 0 !important;
            text-transform: none !important;
            margin: 0 0 4px 2px !important;
            padding: 0 !important;
            line-height: 1.3 !important;
            white-space: nowrap !important;
            opacity: 1 !important;
            visibility: visible !important;
        }}
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.22) !important;
            border-radius: 4px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #ffffff !important;
            box-shadow: none !important;
        }}
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] > div > div,
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] span,
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] p,
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {{
            color: #ffffff !important;
            font-size: 11px !important;
            font-weight: 600 !important;
        }}
        [data-testid="column"]:has(.elx-filter-panel-labeled) div[data-baseweb="select"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
        }}

        .sim-panel-filters-row-marker {{
            display: none !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] {{
            gap: {_PANEL_HEADER_FILTER_GAP} !important;
            justify-content: flex-start !important;
            width: auto !important;
            max-width: 100% !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
            flex: 0 0 auto !important;
            flex-grow: 0 !important;
            flex-shrink: 0 !important;
            width: auto !important;
            max-width: fit-content !important;
            min-width: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"]:has(.elx-filter-panel) {{
            gap: {_PANEL_HEADER_FILTER_GAP} !important;
            justify-content: flex-start !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"]:has(.elx-filter-panel) > [data-testid="column"] {{
            flex: 0 0 auto !important;
            flex-grow: 0 !important;
            flex-shrink: 0 !important;
            width: auto !important;
            max-width: fit-content !important;
            min-width: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) > div[data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
            width: auto !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) > div[data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
            width: 100% !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) [data-testid="stSelectbox"],
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"],
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.12) !important;
            border: 1px solid rgba(255, 255, 255, 0.22) !important;
            border-radius: 4px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #ffffff !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] > div > div,
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] span,
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] p,
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {{
            color: #ffffff !important;
            font-size: 11px !important;
            font-weight: 600 !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"]:has(input:disabled) > div,
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"] div[data-baseweb="select"][aria-disabled="true"] > div {{
            opacity: 0.55 !important;
            cursor: not-allowed !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)):not(:has(.elx-filter-panel)) div[data-baseweb="select"] > div {{
            background-color: #F8F9FC !important;
            border: 1px solid #D8DCE7 !important;
            border-radius: 4px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #011E41 !important;
            box-shadow: none !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)):not(:has(.elx-filter-panel)) div[data-baseweb="select"] > div > div {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
            min-height: {h}px !important;
            height: {h}px !important;
            padding: 0 28px 0 10px !important;
            color: #011E41 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            line-height: 1 !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)):not(:has(.elx-filter-panel)) div[data-baseweb="select"] span {{
            color: #011E41 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-align: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-panel)) div[data-baseweb="select"] svg {{
            fill: #011E41 !important;
            color: #011E41 !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) .elx-filter-slot {{
            display: none !important;
        }}

        /* Select-only dropdowns — pointer cursor, no text caret */
        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"],
        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] > div,
        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] input {{
            cursor: pointer !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] input {{
            caret-color: transparent !important;
            user-select: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_filter_select_js() -> None:
    """Lock filter dropdowns to select-only and apply pointer cursor (older Streamlit fallback)."""
    global _JS_INJECTED
    if _JS_INJECTED:
        return
    _JS_INJECTED = True
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent?.document || document;
          function lockFilterSelects() {
            doc.querySelectorAll(
              '[data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"]'
            ).forEach((selectRoot) => {
              selectRoot.style.setProperty("cursor", "pointer", "important");
              const trigger = selectRoot.querySelector(":scope > div");
              if (trigger) trigger.style.setProperty("cursor", "pointer", "important");
            });
            doc.querySelectorAll(
              '[data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] input'
            ).forEach((input) => {
              input.setAttribute("readonly", "true");
              input.setAttribute("inputmode", "none");
              input.style.setProperty("cursor", "pointer", "important");
              input.style.setProperty("caret-color", "transparent", "important");
              if (input.dataset.elxSelectGuard) return;
              input.dataset.elxSelectGuard = "1";
              input.addEventListener("keydown", (e) => {
                const nav = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Enter", "Escape", "Tab", "Home", "End"];
                if (nav.includes(e.key)) return;
                if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) e.preventDefault();
                if (e.key === "Backspace" || e.key === "Delete") e.preventDefault();
              });
            });
          }
          lockFilterSelects();
          const obs = new MutationObserver(lockFilterSelects);
          if (doc.body) obs.observe(doc.body, { childList: true, subtree: true });
        })();
        </script>
        """,
        height=0,
    )


def _format_live_chip_text(live_label: str) -> str:
    """Normalize live chip copy to 'Live · Databricks Delta Lake' style."""
    text = (live_label or "").strip()
    if not text:
        return "Live"
    if text.lower().startswith("live"):
        rest = text[4:].lstrip(" ·.-—:")
        if rest:
            return f"Live · {html.escape(rest)}"
        return "Live"
    return html.escape(text)


def inject_simulate_context_css() -> None:
    """Simulate CONTEXT bar — white full-bleed row + labeled filter_select (Figma)."""
    inject_filter_select_css()
    h = _FILTER_CTX_H
    st.markdown(
        f"""
        <style>
        .sim-ctx-marker {{
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}

        section.main:has(.sim-ctx-marker),
        [data-testid="stAppViewContainer"]:has(.sim-ctx-marker),
        [data-testid="stMainBlockContainer"]:has(.sim-ctx-marker) {{
            overflow-x: visible !important;
            max-width: 100% !important;
        }}

        [data-testid="stElementContainer"]:has(.sim-ctx-outer-marker),
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) {{
            background: #ffffff !important;
            background-color: #ffffff !important;
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 0 !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) {{
            background: #ffffff !important;
            background-color: #ffffff !important;
            border-bottom: 1px solid #e4eaf2 !important;
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 12px 20px 10px !important;
            min-height: 58px !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 12px !important;
            overflow: visible !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:has(.sim-ctx-left-group),
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:first-child {{
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: none !important;
            overflow: visible !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:has(.sim-ctx-live-col),
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:last-child {{
            flex: 1 1 0 !important;
            width: auto !important;
            min-width: 0 !important;
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
            align-self: center !important;
            overflow: visible !important;
            margin-left: auto !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:last-child > div[data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) > [data-testid="column"]:has(.sim-ctx-live-col) > div[data-testid="stVerticalBlock"] {{
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .sim-ctx-outer-marker,
        .sim-ctx-left-group,
        .sim-ctx-live-col {{
            display: none !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) {{
            background: transparent !important;
            border-bottom: none !important;
            box-sizing: border-box !important;
            width: auto !important;
            max-width: none !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: flex-end !important;
            gap: 12px !important;
            overflow: visible !important;
        }}

        [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(.sim-ctx-marker)),
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"] {{
            overflow: visible !important;
        }}

        .block-container:has(#simulate-page) [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-ctx-outer-marker),
        .block-container:has(#simulate-page) [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-ctx-marker) {{
            background: #ffffff !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            overflow: visible !important;
            background: transparent !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) [data-testid="stVerticalBlock"] > div {{
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }}

        .sim-ctx-title {{
            font-size: 11px; font-weight: 700; color: #6b7280;
            letter-spacing: 0.08em; text-transform: uppercase;
            white-space: nowrap; margin: 0; line-height: 1;
        }}
        .sim-ctx-vdiv {{
            width: 1px; height: 40px; background: #e4eaf2; margin: 0 auto;
        }}
        .sim-ctx-live,
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) .sim-ctx-live {{
            display: inline-flex !important;
            align-items: center !important;
            gap: 8px !important;
            height: {h}px !important;
            padding: 0 14px !important;
            background: #ffffff !important;
            background-color: #ffffff !important;
            border: 1px solid #e4eaf2 !important;
            border-radius: 999px !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            color: #011e41 !important;
            white-space: nowrap !important;
            box-shadow: none !important;
        }}
        .sim-ctx-live .dot,
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) .sim-ctx-live .dot {{
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
            background: #22c55e !important;
            flex-shrink: 0 !important;
            display: inline-block !important;
        }}

        /* Labeled filter_select inside CONTEXT bar */
        [data-testid="column"]:has(.elx-filter-labeled):has(.elx-filter-dd) {{
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            align-self: flex-end !important;
        }}

        [data-testid="column"]:has(.elx-filter-labeled) > div[data-testid="stVerticalBlock"] {{
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            overflow: visible !important;
            gap: 4px !important;
        }}

        [data-testid="stElementContainer"]:has(.elx-filter-upper-lbl),
        [data-testid="stElementContainer"]:has(.elx-filter-upper-lbl) [data-testid="stMarkdownContainer"] {{
            overflow: visible !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"]:has(.sim-ctx-title-wrap),
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"]:has(.sim-ctx-vdiv-wrap),
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) > [data-testid="column"]:has(.elx-filter-ctx) {{
            flex: 0 0 auto !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: none !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx),
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) {{
            height: auto !important; min-height: 0 !important; max-height: none !important;
            min-width: {_CTX_FILTER_MIN_W}px !important;
            max-width: {_CTX_FILTER_W}px !important;
            flex: 0 0 {_CTX_FILTER_W}px !important;
            align-self: flex-end !important; overflow: visible !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) [data-testid="stSelectbox"],
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] {{
            width: 100% !important;
            max-width: {_CTX_FILTER_W}px !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-labeled) div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) > [data-testid="stVerticalBlock"] {{
            width: 100% !important; gap: 4px !important; margin: 0 !important; padding: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) .elx-filter-upper-lbl,
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) .elx-filter-upper-lbl {{
            display: block !important;
            font-size: 10px !important;
            font-weight: 700 !important;
            color: #6b7280 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            margin: 0 0 4px 2px !important;
            padding: 0 !important;
            line-height: 1.3 !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) [data-testid="stSelectbox"] {{
            margin: 0 !important;
            padding: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"],
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] > div,
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] > div > div {{
            background-color: #ffffff !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] > div {{
            border: 1px solid #d8dce7 !important;
            border-radius: 4px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #011e41 !important;
            box-shadow: none !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] > div > div {{
            justify-content: flex-start !important;
            text-align: left !important;
            padding: 0 30px 0 12px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] span {{
            color: #011e41 !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            text-align: left !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] svg {{
            fill: #011e41 !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-outer-marker) .sim-ctx-live {{
            margin-left: 0 !important;
            margin-right: 0 !important;
        }}

        /* Flush white CONTEXT bar directly under navy navbar */
        .block-container:has(#simulate-page) [data-testid="stVerticalBlock"] {{
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
            + [data-testid="stElementContainer"]:has([data-testid="stHorizontalBlock"]:has(.sim-ctx-marker)) {{
            margin-top: 0 !important;
            padding-top: 0 !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_page_body"],
        .block-container:has(#simulate-page) [class*="st-key-sim_page_body"] [data-testid="stVerticalBlockBorderWrapper"] {{
            margin-top: 0 !important;
            padding-top: 0 !important;
            border-top: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_simulate_context_bar(
    context_rows: list[dict[str, str]],
    live_label: str,
    *,
    page_marker: bool = True,
) -> dict[str, str]:
    """Figma CONTEXT row: left group (label + filters) | right live chip."""
    if not context_rows:
        return {}

    inject_simulate_context_css()

    n = len(context_rows)
    outer_left, outer_right = st.columns([1, 1], gap="small", vertical_alignment="center")
    outer_left.markdown('<span class="sim-ctx-outer-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    outer_left.markdown('<span class="sim-ctx-left-group" aria-hidden="true"></span>', unsafe_allow_html=True)

    inner_ratios = [0.35, 0.02] + [0.38] * n
    inner = outer_left.columns(inner_ratios, gap="small", vertical_alignment="center")

    page_id = ' id="simulate-page"' if page_marker else ""
    inner[0].markdown(
        f'<span{page_id} class="sim-ctx-marker sim-ctx-title-wrap" aria-hidden="true"></span>'
        '<div class="sim-ctx-title">CONTEXT:</div>',
        unsafe_allow_html=True,
    )
    # inner[1].markdown(
    #     '<span class="sim-ctx-vdiv-wrap" aria-hidden="true"></span>'
    #     '<div class="sim-ctx-vdiv" aria-hidden="true"></div>',
    #     unsafe_allow_html=True,
    # )

    results: dict[str, str] = {}
    presets = {"Area", "Period", "FADP", "Scenario"}
    for i, row in enumerate(context_rows):
        k = row["key"]
        state_key = f"sim_ctx_{k}"
        ver_key = f"_{state_key}_wver"
        if st.session_state.get(ver_key) != _CTX_BAR_WIDGET_VERSION:
            st.session_state.pop(state_key, None)
            st.session_state[ver_key] = _CTX_BAR_WIDGET_VERSION
        results[k] = filter_select(
            k,
            state_key,
            preset=k if k in presets else None,
            default=None,
            parent=inner[2 + i],
            label_above=k.upper(),
            context_bar=True,
        )

    live = _format_live_chip_text(live_label)
    outer_right.markdown('<span class="sim-ctx-live-col" aria-hidden="true"></span>', unsafe_allow_html=True)
    outer_right.markdown(
        f'<div class="sim-ctx-live"><span class="dot" aria-hidden="true"></span>{live}</div>',
        unsafe_allow_html=True,
    )
    return results


def resolve_options(
    options: list[str] | None,
    *,
    preset: str | None = None,
    default: str | None = None,
) -> list[str]:
    """Build option list from explicit options and/or a named preset."""
    if options:
        opts = list(options)
    elif preset:
        opts = list(PRESET_OPTIONS.get(preset, []))
    else:
        opts = []

    if default and default not in opts:
        opts.insert(0, default)
    if not opts and default:
        opts = [default]
    return opts


def filter_select(
    field_name: str,
    key: str,
    *,
    options: list[str] | None = None,
    preset: str | None = None,
    default: str | None = None,
    placeholder: str | None = "— Select —",
    disabled: bool = False,
    on_change=None,
    parent: DeltaGenerator | None = None,
    label_above: str | None = None,
    context_bar: bool = False,
    panel_header: bool = False,
    option_map: dict[str, str] | None = None,
) -> str:
    """One compact dropdown showing the selected value only (Figma top row).

    ``field_name`` is kept for API compatibility (used in presets). With
    ``label_above``, renders a small uppercase label over the control (simulate CONTEXT bar).

    When ``option_map`` is provided, keys are stored in session state and values
    are shown in the dropdown (e.g. country_cd → country name).

    Args:
        field_name: Preset key / logical name (e.g. ``"Category"``).
        key: Unique Streamlit session key.
        options: Values in the menu.
        preset: Named list in ``PRESET_OPTIONS``.
        default: Initial value.
        parent: Column/container to render into.
        option_map: Stored value → display label mapping.

    Returns:
        Selected value string (stored key when ``option_map`` is used).
    """
    inject_filter_select_css()
    inject_filter_select_js()

    format_func = None
    if option_map:
        value_opts = list(option_map.keys())
        format_func = lambda v, m=option_map: m.get(v, v)
    else:
        value_opts = resolve_options(options, preset=preset, default=default)

    opts = list(value_opts)
    if not opts and not option_map:
        raise ValueError("filter_select requires options, a valid preset with a default, or option_map")

    if placeholder:
        opts = [placeholder, *[o for o in opts if o != placeholder]]

    if key not in st.session_state:
        if default is not None and default in opts:
            st.session_state[key] = default
        elif placeholder:
            st.session_state[key] = placeholder
        else:
            st.session_state[key] = opts[0]

    selected = str(st.session_state[key])
    if option_map:
        name_to_cd = {v: k for k, v in option_map.items()}
        if selected in name_to_cd:
            st.session_state[key] = name_to_cd[selected]
            selected = name_to_cd[selected]
    if selected not in opts:
        opts = [selected, *opts]

    target = parent if parent is not None else st
    if panel_header:
        panel_cls = "elx-filter-panel elx-filter-panel-labeled" if label_above else "elx-filter-panel"
        target.markdown(f'<span class="{panel_cls}" aria-hidden="true"></span>', unsafe_allow_html=True)
    if context_bar or (label_above and not panel_header):
        target.markdown('<span class="elx-filter-ctx elx-filter-labeled" aria-hidden="true"></span>', unsafe_allow_html=True)
    if label_above:
        if panel_header:
            target.markdown(
                f'<div class="elx-filter-upper-lbl elx-filter-panel-lbl" '
                f'style="color:#ffffff;display:block;font-size:11px;font-weight:600;'
                f'margin:0 0 4px 2px;line-height:1.3;white-space:nowrap;">'
                f'{html.escape(label_above)}</div>',
                unsafe_allow_html=True,
            )
        else:
            target.markdown(
                f'<div class="elx-filter-upper-lbl">{html.escape(label_above)}</div>',
                unsafe_allow_html=True,
            )
    target.markdown('<span class="elx-filter-dd" aria-hidden="true"></span>', unsafe_allow_html=True)
    select_kwargs: dict = {
        "options": opts,
        "index": opts.index(selected),
        "key": key,
        "label_visibility": "collapsed",
        "disabled": disabled,
    }
    if format_func is not None:
        select_kwargs["format_func"] = format_func
    if on_change is not None:
        select_kwargs["on_change"] = on_change
    if _SELECTBOX_SUPPORTS_FILTER_MODE:
        select_kwargs["filter_mode"] = None
    target.selectbox("\u200b", **select_kwargs)

    return str(st.session_state[key])


def filter_select_row(
    specs: list[dict[str, str]],
    *,
    key_prefix: str = "filter",
    parent_columns: list[DeltaGenerator] | None = None,
) -> dict[str, str]:
    """Render filters from dashboard DB rows ``{"key", "value"}``."""
    results: dict[str, str] = {}
    for i, spec in enumerate(specs):
        fk = spec["key"]
        parent = parent_columns[i] if parent_columns else None
        state_key = f"{key_prefix}_{i}"
        results[fk] = filter_select(
            fk,
            state_key,
            preset=fk,
            default=spec.get("value"),
            parent=parent,
            label_above=spec.get("label"),
        )
    return results
