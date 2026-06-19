"""Simulate page — pixel-perfect enterprise dashboard (Figma spec)."""
from __future__ import annotations

import html
import json
import re
from functools import partial
from typing import Any
from urllib.parse import quote, unquote

import streamlit as st
import streamlit.components.v1 as components

import db_st
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
_SIDE_CARD_RADIUS = "12px"
_SIDE_CARD_GAP = "12px"
_SIDE_PANEL_W = 330
_MAIN_COL_GAP = "16px"
_SUBMIT_SECTION_PAD = "8px 12px"
_INPUT_BG = "#F9F9F9"
_INPUT_BORDER = "#D4DBE6"
_INPUT_RADIUS = "8px"
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

_INFL_CSS_VERSION = 52
_INFL_CALC_CAPTION_COLOR = "#021632"
_PCT_CHIP_MIN_W = "76px"
_PCT_CHIP_MAX_W = "100px"
_PCT_CHIP_H = "40px"
_PCT_CHIP_PAD = "0 10px"
_PCT_CHIP_GAP = "4px"
_PC_CHIP_MIN_W = "84px"
_PC_CHIP_MAX_W = "108px"
_PC_CHIP_H = "36px"
_PC_TOTAL_ROW_H = "44px"
_PC_TOTAL_BG = "#D4DFE9"
_INFL_PCT_CHIP_MIN_W = _PCT_CHIP_MIN_W
_INFL_PCT_CHIP_MAX_W = _PCT_CHIP_MAX_W

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
_PANEL_HEADER_FILTER_PAD = "0 16px 16px 16px"
_PANEL_PLAN_BTN_TEXT = "#70737B"
_PANEL_PLAN_BTN_TEXT_ENABLED = "#ffffff"
_PANEL_PLAN_BTN_TEXT_ACTIVE = "#ffffff"
_PANEL_PLAN_BTN_BG_DISABLED = "#CBCBCB1A"
_PANEL_PLAN_BTN_BG_ENABLED = "#FFFFFF1A"
_SCOPE_ROOT_PLACEHOLDER = "— Select category —"
_SCOPE_DRILL_KEY = "sim_panel_scope_drill"
_SCOPE_VALUE_KEY = "sim_panel_scope_value"
_SCOPE_INIT_KEY = "sim_panel_scope_initialized"
_SCOPE_PICK_QP = "scope_pick"

_PANEL_FILTER_PLACEHOLDER = "— Select —"
_PANEL_PERIOD_KEY = "sim_panel_period"
_PANEL_PLANNING_LEVEL_KEY = "sim_panel_planning_level"
_PANEL_FILTERS_VER_KEY = "sim_panel_filters_ver"
_PANEL_FILTERS_VERSION = 3
_PANEL_HEADER_FILTERS: tuple[dict[str, Any], ...] = (
    {"label": "Period", "key": "sim_panel_period", "preset": "Panel Period", "requires_period": False},
    {"label": "Business Area", "key": "sim_panel_business_area", "preset": "Business Area", "requires_period": True},
    {"label": "Commercial Area", "key": "sim_panel_commercial_area", "preset": "Commercial Area", "requires_period": True},
    {"label": "Country", "key": "sim_panel_country", "preset": "Panel Country", "requires_period": True},
    {"label": "Company", "key": "sim_panel_company", "preset": "Panel Company", "requires_period": True},
)
_PLANNING_FILTER_KEYS: tuple[str, ...] = tuple(
    spec["key"] for spec in _PANEL_HEADER_FILTERS if spec.get("requires_period")
)
_PANEL_PLANNING_SPECS: tuple[dict[str, Any], ...] = tuple(
    spec for spec in _PANEL_HEADER_FILTERS if spec.get("requires_period")
)
_PANEL_COMPANY_KEY = "sim_panel_company"
_DELIVERY_MIX_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("business_area", "sim_panel_business_area"),
    ("commercial_area", "sim_panel_commercial_area"),
    ("country", "sim_panel_country"),
    ("company", "sim_panel_company"),
)
_DM_PCT_FIELD: dict[str, Any] = {
    "value": 0,
    "min": 0,
    "max": 100,
    "step": None,
    "suffix": "%",
}


def _panel_period_selected() -> bool:
    val = str(st.session_state.get(_PANEL_PERIOD_KEY, _PANEL_FILTER_PLACEHOLDER)).strip()
    if not val:
        return False
    placeholders = {_PANEL_FILTER_PLACEHOLDER, "-- Select --", "- Select -"}
    return val not in placeholders


def _panel_company_selected() -> bool:
    return bool(_panel_filter_value(_PANEL_COMPANY_KEY))


def _reset_dependent_panel_filters() -> None:
    st.session_state[_PANEL_PLANNING_LEVEL_KEY] = ""
    for spec in _PANEL_HEADER_FILTERS:
        if spec.get("requires_period"):
            st.session_state[spec["key"]] = _PANEL_FILTER_PLACEHOLDER


def _on_panel_period_changed() -> None:
    if not _panel_period_selected():
        _reset_dependent_panel_filters()


def _planning_level_spec(key: str) -> dict[str, Any] | None:
    for spec in _PANEL_PLANNING_SPECS:
        if spec["key"] == key:
            return spec
    return None


def _active_planning_level_key() -> str | None:
    """Which planning-level button is active (Business Area / Country / etc.)."""
    lvl = str(st.session_state.get(_PANEL_PLANNING_LEVEL_KEY, "") or "")
    return lvl if lvl else None


def _sync_planning_level_from_values() -> None:
    """Keep button state aligned when a planning value already exists."""
    if _active_planning_level_key():
        return
    for key in _PLANNING_FILTER_KEYS:
        if _panel_filter_value(key):
            st.session_state[_PANEL_PLANNING_LEVEL_KEY] = key
            return


def _on_planning_level_pick(level_key: str) -> None:
    """Activate one planning dimension; lock the other three buttons."""
    st.session_state[_PANEL_PLANNING_LEVEL_KEY] = level_key
    for key in _PLANNING_FILTER_KEYS:
        if key != level_key:
            st.session_state[key] = _PANEL_FILTER_PLACEHOLDER


def _active_planning_filter_key() -> str | None:
    """Active planning dimension — from button selection or selected value."""
    level = _active_planning_level_key()
    if level:
        return level
    for key in _PLANNING_FILTER_KEYS:
        if _panel_filter_value(key):
            return key
    return None


def _enforce_single_planning_filter() -> None:
    """Only one planning dimension may have a value at a time."""
    active: str | None = None
    for key in _PLANNING_FILTER_KEYS:
        if not _panel_filter_value(key):
            continue
        if active is None:
            active = key
        else:
            st.session_state[key] = _PANEL_FILTER_PLACEHOLDER


def _on_planning_filter_changed(changed_key: str) -> None:
    """When a planning value is set, lock dimension and clear the other three."""
    if _panel_filter_value(changed_key):
        st.session_state[_PANEL_PLANNING_LEVEL_KEY] = changed_key
    for key in _PLANNING_FILTER_KEYS:
        if key != changed_key:
            st.session_state[key] = _PANEL_FILTER_PLACEHOLDER


def _affected_forecast_record_count() -> int | None:
    """Demo count shown after period + planning level + value are all set."""
    if not _panel_period_selected():
        return None
    level_key = _active_planning_level_key()
    if not level_key:
        return None
    if not _panel_filter_value(level_key):
        return None
    return 7


def _ensure_panel_filter_state() -> None:
    if st.session_state.get(_PANEL_FILTERS_VER_KEY) == _PANEL_FILTERS_VERSION:
        return
    for spec in _PANEL_HEADER_FILTERS:
        st.session_state[spec["key"]] = _PANEL_FILTER_PLACEHOLDER
    st.session_state[_PANEL_PLANNING_LEVEL_KEY] = ""
    st.session_state[_PANEL_FILTERS_VER_KEY] = _PANEL_FILTERS_VERSION


def _selected_panel_company() -> str:
    """Company code from the panel header Company dropdown."""
    val = _panel_filter_value(_PANEL_COMPANY_KEY)
    return val or _PANEL_FILTER_PLACEHOLDER


def _resolved_panel_company_code() -> str:
    """Company code for baselines — FR10, ES10, etc."""
    val = _panel_filter_value(_PANEL_COMPANY_KEY)
    return db_st.normalize_company_code(val) if val else ""


def _panel_filter_value(key: str) -> str:
    for spec in _PANEL_HEADER_FILTERS:
        if spec["key"] == key:
            val = str(st.session_state.get(key, _PANEL_FILTER_PLACEHOLDER))
            return "" if val == _PANEL_FILTER_PLACEHOLDER else val
    return ""


def _deepest_planning_filter_spec() -> dict[str, Any] | None:
    """Most specific planning dimension with a selected value (BA → Commercial → Country → Company)."""
    deepest: dict[str, Any] | None = None
    for spec in _PANEL_HEADER_FILTERS:
        if spec["key"] == _PANEL_PERIOD_KEY:
            continue
        if _panel_filter_value(spec["key"]):
            deepest = spec
    return deepest


def _build_hierarchy_level_rows() -> list[dict[str, str]]:
    """Sidebar hierarchy card — one row per selected panel filter."""
    rows: list[dict[str, str]] = []
    period_val = _panel_filter_value(_PANEL_PERIOD_KEY)
    if period_val:
        rows.append({"name": "Period", "value": period_val})
    deepest = _deepest_planning_filter_spec()
    if deepest:
        rows.append({"name": "Planning Level", "value": deepest["label"]})
    for spec in _PANEL_HEADER_FILTERS:
        if spec["key"] == _PANEL_PERIOD_KEY:
            continue
        val = _panel_filter_value(spec["key"])
        if val:
            rows.append({"name": spec["label"], "value": val})
    return rows


def _delivery_mix_rows(group: dict[str, Any]) -> list[tuple[int, dict[str, Any]]]:
    """One DD% row per selected panel filter (Business Area, Commercial Area, Country, Company)."""
    if not _panel_period_selected():
        return []
    company = _panel_filter_value(_PANEL_COMPANY_KEY)
    rows: list[tuple[int, dict[str, Any]]] = []
    for fi, (dim_key, panel_key) in enumerate(_DELIVERY_MIX_DIMENSIONS):
        label = _panel_filter_value(panel_key)
        if not label:
            continue
        dd_change = (
            int(db_st._DELIVERY_MIX_DD_CHANGE.get(company, 0))
            if dim_key == "company"
            else 0
        )
        rows.append((
            fi,
            {
                **_DM_PCT_FIELD,
                "name": label,
                "dim_key": dim_key,
                "name_tags": [],
                "desc": "",
                "dd_change": dd_change,
            },
        ))
    return rows


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
            box-sizing: border-box !important;
        }

        /* Panel header filters wrap — reliable 16px inset */
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_filters_wrap"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"][class*="st-key-sim_panel_filters_wrap"],
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"][class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stElementContainer"][class*="st-key-sim_panel_filters_wrap"] {
            padding: 0 16px 16px 16px !important;
            box-sizing: border-box !important;
            background: #042A57 !important;
            background-color: #042A57 !important;
            margin: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stVerticalBlock"] {
            padding: 0 !important;
            margin: 0 !important;
            background: #042A57 !important;
            background-color: #042A57 !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stHorizontalBlock"] {
            justify-content: space-between !important;
            align-items: flex-end !important;
            width: 100% !important;
            max-width: 100% !important;
            gap: 12px !important;
            padding: 0 !important;
            margin: 0 !important;
            box-sizing: border-box !important;
        }

        /* Panel header dropdowns — aligned filter row */
        .sim-panel-filters-row-marker,
        .sim-panel-period-col-marker,
        .sim-panel-select-col-marker,
        .sim-panel-dd-75-marker,
        .sim-planning-level-marker,
        .sim-affected-records-marker { display: none !important; }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] {
            display: flex !important;
            justify-content: space-between !important;
            align-items: flex-end !important;
            width: 100% !important;
            max-width: 100% !important;
            gap: 12px !important;
            padding: 0 16px 16px 16px !important;
            box-sizing: border-box !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-period-col-marker),
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-select-col-marker) {
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: none !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-planning-level-marker) {
            flex: 1 1 auto !important;
            min-width: 260px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-affected-records-marker) {
            flex: 0 0 auto !important;
            margin-left: auto !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) {
            flex: 1 1 auto !important;
            min-width: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-period-col-marker) > [data-testid="stHorizontalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-select-col-marker) > [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            width: 100% !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-planning-level-marker) > [data-testid="stHorizontalBlock"]:has([class*="st-key-sim_plan_btn_"]) {
            justify-content: center !important;
            gap: 4px !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="stHorizontalBlock"] {
            justify-content: flex-start !important;
            gap: 2px !important;
            width: 100% !important;
            max-width: 100% !important;
            overflow: visible !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) {
            min-width: 0 !important;
            overflow: visible !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) > div[data-testid="stVerticalBlock"] {
            align-items: flex-start !important;
            width: 100% !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) [data-testid="stSelectbox"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div {
            width: 100% !important;
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

        /* Planning level buttons — navy panel header */
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-planning-level-marker) {
            flex: 1 1 auto !important;
            min-width: 260px !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-planning-level-heading {
            margin: 0 0 6px 2px !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] {
            min-width: 0 !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button {
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 8px !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            line-height: 1.1 !important;
            border-radius: 4px !important;
            border: none !important;
            white-space: nowrap !important;
            box-shadow: none !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button p,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button span,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button div,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button [data-testid="stMarkdownContainer"] {
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) {
            background: #FFFFFF1A !important;
            background-color: #FFFFFF1A !important;
            background-image: none !important;
            border: none !important;
            color: #ffffff !important;
            cursor: pointer !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) p,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) span,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) div,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) [data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] {
            background: rgba(255, 255, 255, 0.22) !important;
            border: none !important;
            color: #ffffff !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] p,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] span,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] div,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] [data-testid="stMarkdownContainer"] {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:disabled {
            background: #CBCBCB1A !important;
            background-color: #CBCBCB1A !important;
            background-image: none !important;
            border: none !important;
            color: #70737B !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled p,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled span,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled div,
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled [data-testid="stMarkdownContainer"] {
            color: #70737B !important;
            -webkit-text-fill-color: #70737B !important;
        }

        /* Affected forecast records — right side stat */
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .sim-affected-records {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 8px !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            padding-top: 0 !important;
            min-height: 32px !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .elx-affected-records-lbl {
            margin: 0 !important;
            text-align: right !important;
            display: inline !important;
            white-space: nowrap !important;
        }
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] .sim-affected-records-val {
            color: #ffffff !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            min-height: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            white-space: nowrap !important;
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
            overflow: hidden !important;
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
        [data-testid="column"]:has(.sim-pct-chip-row) div[data-baseweb="input"] {
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            min-height: 38px !important;
            height: 38px !important;
            min-width: 44px !important;
            width: auto !important;
            box-shadow: none !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) div[data-baseweb="input"] > div {
            min-height: 38px !important;
            height: 38px !important;
            display: flex !important;
            align-items: center !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) div[data-baseweb="input"] input,
        [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"] input {
            text-align: left !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            color: #011E41 !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 38px !important;
            height: 38px !important;
            width: 52px !important;
            min-width: 44px !important;
            max-width: 72px !important;
            padding: 0 !important;
        }
        [data-testid="column"]:has(.sim-pct-chip-row) div[data-baseweb="input"]:focus-within {
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
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
    """Inject simulate-page styles on every rerun (Streamlit rebuilds DOM each run)."""
    import pages_st.Common_Pages.filter_select as _fs

    _fs._CSS_INJECTED = False
    _fs._SIM_CTX_CSS_INJECTED = False
    st.markdown(
        f"""
        <style id="sim-page-css-v{_INFL_CSS_VERSION}">
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
        [class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stElementContainer"][class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"][class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [data-testid="stElementContainer"][class*="st-key-sim_panel_filters_wrap"] {{
            padding: {_PANEL_HEADER_FILTER_PAD} !important;
            box-sizing: border-box !important;
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            margin: 0 !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_panel_filters_wrap"] [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stVerticalBlock"] {{
            padding: 0 !important;
            margin: 0 !important;
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
        }}
        [class*="st-key-sim_panel_filters_wrap"] [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_filters_wrap"] [data-testid="stHorizontalBlock"] {{
            justify-content: space-between !important;
            align-items: flex-end !important;
            width: calc(100% - 32px) !important;
            max-width: calc(100% - 32px) !important;
            gap: 12px !important;
            padding: 0 !important;
            margin: 0 16px 16px 16px !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] {{
            padding: {_PANEL_HEADER_FILTER_PAD} !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap),
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) .stHtml {{
            background: {_PANEL_HEADER_BG} !important;
            background-color: {_PANEL_HEADER_BG} !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-panel-header-wrap) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] {{
            justify-content: space-between !important;
            align-items: flex-end !important;
            gap: 12px !important;
            width: calc(100% - 32px) !important;
            max-width: calc(100% - 32px) !important;
            overflow: visible !important;
            padding: 0 !important;
            margin: 0 16px 16px 16px !important;
            box-sizing: border-box !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] {{
            justify-content: space-between !important;
            align-items: flex-end !important;
            width: calc(100% - 32px) !important;
            max-width: calc(100% - 32px) !important;
            gap: 12px !important;
            padding: 0 !important;
            margin: 0 16px 16px 16px !important;
            box-sizing: border-box !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-period-col-marker),
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-select-col-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-period-col-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-panel-select-col-marker) {{
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: none !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-planning-level-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-planning-level-marker) {{
            flex: 1 1 auto !important;
            min-width: 260px !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-affected-records-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="stVerticalBlock"]:has(.sim-panel-filters-row-marker) > [data-testid="stHorizontalBlock"] > [data-testid="column"]:has(.sim-affected-records-marker) {{
            flex: 0 0 auto !important;
            margin-left: auto !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
            align-self: flex-end !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) > div[data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) > div[data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
            width: 100% !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) [data-testid="stSelectbox"],
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"],
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) [data-testid="stSelectbox"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-planning-level-marker) > [data-testid="stHorizontalBlock"]:has([class*="st-key-sim_plan_btn_"]),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-planning-level-marker) > [data-testid="stHorizontalBlock"]:has([class*="st-key-sim_plan_btn_"]) {{
            justify-content: center !important;
            gap: 4px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) {{
            height: auto !important;
            min-height: 0 !important;
            max-height: none !important;
            align-self: flex-end !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) > div[data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.elx-filter-panel) > div[data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
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
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [data-testid="column"]:has(.sim-planning-level-marker) {{
            flex: 1 1 auto !important;
            min-width: 240px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button {{
            height: 32px !important;
            min-height: 32px !important;
            padding: 0 8px !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            border-radius: 4px !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button p,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button span,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button [data-testid="stMarkdownContainer"] {{
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) {{
            background: {_PANEL_PLAN_BTN_BG_ENABLED} !important;
            background-color: {_PANEL_PLAN_BTN_BG_ENABLED} !important;
            background-image: none !important;
            border: none !important;
            color: {_PANEL_PLAN_BTN_TEXT_ENABLED} !important;
            cursor: pointer !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) p,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) span,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:not(:disabled) [data-testid="stMarkdownContainer"] {{
            color: {_PANEL_PLAN_BTN_TEXT_ENABLED} !important;
            -webkit-text-fill-color: {_PANEL_PLAN_BTN_TEXT_ENABLED} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] {{
            background: rgba(255, 255, 255, 0.22) !important;
            border: none !important;
            color: {_PANEL_PLAN_BTN_TEXT_ACTIVE} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] p,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] span,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="primary"] [data-testid="stMarkdownContainer"] {{
            color: {_PANEL_PLAN_BTN_TEXT_ACTIVE} !important;
            -webkit-text-fill-color: {_PANEL_PLAN_BTN_TEXT_ACTIVE} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button[kind="secondary"]:disabled {{
            background: {_PANEL_PLAN_BTN_BG_DISABLED} !important;
            background-color: {_PANEL_PLAN_BTN_BG_DISABLED} !important;
            background-image: none !important;
            border: none !important;
            color: {_PANEL_PLAN_BTN_TEXT} !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled p,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled span,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] [class*="st-key-sim_plan_btn_"] button:disabled [data-testid="stMarkdownContainer"] {{
            color: {_PANEL_PLAN_BTN_TEXT} !important;
            -webkit-text-fill-color: {_PANEL_PLAN_BTN_TEXT} !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .sim-affected-records {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            gap: 8px !important;
            flex-wrap: nowrap !important;
            white-space: nowrap !important;
            min-height: 32px !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .elx-affected-records-lbl {{
            text-align: right !important;
            margin: 0 !important;
            display: inline !important;
            white-space: nowrap !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-main-marker) [class*="st-key-sim_panel_header_wrap"] .sim-affected-records-val {{
            color: #ffffff !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            min-height: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            white-space: nowrap !important;
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
        + [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) {{
            padding: 0 !important;
            margin: 0 !important;
            align-items: center !important;
            min-height: 0 !important;
            background: #ffffff !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-last)
        + [data-testid="stHorizontalBlock"] {{
            border-bottom: none !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-section-header-marker)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-section-header-marker)) {{
            margin: 0 !important;
            padding: 10px !important;
            gap: 8px !important;
            align-items: center !important;
            background: #ffffff !important;
            box-sizing: border-box !important;
            width: 100% !important;
            display: flex !important;
            min-height: calc({_PCT_CHIP_H} + 20px) !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-field-row-last)):not(:has(.sim-section-header-marker)),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-field-row-last)):not(:has(.sim-section-header-marker)) {{
            border-bottom: 1px solid #000000 !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-last),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-last) {{
            border-bottom: none !important;
        }}
        hr.sim-dd-row-divider,
        div.sim-dd-row-divider {{
            display: block !important;
            width: 100% !important;
            max-width: 100% !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            border-top: 1px solid #000000 !important;
            background: transparent !important;
            box-sizing: border-box !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stElementContainer"]:has(.sim-dd-row-divider),
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stMarkdownContainer"]:has(.sim-dd-row-divider),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stElementContainer"]:has(.sim-dd-row-divider),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stMarkdownContainer"]:has(.sim-dd-row-divider) {{
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: 100% !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stElementContainer"]:has(.sim-field-row-marker) {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-section-header-marker)) > [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker):not(:has(.sim-section-header-marker)) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            min-height: {_PCT_CHIP_H} !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:first-child,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:first-child {{
            justify-content: flex-start !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child {{
            justify-content: flex-end !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"] {{
            justify-content: center !important;
            gap: 0 !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] [data-testid="stElementContainer"],
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"] [data-testid="stMarkdownContainer"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: inherit !important;
            width: 100% !important;
            min-height: {_PCT_CHIP_H} !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stVerticalBlock"],
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stElementContainer"],
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) > [data-testid="column"]:last-child [data-testid="stMarkdownContainer"] {{
            justify-content: flex-end !important;
        }}
        .sim-dd-row-label {{
            display: flex !important;
            align-items: center !important;
            min-height: {_PCT_CHIP_H} !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            color: {_PRIMARY} !important;
            line-height: 1.3 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [class*="st-key-sim_grp_"]:has(.sim-delivery-mix-wrap) .sim-pct-chip-readonly,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-delivery-mix-wrap) .sim-pct-chip-readonly {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: {_PCT_CHIP_GAP} !important;
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            min-height: {_PCT_CHIP_H} !important;
            height: {_PCT_CHIP_H} !important;
            padding: {_PCT_CHIP_PAD} !important;
            margin-left: auto !important;
            margin-right: 0 !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap):not(:has(.sim-delivery-mix-wrap)) [data-testid="stElementContainer"]:has(.sim-field-row-marker):last-of-type
        + [data-testid="stHorizontalBlock"] {{
            border-bottom: none !important;
        }}

        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_save_"] button {{
            background: {_SAVE_BTN_BG} !important;
            color: {_SAVE_BTN_TEXT} !important;
            border: 1px solid {_SAVE_BTN_BORDER} !important;
            border-radius: {_INPUT_RADIUS} !important;
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
            border-radius: {_INPUT_RADIUS} !important;
        }}
        .block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button,
        .block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button {{
            background: {_SAVE_BTN_BG} !important;
            color: {_SAVE_BTN_TEXT} !important;
            border: 1px solid {_SAVE_BTN_BORDER} !important;
            border-radius: {_INPUT_RADIUS} !important;
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
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) [data-testid="stNumberInputStepDown"],
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) [data-testid="stNumberInputStepUp"],
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) [data-testid="stNumberInput"] button,
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) [data-testid="stNumberInputContainer"] button,
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
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] .sim-pct-inline,
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) .sim-pct-inline {{
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
        [data-testid="stElementContainer"]:has(.sim-field-row-marker) + [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child > div[data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-field-row-marker) [data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {{
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
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([class*="st-key-sim_side_pc_totals_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_side_submit_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_side_infl_calc_"]),
        [data-testid="column"]:has(.sim-sidebar-marker) [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_side_pc_totals_"]) {{
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
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker),
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) > div,
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) [data-testid="stVerticalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) [data-testid="stHorizontalBlock"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) [data-testid="stElementContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) [data-testid="column"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) [data-testid="stMarkdownContainer"],
        [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-card-marker),
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-submit-marker),
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-infl-calc-marker),
        .block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-side-pc-totals-marker) {{
            border: 1px solid {_SIDE_SUBMIT_BORDER} !important;
            border-radius: {_SIDE_CARD_RADIUS} !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_"] {{
            background: {_CARD_BG} !important;
            background-color: {_CARD_BG} !important;
        }}
        .block-container:has(#simulate-page) [class*="st-key-sim_side_impact"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_submit_"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_pc_totals_"],
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-infl-calc-marker),
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-pc-totals-marker) {{
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
        .block-container:has(#simulate-page) [class*="st-key-sim_side_pc_totals_"] [data-testid="stVerticalBlock"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_pc_totals_"] [data-testid="stElementContainer"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_pc_totals_"] .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-card-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-submit-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-infl-calc-marker) .stHtml,
        .block-container:has(#simulate-page) [data-testid="stElementContainer"]:has(.sim-side-pc-totals-marker) .stHtml {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        .sim-side-card-marker,
        .sim-side-submit-marker,
        .sim-side-infl-calc-marker,
        .sim-side-pc-totals-marker {{ display: none !important; }}
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
        .block-container:has(#simulate-page) [class*="st-key-sim_side_infl_calc_"],
        .block-container:has(#simulate-page) [class*="st-key-sim_side_pc_totals_"] {{
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

        /* Inflation matrix table — Figma layout */
        .sim-infl-table-wrap-marker {{ display: none !important; }}
        .sim-infl-matrix-marker {{ display: none !important; }}
        .sim-infl-row-marker {{ display: none !important; }}
        .sim-infl-header-marker {{ display: none !important; }}
        .sim-infl-calc-row-marker {{ display: none !important; }}
        .sim-infl-calc-caption-marker {{ display: none !important; }}
        .sim-infl-calc-caption-wrap {{
            display: block !important;
            margin: 20px 0 4px 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }}
        .sim-infl-calc-caption {{
            margin: 0 !important;
            padding: 0 !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: {_INFL_CALC_CAPTION_COLOR} !important;
            line-height: 1.4 !important;
            visibility: visible !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap),
        [class*="st-key-sim_grp_"] [data-testid="stMarkdownContainer"]:has(.sim-infl-calc-caption-wrap),
        [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap),
        [data-testid="stMarkdownContainer"]:has(.sim-infl-calc-caption-wrap) {{
            display: block !important;
            margin: 20px 0 4px 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            height: auto !important;
            min-height: 0 !important;
            background: transparent !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="stMarkdownContainer"]:has(.sim-infl-calc-caption-wrap) p {{
            margin: 0 !important;
            padding: 0 !important;
            color: {_INFL_CALC_CAPTION_COLOR} !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            line-height: 1.4 !important;
        }}
        [class*="st-key-sim_infl_input_"] + [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap),
        [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap) + [class*="st-key-sim_infl_calc_table_"],
        [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap) + [data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-sim_infl_calc_table_"]) {{
            margin-top: 0 !important;
        }}
        [class*="st-key-sim_infl_calc_table_"] {{
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            padding: 0 !important;
            margin-top: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-infl-table-wrap-marker) {{
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            margin-top: 12px !important;
            padding: 0 !important;
            background: #ffffff !important;
        }}
        [class*="st-key-sim_infl_input_"] {{
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            padding: 0 !important;
            margin-top: 12px !important;
            background: #ffffff !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="column"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="column"],
        [class*="st-key-sim_infl_input_"] [data-testid="stElementContainer"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stElementContainer"],
        [class*="st-key-sim_infl_input_"] [data-testid="stMarkdownContainer"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stMarkdownContainer"] {{
            overflow: visible !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stVerticalBlock"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stVerticalBlock"] {{
            gap: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        .sim-infl-header-bar {{
            display: grid !important;
            width: 100% !important;
            box-sizing: border-box !important;
            border-bottom: 1px solid #000000 !important;
        }}
        .sim-infl-header-bar .sim-infl-hcell {{
            font-size: 12px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            line-height: 1.3 !important;
            padding: 12px 8px !important;
            word-break: break-word !important;
            min-height: 44px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            width: 100% !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stElementContainer"]:has(.sim-infl-header-bar),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stElementContainer"]:has(.sim-infl-header-bar) {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.sim-infl-header-marker) {{
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.sim-infl-header-marker) [data-testid="column"] {{
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
        }}
        .sim-infl-hcell {{
            font-size: 12px !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            line-height: 1.3 !important;
            padding: 12px 8px !important;
            word-break: break-word !important;
            min-height: 44px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker),
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker),
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker),
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) {{
            margin: 0 !important;
            padding: 8px 10px !important;
            gap: 8px !important;
            align-items: center !important;
            border-bottom: 1px solid #000000 !important;
            background: #ffffff !important;
            box-sizing: border-box !important;
            width: 100% !important;
            min-height: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 40px !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"]:first-child,
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"]:first-child {{
            justify-content: flex-start !important;
            align-items: center !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: 40px !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
            justify-content: center !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stElementContainer"]:has(.sim-pct-chip-readonly),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stElementContainer"]:has(.sim-pct-chip-readonly),
        [class*="st-key-sim_infl_input_"] [data-testid="stMarkdownContainer"]:has(.sim-pct-chip-readonly),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stMarkdownContainer"]:has(.sim-pct-chip-readonly) {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 40px !important;
        }}
        .sim-pct-chip-readonly {{
            margin: 0 auto !important;
            display: inline-flex !important;
            vertical-align: middle !important;
        }}
        [data-testid="stHorizontalBlock"]:has(.sim-infl-row-last),
        [data-testid="stHorizontalBlock"]:has(.sim-infl-calc-row-last) {{
            border-bottom: none !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stElementContainer"]:has(.sim-infl-row-marker),
        [class*="st-key-sim_infl_input_"] [data-testid="stElementContainer"]:has(.sim-infl-calc-row-marker),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stElementContainer"]:has(.sim-infl-row-marker),
        [class*="st-key-sim_infl_calc_table_"] [data-testid="stElementContainer"]:has(.sim-infl-calc-row-marker) {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }}
        .sim-infl-row-label {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 4px;
            font-size: 12px;
            font-weight: 400;
            color: #374151;
            padding: 0 !important;
            min-height: 40px;
            line-height: 1.3;
        }}
        .sim-infl-pct-chip {{
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            width: fit-content !important;
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            min-height: 40px !important;
            height: 40px !important;
            padding: 0 12px !important;
            box-sizing: border-box !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
        }}
        .sim-infl-pct-chip-readonly {{
            background: {_INPUT_BG} !important;
        }}
        .sim-pct-chip-right {{
            margin-left: auto !important;
            margin-right: 0 !important;
        }}
        .sim-pct-chip-right .sim-infl-pct-val {{
            font-size: 14px !important;
            font-weight: 700 !important;
        }}
        .sim-pct-chip-right .sim-infl-pct-suffix {{
            font-size: 13px !important;
            font-weight: 600 !important;
        }}
        .sim-infl-pct-val {{
            font-size: 12px;
            font-weight: 400;
            color: {_PRIMARY};
            flex: 1;
            text-align: left;
        }}
        .sim-infl-pct-suffix {{
            font-size: 12px;
            font-weight: 400;
            color: #64748b;
            flex-shrink: 0;
            margin-left: 4px;
        }}
        .sim-infl-pct-input-marker,
        .sim-pct-input-marker {{ display: none !important; }}
        [data-testid="column"]:has(.sim-infl-pct-input-marker),
        [data-testid="column"]:has(.sim-pct-input-marker),
        [class*="st-key-sim_infl_input_"] [data-testid="column"]:has(.sim-infl-pct-input-marker),
        [class*="st-key-sim_infl_input_"] [data-testid="column"]:has(.sim-pct-input-marker) {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) {{
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }}
        [data-testid="column"]:has(.sim-infl-pct-input-marker) > div[data-testid="stVerticalBlock"],
        [data-testid="column"]:has(.sim-pct-input-marker) > div[data-testid="stVerticalBlock"],
        [class*="st-key-sim_infl_input_"] [data-testid="column"]:has(.sim-infl-pct-input-marker) > div[data-testid="stVerticalBlock"],
        [class*="st-key-sim_infl_input_"] [data-testid="column"]:has(.sim-pct-input-marker) > div[data-testid="stVerticalBlock"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) > div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
            align-items: center !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) > div[data-testid="stVerticalBlock"] {{
            align-items: flex-end !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"],
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"] > div,
        [data-testid="column"]:has(.sim-infl-pct-input-marker) [data-testid="stTextInput"],
        [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"],
        [data-testid="column"]:has(.sim-infl-pct-input-marker) [data-testid="stTextInput"] > div,
        [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] > div,
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] > div {{
            width: fit-content !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] > div {{
            margin-right: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"] label,
        [class*="st-key-sim_infl_input_"] [data-testid="stWidgetLabel"],
        [data-testid="column"]:has(.sim-infl-pct-input-marker) [data-testid="stTextInput"] label,
        [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] label,
        [data-testid="column"]:has(.sim-infl-pct-input-marker) [data-testid="stWidgetLabel"],
        [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stWidgetLabel"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] label,
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"],
        [data-testid="column"]:has(.sim-infl-pct-input-marker) div[data-baseweb="input"],
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] {{
            position: relative !important;
            width: fit-content !important;
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            min-height: {_PCT_CHIP_H} !important;
            height: {_PCT_CHIP_H} !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            margin-left: auto !important;
            margin-right: auto !important;
            box-shadow: none !important;
            overflow: visible !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] {{
            padding: {_PCT_CHIP_PAD} !important;
            gap: {_PCT_CHIP_GAP} !important;
        }}
        [data-testid="column"]:has(.sim-infl-pct-input-marker) div[data-baseweb="input"],
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"],
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] {{
            padding: 0 24px 0 10px !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] {{
            margin-right: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] > div,
        [data-testid="column"]:has(.sim-infl-pct-input-marker) div[data-baseweb="input"] > div,
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] > div,
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] > div {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            min-height: 38px !important;
            height: 38px !important;
            display: flex !important;
            align-items: center !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] input,
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"] input,
        [data-testid="column"]:has(.sim-infl-pct-input-marker) div[data-baseweb="input"] input,
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] input,
        [data-testid="column"]:has(.sim-infl-pct-input-marker) [data-testid="stTextInput"] input,
        [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] input {{
            text-align: left !important;
            font-weight: 400 !important;
            font-size: 12px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 38px !important;
            height: 38px !important;
            width: 44px !important;
            min-width: 32px !important;
            max-width: 52px !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] input,
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] input {{
            font-weight: 700 !important;
            font-size: 14px !important;
            width: 52px !important;
            min-width: 44px !important;
            max-width: 72px !important;
        }}
        [class*="st-key-sim_grp_"] [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"]:focus-within {{
            border-color: #94a3b8 !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"]:focus-within,
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"]:focus-within,
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"]:focus-within {{
            border-color: #94a3b8 !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"]:has(input:disabled),
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"]:has(input:disabled),
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"]:has(input:disabled) {{
            cursor: default !important;
            opacity: 1 !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] input:disabled,
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"] input:disabled,
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"] input:disabled {{
            opacity: 1 !important;
            color: {_PRIMARY} !important;
            -webkit-text-fill-color: {_PRIMARY} !important;
            cursor: default !important;
        }}
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] [data-testid="stTextInput"],
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] [data-testid="stTextInput"] > div {{
            width: fit-content !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            margin-left: auto !important;
            margin-right: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"] {{
            position: relative !important;
            width: fit-content !important;
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            min-height: 40px !important;
            height: 40px !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            padding: 0 24px 0 10px !important;
            display: flex !important;
            align-items: center !important;
            margin-left: auto !important;
            margin-right: 0 !important;
            box-shadow: none !important;
            overflow: visible !important;
        }}
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"] > div {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            min-height: 38px !important;
            height: 38px !important;
            display: flex !important;
            align-items: center !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: visible !important;
        }}
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] div[data-baseweb="input"] input,
        [data-testid="stElementContainer"][class*="st-key-sim_f_"] [data-testid="stTextInput"] input {{
            text-align: left !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            min-height: 38px !important;
            height: 38px !important;
            width: 52px !important;
            min-width: 44px !important;
            max-width: 72px !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"]::after {{
            content: "%" !important;
            position: static !important;
            right: auto !important;
            top: auto !important;
            transform: none !important;
            display: inline-block !important;
            flex-shrink: 0 !important;
            color: #64748b !important;
            font-size: 12px !important;
            font-weight: 400 !important;
            pointer-events: none !important;
            user-select: none !important;
            line-height: 1 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"]::after,
        [class*="st-key-sim_f_"] div[data-baseweb="input"]::after {{
            content: "%" !important;
            position: absolute !important;
            right: 12px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            color: #64748b !important;
            pointer-events: none !important;
            user-select: none !important;
            line-height: 1 !important;
            z-index: 6 !important;
        }}
        [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"]::after,
        [class*="st-key-sim_f_"] div[data-baseweb="input"]::after {{
            font-size: 13px !important;
            font-weight: 600 !important;
        }}
        .sim-infl-pct-suffix-inline,
        .sim-pct-suffix-inline {{
            position: absolute !important;
            right: 12px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            font-size: 12px !important;
            font-weight: 400 !important;
            color: #64748b !important;
            pointer-events: none !important;
            user-select: none !important;
            line-height: 1 !important;
            z-index: 5 !important;
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
              wrapper.style.setProperty("border-radius", "12px", "important");
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
              '[class*="st-key-sim_side_impact"], [class*="st-key-sim_side_submit_"], [class*="st-key-sim_side_infl_calc_"], [class*="st-key-sim_side_pc_totals_"]'
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
            doc.querySelectorAll('[class*="st-key-sim_side_infl_calc_"], [class*="st-key-sim_side_pc_totals_"]').forEach((card) => {
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
              if (!chip || chip.querySelector(".sim-pct-input-marker, .sim-infl-pct-input-marker")) return;
              numCol.style.setProperty("display", "flex", "important");
              numCol.style.setProperty("justify-content", "flex-end", "important");
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("flex-direction", "row", "important");
              chip.style.setProperty("align-items", "center", "important");
              chip.style.setProperty("background-color", inputBg, "important");
              chip.style.setProperty("background", inputBg, "important");
              chip.style.setProperty("border", inputBorder, "important");
              chip.style.setProperty("border-radius", "8px", "important");
              chip.style.setProperty("overflow", "hidden", "important");
              chip.style.setProperty("padding", "0 12px", "important");
              chip.style.setProperty("min-height", "40px", "important");
              chip.style.setProperty("height", "40px", "important");
              chip.style.setProperty("width", "fit-content", "important");
              chip.style.setProperty("margin-left", "auto", "important");
              chip.querySelectorAll('div[data-baseweb="input"]').forEach((wrap) => {
                wrap.style.setProperty("background", "transparent", "important");
                wrap.style.setProperty("border", "none", "important");
                wrap.style.setProperty("border-radius", "0", "important");
                wrap.style.setProperty("box-shadow", "none", "important");
              });
              chip.querySelectorAll('[data-testid="stTextInput"] input').forEach((input) => {
                input.style.setProperty("text-align", "left", "important");
                input.style.setProperty("font-weight", "700", "important");
                input.style.setProperty("border", "none", "important");
                input.style.setProperty("border-radius", "0", "important");
                input.style.setProperty("background", "transparent", "important");
                input.style.setProperty("box-shadow", "none", "important");
              });
              chip.querySelectorAll(".sim-pct-chip-suffix").forEach((pct) => {
                pct.style.setProperty("font-size", "13px", "important");
                pct.style.setProperty("font-weight", "600", "important");
                pct.style.setProperty("color", "#64748b", "important");
              });
            });

            doc.querySelectorAll(".sim-infl-header-bar").forEach((bar) => {
              bar.style.setProperty("display", "grid", "important");
              bar.style.setProperty("width", "100%", "important");
              bar.style.setProperty("box-sizing", "border-box", "important");
              bar.style.setProperty("border-bottom", "1px solid #000000", "important");
            });
            doc.querySelectorAll(".sim-infl-header-bar .sim-infl-hcell").forEach((cell) => {
              cell.style.setProperty("color", "#ffffff", "important");
              cell.style.setProperty("font-size", "12px", "important");
              cell.style.setProperty("font-weight", "700", "important");
              cell.style.setProperty("display", "flex", "important");
              cell.style.setProperty("align-items", "center", "important");
              cell.style.setProperty("justify-content", "center", "important");
              cell.style.setProperty("text-align", "center", "important");
              cell.style.setProperty("min-height", "44px", "important");
            });

            doc.querySelectorAll(".sim-infl-row-marker, .sim-infl-calc-row-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stHorizontalBlock"]');
              if (!row) return;
              const isLast = marker.classList.contains("sim-infl-row-last")
                || marker.classList.contains("sim-infl-calc-row-last");
              row.style.setProperty(
                "border-bottom",
                isLast ? "none" : "1px solid #000000",
                "important"
              );
              row.style.setProperty("display", "flex", "important");
              row.style.setProperty("align-items", "center", "important");
              row.style.setProperty("padding", "8px 10px", "important");
              row.style.setProperty("margin", "0", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
              row.style.setProperty("width", "100%", "important");
              row.style.setProperty("min-height", "0", "important");
              row.style.setProperty("background", "#ffffff", "important");
              row.querySelectorAll(':scope > [data-testid="column"]').forEach((col, idx) => {
                col.style.setProperty("display", "flex", "important");
                col.style.setProperty("align-items", "center", "important");
                col.style.setProperty(
                  "justify-content",
                  idx === 0 ? "flex-start" : "center",
                  "important"
                );
                col.style.setProperty("min-height", "40px", "important");
                col.style.setProperty("padding", "0", "important");
                col.style.setProperty("margin", "0", "important");
                const vb = col.querySelector(':scope > [data-testid="stVerticalBlock"]');
                if (vb) {
                  vb.style.setProperty("width", "100%", "important");
                  vb.style.setProperty("align-items", idx === 0 ? "flex-start" : "center", "important");
                  vb.style.setProperty("justify-content", "center", "important");
                  vb.style.setProperty("min-height", "40px", "important");
                  vb.style.setProperty("gap", "0", "important");
                  vb.style.setProperty("padding", "0", "important");
                  vb.style.setProperty("margin", "0", "important");
                }
              });
            });
            doc.querySelectorAll(".sim-infl-calc-caption-wrap").forEach((wrap) => {
              wrap.style.setProperty("display", "block", "important");
              wrap.style.setProperty("margin", "20px 0 4px 0", "important");
              wrap.style.setProperty("padding", "0", "important");
              wrap.style.setProperty("overflow", "visible", "important");
              const ec = wrap.closest('[data-testid="stElementContainer"]');
              if (ec) {
                ec.style.setProperty("display", "block", "important");
                ec.style.setProperty("margin", "20px 0 4px 0", "important");
                ec.style.setProperty("padding", "0", "important");
                ec.style.setProperty("overflow", "visible", "important");
                ec.style.setProperty("height", "auto", "important");
                ec.style.setProperty("background", "transparent", "important");
              }
              wrap.querySelectorAll(".sim-infl-calc-caption").forEach((cap) => {
                cap.style.setProperty("margin", "0", "important");
                cap.style.setProperty("font-size", "14px", "important");
                cap.style.setProperty("font-weight", "700", "important");
                cap.style.setProperty("color", "#021632", "important");
                cap.style.setProperty("line-height", "1.4", "important");
                cap.style.setProperty("visibility", "visible", "important");
              });
            });
            doc.querySelectorAll('[class*="st-key-sim_infl_calc_table_"]').forEach((box) => {
              const parent = box.parentElement;
              if (parent && parent.querySelector(".sim-infl-calc-caption-wrap")) {
                box.style.setProperty("margin-top", "0", "important");
              }
            });
            doc.querySelectorAll(".sim-pct-chip-readonly").forEach((chip) => {
              const inParam = chip.closest('[class*="st-key-sim_f_"]');
              if (inParam) return;
              chip.style.setProperty("margin-left", "auto", "important");
              chip.style.setProperty("margin-right", "auto", "important");
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("vertical-align", "middle", "important");
            });
            doc.querySelectorAll(
              '[class*="st-key-sim_infl_input_"] [data-testid="stMarkdownContainer"], [class*="st-key-sim_infl_calc_table_"] [data-testid="stMarkdownContainer"]'
            ).forEach((md) => {
              if (!md.querySelector(".sim-pct-chip-readonly")) return;
              md.style.setProperty("display", "flex", "important");
              md.style.setProperty("align-items", "center", "important");
              md.style.setProperty("justify-content", "center", "important");
              md.style.setProperty("width", "100%", "important");
              md.style.setProperty("min-height", "40px", "important");
              md.style.setProperty("margin", "0", "important");
              md.style.setProperty("padding", "0", "important");
            });
            doc.querySelectorAll(".sim-infl-row-label").forEach((el) => {
              el.style.setProperty("display", "flex", "important");
              el.style.setProperty("align-items", "center", "important");
              el.style.setProperty("min-height", "40px", "important");
              el.style.setProperty("font-size", "12px", "important");
              el.style.setProperty("font-weight", "400", "important");
              el.style.setProperty("margin", "0", "important");
              el.style.setProperty("padding", "0", "important");
            });

            function paintPctInputChip(wrap) {
              const col = wrap.closest('[data-testid="column"]');
              const isParam = Boolean(wrap.closest('[class*="st-key-sim_f_"]'));
              const inInfl = Boolean(wrap.closest('[class*="st-key-sim_infl_input_"]'));
              const fontSize = isParam ? "14px" : "12px";
              const fontWeight = isParam ? "700" : "400";
              const inputWidth = isParam ? "52px" : "auto";
              const inputMin = isParam ? "44px" : "24px";
              const inputMax = isParam ? "72px" : "48px";
              const marginRight = inInfl ? "auto" : "0";
              const chipPad = inInfl ? "0 10px" : "0 24px 0 10px";
              const chipGap = inInfl ? "4px" : "0";
              wrap.setAttribute("data-pct-suffix", "1");
              wrap.style.setProperty("position", "relative", "important");
              wrap.style.setProperty("width", "fit-content", "important");
              wrap.style.setProperty("min-width", "76px", "important");
              wrap.style.setProperty("max-width", "100px", "important");
              wrap.style.setProperty("min-height", "40px", "important");
              wrap.style.setProperty("height", "40px", "important");
              wrap.style.setProperty("background", inputBg, "important");
              wrap.style.setProperty("background-color", inputBg, "important");
              wrap.style.setProperty("border", inputBorder, "important");
              wrap.style.setProperty("border-radius", "8px", "important");
              wrap.style.setProperty("box-sizing", "border-box", "important");
              wrap.style.setProperty("padding", chipPad, "important");
              wrap.style.setProperty("gap", chipGap, "important");
              wrap.style.setProperty("display", "inline-flex", "important");
              wrap.style.setProperty("align-items", "center", "important");
              wrap.style.setProperty("justify-content", "flex-start", "important");
              wrap.style.setProperty("margin-left", "auto", "important");
              wrap.style.setProperty("margin-right", marginRight, "important");
              wrap.style.setProperty("box-shadow", "none", "important");
              wrap.style.setProperty("overflow", "visible", "important");
              wrap.querySelectorAll(':scope > div').forEach((inner) => {
                inner.style.setProperty("flex", "1 1 auto", "important");
                inner.style.setProperty("min-width", "0", "important");
                inner.style.setProperty("background", "transparent", "important");
                inner.style.setProperty("border", "none", "important");
                inner.style.setProperty("box-shadow", "none", "important");
                inner.style.setProperty("display", "flex", "important");
                inner.style.setProperty("align-items", "center", "important");
                inner.style.setProperty("overflow", "visible", "important");
              });
              wrap.querySelectorAll("input").forEach((input) => {
                input.style.setProperty("text-align", "left", "important");
                input.style.setProperty("font-size", fontSize, "important");
                input.style.setProperty("font-weight", fontWeight, "important");
                input.style.setProperty("color", "#011E41", "important");
                input.style.setProperty("-webkit-text-fill-color", "#011E41", "important");
                input.style.setProperty("border", "none", "important");
                input.style.setProperty("background", "transparent", "important");
                input.style.setProperty("box-shadow", "none", "important");
                input.style.setProperty("outline", "none", "important");
                input.style.setProperty("width", inputWidth, "important");
                input.style.setProperty("min-width", inputMin, "important");
                input.style.setProperty("max-width", inputMax, "important");
                input.style.setProperty("padding", "0", "important");
                input.style.setProperty("min-height", inInfl ? "auto" : "38px", "important");
                input.style.setProperty("height", inInfl ? "auto" : "38px", "important");
                if (input.disabled) {
                  input.style.setProperty("opacity", "1", "important");
                  input.style.setProperty("cursor", "default", "important");
                  wrap.style.setProperty("cursor", "default", "important");
                }
              });
              if (inInfl) {
                const afterContent = window.getComputedStyle(wrap, "::after").getPropertyValue("content");
                const hasSuffix = wrap.querySelector("[data-sim-pct-suffix]");
                if (!hasSuffix && (afterContent === "none" || afterContent === '""' || afterContent === "")) {
                  const suffix = doc.createElement("span");
                  suffix.setAttribute("data-sim-pct-suffix", "1");
                  suffix.textContent = "%";
                  suffix.style.setProperty("flex-shrink", "0", "important");
                  suffix.style.setProperty("color", "#64748b", "important");
                  suffix.style.setProperty("font-size", "12px", "important");
                  suffix.style.setProperty("font-weight", "400", "important");
                  suffix.style.setProperty("line-height", "1", "important");
                  suffix.style.setProperty("pointer-events", "none", "important");
                  wrap.appendChild(suffix);
                }
              }
              if (col) {
                col.style.setProperty("display", "flex", "important");
                col.style.setProperty("align-items", "center", "important");
                col.style.setProperty(
                  "justify-content",
                  isParam ? "flex-end" : "center",
                  "important"
                );
                const vb = col.querySelector(':scope > [data-testid="stVerticalBlock"]');
                if (vb) {
                  vb.style.setProperty("width", "100%", "important");
                  vb.style.setProperty("align-items", isParam ? "flex-end" : "center", "important");
                  vb.style.setProperty("justify-content", "center", "important");
                  vb.style.setProperty("min-height", "40px", "important");
                  vb.style.setProperty("gap", "0", "important");
                  vb.style.setProperty("padding", "0", "important");
                  vb.style.setProperty("margin", "0", "important");
                }
              }
            }
            doc.querySelectorAll('[class*="st-key-sim_infl_input_"] [data-testid="column"], [class*="st-key-sim_infl_calc_table_"] [data-testid="column"]').forEach((col) => {
              col.style.setProperty("overflow", "visible", "important");
              col.style.setProperty("min-width", "0", "important");
            });
            doc.querySelectorAll('[class*="st-key-sim_infl_input_"] div[data-baseweb="input"]').forEach(paintPctInputChip);
            doc.querySelectorAll('[class*="st-key-sim_f_"]').forEach((widgetRoot) => {
              if (!widgetRoot.querySelector('[data-testid="stTextInput"]')) return;
              const wrap = widgetRoot.querySelector('div[data-baseweb="input"]');
              if (wrap) paintPctInputChip(wrap);
            });
            doc.querySelectorAll(".sim-pct-input-marker, .sim-infl-pct-input-marker").forEach((marker) => {
              const col = marker.closest('[data-testid="column"]');
              if (!col) return;
              const wrap = col.querySelector('div[data-baseweb="input"]');
              if (wrap) paintPctInputChip(wrap);
            });

            doc.querySelectorAll(".sim-infl-row-label, .sim-infl-pct-val").forEach((el) => {
              el.style.setProperty("font-size", "12px", "important");
              el.style.setProperty("font-weight", "400", "important");
            });

            doc.querySelectorAll(".sim-pc-row-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stHorizontalBlock"]');
              if (!row) return;
              row.style.setProperty("display", "flex", "important");
              row.style.setProperty("align-items", "center", "important");
              row.style.setProperty("padding", "8px 10px", "important");
              row.style.setProperty("margin", "0", "important");
              row.style.setProperty("gap", "8px", "important");
              row.style.setProperty("border-bottom", "1px solid #000000", "important");
              row.style.setProperty("background", "#ffffff", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
              row.style.setProperty("width", "100%", "important");
              row.querySelectorAll(':scope > [data-testid="column"]').forEach((col, idx) => {
                col.style.setProperty("display", "flex", "important");
                col.style.setProperty("align-items", "center", "important");
                col.style.setProperty("justify-content", idx < 2 ? "flex-start" : "center", "important");
                col.style.setProperty("overflow", "visible", "important");
                col.style.setProperty("min-height", "36px", "important");
                if (idx >= 2) {
                  col.querySelectorAll('[data-testid="stVerticalBlock"], [data-testid="stElementContainer"], [data-testid="stMarkdownContainer"]').forEach((el) => {
                    el.style.setProperty("display", "flex", "important");
                    el.style.setProperty("align-items", "center", "important");
                    el.style.setProperty("justify-content", "center", "important");
                    el.style.setProperty("width", "100%", "important");
                    el.style.setProperty("margin", "0", "important");
                    el.style.setProperty("padding", "0", "important");
                  });
                }
              });
            });
            doc.querySelectorAll('[class*="st-key-sim_pc_input_"] div[data-baseweb="input"]').forEach((wrap) => {
              wrap.style.setProperty("display", "inline-flex", "important");
              wrap.style.setProperty("align-items", "center", "important");
              wrap.style.setProperty("justify-content", "center", "important");
              wrap.style.setProperty("min-width", "84px", "important");
              wrap.style.setProperty("max-width", "108px", "important");
              wrap.style.setProperty("min-height", "36px", "important");
              wrap.style.setProperty("height", "36px", "important");
              wrap.style.setProperty("padding", "0 8px", "important");
              wrap.style.setProperty("margin-left", "auto", "important");
              wrap.style.setProperty("margin-right", "auto", "important");
              wrap.style.setProperty("background", inputBg, "important");
              wrap.style.setProperty("background-color", inputBg, "important");
              wrap.style.setProperty("border", inputBorder, "important");
              wrap.style.setProperty("border-radius", "8px", "important");
              wrap.style.setProperty("box-shadow", "none", "important");
              wrap.style.setProperty("overflow", "hidden", "important");
              wrap.querySelectorAll(":scope > div").forEach((inner) => {
                inner.style.setProperty("display", "flex", "important");
                inner.style.setProperty("align-items", "center", "important");
                inner.style.setProperty("justify-content", "center", "important");
                inner.style.setProperty("width", "100%", "important");
                inner.style.setProperty("height", "100%", "important");
                inner.style.setProperty("background", "transparent", "important");
                inner.style.setProperty("background-color", "transparent", "important");
                inner.style.setProperty("border", "none", "important");
                inner.style.setProperty("box-shadow", "none", "important");
              });
              wrap.querySelectorAll("input").forEach((input) => {
                input.style.setProperty("text-align", "center", "important");
                input.style.setProperty("font-size", "12px", "important");
                input.style.setProperty("font-weight", "400", "important");
                input.style.setProperty("color", "#011E41", "important");
                input.style.setProperty("border", "none", "important");
                input.style.setProperty("background", "transparent", "important");
                input.style.setProperty("background-color", "transparent", "important");
                input.style.setProperty("width", "100%", "important");
                input.style.setProperty("padding", "0", "important");
                input.style.setProperty("box-shadow", "none", "important");
              });
            });
            doc.querySelectorAll(".sim-pc-value-chip").forEach((chip) => {
              chip.style.setProperty("display", "inline-flex", "important");
              chip.style.setProperty("align-items", "center", "important");
              chip.style.setProperty("justify-content", "center", "important");
              chip.style.setProperty("min-width", "84px", "important");
              chip.style.setProperty("max-width", "108px", "important");
              chip.style.setProperty("width", "fit-content", "important");
              chip.style.setProperty("min-height", "36px", "important");
              chip.style.setProperty("height", "36px", "important");
              chip.style.setProperty("margin", "0 auto", "important");
              chip.style.setProperty("white-space", "nowrap", "important");
              if (chip.classList.contains("sim-pc-total-chip")) {
                chip.style.setProperty("background", "#D4DFE9", "important");
                chip.style.setProperty("background-color", "#D4DFE9", "important");
                chip.style.setProperty("font-weight", "700", "important");
                chip.style.setProperty("border", inputBorder, "important");
              } else {
                chip.style.setProperty("background", inputBg, "important");
                chip.style.setProperty("background-color", inputBg, "important");
                chip.style.setProperty("border", inputBorder, "important");
              }
              const md = chip.closest('[data-testid="stMarkdownContainer"]');
              if (md) {
                md.style.setProperty("display", "flex", "important");
                md.style.setProperty("align-items", "center", "important");
                md.style.setProperty("justify-content", "center", "important");
                md.style.setProperty("width", "100%", "important");
              }
            });

            doc.querySelectorAll(".sim-pc-total-marker").forEach((marker) => {
              const row = marker.closest('[data-testid="stHorizontalBlock"]');
              if (!row) return;
              row.style.setProperty("display", "flex", "important");
              row.style.setProperty("align-items", "center", "important");
              row.style.setProperty("padding", "10px", "important");
              row.style.setProperty("margin", "0", "important");
              row.style.setProperty("gap", "8px", "important");
              row.style.setProperty("border-top", "1px solid #000000", "important");
              row.style.setProperty("border-bottom", "none", "important");
              row.style.setProperty("background", "#ffffff", "important");
              row.style.setProperty("box-sizing", "border-box", "important");
              row.style.setProperty("width", "100%", "important");
              row.style.setProperty("min-height", "44px", "important");
              row.style.setProperty("overflow", "visible", "important");
              row.querySelectorAll(':scope > [data-testid="column"]').forEach((col, idx) => {
                col.style.setProperty("display", "flex", "important");
                col.style.setProperty("align-items", "center", "important");
                col.style.setProperty("justify-content", idx < 2 ? "flex-start" : "center", "important");
                col.style.setProperty("overflow", "visible", "important");
                col.style.setProperty("min-height", "44px", "important");
                if (idx >= 2) {
                  col.querySelectorAll('[data-testid="stVerticalBlock"], [data-testid="stElementContainer"], [data-testid="stMarkdownContainer"]').forEach((el) => {
                    el.style.setProperty("display", "flex", "important");
                    el.style.setProperty("align-items", "center", "important");
                    el.style.setProperty("justify-content", "center", "important");
                    el.style.setProperty("width", "100%", "important");
                    el.style.setProperty("margin", "0", "important");
                    el.style.setProperty("padding", "0", "important");
                  });
                }
              });
            });
            doc.querySelectorAll('[class*="st-key-sim_pc_input_"]').forEach((box) => {
              box.style.setProperty("overflow", "visible", "important");
              box.style.setProperty("padding-bottom", "10px", "important");
            });

            doc.querySelectorAll(".sim-delivery-mix-wrap").forEach((marker) => {
              const root = marker.closest('[class*="st-key-sim_grp_"]')
                || marker.closest('[data-testid="stVerticalBlockBorderWrapper"]');
              if (!root) return;
              root.querySelectorAll('[data-testid="stHorizontalBlock"]:has(.sim-field-row-marker)').forEach((row) => {
                if (row.querySelector(".sim-section-header-marker")) return;
                const isLast = Boolean(row.querySelector(".sim-field-row-last"));
                row.style.setProperty("padding", "10px", "important");
                row.style.setProperty("margin", "0", "important");
                row.style.setProperty("gap", "8px", "important");
                row.style.setProperty("align-items", "center", "important");
                row.style.setProperty("box-sizing", "border-box", "important");
                row.style.setProperty("width", "100%", "important");
                row.style.setProperty("background", "#ffffff", "important");
                row.style.setProperty("display", "flex", "important");
                row.style.setProperty("min-height", "60px", "important");
                row.style.setProperty("border-bottom", isLast ? "none" : "1px solid #000000", "important");
                row.querySelectorAll(':scope > [data-testid="column"]').forEach((col, idx) => {
                  col.style.setProperty("display", "flex", "important");
                  col.style.setProperty("align-items", "center", "important");
                  col.style.setProperty("min-height", "40px", "important");
                  col.style.setProperty("justify-content", idx === 0 ? "flex-start" : "flex-end", "important");
                  col.querySelectorAll('[data-testid="stVerticalBlock"]').forEach((vb) => {
                    vb.style.setProperty("display", "flex", "important");
                    vb.style.setProperty("flex-direction", "column", "important");
                    vb.style.setProperty("align-items", idx === 0 ? "flex-start" : "flex-end", "important");
                    vb.style.setProperty("justify-content", "center", "important");
                    vb.style.setProperty("width", "100%", "important");
                    vb.style.setProperty("min-height", "40px", "important");
                    vb.style.setProperty("margin", "0", "important");
                    vb.style.setProperty("padding", "0", "important");
                    vb.style.setProperty("gap", "0", "important");
                  });
                  col.querySelectorAll('[data-testid="stElementContainer"], [data-testid="stMarkdownContainer"]').forEach((el) => {
                    if (el.querySelector(".sim-field-row-marker")) return;
                    el.style.setProperty("display", "flex", "important");
                    el.style.setProperty("align-items", "center", "important");
                    el.style.setProperty("justify-content", idx === 0 ? "flex-start" : "flex-end", "important");
                    el.style.setProperty("width", "100%", "important");
                    el.style.setProperty("min-height", "40px", "important");
                    el.style.setProperty("margin", "0", "important");
                    el.style.setProperty("padding", "0", "important");
                  });
                });
              });
              root.querySelectorAll(".sim-dd-row-label").forEach((label) => {
                label.style.setProperty("display", "flex", "important");
                label.style.setProperty("align-items", "center", "important");
                label.style.setProperty("min-height", "40px", "important");
                label.style.setProperty("margin", "0", "important");
                label.style.setProperty("padding", "0", "important");
              });
              root.querySelectorAll(".sim-pct-input-marker").forEach((marker) => {
                const col = marker.closest('[data-testid="column"]');
                if (!col || !root.contains(col)) return;
                const wrap = col.querySelector('div[data-baseweb="input"]');
                if (wrap) paintPctInputChip(wrap);
              });
              root.querySelectorAll(".sim-dd-row-divider").forEach((line) => {
                line.style.setProperty("display", "block", "important");
                line.style.setProperty("width", "100%", "important");
                line.style.setProperty("max-width", "100%", "important");
                line.style.setProperty("height", "0", "important");
                line.style.setProperty("margin", "0", "important");
                line.style.setProperty("padding", "0", "important");
                line.style.setProperty("border", "none", "important");
                line.style.setProperty("border-top", "1px solid #000000", "important");
                line.style.setProperty("background", "transparent", "important");
                const ec = line.closest('[data-testid="stElementContainer"]');
                if (ec) {
                  ec.style.setProperty("margin", "0", "important");
                  ec.style.setProperty("padding", "0", "important");
                  ec.style.setProperty("width", "100%", "important");
                }
              });
            });

            doc.querySelectorAll('[class*="st-key-sim_save_"] button, [class*="st-key-sim_toggle_"] button').forEach((btn) => {
              btn.style.setProperty("border-radius", "8px", "important");
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
              const panelGap = "12px";
              const panelDdWidth = "100%";
              const panelFilterPad = "{_PANEL_HEADER_FILTER_PAD}";
              const navy = "#042A57";
              root.querySelectorAll('[class*="st-key-sim_panel_filters_wrap"]').forEach((wrap) => {
                wrap.style.setProperty("padding", panelFilterPad, "important");
                wrap.style.setProperty("box-sizing", "border-box", "important");
                wrap.style.setProperty("background", navy, "important");
                wrap.style.setProperty("background-color", navy, "important");
                wrap.style.setProperty("margin", "0", "important");
              });
              root.querySelectorAll('[class*="st-key-sim_panel_filters_wrap"] [data-testid="stHorizontalBlock"]').forEach((row) => {
                if (!row.querySelector(".sim-panel-period-col-marker")) return;
                row.style.setProperty("justify-content", "space-between", "important");
                row.style.setProperty("align-items", "flex-end", "important");
                row.style.setProperty("width", "calc(100% - 32px)", "important");
                row.style.setProperty("max-width", "calc(100% - 32px)", "important");
                row.style.setProperty("gap", panelGap, "important");
                row.style.setProperty("padding", "0", "important");
                row.style.setProperty("margin", "0 16px 16px 16px", "important");
                row.style.setProperty("box-sizing", "border-box", "important");
                row.querySelectorAll(':scope > [data-testid="column"]').forEach((col) => {
                  col.style.setProperty("padding-left", "0", "important");
                  col.style.setProperty("padding-right", "0", "important");
                  col.style.setProperty("align-self", "flex-end", "important");
                  if (col.querySelector(".sim-planning-level-marker")) {
                    col.style.setProperty("flex", "1 1 auto", "important");
                    col.style.setProperty("min-width", "260px", "important");
                  } else if (col.querySelector(".sim-affected-records-marker")) {
                    col.style.setProperty("flex", "0 0 auto", "important");
                    col.style.setProperty("margin-left", "auto", "important");
                  } else {
                    col.style.setProperty("flex", "0 0 auto", "important");
                    col.style.setProperty("width", "auto", "important");
                    col.style.setProperty("max-width", "none", "important");
                  }
                });
              });
              root.querySelectorAll('[data-testid="column"]:has(.sim-panel-dd-75-marker) > div[data-testid="stVerticalBlock"]').forEach((vb) => {
                vb.style.setProperty("align-items", "flex-start", "important");
                vb.style.setProperty("width", "100%", "important");
              });
              root.querySelectorAll('[data-testid="column"]:has(.elx-filter-panel):not(:has(.sim-panel-dd-75-marker)) > div[data-testid="stVerticalBlock"]').forEach((vb) => {
                vb.style.setProperty("align-items", "flex-start", "important");
                vb.style.setProperty("width", "auto", "important");
              });
              root.querySelectorAll(".elx-filter-upper-lbl, .elx-filter-panel-lbl").forEach((lbl) => {
                const inAffectedRow = !!lbl.closest(".sim-affected-records");
                lbl.style.setProperty("display", inAffectedRow ? "inline" : "block", "important");
                lbl.style.setProperty("color", "#ffffff", "important");
                lbl.style.setProperty("-webkit-text-fill-color", "#ffffff", "important");
                lbl.style.setProperty("font-size", inAffectedRow ? "11px" : "11px", "important");
                lbl.style.setProperty("font-weight", "600", "important");
                lbl.style.setProperty("opacity", "1", "important");
                lbl.style.setProperty("visibility", "visible", "important");
                if (inAffectedRow) {
                  lbl.style.setProperty("margin", "0", "important");
                  lbl.style.setProperty("white-space", "nowrap", "important");
                }
                const md = lbl.closest('[data-testid="stMarkdownContainer"]');
                if (md) {
                  md.style.setProperty("color", "#ffffff", "important");
                  md.querySelectorAll("p").forEach((p) => {
                    p.style.setProperty("color", "#ffffff", "important");
                    p.style.setProperty("-webkit-text-fill-color", "#ffffff", "important");
                  });
                }
              });
              root.querySelectorAll(".sim-affected-records").forEach((row) => {
                row.style.setProperty("display", "flex", "important");
                row.style.setProperty("align-items", "center", "important");
                row.style.setProperty("justify-content", "flex-end", "important");
                row.style.setProperty("gap", "8px", "important");
                row.style.setProperty("flex-wrap", "nowrap", "important");
                row.style.setProperty("white-space", "nowrap", "important");
                row.style.setProperty("min-height", "32px", "important");
              });
              root.querySelectorAll(".sim-affected-records-val").forEach((val) => {
                val.style.setProperty("display", "inline-flex", "important");
                val.style.setProperty("align-items", "center", "important");
                val.style.setProperty("font-size", "14px", "important");
                val.style.setProperty("font-weight", "700", "important");
                val.style.setProperty("color", "#ffffff", "important");
              });
              root.querySelectorAll('[class*="st-key-sim_plan_btn_"] button').forEach((btn) => {
                const isDisabled = btn.disabled;
                const isPrimary = btn.getAttribute("kind") === "primary" && !isDisabled;
                const disabledBg = "#CBCBCB1A";
                const disabledText = "#70737B";
                const enabledText = "#ffffff";
                const primaryBg = "rgba(255, 255, 255, 0.22)";
                let textColor = disabledText;
                let bg = disabledBg;
                if (isPrimary) {
                  textColor = enabledText;
                  bg = primaryBg;
                } else if (!isDisabled) {
                  textColor = enabledText;
                  bg = "#FFFFFF1A";
                }
                btn.style.setProperty("border", "none", "important");
                btn.style.setProperty("border-radius", "4px", "important");
                btn.style.setProperty("box-shadow", "none", "important");
                btn.style.setProperty("color", textColor, "important");
                btn.style.setProperty("background", bg, "important");
                btn.style.setProperty("background-color", bg, "important");
                btn.style.setProperty("background-image", "none", "important");
                if (isDisabled) {
                  btn.style.setProperty("opacity", "1", "important");
                  btn.style.setProperty("cursor", "not-allowed", "important");
                } else {
                  btn.style.setProperty("cursor", "pointer", "important");
                }
                btn.querySelectorAll("p, span, div, [data-testid='stMarkdownContainer']").forEach((inner) => {
                  inner.style.setProperty("background", "transparent", "important");
                  inner.style.setProperty("background-color", "transparent", "important");
                  inner.style.setProperty("color", textColor, "important");
                  inner.style.setProperty("-webkit-text-fill-color", textColor, "important");
                  inner.style.setProperty("box-shadow", "none", "important");
                });
              });
              root.querySelectorAll('[data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"], [data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div').forEach((sel) => {
                sel.style.setProperty("width", panelDdWidth, "important");
                sel.style.setProperty("min-width", "0", "important");
                sel.style.setProperty("max-width", panelDdWidth, "important");
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
              root.querySelectorAll('[data-testid="column"]:has(.sim-panel-dd-75-marker) div[data-baseweb="select"] > div').forEach((sel) => {
                sel.style.setProperty("width", panelDdWidth, "important");
                sel.style.setProperty("min-width", "0", "important");
                sel.style.setProperty("max-width", panelDdWidth, "important");
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
                ).forEach((node) => {
                  if (node.closest('[class*="st-key-sim_plan_btn_"]')) return;
                  paintPanelHeaderNode(node, navy);
                });
                const wrap = root.querySelector(".sim-panel-header-wrap");
                const wrapRow = wrap?.closest('[data-testid="stElementContainer"]');
                const pillsRow = wrapRow?.nextElementSibling;
                if (wrapRow) paintPanelHeaderNode(wrapRow, navy);
                if (pillsRow && pillsRow.matches('[data-testid="stElementContainer"]')) {
                  paintPanelHeaderNode(pillsRow, navy);
                  pillsRow.style.setProperty("padding", "0 16px 16px 16px", "important");
                  pillsRow.style.setProperty("margin", "0", "important");
                  pillsRow.style.setProperty("box-sizing", "border-box", "important");
                  pillsRow.querySelectorAll(
                    '[data-testid="stHorizontalBlock"], [data-testid="column"], [data-testid="stSelectbox"]'
                  ).forEach((node) => paintPanelHeaderNode(node, navy));
                }
                paintPanelHeaderDropdowns(root);
                doc.querySelectorAll('[class*="st-key-sim_panel_filters_wrap"]').forEach((wrap) => {
                  wrap.style.setProperty("padding", "0 16px 16px 16px", "important");
                  wrap.style.setProperty("box-sizing", "border-box", "important");
                });
              });
            }
            paintPanelHeader();
            paintPanelHeaderDropdowns(doc);

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
            if (++ticks > 80) clearInterval(timer);
          }, 125);
          const obs = new MutationObserver(paint);
          obs.observe(doc.body, { childList: true, subtree: true });
          setTimeout(() => obs.disconnect(), 30000);
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
    if _is_inflation_rates_group(group):
        config = db_st.get_inflation_matrix_config()
        fake_field = {"value": 0.0, "min": None, "max": None, "step": 0.1}
        return [
            (idx, {**fake_field, "_infl_row": row["key"], "_infl_col": None})
            for idx, row in enumerate(config["input_rows"])
        ]
    if _is_process_cost_group(group):
        config = db_st.get_process_cost_matrix_config()
        fake_field = {"value": 0, "min": None, "max": None, "step": None}
        return [
            (idx, {**fake_field, "_pc_row": row["key"]})
            for idx, row in enumerate(config["input_rows"])
        ]
    if _is_delivery_mix_group(group):
        return _delivery_mix_rows(group)
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
    if _is_inflation_rates_group(group) and "_infl_row" in field:
        if field.get("_infl_col") is None:
            config = db_st.get_inflation_matrix_config()
            return any(
                _infl_matrix_cell_has_user_entry(group_index, field["_infl_row"], col)
                for col in range(len(config["columns"]))
            )
        return _infl_matrix_cell_has_user_entry(group_index, field["_infl_row"], field["_infl_col"])
    if _is_process_cost_group(group) and "_pc_row" in field:
        config = db_st.get_process_cost_matrix_config()
        return any(
            _pc_matrix_cell_has_user_entry(group_index, field["_pc_row"], col)
            for col in range(len(config["columns"]))
        )
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
_PENDING_SAVE_KEY = "sim_pending_save_group"
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
_PROCESS_COST_TITLES = frozenset({"Process cost", "Project Costs (EUR)"})
_PC_TOTAL_SIDEBAR_LABELS = {
    "PTC": "PTC Total",
    "STC": "STC Total",
    "SWC Var": "SWC Var",
    "SWC Fixed": "SWC Fixed",
    "SWC Obs. fix.": "SWC Obs Fixed",
}
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


def _infl_draft_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_infl_draft_{group_index}_{row_key}_{col}"


def _infl_value_from_state(raw: Any, default: float) -> float:
    if isinstance(raw, (int, float)):
        return float(raw)
    parsed = _parse_infl_cell_text(str(raw))
    return float(default if parsed is None else parsed)


def _infl_matrix_raw_value(group_index: int, row_key: str, col: int) -> float:
    """Read a matrix cell from widget, draft, or saved state."""
    default = _infl_matrix_default(row_key, col)
    key = _infl_matrix_key(group_index, row_key, col)
    saved_key = _infl_matrix_saved_key(group_index, row_key, col)
    draft_key = _infl_draft_key(group_index, row_key, col)
    if _group_is_saved(group_index):
        state_keys = (saved_key, key, draft_key)
    else:
        state_keys = (key, draft_key, saved_key)
    for state_key in state_keys:
        if state_key not in st.session_state:
            continue
        return _infl_value_from_state(st.session_state[state_key], default)
    return float(default)


def _infl_matrix_persist_value(group_index: int, row_key: str, col: int) -> float:
    """Read live widget value for Save — widget state wins over stale drafts."""
    default = _infl_matrix_default(row_key, col)
    key = _infl_matrix_key(group_index, row_key, col)
    draft_key = _infl_draft_key(group_index, row_key, col)
    for state_key in (key, draft_key):
        if state_key not in st.session_state:
            continue
        return _infl_value_from_state(st.session_state[state_key], default)
    return float(default)


def _sync_infl_draft_cell(group_index: int, row_key: str, col: int) -> None:
    key = _infl_matrix_key(group_index, row_key, col)
    draft_key = _infl_draft_key(group_index, row_key, col)
    default = _infl_matrix_default(row_key, col)
    raw = st.session_state.get(key, "")
    st.session_state[draft_key] = _infl_display_str(_infl_value_from_state(raw, default))


def _capture_infl_matrix_drafts(group_index: int) -> None:
    config = db_st.get_inflation_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            _sync_infl_draft_cell(group_index, row["key"], col)


def _persist_infl_matrix_displays(index: int) -> None:
    config = db_st.get_inflation_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            value = _infl_matrix_persist_value(index, row["key"], col)
            display = _infl_display_str(value)
            saved_key = _infl_matrix_saved_key(index, row["key"], col)
            draft_key = _infl_draft_key(index, row["key"], col)
            st.session_state[saved_key] = display
            st.session_state[draft_key] = display


def _persist_pc_matrix_displays(index: int) -> None:
    config = db_st.get_process_cost_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            value = _pc_matrix_persist_value(index, row["key"], col)
            display = _pc_display_str(value)
            saved_key = _pc_matrix_saved_key(index, row["key"], col)
            draft_key = _pc_draft_key(index, row["key"], col)
            st.session_state[saved_key] = display
            st.session_state[draft_key] = display


def _persist_group_field_displays(index: int, group: dict[str, Any]) -> None:
    """Freeze entered values on Save so locked rows keep what the user typed."""
    if _is_inflation_rates_group(group):
        _persist_infl_matrix_displays(index)
        return
    if _is_process_cost_group(group):
        _persist_pc_matrix_displays(index)
        return
    if _is_delivery_mix_group(group):
        for fi, field in _delivery_mix_rows(group):
            value = _delivery_mix_persist_value(index, fi, field)
            display = _field_display_str(field, value)
            st.session_state[_saved_display_key(index, fi)] = display
        return
    for fi, field in enumerate(group.get("fields", [])):
        if _is_inflation_calculated_field(field):
            continue
        key = _field_key(index, fi)
        raw = st.session_state.get(key, "")
        parsed = _parse_field_text(field, str(raw))
        value = parsed if parsed is not None else field["value"]
        display = _field_display_str(field, value)
        st.session_state[_saved_display_key(index, fi)] = display


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


def _dm_staged_key(group_index: int) -> str:
    return f"sim_dm_staged_{group_index}"


def _sync_dm_field_staged(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
) -> None:
    """Keep non-widget staging keys in sync while the user edits DD%."""
    key = _field_key(group_index, field_index)
    parsed = _parse_field_text(field, str(st.session_state.get(key, "")))
    if parsed is None:
        return
    staged = dict(st.session_state.get(_dm_staged_key(group_index), {}))
    staged[field_index] = int(parsed)
    st.session_state[_dm_staged_key(group_index)] = staged


def _capture_dm_staged_values(group_index: int, group: dict[str, Any]) -> None:
    """Copy live DD% widget values into non-widget staging keys (safe after render)."""
    staged: dict[int, int] = dict(st.session_state.get(_dm_staged_key(group_index), {}))
    for fi, field in _delivery_mix_rows(group):
        key = _field_key(group_index, fi)
        if key not in st.session_state:
            continue
        parsed = _parse_field_text(field, str(st.session_state[key]))
        if parsed is not None:
            staged[fi] = int(parsed)
    st.session_state[_dm_staged_key(group_index)] = staged


def _is_delivery_mix_group(group: dict[str, Any]) -> bool:
    return group.get("title") == _DELIVERY_MIX_TITLE


def _delivery_mix_effective_dd(dd_change: int | float, user_input: int | float) -> int:
    """Effective DD% = baseline DD_change + user adjustment (0–100)."""
    return max(0, min(100, int(round(dd_change + user_input))))


def _delivery_mix_persist_value(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
) -> int:
    """Read live widget value for Save — never write back to the widget key."""
    staged: dict[int, int] = st.session_state.get(_dm_staged_key(group_index), {})
    if field_index in staged:
        return int(staged[field_index])
    key = _field_key(group_index, field_index)
    saved_key = _saved_display_key(group_index, field_index)
    default = int(field["value"])
    for state_key in (key, saved_key):
        if state_key not in st.session_state:
            continue
        parsed = _parse_field_text(field, str(st.session_state[state_key]))
        if parsed is not None:
            return int(parsed)
    return default


def _delivery_mix_user_input(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
) -> int:
    """Read DD% adjustment from widget or saved display."""
    staged: dict[int, int] = st.session_state.get(_dm_staged_key(group_index), {})
    if field_index in staged:
        return int(staged[field_index])
    key = _field_key(group_index, field_index)
    saved_key = _saved_display_key(group_index, field_index)
    default = int(field["value"])
    if _group_is_saved(group_index):
        state_keys = (saved_key, key)
    else:
        state_keys = (key, saved_key)
    for state_key in state_keys:
        if state_key not in st.session_state:
            continue
        parsed = _parse_field_text(field, str(st.session_state[state_key]))
        if parsed is not None:
            return int(parsed)
    return default


def _dm_calc_row_for_field(
    calc_rows: list[dict[str, Any]],
    field_index: int,
    group_index: int,
    group: dict[str, Any],
) -> dict[str, Any] | None:
    for row in calc_rows:
        if row.get("field_index") == field_index:
            return row
    for row_idx, (fi, _field) in enumerate(_delivery_mix_rows(group)):
        if fi == field_index and row_idx < len(calc_rows):
            return calc_rows[row_idx]
    return None


def _compute_delivery_mix(group_index: int, group: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fi, field in _delivery_mix_rows(group):
        user_input = _delivery_mix_user_input(group_index, fi, field)
        dd_change = int(field.get("dd_change", 0))
        rows.append({
            "field_index": fi,
            "dimension": field.get("dim_key", ""),
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
    calc_row = _dm_calc_row_for_field(calc_rows, field_index, group_index, group)
    if calc_row is not None:
        return int(calc_row["effective_dd"])
    user_input = _delivery_mix_user_input(group_index, field_index, field)
    return _delivery_mix_effective_dd(field.get("dd_change", 0), user_input)


def _infl_calc_key(group_index: int) -> str:
    return f"sim_infl_calc_{group_index}"


def _pc_calc_key(group_index: int) -> str:
    return f"sim_pc_calc_{group_index}"


def _is_inflation_rates_group(group: dict[str, Any]) -> bool:
    return group.get("title") == _INFLATION_RATES_TITLE


def _is_process_cost_group(group: dict[str, Any]) -> bool:
    return group.get("title") in _PROCESS_COST_TITLES


_INFL_MATRIX_VERSION = 5
_PC_MATRIX_VERSION = 4
_INFL_PCT_FIELD = {"value": 0.0, "min": None, "max": None, "step": 0.1}
_PC_INT_FIELD = {"value": 0, "min": None, "max": None, "step": None}


def _infl_matrix_row_spec(row_key: str) -> dict[str, Any]:
    for row in db_st.get_inflation_matrix_config()["input_rows"]:
        if row["key"] == row_key:
            return row
    raise KeyError(row_key)


def _infl_matrix_default(row_key: str, col: int) -> float:
    return float(_infl_matrix_row_spec(row_key)["defaults"][col])


def _infl_matrix_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_infl_{group_index}_{row_key}_{col}"


def _infl_matrix_saved_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_infl_saved_{group_index}_{row_key}_{col}"


def _infl_matrix_ver_key(group_index: int) -> str:
    return f"sim_infl_ver_{group_index}"


def _parse_infl_cell_text(raw: str) -> float | None:
    text = (raw or "").strip().replace("%", "").replace(",", "")
    if not text or text == "-":
        return None
    try:
        return round(float(text), 1)
    except ValueError:
        return None


def _ensure_infl_matrix_version(group_index: int) -> None:
    """Reset all inflation matrix cells when defaults/version change."""
    ver_key = _infl_matrix_ver_key(group_index)
    if st.session_state.get(ver_key) == _INFL_MATRIX_VERSION:
        return
    config = db_st.get_inflation_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            st.session_state.pop(_infl_matrix_key(group_index, row["key"], col), None)
            st.session_state.pop(_infl_matrix_saved_key(group_index, row["key"], col), None)
            st.session_state.pop(_infl_draft_key(group_index, row["key"], col), None)
    st.session_state[ver_key] = _INFL_MATRIX_VERSION


def _ensure_infl_matrix_cell_state(group_index: int, row_key: str, col: int) -> None:
    _ensure_infl_matrix_version(group_index)
    key = _infl_matrix_key(group_index, row_key, col)
    draft_key = _infl_draft_key(group_index, row_key, col)
    default = _infl_matrix_default(row_key, col)
    default_display = _infl_display_str(default)
    if draft_key not in st.session_state:
        st.session_state[draft_key] = default_display
    if key not in st.session_state:
        st.session_state[key] = st.session_state[draft_key]
    elif isinstance(st.session_state[key], (int, float)):
        st.session_state[key] = _infl_display_str(st.session_state[key])


def _infl_matrix_cell_value(group_index: int, row_key: str, col: int) -> float:
    return _infl_matrix_raw_value(group_index, row_key, col)


def _infl_matrix_cell_display(group_index: int, row_key: str, col: int) -> str:
    saved_key = _infl_matrix_saved_key(group_index, row_key, col)
    if saved_key in st.session_state:
        return str(st.session_state[saved_key])
    return _field_display_str(_INFL_PCT_FIELD, _infl_matrix_cell_value(group_index, row_key, col))


def _infl_matrix_cell_has_user_entry(group_index: int, row_key: str, col: int) -> bool:
    key = _infl_matrix_key(group_index, row_key, col)
    default = _infl_matrix_default(row_key, col)
    raw = st.session_state.get(key, _field_display_str(_INFL_PCT_FIELD, default))
    parsed = _parse_infl_cell_text(str(raw))
    if parsed is None:
        return False
    return abs(float(parsed) - float(default)) > 1e-9


def _infl_matrix_vector(group_index: int, row_key: str) -> list[float]:
    config = db_st.get_inflation_matrix_config()
    return [_infl_matrix_cell_value(group_index, row_key, col) for col in range(len(config["columns"]))]


def _inflation_input_total(group_index: int) -> float:
    """Sum of user-entered Inflation row values across all columns."""
    return round(sum(_infl_matrix_vector(group_index, "inflation")), 1)


def _inflation_cell_values(inflation_vector: tuple[float, ...] | list[float], impact: list[int] | tuple[int, ...] | list[float]) -> list[float]:
    """Effective % per column = impact[col] × inflation[col]."""
    return [round(float(inflation_vector[i]) * float(impact[i]), 1) for i in range(len(inflation_vector))]


def _compute_inflation_matrix(group_index: int) -> list[dict[str, Any]]:
    """Compute PTC/STC/SWC rows from saved inflation + impact matrix inputs."""
    config = db_st.get_inflation_matrix_config()
    inflation_vector = _infl_matrix_vector(group_index, "inflation")
    rows: list[dict[str, Any]] = []
    for calc_row in config["calc_rows"]:
        impact = _infl_matrix_vector(group_index, calc_row["impact_key"])
        cells = _inflation_cell_values(inflation_vector, impact)
        rows.append({
            "key": calc_row["key"],
            "name": calc_row["label"],
            "name_tags": calc_row.get("name_tags", []),
            "cells": cells,
            "effective_total": round(sum(cells), 1),
        })
    return rows


def _pc_matrix_row_spec(row_key: str) -> dict[str, Any]:
    for row in db_st.get_process_cost_matrix_config()["input_rows"]:
        if row["key"] == row_key:
            return row
    raise KeyError(row_key)


def _pc_matrix_default(row_key: str, col: int) -> int:
    return int(_pc_matrix_row_spec(row_key)["defaults"][col])


def _pc_matrix_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_pc_{group_index}_{row_key}_{col}"


def _pc_matrix_saved_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_pc_saved_{group_index}_{row_key}_{col}"


def _pc_draft_key(group_index: int, row_key: str, col: int) -> str:
    return f"sim_pc_draft_{group_index}_{row_key}_{col}"


def _pc_staged_key(group_index: int) -> str:
    return f"sim_pc_staged_{group_index}"


def _pc_staged_cell_id(row_key: str, col: int) -> str:
    return f"{row_key}_{col}"


def _pc_matrix_ver_key(group_index: int) -> str:
    return f"sim_pc_ver_{group_index}"


def _parse_pc_cell_text(raw: str) -> int | None:
    text = (raw or "").strip().replace(",", "").replace(" ", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _pc_value_from_state(raw: Any, default: int) -> int:
    if isinstance(raw, (int, float)):
        return int(round(float(raw)))
    parsed = _parse_pc_cell_text(str(raw))
    return int(default if parsed is None else parsed)


def _pc_display_str(value: Any) -> str:
    return str(int(round(float(value))))


def _ensure_pc_matrix_version(group_index: int) -> None:
    """Reset all process-cost cells when matrix defaults/version change."""
    ver_key = _pc_matrix_ver_key(group_index)
    if st.session_state.get(ver_key) == _PC_MATRIX_VERSION:
        return
    config = db_st.get_process_cost_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            st.session_state.pop(_pc_matrix_key(group_index, row["key"], col), None)
            st.session_state.pop(_pc_matrix_saved_key(group_index, row["key"], col), None)
            st.session_state.pop(_pc_draft_key(group_index, row["key"], col), None)
    st.session_state[ver_key] = _PC_MATRIX_VERSION


def _ensure_pc_matrix_cell_state(group_index: int, row_key: str, col: int) -> None:
    _ensure_pc_matrix_version(group_index)
    key = _pc_matrix_key(group_index, row_key, col)
    default = _pc_matrix_default(row_key, col)
    if key not in st.session_state:
        st.session_state[key] = _pc_display_str(default)
    elif isinstance(st.session_state[key], (int, float)):
        st.session_state[key] = _pc_display_str(st.session_state[key])


def _pc_matrix_raw_value(group_index: int, row_key: str, col: int) -> int:
    """Read a process-cost cell from widget, draft, or saved state."""
    default = _pc_matrix_default(row_key, col)
    key = _pc_matrix_key(group_index, row_key, col)
    saved_key = _pc_matrix_saved_key(group_index, row_key, col)
    draft_key = _pc_draft_key(group_index, row_key, col)
    if _group_is_saved(group_index):
        state_keys = (saved_key, key, draft_key)
    else:
        state_keys = (key, draft_key, saved_key)
    for state_key in state_keys:
        if state_key not in st.session_state:
            continue
        return _pc_value_from_state(st.session_state[state_key], default)
    return default


def _pc_read_cell_live_value(group_index: int, row_key: str, col: int) -> int:
    """Best-effort read from widget/draft session keys (no widget instantiation required)."""
    default = _pc_matrix_default(row_key, col)
    key = _pc_matrix_key(group_index, row_key, col)
    draft_key = _pc_draft_key(group_index, row_key, col)
    best = default
    for state_key in (key, draft_key):
        if state_key not in st.session_state:
            continue
        value = _pc_value_from_state(st.session_state[state_key], default)
        if value != default or best == default:
            best = value
    return best


def _pc_matrix_persist_value(group_index: int, row_key: str, col: int) -> int:
    """Read staged or live values for Save — never write back to widget keys."""
    default = _pc_matrix_default(row_key, col)
    cell_id = _pc_staged_cell_id(row_key, col)
    staged: dict[str, int] = st.session_state.get(_pc_staged_key(group_index), {})
    if cell_id in staged:
        return int(staged[cell_id])
    return _pc_read_cell_live_value(group_index, row_key, col)


def _sync_pc_draft_cell(group_index: int, row_key: str, col: int) -> None:
    draft_key = _pc_draft_key(group_index, row_key, col)
    default = _pc_matrix_default(row_key, col)
    st.session_state[draft_key] = _pc_display_str(
        _pc_read_cell_live_value(group_index, row_key, col)
    )


def _capture_pc_matrix_drafts(group_index: int) -> None:
    config = db_st.get_process_cost_matrix_config()
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            _sync_pc_draft_cell(group_index, row["key"], col)


def _capture_pc_staged_values(group_index: int, *, preserve_non_default: bool = False) -> None:
    """Copy live process-cost values into staging keys (safe after render or on Save click)."""
    config = db_st.get_process_cost_matrix_config()
    staged: dict[str, int] = dict(st.session_state.get(_pc_staged_key(group_index), {}))
    for row in config["input_rows"]:
        for col in range(len(config["columns"])):
            cell_id = _pc_staged_cell_id(row["key"], col)
            default = _pc_matrix_default(row["key"], col)
            new_value = _pc_read_cell_live_value(group_index, row["key"], col)
            if preserve_non_default:
                prev = staged.get(cell_id)
                if prev is not None and prev != default and new_value == default:
                    continue
            staged[cell_id] = new_value
    st.session_state[_pc_staged_key(group_index)] = staged


def _pc_matrix_cell_value(group_index: int, row_key: str, col: int) -> int:
    return _pc_matrix_raw_value(group_index, row_key, col)


def _pc_matrix_cell_display(group_index: int, row_key: str, col: int) -> str:
    saved_key = _pc_matrix_saved_key(group_index, row_key, col)
    if saved_key in st.session_state:
        return str(st.session_state[saved_key])
    return _pc_display_str(_pc_matrix_cell_value(group_index, row_key, col))


def _pc_matrix_cell_has_user_entry(group_index: int, row_key: str, col: int) -> bool:
    default = _pc_matrix_default(row_key, col)
    return _pc_matrix_raw_value(group_index, row_key, col) != int(default)


def _compute_pc_column_totals(group_index: int) -> list[int]:
    config = db_st.get_process_cost_matrix_config()
    totals: list[int] = []
    for col in range(len(config["columns"])):
        total = sum(
            _pc_matrix_cell_value(group_index, row["key"], col)
            for row in config["input_rows"]
        )
        totals.append(int(total))
    return totals


def _format_share_pct(value: float) -> str:
    """Display share % with up to 2 decimal places."""
    rounded = round(float(value), 2)
    if abs(rounded) < 1e-9:
        return "0%"
    text = f"{abs(rounded):.2f}".rstrip("0").rstrip(".")
    sign = "+" if rounded > 0 else "-"
    return f"{sign}{text}%"


def _compute_process_cost_share_pct(project_total: float, company_baseline: float) -> float:
    if not company_baseline:
        return 0.0
    return round(project_total / company_baseline * 100, 4)


def _compute_process_cost_calculation(group_index: int) -> dict[str, Any]:
    """Steps 1–3: company baselines → share % → PLC line impacts."""
    config = db_st.get_process_cost_matrix_config()
    company_code = _resolved_panel_company_code()
    baselines = db_st.get_process_cost_company_baselines(company_code)
    totals = _compute_pc_column_totals(group_index)
    column_shares: list[dict[str, Any]] = []
    share_by_column: dict[str, float] = {}
    for col_idx, col_name in enumerate(config["columns"]):
        project_total = float(totals[col_idx])
        company_total = float(baselines.get(col_name, 0.0))
        share_pct = _compute_process_cost_share_pct(project_total, company_total)
        share_by_column[col_name] = share_pct
        column_shares.append({
            "column": col_name,
            "project_total": project_total,
            "company_baseline": company_total,
            "share_pct": share_pct,
        })
    plc_impacts: list[dict[str, Any]] = []
    for plc_row in db_st.get_process_cost_plc_forecasts(company_code):
        forecasts = plc_row.get("forecast_costs") or {}
        impacts: dict[str, float] = {}
        for col_name in config["columns"]:
            forecast_cost = float(forecasts.get(col_name, 0.0))
            share_pct = share_by_column.get(col_name, 0.0)
            impacts[col_name] = round(forecast_cost * share_pct / 100, 2)
        plc_impacts.append({
            "plc": plc_row.get("plc", ""),
            "product_subgroup": plc_row.get("product_subgroup", ""),
            "ext_mat_group": plc_row.get("ext_mat_group", ""),
            "forecast_costs": forecasts,
            "impacts": impacts,
        })
    return {
        "company_code": company_code,
        "column_shares": column_shares,
        "plc_impacts": plc_impacts,
        "company_baselines": baselines,
    }


def _process_cost_calc_state(group_index: int) -> dict[str, Any]:
    """Always recompute so share % reflects current matrix totals."""
    calc = _compute_process_cost_calculation(group_index)
    st.session_state[_pc_calc_key(group_index)] = calc
    return calc


def _refresh_pc_calc_state(group_index: int) -> None:
    st.session_state[_pc_calc_key(group_index)] = _compute_process_cost_calculation(group_index)


def _pc_total_sidebar_label(col_name: str) -> str:
    return _PC_TOTAL_SIDEBAR_LABELS.get(col_name, f"{col_name} Total")


def _format_process_cost_total_eur(value: int | float) -> str:
    """Sidebar totals — k suffix only when total >= 1000 (10000 → -€10k, 10 → -€10)."""
    amount = int(round(float(value)))
    if amount == 0:
        return "€0"
    abs_amount = abs(amount)
    if abs_amount >= 1000:
        k = abs_amount / 1000
        if abs(k - round(k)) < 1e-9:
            return f"-€{int(round(k))}k"
        return f"-€{k:.1f}k"
    return f"-€{abs_amount}"


def _pc_column_from_sidebar_label(label: str) -> str:
    for col, sidebar_label in _PC_TOTAL_SIDEBAR_LABELS.items():
        if sidebar_label == label:
            return col
    return label


def _process_cost_project_totals_by_column(
    group_index: int,
    entry: dict[str, Any] | None = None,
) -> dict[str, float]:
    """Project cost totals per column — matrix first, saved snapshot fills gaps."""
    config = db_st.get_process_cost_matrix_config()
    matrix_totals = _compute_pc_column_totals(group_index)
    by_col: dict[str, float] = {
        col_name: float(matrix_totals[col_idx])
        for col_idx, col_name in enumerate(config["columns"])
    }
    if not entry:
        return by_col
    for field in entry.get("calculated_fields") or []:
        if field.get("kind") == "share":
            continue
        raw = field.get("value")
        if not isinstance(raw, (int, float)):
            continue
        name = str(field.get("name", ""))
        if name.startswith("Total — "):
            name = _pc_total_sidebar_label(name.removeprefix("Total — "))
        col_name = _pc_column_from_sidebar_label(name)
        saved_total = float(raw)
        if by_col.get(col_name, 0.0) == 0.0 and saved_total != 0.0:
            by_col[col_name] = saved_total
    return by_col


def _process_cost_share_by_column(
    group_index: int,
    entry: dict[str, Any] | None = None,
) -> dict[str, float]:
    company_code = _resolved_panel_company_code()
    baselines = db_st.get_process_cost_company_baselines(company_code)
    project_totals = _process_cost_project_totals_by_column(group_index, entry)
    return {
        col_name: _compute_process_cost_share_pct(project_totals.get(col_name, 0.0), baselines.get(col_name, 0.0))
        for col_name in db_st.get_process_cost_matrix_config()["columns"]
    }


def _process_cost_sidebar_display_rows(
    group_index: int,
    entry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Sidebar rows — calculated share % only (no euro totals)."""
    config = db_st.get_process_cost_matrix_config()
    share_by_col = _process_cost_share_by_column(group_index, entry)
    rows: list[dict[str, Any]] = []
    for col_name in config["columns"]:
        share_pct = share_by_col.get(col_name, 0.0)
        rows.append({
            "name": _pc_total_sidebar_label(col_name),
            "share_display": _format_share_pct(share_pct),
            "share_class": "red" if share_pct != 0 else "neutral",
        })
    return rows


def _process_cost_totals_display_rows(group_index: int) -> list[dict[str, Any]]:
    return _process_cost_sidebar_display_rows(group_index)


def _process_cost_share_display_rows(group_index: int) -> list[dict[str, Any]]:
    calc = _process_cost_calc_state(group_index)
    rows: list[dict[str, Any]] = []
    for share_row in calc.get("column_shares") or []:
        share_pct = float(share_row.get("share_pct", 0.0))
        col_name = str(share_row.get("column", ""))
        rows.append({
            "name": f"{col_name} Share",
            "value": _format_share_pct(share_pct),
            "value_class": "red" if share_pct != 0 else "neutral",
            "kind": "share",
        })
    return rows


def _process_cost_totals_from_entry(entry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in entry.get("calculated_fields") or []:
        if field.get("kind") == "share":
            continue
        raw = field.get("value", 0)
        if isinstance(raw, (int, float)):
            display = _format_process_cost_total_eur(raw)
        else:
            display = str(raw)
        name = str(field.get("name", ""))
        if name.startswith("Total — "):
            name = _pc_total_sidebar_label(name.removeprefix("Total — "))
        rows.append({
            "name": name,
            "value": display,
            "value_class": field.get("value_class", "red" if display != "€0" else "neutral"),
            "kind": "total",
        })
    return rows


def _process_cost_share_from_entry(entry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in entry.get("calculated_fields") or []:
        if field.get("kind") != "share":
            continue
        raw = field.get("value", 0)
        if isinstance(raw, (int, float)):
            display = _format_share_pct(float(raw))
        else:
            display = str(raw)
        rows.append({
            "name": str(field.get("name", "")),
            "value": display,
            "value_class": field.get("value_class", "neutral"),
            "kind": "share",
        })
    return rows


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


def _inflation_baseline_from_field(field: dict[str, Any]) -> float:
    if "infl_baseline" in field:
        return float(field["infl_baseline"])
    impact = field.get("impact") or ()
    inflation_vector = field.get("inflation_vector") or db_st.get_inflation_matrix_config()["input_rows"][0]["defaults"]
    return round(sum(_inflation_cell_values(inflation_vector, impact)), 1)


def _inflation_effective_total(baseline: float, user_input: float) -> float:
    return round(baseline + user_input, 1)


def _compute_inflation_rates(group_index: int, group: dict[str, Any]) -> list[dict[str, Any]]:
    return _compute_inflation_matrix(group_index)


def _inflation_calc_row_by_name(group_index: int, name: str) -> dict[str, Any] | None:
    calc_rows: list[dict[str, Any]] = st.session_state.get(_infl_calc_key(group_index), [])
    for row in calc_rows:
        if row.get("name") == name:
            return row
    return None


def _inflation_field_value(
    group_index: int,
    field_index: int,
    field: dict[str, Any],
    group: dict[str, Any],
) -> float:
    """Resolved inflation % for snapshots — uses saved calculation when available."""
    if _is_inflation_calculated_field(field):
        calc_row = _inflation_calc_row_by_name(group_index, field["name"])
        if calc_row is not None:
            return float(calc_row["effective_total"])
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
    st.session_state.pop(_PENDING_SAVE_KEY, None)
    st.session_state.pop(_SIM_SNAPSHOT_KEY, None)
    st.session_state.pop(_SIM_HISTORY_KEY, None)
    st.session_state[_SIDE_GAP_GEN_KEY] = st.session_state.get(_SIDE_GAP_GEN_KEY, 0) + 1
    for i, group in enumerate(groups):
        st.session_state[_saved_key(i)] = False
        st.session_state.pop(f"sim_open_{i}", None)
        st.session_state.pop(_dm_calc_key(i), None)
        st.session_state.pop(_dm_staged_key(i), None)
        st.session_state.pop(_infl_calc_key(i), None)
        st.session_state.pop(_infl_matrix_ver_key(i), None)
        st.session_state.pop(_pc_calc_key(i), None)
        st.session_state.pop(_pc_matrix_ver_key(i), None)
        st.session_state.pop(_pc_staged_key(i), None)
        infl_config = db_st.get_inflation_matrix_config()
        for row in infl_config["input_rows"]:
            for col in range(len(infl_config["columns"])):
                st.session_state.pop(_infl_matrix_key(i, row["key"], col), None)
                st.session_state.pop(_infl_matrix_saved_key(i, row["key"], col), None)
                st.session_state.pop(_infl_draft_key(i, row["key"], col), None)
        pc_config = db_st.get_process_cost_matrix_config()
        for row in pc_config["input_rows"]:
            for col in range(len(pc_config["columns"])):
                st.session_state.pop(_pc_matrix_key(i, row["key"], col), None)
                st.session_state.pop(_pc_matrix_saved_key(i, row["key"], col), None)
                st.session_state.pop(_pc_draft_key(i, row["key"], col), None)
        for fi, _field in enumerate(group.get("fields", [])):
            key = _field_key(i, fi)
            st.session_state.pop(key, None)
            st.session_state.pop(_saved_display_key(i, fi), None)
            st.session_state.pop(f"_{key}", None)
            st.session_state.pop(f"_{key}_wver", None)
    for spec in _PANEL_HEADER_FILTERS:
        st.session_state.pop(spec["key"], None)
    st.session_state.pop(_PANEL_PLANNING_LEVEL_KEY, None)
    st.session_state.pop(_PANEL_FILTERS_VER_KEY, None)
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
    if _is_inflation_rates_group(group):
        for calc_row in infl_calc:
            calculated_fields.append({
                "name": calc_row["name"],
                "name_tags": calc_row.get("name_tags", []),
                "value": _field_display_str(_INFL_PCT_FIELD, calc_row["effective_total"]),
                "suffix": "%",
            })
        return {
            "title": group["title"],
            "status_summary": _status_summary(groups),
            "status_rows": build_status_rows(groups),
            "fields": fields,
            "calculated_fields": calculated_fields,
        }
    if _is_process_cost_group(group):
        config = db_st.get_process_cost_matrix_config()
        calc = _process_cost_calc_state(index)
        totals = _compute_pc_column_totals(index)
        for col_idx, col_name in enumerate(config["columns"]):
            total = totals[col_idx]
            calculated_fields.append({
                "name": _pc_total_sidebar_label(col_name),
                "value": total,
                "suffix": "",
                "value_class": "red" if total != 0 else "neutral",
                "kind": "total",
            })
        for share_row in calc.get("column_shares") or []:
            share_pct = float(share_row.get("share_pct", 0.0))
            col_name = str(share_row.get("column", ""))
            calculated_fields.append({
                "name": f"{col_name} Share",
                "value": share_pct,
                "suffix": "%",
                "value_class": "red" if share_pct != 0 else "neutral",
                "kind": "share",
            })
        return {
            "title": group["title"],
            "status_summary": _status_summary(groups),
            "status_rows": build_status_rows(groups),
            "fields": [],
            "calculated_fields": calculated_fields,
            "process_cost_calc": calc,
        }
    if _is_delivery_mix_group(group):
        for fi, field in _delivery_mix_rows(group):
            fields.append({
                "name": field["name"],
                "value": _delivery_mix_field_value(index, fi, field, group),
                "suffix": field.get("suffix") or "",
            })
        return {
            "title": group["title"],
            "status_summary": _status_summary(groups),
            "status_rows": build_status_rows(groups),
            "fields": fields,
            "calculated_fields": calculated_fields,
        }
    for fi, field in enumerate(group.get("fields", [])):
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
    st.session_state[_saved_key(index)] = True
    if _is_delivery_mix_group(group):
        st.session_state[_dm_calc_key(index)] = _compute_delivery_mix(index, group)
        st.session_state.pop(_dm_staged_key(index), None)
    elif _is_inflation_rates_group(group):
        st.session_state[_infl_calc_key(index)] = _compute_inflation_rates(index, group)
    elif _is_process_cost_group(group):
        _refresh_pc_calc_state(index)
        st.session_state.pop(_pc_staged_key(index), None)
    st.session_state[_SIM_RUN_KEY] = False
    history = st.session_state.setdefault(_SIM_HISTORY_KEY, [])
    history.append(_capture_group_submission(index, group, groups))


def process_pending_save(groups: list[dict[str, Any]]) -> None:
    """Run Save after all parameter widgets have rendered for the rerun."""
    pending_save = st.session_state.pop(_PENDING_SAVE_KEY, None)
    if pending_save is None:
        return
    if pending_save < 0 or pending_save >= len(groups):
        return
    group = groups[pending_save]
    if _is_inflation_rates_group(group):
        _capture_infl_matrix_drafts(pending_save)
    elif _is_delivery_mix_group(group):
        _capture_dm_staged_values(pending_save, group)
    _on_save_group(pending_save, group, groups)
    st.rerun()


def request_reset_simulate() -> None:
    """Schedule reset on next rerun (must run before widgets are drawn)."""
    st.session_state[_RESET_KEY] = True


def _capture_submission_snapshot(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Store parameter values at Start simulation — right panel shows only this data."""
    rows: list[dict[str, Any]] = []
    for i, group in enumerate(groups):
        if _is_process_cost_group(group):
            config = db_st.get_process_cost_matrix_config()
            calc = _process_cost_calc_state(i)
            for row in config["input_rows"]:
                for col_idx, col_name in enumerate(config["columns"]):
                    rows.append({
                        "group": group["title"],
                        "name": f'{row["label"]} — {col_name}',
                        "value": _pc_matrix_cell_value(i, row["key"], col_idx),
                        "suffix": "",
                    })
            for share_row in calc.get("column_shares") or []:
                col_name = str(share_row.get("column", ""))
                rows.append({
                    "group": group["title"],
                    "name": f"{col_name} Share %",
                    "value": _format_share_pct(float(share_row.get("share_pct", 0.0))),
                    "suffix": "",
                })
            for plc_row in calc.get("plc_impacts") or []:
                plc_name = str(plc_row.get("plc", ""))
                for col_name, impact in (plc_row.get("impacts") or {}).items():
                    rows.append({
                        "group": group["title"],
                        "name": f"{plc_name} — {col_name} impact",
                        "value": round(float(impact), 2),
                        "suffix": "",
                    })
            continue
        if _is_delivery_mix_group(group):
            for fi, field in _delivery_mix_rows(group):
                rows.append({
                    "group": group["title"],
                    "name": field["name"],
                    "value": _delivery_mix_field_value(i, fi, field, group),
                    "suffix": field.get("suffix") or "",
                })
            continue
        for fi, field in enumerate(group.get("fields", [])):
            if _is_inflation_rates_group(group) and not _is_inflation_calculated_field(field):
                continue
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
        st.markdown('<span class="sim-panel-filters-row-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        try:
            filters_wrap = st.container(key="sim_panel_filters_wrap")
        except TypeError:
            filters_wrap = st.container()
        with filters_wrap:
            _ensure_panel_filter_state()
            if not _panel_period_selected():
                _reset_dependent_panel_filters()
            _sync_planning_level_from_values()
            _enforce_single_planning_filter()
            period_enabled = _panel_period_selected()
            active_level = _active_planning_level_key()
            period_spec = _PANEL_HEADER_FILTERS[0]
            filter_cols = st.columns([1, 3.2, 1, 1], gap="small", vertical_alignment="bottom")

            with filter_cols[0]:
                st.markdown('<span class="sim-panel-period-col-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                period_dd, _period_sp = st.columns([3, 1], gap="small")
                with period_dd:
                    st.markdown('<span class="sim-panel-dd-75-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                    filter_select(
                        period_spec["label"],
                        period_spec["key"],
                        preset=period_spec["preset"],
                        parent=period_dd,
                        panel_header=True,
                        label_above=period_spec["label"],
                        placeholder=_PANEL_FILTER_PLACEHOLDER,
                        on_change=_on_panel_period_changed,
                    )

            with filter_cols[1]:
                st.markdown('<span class="sim-planning-level-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                st.markdown(
                    '<div class="elx-filter-upper-lbl elx-filter-panel-lbl elx-planning-level-heading">'
                    "Planning Level</div>",
                    unsafe_allow_html=True,
                )
                btn_cols = st.columns(4, gap="xxsmall")
                level_locked = bool(active_level)
                for btn_col, spec in zip(btn_cols, _PANEL_PLANNING_SPECS):
                    level_key = spec["key"]
                    is_active = active_level == level_key
                    btn_disabled = (not period_enabled) or (level_locked and not is_active)
                    btn_type = "primary" if is_active and period_enabled else "secondary"
                    with btn_col:
                        try:
                            btn_col.button(
                                spec["label"],
                                key=f"sim_plan_btn_{level_key}",
                                disabled=btn_disabled,
                                use_container_width=True,
                                type=btn_type,
                                on_click=_on_planning_level_pick,
                                args=(level_key,),
                            )
                        except TypeError:
                            btn_col.button(
                                spec["label"],
                                key=f"sim_plan_btn_{level_key}",
                                disabled=btn_disabled,
                                use_container_width=True,
                                on_click=_on_planning_level_pick,
                                args=(level_key,),
                            )

            with filter_cols[2]:
                st.markdown('<span class="sim-panel-select-col-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                select_dd, _select_sp = st.columns([3, 1], gap="small")
                with select_dd:
                    st.markdown('<span class="sim-panel-dd-75-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                    if active_level:
                        value_spec = _planning_level_spec(active_level)
                        assert value_spec is not None
                        filter_select(
                            value_spec["label"],
                            value_spec["key"],
                            preset=value_spec["preset"],
                            parent=select_dd,
                            panel_header=True,
                            label_above=f"Select {value_spec['label']}",
                            placeholder=_PANEL_FILTER_PLACEHOLDER,
                            disabled=not period_enabled,
                            on_change=partial(_on_planning_filter_changed, active_level),
                        )
                    else:
                        filter_select(
                            "Select",
                            "sim_panel_planning_value_idle",
                            options=[_PANEL_FILTER_PLACEHOLDER],
                            parent=select_dd,
                            panel_header=True,
                            label_above="Select",
                            placeholder=_PANEL_FILTER_PLACEHOLDER,
                            disabled=True,
                        )

            with filter_cols[3]:
                st.markdown('<span class="sim-affected-records-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
                forecast_count = _affected_forecast_record_count()
                count_html = (
                    f"<strong>{forecast_count}</strong>"
                    if forecast_count is not None
                    else "<span style='opacity:0.55;'>—</span>"
                )
                _html(
                    f"""
                    <div class="sim-affected-records">
                      <span class="elx-filter-upper-lbl elx-filter-panel-lbl elx-affected-records-lbl">
                        Affected Forecast Records
                      </span>
                      <span class="sim-affected-records-val">{count_html}</span>
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
              <div style="width:44px;height:44px;background:{_ICON_BG};border-radius:0;
                  display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;">
                {html.escape(group["icon"])}
              </div>
              <div style="min-width:0;">
                <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;">
                  <p style="margin:0;font-size:15px;font-weight:700;color:{_PRIMARY};line-height:1.25;">
                    {html.escape(group["title"])}
                  </p>
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
                if _is_delivery_mix_group(group):
                    _capture_dm_staged_values(index, group)
                    st.session_state[_PENDING_SAVE_KEY] = index
                    st.rerun()
                elif _is_process_cost_group(group):
                    _capture_pc_staged_values(index)
                    _on_save_group(index, group, groups)
                    st.rerun()
                else:
                    st.session_state[_PENDING_SAVE_KEY] = index
                    st.rerun()
        with btn_t:
            st.markdown('<span class="sim-toggle-col"></span>', unsafe_allow_html=True)
            if st.button(chevron, key=f"sim_toggle_{index}"):
                st.session_state[open_key] = not st.session_state[open_key]
                st.rerun()


def _infl_display_str(value: Any) -> str:
    v = float(value)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.1f}"


def _render_pct_chip_html(
    display: str,
    *,
    align: str = "center",
    value_size: str = "12px",
    value_weight: str = "400",
    suffix_size: str = "12px",
    suffix_weight: str = "400",
) -> None:
    """Read-only value + % chip — inline styles so % shows inside st.html and st.markdown."""
    margin = "margin:0 auto;" if align == "center" else "margin-left:auto;margin-right:0;"
    align_cls = " sim-pct-chip-right" if align == "right" else ""
    st.markdown(
        f'<div class="sim-pct-chip-readonly{align_cls}" style="display:inline-flex;align-items:center;'
        f'justify-content:flex-start;gap:4px;width:fit-content;max-width:100%;'
        f'min-width:{_PCT_CHIP_MIN_W};{margin}background:{_INPUT_BG};border:1px solid {_INPUT_BORDER};'
        f'border-radius:8px;padding:{_PCT_CHIP_PAD};gap:{_PCT_CHIP_GAP};min-height:{_PCT_CHIP_H};'
        f'height:{_PCT_CHIP_H};box-sizing:border-box;overflow:visible;vertical-align:middle;">'
        f'<span style="font-size:{value_size};font-weight:{value_weight};color:{_PRIMARY};'
        f'flex-shrink:0;white-space:nowrap;">{html.escape(display)}</span>'
        f'<span style="font-size:{suffix_size};font-weight:{suffix_weight};color:#64748b;'
        f'flex-shrink:0;white-space:nowrap;">&#37;</span></div>',
        unsafe_allow_html=True,
    )


def _render_infl_pct_chip(display: str, *, readonly: bool = True) -> None:
    _render_pct_chip_html(display)


def _inject_infl_matrix_chip_css() -> None:
    """Co-located chip styles — guarantees same padding/% on first visit, Save, and Reset."""
    st.markdown(
        f"""
        <style id="sim-infl-matrix-chip-v{_INFL_CSS_VERSION}">
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"],
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"] > div {{
            width: fit-content !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_infl_input_"] [data-testid="stTextInput"] label,
        [class*="st-key-sim_infl_input_"] [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] {{
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            gap: {_PCT_CHIP_GAP} !important;
            width: fit-content !important;
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            min-height: {_PCT_CHIP_H} !important;
            height: {_PCT_CHIP_H} !important;
            padding: {_PCT_CHIP_PAD} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] > div {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            display: flex !important;
            align-items: center !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: unset !important;
            height: auto !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"] input {{
            text-align: left !important;
            font-weight: 400 !important;
            font-size: 12px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            outline: none !important;
            width: auto !important;
            min-width: 24px !important;
            max-width: 48px !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: unset !important;
            height: auto !important;
        }}
        [class*="st-key-sim_infl_input_"] div[data-baseweb="input"]::after {{
            content: "%" !important;
            position: static !important;
            right: auto !important;
            top: auto !important;
            transform: none !important;
            display: inline-block !important;
            flex-shrink: 0 !important;
            color: #64748b !important;
            font-size: 12px !important;
            font-weight: 400 !important;
            line-height: 1 !important;
            pointer-events: none !important;
            user-select: none !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [class*="st-key-sim_infl_input_"] .sim-pct-chip-readonly,
        [class*="st-key-sim_infl_calc_table_"] .sim-pct-chip-readonly {{
            min-width: {_PCT_CHIP_MIN_W} !important;
            max-width: {_PCT_CHIP_MAX_W} !important;
            min-height: {_PCT_CHIP_H} !important;
            height: {_PCT_CHIP_H} !important;
            padding: {_PCT_CHIP_PAD} !important;
            gap: {_PCT_CHIP_GAP} !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        .sim-infl-calc-caption-wrap {{
            display: block !important;
            margin: 20px 0 4px 0 !important;
            padding: 0 !important;
            overflow: visible !important;
        }}
        .sim-infl-calc-caption {{
            margin: 0 !important;
            padding: 0 !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            color: {_INFL_CALC_CAPTION_COLOR} !important;
            line-height: 1.4 !important;
            visibility: visible !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-infl-calc-caption-wrap),
        [data-testid="stMarkdownContainer"]:has(.sim-infl-calc-caption-wrap) {{
            display: block !important;
            margin: 20px 0 4px 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            height: auto !important;
            background: transparent !important;
        }}
        [class*="st-key-sim_infl_calc_table_"] {{
            margin-top: 0 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_infl_matrix_cell_input(
    group_index: int,
    row_key: str,
    col: int,
    *,
    locked: bool,
) -> None:
    key = _infl_matrix_key(group_index, row_key, col)
    if locked:
        display = _infl_matrix_cell_display(group_index, row_key, col)
        _render_infl_pct_chip(display, readonly=True)
        return
    _ensure_infl_matrix_cell_state(group_index, row_key, col)
    st.text_input(
        "\u200b",
        key=key,
        label_visibility="collapsed",
        on_change=_sync_infl_draft_cell,
        args=(group_index, row_key, col),
    )


def _infl_matrix_column_weights(num_columns: int, *, include_total: bool) -> list[float]:
    weights = [2.0] + [1.0] * num_columns
    if include_total:
        weights.append(0.9)
    return weights


def _render_infl_matrix_header_row(columns: tuple[str, ...], *, variant: str) -> None:
    """Single HTML header bar — avoids white-on-white when Streamlit skips parent bg."""
    header_bg = _PANEL_HEADER_BG if variant == "input" else "#4B5563"
    labels = ["Inflation Type", *columns]
    if variant == "calc":
        labels.append("Total")
    if variant == "calc":
        grid_cols = "2fr " + " ".join(["1fr"] * len(columns)) + " 0.9fr"
    else:
        grid_cols = "2fr " + " ".join(["1fr"] * len(columns))
    cells: list[str] = []
    for label in labels:
        cells.append(
            f'<div class="sim-infl-hcell" style="background:{header_bg};color:#ffffff !important;'
            f'font-size:12px;font-weight:700;justify-content:center;text-align:center;">'
            f"{html.escape(label)}</div>"
        )
    st.markdown('<span class="sim-infl-header-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _html(
        f'<div class="sim-infl-header-bar sim-infl-header-bar-{variant}" '
        f'style="display:grid;grid-template-columns:{grid_cols};gap:0;'
        f'background:{header_bg};border-radius:8px 8px 0 0;overflow:hidden;'
        f'border-bottom:1px solid #000000;">'
        f"{''.join(cells)}</div>"
    )


def _render_infl_row_label(label: str) -> None:
    st.markdown(
        f'<div class="sim-infl-row-label" style="display:flex;align-items:center;min-height:{_PCT_CHIP_H};'
        f'font-size:12px;font-weight:400;color:#374151;line-height:1.3;margin:0;padding:0;">'
        f"<span>{label}</span></div>",
        unsafe_allow_html=True,
    )


def _render_infl_matrix_input_table(group_index: int, *, locked: bool) -> None:
    config = db_st.get_inflation_matrix_config()
    columns = config["columns"]
    st.markdown('<span class="sim-infl-matrix-marker sim-infl-input-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _render_infl_matrix_header_row(columns, variant="input")
    input_rows = config["input_rows"]
    for row_idx, row in enumerate(input_rows):
        label = html.escape(row["label"])
        last_cls = " sim-infl-row-last" if row_idx == len(input_rows) - 1 else ""
        cols = st.columns(_infl_matrix_column_weights(len(columns), include_total=False), gap="small", vertical_alignment="center")
        with cols[0]:
            st.markdown(
                f'<span class="sim-infl-row-marker{last_cls}" data-row="{html.escape(row["key"])}" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
            _render_infl_row_label(label)
        for col_idx, col_widget in enumerate(cols[1:]):
            with col_widget:
                _render_infl_matrix_cell_input(group_index, row["key"], col_idx, locked=locked)
    if not locked:
        _capture_infl_matrix_drafts(group_index)


def _render_infl_matrix_calc_table(group_index: int) -> None:
    config = db_st.get_inflation_matrix_config()
    columns = config["columns"]
    calc_rows = _compute_inflation_matrix(group_index)
    st.session_state[_infl_calc_key(group_index)] = calc_rows
    st.markdown('<span class="sim-infl-matrix-marker sim-infl-calc-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _render_infl_matrix_header_row(columns, variant="calc")
    for row_idx, calc_row in enumerate(calc_rows):
        label = html.escape(calc_row["name"])
        cells = calc_row.get("cells") or []
        total = _infl_display_str(calc_row.get("effective_total", 0.0))
        last_cls = " sim-infl-calc-row-last" if row_idx == len(calc_rows) - 1 else ""
        cols = st.columns(_infl_matrix_column_weights(len(columns), include_total=True), gap="small", vertical_alignment="center")
        with cols[0]:
            st.markdown(
                f'<span class="sim-infl-calc-row-marker{last_cls}" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
            _render_infl_row_label(label)
        for col_idx, col_widget in enumerate(cols[1:-1]):
            with col_widget:
                _render_infl_pct_chip(_infl_display_str(cells[col_idx]), readonly=True)
        with cols[-1]:
            _render_infl_pct_chip(total, readonly=True)


def _inject_pc_matrix_css() -> None:
    st.markdown(
        f"""
        <style id="sim-pc-matrix-chip-v{_INFL_CSS_VERSION}">
        [class*="st-key-sim_pc_input_"] {{
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            overflow: visible !important;
            padding: 0 0 10px 0 !important;
            margin-top: 12px !important;
            background: #ffffff !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stVerticalBlockBorderWrapper"],
        [class*="st-key-sim_pc_input_"] [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"],
        [class*="st-key-sim_pc_input_"] [data-testid="stMarkdownContainer"],
        [class*="st-key-sim_pc_input_"] [data-testid="column"] {{
            overflow: visible !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) {{
            margin: 0 !important;
            padding: 8px 10px !important;
            gap: 8px !important;
            align-items: center !important;
            border-bottom: 1px solid #000000 !important;
            background: #ffffff !important;
            box-sizing: border-box !important;
            width: 100% !important;
            display: flex !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: {_PC_CHIP_H} !important;
            padding: 0 !important;
            margin: 0 !important;
            overflow: visible !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:first-child,
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(2),
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:first-child,
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(2) {{
            justify-content: flex-start !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"] > [data-testid="stVerticalBlock"] {{
            width: 100% !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(2) > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:first-child > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(2) > [data-testid="stVerticalBlock"] {{
            align-items: flex-start !important;
            justify-content: center !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(n+3) > [data-testid="stVerticalBlock"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(n+3) > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(n+3) > [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(n+3) > [data-testid="stVerticalBlock"] {{
            align-items: center !important;
            justify-content: center !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(n+3) [data-testid="stElementContainer"],
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(n+3) [data-testid="stElementContainer"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-marker) > [data-testid="column"]:nth-child(n+3) [data-testid="stElementContainer"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(n+3) [data-testid="stElementContainer"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"]:has(.sim-pc-value-chip),
        [class*="st-key-sim_pc_input_"] [data-testid="stMarkdownContainer"]:has(.sim-pc-value-chip) {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: visible !important;
            min-height: {_PC_CHIP_H} !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"]:has(.sim-pc-row-marker),
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"]:has(.sim-pc-total-marker) {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}
        .sim-pc-value-chip {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-width: {_PC_CHIP_MIN_W} !important;
            max-width: {_PC_CHIP_MAX_W} !important;
            width: fit-content !important;
            min-height: {_PC_CHIP_H} !important;
            height: {_PC_CHIP_H} !important;
            padding: 0 8px !important;
            margin: 0 auto !important;
            background: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            font-size: 12px !important;
            font-weight: 400 !important;
            color: {_PRIMARY} !important;
            white-space: nowrap !important;
            overflow: visible !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stTextInput"],
        [class*="st-key-sim_pc_input_"] [data-testid="stTextInput"] > div,
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"]:has([data-testid="stTextInput"]) {{
            width: fit-content !important;
            max-width: {_PC_CHIP_MAX_W} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stTextInput"] label,
        [class*="st-key-sim_pc_input_"] [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}
        [class*="st-key-sim_pc_input_"] div[data-baseweb="input"] {{
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: fit-content !important;
            min-width: {_PC_CHIP_MIN_W} !important;
            max-width: {_PC_CHIP_MAX_W} !important;
            min-height: {_PC_CHIP_H} !important;
            height: {_PC_CHIP_H} !important;
            padding: 0 8px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            background: {_INPUT_BG} !important;
            background-color: {_INPUT_BG} !important;
            border: 1px solid {_INPUT_BORDER} !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_pc_input_"] div[data-baseweb="input"] > div {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 100% !important;
            min-height: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_pc_input_"] div[data-baseweb="input"] input {{
            text-align: center !important;
            font-weight: 400 !important;
            font-size: 12px !important;
            color: {_PRIMARY} !important;
            border: none !important;
            background: transparent !important;
            background-color: transparent !important;
            width: 100% !important;
            min-width: 48px !important;
            max-width: 80px !important;
            padding: 0 !important;
            margin: 0 !important;
            box-shadow: none !important;
        }}
        [class*="st-key-sim_pc_input_"] div[data-baseweb="input"]:focus-within {{
            border: 1px solid {_INPUT_BORDER} !important;
            box-shadow: none !important;
            background: {_INPUT_BG} !important;
            background-color: {_INPUT_BG} !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-row-last),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-row-last) {{
            border-bottom: none !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) {{
            border-bottom: none !important;
            border-top: 1px solid #000000 !important;
            background: #ffffff !important;
            margin: 0 !important;
            padding: 10px !important;
            gap: 8px !important;
            align-items: center !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
            box-sizing: border-box !important;
            width: 100% !important;
            overflow: visible !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: visible !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:first-child,
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-pc-total-marker) > [data-testid="column"]:nth-child(2) {{
            justify-content: flex-start !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stElementContainer"]:has(.sim-pc-total-chip),
        [class*="st-key-sim_pc_input_"] [data-testid="stMarkdownContainer"]:has(.sim-pc-total-chip) {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: visible !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .sim-pc-company-label,
        .sim-pc-category-label {{
            display: flex !important;
            align-items: center !important;
            min-height: {_PC_CHIP_H} !important;
            font-size: 12px !important;
            font-weight: 400 !important;
            color: #374151 !important;
            line-height: 1.3 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        .sim-pc-category-label {{
            font-weight: 400 !important;
        }}
        .sim-pc-value-chip.sim-pc-total-chip {{
            background: {_PC_TOTAL_BG} !important;
            background-color: {_PC_TOTAL_BG} !important;
            font-weight: 700 !important;
            border: 1px solid {_INPUT_BORDER} !important;
        }}
        .sim-pc-total-label {{
            font-weight: 700 !important;
            color: {_PRIMARY} !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) {{
            border-bottom: none !important;
            border-top: 1px solid #000000 !important;
            background: #ffffff !important;
            margin: 0 !important;
            padding: 10px !important;
            gap: 8px !important;
            align-items: center !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
            box-sizing: border-box !important;
            width: 100% !important;
            overflow: visible !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"],
        [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            overflow: visible !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
        }}
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"]:first-child,
        [class*="st-key-sim_pc_input_"] [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"]:nth-child(2),
        [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"]:first-child,
        [data-testid="stHorizontalBlock"]:has(.sim-pc-share-marker) > [data-testid="column"]:nth-child(2) {{
            justify-content: flex-start !important;
        }}
        .sim-pc-share-label {{
            font-weight: 700 !important;
            color: #166534 !important;
            min-height: {_PC_TOTAL_ROW_H} !important;
        }}
        .sim-pc-value-chip.sim-pc-share-chip {{
            background: #DCFCE7 !important;
            background-color: #DCFCE7 !important;
            font-weight: 700 !important;
            color: #166534 !important;
            border: 1px solid #86EFAC !important;
        }}
        .sim-pc-plc-wrap {{
            margin: 12px 10px 0 10px !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            background: #ffffff !important;
        }}
        .sim-pc-plc-title {{
            margin: 0 !important;
            padding: 10px 12px !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            color: {_PRIMARY} !important;
            background: {_INPUT_BG} !important;
            border-bottom: 1px solid #E5E7EB !important;
        }}
        .sim-pc-plc-table {{
            width: 100% !important;
            border-collapse: collapse !important;
            font-size: 11px !important;
        }}
        .sim-pc-plc-table th,
        .sim-pc-plc-table td {{
            padding: 8px 10px !important;
            border-bottom: 1px solid #EEF2F7 !important;
            text-align: left !important;
            vertical-align: top !important;
            color: #374151 !important;
        }}
        .sim-pc-plc-table th {{
            font-weight: 700 !important;
            color: {_PRIMARY} !important;
            background: #F8FAFC !important;
        }}
        .sim-pc-plc-table td.num,
        .sim-pc-plc-table th.num {{
            text-align: right !important;
            white-space: nowrap !important;
        }}
        .sim-pc-plc-table tr:last-child td {{
            border-bottom: none !important;
        }}
        .sim-pc-plc-impact {{
            font-weight: 700 !important;
            color: {_DANGER} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_pc_chip_html(display: str, *, total: bool = False, share: bool = False) -> None:
    if share:
        total_cls = " sim-pc-share-chip"
        bg = "#DCFCE7"
        weight = "700"
        color = "#166534"
    elif total:
        total_cls = " sim-pc-total-chip"
        bg = _PC_TOTAL_BG
        weight = "700"
        color = _PRIMARY
    else:
        total_cls = ""
        bg = _INPUT_BG
        weight = "400"
        color = _PRIMARY
    border = "1px solid #86EFAC" if share else f"1px solid {_INPUT_BORDER}"
    st.markdown(
        f'<div class="sim-pc-value-chip{total_cls}" style="display:inline-flex;align-items:center;'
        f'justify-content:center;min-width:{_PC_CHIP_MIN_W};max-width:{_PC_CHIP_MAX_W};width:fit-content;'
        f'min-height:{_PC_CHIP_H};height:{_PC_CHIP_H};padding:0 8px;margin:0 auto;'
        f'background:{bg};border:{border};border-radius:8px;box-sizing:border-box;'
        f'font-size:12px;font-weight:{weight};color:{color};white-space:nowrap;">'
        f"{html.escape(display)}</div>",
        unsafe_allow_html=True,
    )


def _render_pc_matrix_cell_input(
    group_index: int,
    row_key: str,
    col: int,
    *,
    locked: bool,
) -> None:
    key = _pc_matrix_key(group_index, row_key, col)
    if locked:
        _render_pc_chip_html(_pc_matrix_cell_display(group_index, row_key, col))
        return
    _ensure_pc_matrix_cell_state(group_index, row_key, col)
    st.text_input(
        "\u200b",
        key=key,
        label_visibility="collapsed",
        on_change=_sync_pc_draft_cell,
        args=(group_index, row_key, col),
    )
    _sync_pc_draft_cell(group_index, row_key, col)


def _pc_matrix_column_weights(num_value_cols: int) -> list[float]:
    return [0.75, 2.2] + [1.0] * num_value_cols


def _render_pc_matrix_header_row(config: dict) -> None:
    header_bg = _PANEL_HEADER_BG
    labels = [config["company_label"], config["category_label"], *config["columns"]]
    grid_cols = "0.75fr 2.2fr " + " ".join(["1fr"] * len(config["columns"]))
    cells: list[str] = []
    for label in labels:
        cells.append(
            f'<div class="sim-infl-hcell" style="background:{header_bg};color:#ffffff !important;'
            f'font-size:12px;font-weight:700;justify-content:center;text-align:center;">'
            f"{html.escape(label)}</div>"
        )
    st.markdown('<span class="sim-pc-header-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _html(
        f'<div class="sim-infl-header-bar sim-pc-header-bar" '
        f'style="display:grid;grid-template-columns:{grid_cols};gap:0;'
        f'background:{header_bg};border-radius:8px 8px 0 0;overflow:hidden;'
        f'border-bottom:1px solid #000000;">'
        f"{''.join(cells)}</div>"
    )


def _render_pc_matrix_input_table(group_index: int, *, locked: bool) -> None:
    config = db_st.get_process_cost_matrix_config()
    columns = config["columns"]
    company_code = _selected_panel_company()
    st.markdown('<span class="sim-pc-matrix-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    _render_pc_matrix_header_row(config)
    input_rows = config["input_rows"]
    for row_idx, row in enumerate(input_rows):
        cols = st.columns(_pc_matrix_column_weights(len(columns)), gap="small", vertical_alignment="center")
        last_cls = " sim-pc-row-last" if row_idx == len(input_rows) - 1 else ""
        with cols[0]:
            st.markdown(
                f'<span class="sim-pc-row-marker{last_cls}" aria-hidden="true"></span>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="sim-pc-company-label"><span>{html.escape(company_code)}</span></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f'<div class="sim-pc-category-label"><span>{html.escape(row["label"])}</span></div>',
                unsafe_allow_html=True,
            )
        for col_idx, col_widget in enumerate(cols[2:]):
            with col_widget:
                _render_pc_matrix_cell_input(group_index, row["key"], col_idx, locked=locked)

    if not locked:
        _capture_pc_staged_values(group_index, preserve_non_default=True)
        _capture_pc_matrix_drafts(group_index)

    totals = _compute_pc_column_totals(group_index)
    cols = st.columns(_pc_matrix_column_weights(len(columns)), gap="small", vertical_alignment="center")
    with cols[0]:
        st.markdown('<span class="sim-pc-total-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sim-pc-company-label" aria-hidden="true"><span>&nbsp;</span></div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f'<div class="sim-pc-category-label sim-pc-total-label" '
            f'style="min-height:{_PC_TOTAL_ROW_H};display:flex;align-items:center;">'
            f"<span>Total</span></div>",
            unsafe_allow_html=True,
        )
    for col_idx, col_widget in enumerate(cols[2:]):
        with col_widget:
            _render_pc_chip_html(_pc_display_str(totals[col_idx]), total=True)

    if not locked:
        calc = _process_cost_calc_state(group_index)
        share_values = [
            float(row.get("share_pct", 0.0))
            for row in calc.get("column_shares") or []
        ]
        if len(share_values) < len(columns):
            share_values.extend([0.0] * (len(columns) - len(share_values)))
        cols = st.columns(_pc_matrix_column_weights(len(columns)), gap="small", vertical_alignment="center")
        with cols[0]:
            st.markdown('<span class="sim-pc-share-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
            st.markdown(
                '<div class="sim-pc-company-label" aria-hidden="true"><span>&nbsp;</span></div>',
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.markdown(
                f'<div class="sim-pc-category-label sim-pc-share-label" '
                f'style="min-height:{_PC_TOTAL_ROW_H};display:flex;align-items:center;">'
                f"<span>Share %</span></div>",
                unsafe_allow_html=True,
            )
        for col_idx, col_widget in enumerate(cols[2:]):
            with col_widget:
                _render_pc_chip_html(_format_share_pct(share_values[col_idx]), share=True)


def _render_pc_plc_impact_table(calc: dict[str, Any]) -> None:
    """Step 3 — line-level project impact at PLC."""
    plc_rows = calc.get("plc_impacts") or []
    if not plc_rows:
        return
    config = db_st.get_process_cost_matrix_config()
    columns = config["columns"]
    header_cells = "".join(
        f'<th class="num">{html.escape(col)} impact</th>' for col in columns
    )
    body_rows: list[str] = []
    for plc_row in plc_rows:
        impacts = plc_row.get("impacts") or {}
        impact_cells = "".join(
            f'<td class="num sim-pc-plc-impact">{html.escape(_pc_display_str(impacts.get(col, 0)))}</td>'
            for col in columns
        )
        body_rows.append(
            f"<tr>"
            f'<td>{html.escape(str(plc_row.get("plc", "")))}</td>'
            f'<td>{html.escape(str(plc_row.get("product_subgroup", "")))}</td>'
            f"{impact_cells}"
            f"</tr>"
        )
    st.markdown(
        f"""
        <div class="sim-pc-plc-wrap">
          <p class="sim-pc-plc-title">Line-level project impact (Step 3)</p>
          <table class="sim-pc-plc-table">
            <thead>
              <tr>
                <th>PLC</th>
                <th>Product subgroup</th>
                {header_cells}
              </tr>
            </thead>
            <tbody>
              {"".join(body_rows)}
            </tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_process_cost_matrix_fields(group: dict[str, Any], index: int) -> None:
    """Process cost matrix — company × category rows with PTC/STC/SWC value columns."""
    locked = _group_is_saved(index)
    _ensure_pc_matrix_version(index)
    _inject_pc_matrix_css()
    if locked:
        _refresh_pc_calc_state(index)
    try:
        input_box = st.container(border=True, key=f"sim_pc_input_{index}")
    except TypeError:
        input_box = st.container(border=True)
    with input_box:
        _render_pc_matrix_input_table(index, locked=locked)


def _refresh_infl_calc_state(group_index: int) -> None:
    """Store calculated PTC/STC/SWC rows without rendering the matrix table."""
    st.session_state[_infl_calc_key(group_index)] = _compute_inflation_matrix(group_index)


def render_inflation_matrix_fields(group: dict[str, Any], index: int) -> None:
    """Inflation matrix — editable inputs; calc runs on Save but table stays hidden."""
    locked = _group_is_saved(index)
    _ensure_infl_matrix_version(index)
    _inject_infl_matrix_chip_css()
    if locked:
        _refresh_infl_calc_state(index)
    try:
        input_box = st.container(border=True, key=f"sim_infl_input_{index}")
    except TypeError:
        input_box = st.container(border=True)
    with input_box:
        _render_infl_matrix_input_table(index, locked=locked)


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
    pending_save = st.session_state.get(_PENDING_SAVE_KEY)
    if not _group_is_open(index, group) and pending_save != index:
        return

    st.markdown('<span class="sim-group-fields-marker" aria-hidden="true"></span>', unsafe_allow_html=True)

    if _is_inflation_rates_group(group):
        render_inflation_matrix_fields(group, index)
        return

    if _is_process_cost_group(group):
        render_process_cost_matrix_fields(group, index)
        return

    if _is_delivery_mix_group(group):
        dm_rows = _delivery_mix_rows(group)
        for i, (fi, field) in enumerate(dm_rows):
            _render_parameter_field(
                field,
                index,
                fi,
                is_last_row=i == len(dm_rows) - 1,
                is_delivery_mix=True,
            )
        if dm_rows:
            _capture_dm_staged_values(index, group)
        return

    fields = group.get("fields", [])
    if not fields:
        return

    content_started = False
    prev_was_section = False
    delivery_last_fi: int | None = None
    if _is_delivery_mix_group(group):
        delivery_fis = [
            fi
            for fi, f in enumerate(fields)
            if not _is_section_field(f)
            and not (_is_inflation_rates_group(group) and _is_inflation_calculated_field(f))
        ]
        delivery_last_fi = delivery_fis[-1] if delivery_fis else None
    for fi, field in enumerate(fields):
        if _is_inflation_rates_group(group) and _is_inflation_calculated_field(field):
            continue
        if _is_section_field(field):
            _render_process_section_header(field, show_divider=content_started)
            content_started = True
            prev_was_section = True
            continue
        if content_started and not prev_was_section and not _is_delivery_mix_group(group):
            st.markdown('<hr class="sim-row-divider" aria-hidden="true" />', unsafe_allow_html=True)
        prev_was_section = False
        _render_parameter_field(
            field,
            index,
            fi,
            is_last_row=_is_delivery_mix_group(group) and fi == delivery_last_fi,
            is_delivery_mix=_is_delivery_mix_group(group),
        )
        content_started = True


def render_parameter_group(
    group: dict[str, Any],
    index: int,
    groups: list[dict[str, Any]],
) -> None:
    """One Figma accordion card: header and fields inside the same bordered section."""
    if _is_process_cost_group(group) and not _panel_company_selected():
        return
    try:
        box = st.container(border=True, key=f"sim_grp_{index}")
    except TypeError:
        box = st.container(border=True)
    with box:
        wrap_cls = "sim-param-group-wrap"
        if _is_delivery_mix_group(group):
            wrap_cls += " sim-delivery-mix-wrap"
        st.markdown(
            f'<span class="{wrap_cls}" data-group="{index}" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        render_parameter_group_header(group, index, groups)
        render_parameter_group_fields(group, index)


def _render_parameter_field(
    field: dict[str, Any],
    group_index: int,
    field_index: int,
    *,
    is_last_row: bool = False,
    is_delivery_mix: bool = False,
) -> None:
    key = _field_key(group_index, field_index)
    locked = _group_is_saved(group_index)
    tags = _tags_html(field.get("name_tags", []))
    last_cls = " sim-field-row-last" if is_last_row else ""
    col_l, col_r = st.columns([5.2, 1.5], gap="small", vertical_alignment="center")
    with col_l:
        st.markdown(
            f'<span class="sim-field-row-marker{last_cls}" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        if is_delivery_mix:
            st.markdown(
                f'<div class="sim-dd-row-label"><span>{html.escape(field["name"])}</span>{tags}</div>',
                unsafe_allow_html=True,
            )
        else:
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
        if is_delivery_mix:
            st.markdown('<span class="sim-pct-input-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
            if locked:
                display = _saved_field_display(group_index, field_index, field)
                _render_pct_chip_html(
                    display,
                    align="right",
                    value_size="14px",
                    value_weight="700",
                    suffix_size="13px",
                    suffix_weight="600",
                )
            else:
                pending_save = st.session_state.get(_PENDING_SAVE_KEY)
                if pending_save != group_index:
                    _ensure_field_text_state(key, field)
                st.text_input(
                    "\u200b",
                    key=key,
                    label_visibility="collapsed",
                    on_change=_sync_dm_field_staged,
                    args=(group_index, field_index, field),
                )
        elif locked:
            display = _saved_field_display(group_index, field_index, field)
            _render_pct_chip_html(
                display,
                align="right",
                value_size="14px",
                value_weight="700",
                suffix_size="13px",
                suffix_weight="600",
            )
        else:
            st.markdown('<span class="sim-pct-input-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
            _ensure_field_text_state(key, field)
            st.text_input("\u200b", key=key, label_visibility="collapsed")


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
    pc_totals: bool = False,
) -> None:
    if infl_calc:
        marker = '<span class="sim-side-infl-calc-marker" aria-hidden="true"></span>'
    elif pc_totals:
        marker = '<span class="sim-side-pc-totals-marker" aria-hidden="true"></span>'
    elif submit:
        marker = '<span class="sim-side-submit-marker" aria-hidden="true"></span>'
    else:
        marker = '<span class="sim-side-card-marker" aria-hidden="true"></span>'
    try:
        bordered = infl_calc or pc_totals
        box = st.container(border=True, key=card_key) if bordered else st.container(key=card_key)
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


def _hierarchy_level_rows_html(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            f'<div style="padding:{_SUBMIT_SECTION_PAD};font-size:12px;color:{_TEXT_MUTED};">'
            f"Select filters above to view hierarchy.</div>"
        )
    return "".join(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;font-size:12px;">
          <span style="font-size:12px;font-weight:700;color:#475569;">{html.escape(r["name"])}</span>
          <span style="font-weight:700;color:{_PRIMARY};">{html.escape(r["value"])}</span>
        </div>
        """
        for r in rows
    )


def render_hierarchy_level_card() -> None:
    """Top sidebar card — selected panel filters as hierarchy rows."""
    rows = _build_hierarchy_level_rows()
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;background:{_INPUT_BG};">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Hierarchy Level</span>
        </div>
        {_hierarchy_level_rows_html(rows)}
        """,
        card_key="sim_side_impact",
    )


def render_live_impact_card(data: dict[str, Any]) -> None:
    """Top sidebar card — hierarchy level from panel filters."""
    del data
    render_hierarchy_level_card()


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
          <span style="font-size:12px;font-weight:700;color:#475569;max-width:62%;">{html.escape(f["name"])}</span>
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
    for calc_row in infl_calc:
        rows.append({
            "name": calc_row["name"],
            "name_tags": calc_row.get("name_tags", []),
            "value": _field_display_str(_INFL_PCT_FIELD, calc_row["effective_total"]),
            "suffix": "%",
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


def render_inflation_calculated_card(
    rows: list[dict[str, Any]],
    card_index: int,
    *,
    inflation_group_index: int | None = None,
) -> None:
    """Right sidebar — calculated PTC/STC/SWC rates after inflation Save."""
    if not rows:
        return
    total_label = ""
    if inflation_group_index is not None:
        total = _infl_display_str(_inflation_input_total(inflation_group_index))
        total_label = (
            f'<span style="font-size:14px;font-weight:700;color:{_PRIMARY};">'
            f"{html.escape(total)}%</span>"
        )
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;background:{_INPUT_BG};">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Inflation rates</span>
          {total_label}
        </div>
        {_inflation_calculated_rows_html(rows)}
        """,
        card_key=f"sim_side_infl_calc_{card_index}",
        infl_calc=True,
    )


def _process_cost_totals_rows_html(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    parts: list[str] = []
    for i, row in enumerate(rows):
        border = "border-bottom:1px solid #eef2f7;" if i < len(rows) - 1 else ""
        share_display = str(row.get("share_display", "0%"))
        share_class = row.get("share_class", "neutral")
        share_color = _VAL.get(share_class, _TEXT)
        parts.append(
            f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                padding:{_SUBMIT_SECTION_PAD};{border}font-size:12px;">
              <span style="font-weight:600;color:{_TEXT_MUTED};">{html.escape(row["name"])}</span>
              <span style="font-weight:700;color:{share_color};">{html.escape(share_display)}</span>
            </div>
            """
        )
    return "".join(parts)


def render_process_cost_totals_card(
    rows: list[dict[str, Any]],
    card_index: int,
) -> None:
    """Right sidebar — calculated share % per category after process cost Save."""
    if not rows:
        return
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;background:{_INPUT_BG};">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">Process Costs</span>
        </div>
        {_process_cost_totals_rows_html(rows)}
        """,
        card_key=f"sim_side_pc_totals_{card_index}",
        pc_totals=True,
    )


def render_section_submission_card(entry: dict[str, Any], index: int) -> None:
    """One card per Save — shows submitted section data (Figma status card)."""
    title = html.escape(entry["title"])
    is_direct_delivery_card = entry["title"] == _DELIVERY_MIX_TITLE
    is_process_cost_card = entry["title"] in _PROCESS_COST_TITLES
    hide_status = is_direct_delivery_card or is_process_cost_card
    summary_html = ""
    if not hide_status:
        summary_html = (
            f'<span style="font-size:12px;font-weight:700;color:#b45309;">'
            f'{html.escape(entry.get("status_summary", ""))}</span>'
        )
    field_block = _submission_field_rows_html(entry.get("fields") or [], compact=True)
    status_block = ""
    if not hide_status:
        status_block = _status_rows_html(entry.get("status_rows") or [], compact=True)
    _side_card(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:baseline;
            padding:{_SUBMIT_SECTION_PAD};border-bottom:1px solid #eef2f7;background:{_INPUT_BG};">
          <span style="font-size:14px;font-weight:700;color:{_PRIMARY};">{title}</span>
          {summary_html}
        </div>
        {field_block}
        {status_block}
        """,
        card_key=f"sim_side_submit_{index}",
        submit=True,
    )


def _history_entries_by_title(history: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Latest saved snapshot per section title (last save wins)."""
    by_title: dict[str, dict[str, Any]] = {}
    for entry in history:
        title = str(entry.get("title", ""))
        if title:
            by_title[title] = entry
    return by_title


def render_submission_history_cards(groups: list[dict[str, Any]]) -> None:
    """Sidebar cards below hierarchy — fixed order: Direct Delivery, Inflation, Process cost."""
    history: list[dict[str, Any]] = st.session_state.get(_SIM_HISTORY_KEY) or []
    by_title = _history_entries_by_title(history)
    dm_idx = next((i for i, group in enumerate(groups) if _is_delivery_mix_group(group)), None)
    inflation_idx = next(
        (i for i, group in enumerate(groups) if _is_inflation_rates_group(group)),
        None,
    )
    pc_idx = next(
        (i for i, group in enumerate(groups) if _is_process_cost_group(group)),
        None,
    )
    slot = 0

    if dm_idx is not None and _group_is_saved(dm_idx):
        entry = by_title.get(_DELIVERY_MIX_TITLE)
        if entry is None:
            entry = _capture_group_submission(dm_idx, groups[dm_idx], groups)
        _side_card_spacer("before_submit_dd")
        render_section_submission_card(entry, slot)
        slot += 1

    if inflation_idx is not None and _group_is_saved(inflation_idx):
        entry = by_title.get(_INFLATION_RATES_TITLE)
        calc_rows = (entry or {}).get("calculated_fields") or []
        if not calc_rows:
            calc_rows = _inflation_calculated_display_rows(inflation_idx, groups[inflation_idx])
        if calc_rows:
            _side_card_spacer("before_calc_infl")
            render_inflation_calculated_card(
                calc_rows,
                slot,
                inflation_group_index=inflation_idx,
            )
            slot += 1

    if pc_idx is not None and _group_is_saved(pc_idx):
        entry: dict[str, Any] | None = None
        for title in _PROCESS_COST_TITLES:
            if title in by_title:
                entry = by_title[title]
                break
        sidebar_rows = _process_cost_sidebar_display_rows(pc_idx, entry)
        if sidebar_rows:
            _side_card_spacer("before_pc_totals")
            render_process_cost_totals_card(sidebar_rows, slot)


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
