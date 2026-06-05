"""Dashboard HTML/CSS helpers matching the Electrolux mockup."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from pages_st.Common_Pages.filter_select import filter_select, inject_filter_select_css

_DOT_COLORS: dict[str, str] = {
    "red": "#ef4444",
    "blue": "#3b82f6",
    "green": "#22c55e",
    "green-dark": "#15803d",
    "orange": "#f59e0b",
    "grey": "#94a3b8",
}

_DELTA_STYLES: dict[str, tuple[str, str]] = {
    "delta-red": ("#fee2e2", "#dc2626"),
    "delta-green": ("#dcfce7", "#16a34a"),
    "delta-grey": ("#f3f4f6", "#6b7280"),
}

_STATUS_STYLES: dict[str, tuple[str, str]] = {
    "simulated": ("#eff6ff", "#1d4ed8"),
    "baseline": ("#f3f4f6", "#475569"),
    "project": ("#fff7ed", "#c2410c"),
}

_COUNTRY_BAR: dict[str, str] = {
    "ok": "#22c55e",
    "warn": "#f59e0b",
    "danger": "#ef4444",
}

_ACTIVITY_ICON: dict[str, tuple[str, str, str]] = {
    "check": ("✓", "#dcfce7", "#16a34a"),
    "download": ("↓", "#dbeafe", "#1d4ed8"),
    "bolt": ("⚡", "#fef3c7", "#d97706"),
}


def dash_spacer() -> None:
    """24px vertical gap between dashboard sections (works in all Streamlit versions)."""
    st.markdown('<div class="dash-spacer-24" aria-hidden="true"></div>', unsafe_allow_html=True)


def inject_dashboard_css() -> None:
    inject_filter_select_css()
    st.markdown(
        """
        <style>
        .block-container:has(#dashboard-page) {
            padding: 0 0 24px 0 !important;
            max-width: 100% !important;
            background: #f1f3fb !important;
        }

        /* Dashboard content inset — filter bar is full-bleed (excluded below) */
        .block-container:has(#dashboard-page)
        [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:not(:has(.dash-filters-marker)) {
            padding-left: 24px !important;
            padding-right: 24px !important;
            box-sizing: border-box !important;
        }

        /* 24px vertical gaps — margin on sibling after spacer (Streamlit-safe) */
        .block-container:has(#dashboard-page) .dash-spacer-24 {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stElementContainer"]:has(.dash-spacer-24),
        .block-container:has(#dashboard-page) [data-testid="stMarkdownContainer"]:has(.dash-spacer-24) {
            min-height: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stElementContainer"]:has(.dash-spacer-24) + [data-testid="stElementContainer"],
        .block-container:has(#dashboard-page) [data-testid="stElementContainer"]:has(.dash-spacer-24) + div {
            margin-top: 24px !important;
        }

        /* ----- Filters bar — edge-to-edge white (same technique as navbar) ----- */
        .dash-filters-marker {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        section.main:has(.dash-filters-marker),
        [data-testid="stAppViewContainer"]:has(.dash-filters-marker),
        [data-testid="stMainBlockContainer"]:has(.dash-filters-marker) {
            overflow-x: visible !important;
            max-width: 100% !important;
        }

        [data-testid="stElementContainer"]:has(.dash-filters-marker) {
            background: #ffffff !important;
            box-sizing: border-box !important;
            width: 100vw !important;
            max-width: 100vw !important;
            margin-left: calc(50% - 50vw) !important;
            margin-right: calc(50% - 50vw) !important;
            padding: 0 !important;
        }

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) {
            background: #ffffff !important;
            border-bottom: 1px solid #e4eaf2 !important;
            box-sizing: border-box !important;
            width: 100vw !important;
            max-width: 100vw !important;
            margin-left: calc(50% - 50vw) !important;
            margin-right: calc(50% - 50vw) !important;
            padding: 10px 20px !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            gap: 8px !important;
            overflow: visible !important;
        }

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) > [data-testid="column"] {
            display: flex !important;
            align-items: center !important;
            overflow: visible !important;
            background: transparent !important;
        }

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) [data-testid="stVerticalBlock"] > div {
            margin: 0 !important;
            padding: 0 !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* DD% / INFL — label | slider | value inside one bordered container */
        .block-container:has(#dashboard-page) [data-testid="column"]:has(.dash-filter-slider) {
            min-width: 168px !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) {
            background: #ffffff !important;
            border: 1px solid #e4eaf2 !important;
            border-radius: 8px !important;
            box-sizing: border-box !important;
            padding: 0 10px !important;
            margin: 0 !important;
            min-height: 40px !important;
            max-height: 40px !important;
            height: 40px !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stHorizontalBlock"] {
            align-items: center !important;
            gap: 4px !important;
            min-height: 38px !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"] {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            min-height: 0 !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"]:nth-child(2) {
            flex: 1 1 auto !important;
            min-width: 0 !important;
            padding-right: 2px !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"]:nth-child(3) {
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: 40px !important;
            min-width: 32px !important;
            padding-left: 0 !important;
            justify-content: flex-end !important;
        }

        .block-container:has(#dashboard-page) .dash-filter-slider-name {
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #545f6f !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            margin: 0 !important;
        }

        .block-container:has(#dashboard-page) .dash-filter-slider-val {
            font-size: 13px !important;
            font-weight: 700 !important;
            color: #011e41 !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            margin: 0 !important;
            text-align: right !important;
            display: block !important;
            width: 100% !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stSlider"] {
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
            width: 100% !important;
            min-height: 0 !important;
            max-height: 20px !important;
            overflow: hidden !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stElementContainer"]:has([data-testid="stSlider"]) {
            overflow: hidden !important;
            max-height: 22px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Hide floating % above thumb — keep only right-side value */
        .block-container:has(#dashboard-page) [data-testid="column"]:has(.dash-filter-slider) [data-testid="stThumbValue"],
        .block-container:has(#dashboard-page) [data-testid="column"]:has(.dash-filter-slider) [data-testid="stThumbValue"] *,
        .block-container:has(#dashboard-page) [data-testid="column"]:has(.dash-filter-slider) [class*="st-key-slider_"] [data-testid="stThumbValue"],
        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stThumbValue"],
        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stThumbValue"] * {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            max-height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            opacity: 0 !important;
            position: absolute !important;
            left: -9999px !important;
            top: -9999px !important;
            pointer-events: none !important;
            font-size: 0 !important;
            line-height: 0 !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stWidgetLabel"],
        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stTickBarMin"],
        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stTickBarMax"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            opacity: 0 !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] {
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] > div {
            background: #e4eaf2 !important;
            height: 4px !important;
            border-radius: 999px !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] > div > div {
            background: #011e41 !important;
            border-radius: 999px !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] [role="slider"] {
            background: #011e41 !important;
            border: 2px solid #011e41 !important;
            width: 14px !important;
            height: 14px !important;
            box-shadow: none !important;
        }

        .block-container:has(#dashboard-page) .figma-filters-title,
        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) .figma-filters-title {
            font-size: 11px;
            font-weight: 700;
            color: #6b7280;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .block-container:has(#dashboard-page) .figma-filters-vdiv {
            width: 1px;
            height: 40px;
            background: #e4eaf2;
            margin: 0 auto;
        }

        .block-container:has(#dashboard-page) .figma-filters-live {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            height: 40px;
            padding: 0 14px;
            background: #eef4ff;
            border: 1px solid #e4eaf2;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            color: #011e41;
            white-space: nowrap;
        }

        .block-container:has(#dashboard-page) .figma-filters-live .dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            flex-shrink: 0;
        }

        .block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) {
            min-width: 160px !important;
            flex-shrink: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button,
        .block-container:has(#dashboard-page) [class*="st-key-dash_start_sim"] button {
            background: #011e41 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            min-height: 40px !important;
            height: 40px !important;
            width: 100% !important;
            opacity: 1 !important;
            visibility: visible !important;
            box-shadow: none !important;
        }

        .block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button:hover,
        .block-container:has(#dashboard-page) [class*="st-key-dash_start_sim"] button:hover {
            background: #013060 !important;
            color: #ffffff !important;
        }

        .block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button:focus,
        .block-container:has(#dashboard-page) [class*="st-key-dash_start_sim"] button:focus {
            background: #011e41 !important;
            color: #ffffff !important;
            box-shadow: none !important;
        }

        /* ----- Hero banner (row immediately after hero marker) ----- */
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + div [data-testid="stHorizontalBlock"] {
            background: linear-gradient(120deg, #011e41 0%, #032b5a 55%, #011e41 100%) !important;
            border-radius: 12px !important;
            padding: 22px 26px !important;
            margin: 24px 24px 0 24px !important;
            align-items: center !important;
            position: relative !important;
            overflow: hidden !important;
            width: calc(100% - 48px) !important;
            max-width: calc(100% - 48px) !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"]::before,
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + div [data-testid="stHorizontalBlock"]::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                radial-gradient(circle at 88% 40%, rgba(255,255,255,0.07), transparent 45%),
                linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
            background-size: auto, 72px 72px, 72px 72px;
            pointer-events: none;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] > div,
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-hero-marker) + div [data-testid="stHorizontalBlock"] > div {
            z-index: 1;
        }

        .block-container:has(#dashboard-page) .dash-hero-open div[data-testid="stButton"] button {
            background: #b8956b !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            min-height: 40px !important;
        }

        /* ----- KPI row — 24px horizontal gap ----- */
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-kpi-marker) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-kpi-marker) + div [data-testid="stHorizontalBlock"] {
            gap: 24px !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-kpi-marker) + [data-testid="stElementContainer"] [data-testid="column"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-kpi-marker) + div [data-testid="column"] {
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page) .dash-section-table {
            margin: 0 !important;
            padding: 0 !important;
        }

        /* ----- Table toolbar — whole row: white card, 10px padding, vertically centered ----- */
        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker) {
            background: #ffffff !important;
            padding: 10px 0 !important;
            box-sizing: border-box !important;
            border-radius: 8px !important;
            align-items: stretch !important;
            align-content: stretch !important;
            gap: 16px !important;
            margin: 0 24px 0 24px !important;
            width: calc(100% - 48px) !important;
            max-width: calc(100% - 48px) !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"] {
            background: transparent !important;
            display: flex !important;
            align-items: stretch !important;
            align-self: stretch !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:not(:last-child) > div[data-testid="stVerticalBlock"] {
            justify-content: center !important;
            align-items: flex-start !important;
            height: auto !important;
            min-height: unset !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child {
            align-self: stretch !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child > div[data-testid="stVerticalBlock"] {
            align-items: flex-end !important;
            justify-content: center !important;
            align-self: stretch !important;
            height: 100% !important;
            min-height: 100% !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            gap: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        [data-testid="stMarkdownContainer"],
        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        div[data-testid="stMarkdown"] {
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        .stMarkdown p {
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        .dash-table-toolbar-marker {
            display: none !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] {
            justify-content: flex-end !important;
            align-items: center !important;
            align-self: center !important;
            gap: 10px !important;
            width: auto !important;
            max-width: calc(100% - 2px) !important;
            margin: 0 !important;
            padding: 0 !important;
            flex-shrink: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            display: flex !important;
            align-items: center !important;
            align-self: center !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stHorizontalBlock"] > [data-testid="column"]
        > div[data-testid="stVerticalBlock"] {
            justify-content: center !important;
            align-items: stretch !important;
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stElementContainer"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            align-self: center !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stDownloadButton"],
        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stButton"] {
            margin: 0 !important;
            align-self: center !important;
        }

        .block-container:has(#dashboard-page) .dash-table-toolbar-actions,
        .block-container:has(#dashboard-page) .dash-table-actions {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            visibility: hidden !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stElementContainer"]:has(.dash-table-toolbar-actions),
        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stElementContainer"]:has(.dash-table-actions):not(:has([data-testid="stDownloadButton"])):not(:has([data-testid="stButton"])) {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [data-testid="stDownloadButton"] button,
        .block-container:has(#dashboard-page) .dash-table-actions [data-testid="stDownloadButton"] button {
            background: #ffffff !important;
            color: #344054 !important;
            border: 1px solid #e4eaf2 !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            min-height: 38px !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        .block-container:has(#dashboard-page) [data-testid="stHorizontalBlock"]:has(.dash-table-toolbar-marker)
        > [data-testid="column"]:last-child [class*="st-key-dash_submit"] button,
        .block-container:has(#dashboard-page) [class*="st-key-dash_submit"] button {
            background: #011e41 !important;
            color: #ffffff !important;
            border: none !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        /* ----- Bottom panels — 24px gap, equal card height ----- */
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] > [data-testid="stHorizontalBlock"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="stHorizontalBlock"] {
            gap: 24px !important;
            column-gap: 24px !important;
            align-items: stretch !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] {
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
            align-self: stretch !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"] > div[data-testid="stVerticalBlock"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] > div[data-testid="stVerticalBlock"] {
            flex: 1 1 auto !important;
            height: 100% !important;
            min-height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"] [data-testid="stElementContainer"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] [data-testid="stElementContainer"] {
            flex: 1 1 auto !important;
            height: 100% !important;
            min-height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"] [data-testid="stMarkdown"] > div,
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] [data-testid="stMarkdown"] > div {
            height: 100% !important;
            min-height: 100% !important;
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"] [data-testid="stMarkdown"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] [data-testid="stMarkdown"] {
            flex: 1 1 auto !important;
            height: 100% !important;
            min-height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + [data-testid="stElementContainer"] [data-testid="column"] [data-testid="stMarkdownContainer"],
        .block-container:has(#dashboard-page)
        [data-testid="stElementContainer"]:has(.dash-panels-marker) + div [data-testid="column"] [data-testid="stMarkdownContainer"] {
            height: 100% !important;
            flex: 1 1 auto !important;
        }

        .block-container:has(#dashboard-page) .dash-panel-card {
            background: #ffffff;
            border: 1px solid #e4eaf2;
            border-radius: 12px;
            padding: 18px 20px;
            height: 100% !important;
            min-height: 100% !important;
            box-sizing: border-box;
            display: flex !important;
            flex-direction: column !important;
        }

        .block-container:has(#dashboard-page) .dash-panel-body {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _pill(text: str, bg: str, fg: str) -> str:
    safe = html.escape(text)
    return (
        f'<span class="dash-pill" style="background:{bg};color:{fg};">'
        f"{safe}</span>"
    )


def render_hero_tag_title(hero: dict[str, Any]) -> str:
    tag = html.escape(hero["tag"].upper())
    title = html.escape(hero["title"])
    sub = html.escape(hero["sub"])
    return f"""
    <div class="dash-hero-left">
      <div class="dash-hero-tag">⚡ {tag}</div>
      <div class="dash-hero-title">{title}</div>
      <div class="dash-hero-sub">{sub}</div>
    </div>
    <style>
    .dash-hero-tag {{
      font-size: 11px; font-weight: 700; letter-spacing: 0.06em;
      color: #d4a853; text-transform: uppercase; margin-bottom: 8px;
    }}
    .dash-hero-title {{
      font-size: 22px; font-weight: 700; color: #ffffff; line-height: 1.25;
      margin-bottom: 8px;
    }}
    .dash-hero-sub {{
      font-size: 12px; color: rgba(198, 210, 225, 0.95); line-height: 1.45;
    }}
    </style>
    """


def render_hero_stats(stats: list[dict[str, str]]) -> str:
    items: list[str] = []
    for i, s in enumerate(stats):
        border = "" if i == 0 else "border-left:1px solid rgba(255,255,255,0.2);"
        items.append(
            f'<div class="dash-hero-stat" style="{border}padding:0 20px;">'
            f'<div class="dash-hero-stat-num">{html.escape(s["num"])}</div>'
            f'<div class="dash-hero-stat-lbl">{html.escape(s["label"])}</div>'
            f"</div>"
        )
    return f"""
    <div class="dash-hero-stats">{"".join(items)}</div>
    <style>
    .dash-hero-stats {{ display:flex; align-items:center; justify-content:flex-end; }}
    .dash-hero-stat-num {{ font-size: 26px; font-weight: 700; color:#fff; line-height:1.1; }}
    .dash-hero-stat-lbl {{ font-size: 12px; color: rgba(198,210,225,0.95); margin-top:4px; }}
    </style>
    """


def render_simulation_table(rows: list[dict[str, Any]], pagination: dict[str, Any]) -> str:
    body_rows: list[str] = []
    for i, r in enumerate(rows):
        bg = "#ffffff" if i % 2 == 0 else "#f9fafb"
        dot = _DOT_COLORS.get(r.get("dot", "grey"), "#94a3b8")
        d_bg, d_fg = _DELTA_STYLES.get(r.get("delta_pct_class", "delta-grey"), _DELTA_STYLES["delta-grey"])
        s_bg, s_fg = _STATUS_STYLES.get(r.get("status_class", "baseline"), _STATUS_STYLES["baseline"])

        actual_cls = ""
        if r.get("actual_class") == "delta-grey":
            actual_cls = ' style="color:#9ca3af;"'

        body_rows.append(
            f'<tr style="background:{bg};">'
            f'<td><span class="dash-dot" style="background:{dot};"></span>'
            f'{html.escape(r["category"])}</td>'
            f'<td>{html.escape(r["bucket"])}</td>'
            f'<td{actual_cls}>{html.escape(r["actual"])}</td>'
            f'<td>{html.escape(r["forecast"])}</td>'
            f'<td>{html.escape(r["simulation"])}</td>'
            f'<td>{_pill(r["delta_text"], d_bg, d_fg)}</td>'
            f'<td>{_pill(r["delta_pct"], d_bg, d_fg)}</td>'
            f'<td>{_pill(r["source"], "#f3f4f6", "#475569")}</td>'
            f'<td>{_pill(r["status"], s_bg, s_fg)}</td>'
            f"</tr>"
        )

    pages_html = []
    page_param = html.escape(str(pagination.get("page_param", "table_page")))
    link_pages = pagination.get("link_pages", False)
    for p in pagination.get("pages", [1, 2, 3]):
        active = p == pagination.get("active", 1)
        cls = "dash-page active" if active else "dash-page"
        if link_pages and not active:
            pages_html.append(
                f'<a class="{cls}" href="?{page_param}={p}" target="_self">{p}</a>'
            )
        else:
            pages_html.append(f'<span class="{cls}">{p}</span>')

    showing = html.escape(str(pagination.get("showing", "")))
    total = pagination.get("total", 0)

    return f"""
    <div class="dash-table-wrap">
      <table class="dash-table">
        <thead>
          <tr>
            <th>Cost category</th><th>Bucket</th><th>Actual (EUR)</th>
            <th>Forecast (EUR)</th><th>Simulation (EUR)</th>
            <th>Δ vs baseline</th><th>Δ %</th><th>Source</th><th>Status</th>
          </tr>
        </thead>
        <tbody>{"".join(body_rows)}</tbody>
      </table>
      <div class="dash-table-footer">
        <span class="dash-table-count">Showing {showing} of {total} records</span>
        <div class="dash-pagination">{"".join(pages_html)}</div>
      </div>
    </div>
    <style>
    .dash-table-wrap {{
      background:#fff; border:1px solid #e4eaf2; border-radius:12px;
      overflow:hidden; margin-bottom:0;
    }}
    .dash-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    .dash-table thead tr {{
      background:#011e41; color:#fff;
    }}
    .dash-table th {{
      text-align:left; padding:12px 14px; font-size:11px; font-weight:700;
      letter-spacing:0.04em; text-transform:uppercase; white-space:nowrap;
    }}
    .dash-table td {{
      padding:12px 14px; color:#1f2937; vertical-align:middle;
      border-bottom:1px solid #f1f5f9;
    }}
    .dash-dot {{
      display:inline-block; width:8px; height:8px; border-radius:2px;
      margin-right:8px; vertical-align:middle;
    }}
    .dash-pill {{
      display:inline-block; padding:3px 10px; border-radius:999px;
      font-size:12px; font-weight:600; white-space:nowrap;
    }}
    .dash-table-footer {{
      display:flex; justify-content:space-between; align-items:center;
      padding:12px 16px; background:#fff;
    }}
    .dash-table-count {{ font-size:12px; color:#6b7280; }}
    .dash-pagination {{ display:flex; gap:6px; }}
    .dash-page {{
      width:28px; height:28px; display:inline-flex; align-items:center;
      justify-content:center; border-radius:6px; font-size:13px; font-weight:600;
      color:#64748b; cursor:default; text-decoration:none;
    }}
    a.dash-page {{ cursor:pointer; }}
    a.dash-page:hover {{ color:#011e41; }}
    .dash-page.active {{
      background:#011e41; color:#fff;
    }}
    </style>
    """


def render_country_panel(countries: list[dict[str, Any]]) -> str:
    rows: list[str] = []
    status_icon = {"ok": "✓", "warn": "◷", "danger": "⚠"}
    for c in countries:
        bar_color = _COUNTRY_BAR.get(c["status"], "#94a3b8")
        width = max(c.get("bar_width", 0), 2 if c["status"] == "danger" else 0)
        icon = status_icon.get(c["status"], "•")
        icon_color = _COUNTRY_BAR.get(c["status"], "#94a3b8")
        rows.append(
            f'<div class="dash-country-row">'
            f'<div class="dash-country-label">'
            f'<span class="dash-country-flag">{c["flag"]}</span>'
            f'<span><b>{html.escape(c["code"])}</b> — {html.escape(c["name"])}</span>'
            f"</div>"
            f'<div class="dash-country-bar-track">'
            f'<div class="dash-country-bar" style="width:{width}%;background:{bar_color};"></div>'
            f"</div>"
            f'<span class="dash-country-pct">{c["pct"]}%</span>'
            f'<span class="dash-country-icon" style="color:{icon_color};">{icon}</span>'
            f"</div>"
        )
    return f"""
    <div class="dash-panel-card">
      <div class="dash-panel-title">Country status — EA1 BC04</div>
      <div class="dash-panel-body">{"".join(rows)}</div>
    </div>
    <style>
    .dash-panel-title {{
      font-size:15px; font-weight:700; color:#111827; margin-bottom:14px;
    }}
    .dash-country-row {{
      display:grid; grid-template-columns: 1.4fr 2fr 40px 24px;
      align-items:center; gap:10px; margin-bottom:12px;
    }}
    .dash-country-label {{ font-size:13px; color:#374151; }}
    .dash-country-flag {{ margin-right:6px; }}
    .dash-country-bar-track {{
      height:8px; background:#eef2f6; border-radius:999px; overflow:hidden;
    }}
    .dash-country-bar {{ height:100%; border-radius:999px; }}
    .dash-country-pct {{ font-size:13px; font-weight:600; color:#374151; text-align:right; }}
    .dash-country-icon {{ font-size:14px; font-weight:700; text-align:center; }}
    </style>
    """


def render_deadlines_panel(deadlines: list[dict[str, Any]]) -> str:
    items: list[str] = []
    for d in deadlines:
        chip_bg = "#fee2e2" if d.get("urgent") else "#dcfce7"
        chip_fg = "#dc2626" if d.get("urgent") else "#16a34a"
        items.append(
            f'<div class="dash-deadline-item">'
            f'<div class="dash-deadline-date">'
            f'<div class="dash-deadline-day">{html.escape(d["day"])}</div>'
            f'<div class="dash-deadline-month">{html.escape(d["month"])}</div>'
            f"</div>"
            f'<div class="dash-deadline-body">'
            f'<div class="dash-deadline-title">{html.escape(d["title"])}</div>'
            f'<div class="dash-deadline-meta">{html.escape(d["meta"])}</div>'
            f"</div>"
            f'{_pill(d["chip"], chip_bg, chip_fg)}'
            f"</div>"
        )
    return f"""
    <div class="dash-panel-card">
      <div class="dash-panel-title">Upcoming deadlines</div>
      <div class="dash-panel-body">{"".join(items)}</div>
    </div>
    <style>
    .dash-deadline-item {{
      display:flex; align-items:center; gap:14px;
      padding:12px 0; border-bottom:1px solid #f1f5f9;
    }}
    .dash-deadline-item:last-child {{ border-bottom:none; }}
    .dash-deadline-date {{
      width:48px; text-align:center; flex-shrink:0;
      background:#f8fafc; border-radius:8px; padding:8px 4px;
    }}
    .dash-deadline-day {{ font-size:18px; font-weight:700; color:#011e41; line-height:1; }}
    .dash-deadline-month {{ font-size:10px; font-weight:700; color:#64748b; letter-spacing:0.04em; }}
    .dash-deadline-body {{ flex:1; min-width:0; }}
    .dash-deadline-title {{ font-size:13px; font-weight:600; color:#1f2937; }}
    .dash-deadline-meta {{ font-size:12px; color:#6b7280; margin-top:2px; }}
    </style>
    """


def render_activity_panel(activities: list[dict[str, Any]]) -> str:
    items: list[str] = []
    for a in activities:
        sym, bg, fg = _ACTIVITY_ICON.get(a.get("icon", "check"), ("•", "#f3f4f6", "#64748b"))
        warn = ' <span style="color:#dc2626;font-weight:600;">⚠ urgent</span>' if a.get("meta_warn") else ""
        items.append(
            f'<div class="dash-activity-item">'
            f'<div class="dash-activity-icon" style="background:{bg};color:{fg};">{sym}</div>'
            f'<div class="dash-activity-body">'
            f'<div class="dash-activity-title">{html.escape(a["title"])}</div>'
            f'<div class="dash-activity-meta">{html.escape(a["meta"])}{warn}</div>'
            f"</div></div>"
        )
    return f"""
    <div class="dash-panel-card">
      <div class="dash-panel-head">
        <div class="dash-panel-title" style="margin:0;">Recent activity</div>
        <a class="dash-view-all" href="#">View all →</a>
      </div>
      <div class="dash-panel-body">{"".join(items)}</div>
    </div>
    <style>
    .dash-panel-head {{
      display:flex; justify-content:space-between; align-items:center;
      margin-bottom:14px;
    }}
    .dash-view-all {{
      font-size:12px; font-weight:600; color:#2563eb; text-decoration:none;
    }}
    .dash-activity-item {{
      display:flex; gap:12px; padding:10px 0;
      border-bottom:1px solid #f1f5f9;
    }}
    .dash-activity-item:last-child {{ border-bottom:none; }}
    .dash-activity-icon {{
      width:32px; height:32px; border-radius:50%; flex-shrink:0;
      display:flex; align-items:center; justify-content:center;
      font-size:14px; font-weight:700;
    }}
    .dash-activity-title {{ font-size:13px; font-weight:600; color:#1f2937; }}
    .dash-activity-meta {{ font-size:12px; color:#6b7280; margin-top:2px; }}
    </style>
    """


def _filter_slider_label(name: str) -> str:
    return f'<span class="dash-filter-slider-name">{html.escape(name)}</span>'


def _filter_slider_value(value: int, suffix: str) -> str:
    return f'<span class="dash-filter-slider-val">{html.escape(f"{value}{suffix}")}</span>'


def render_filter_bar(data: dict[str, Any], on_start_simulation) -> None:
    """Filter bar directly under navbar — Figma layout (all logic in one place)."""
    filters: list[dict[str, str]] = data["filters"]
    sliders: list[dict[str, Any]] = data["sliders"]
    n_filters = len(filters)
    n_sliders = len(sliders)

    ratios = (
        [0.6]
        + [0.82] * n_filters
        + [0.03]
        + [1.25] * n_sliders
        + [1.35, 1.55]
    )
    cols = st.columns(ratios, vertical_alignment="center")

    cols[0].markdown(
        '<span class="dash-filters-marker" aria-hidden="true"></span>'
        '<div class="figma-filters-title">Filters:</div>',
        unsafe_allow_html=True,
    )

    for i, f in enumerate(filters):
        filter_select(
            f["key"],
            f"filter_{i}",
            preset=f["key"],
            default=f["value"],
            parent=cols[1 + i],
        )

    cols[1 + n_filters].markdown('<div class="figma-filters-vdiv"></div>', unsafe_allow_html=True)

    for j, s in enumerate(sliders):
        col = cols[2 + n_filters + j]
        suffix = s["suffix"] or ""
        suffix_fmt = suffix.replace("%", "%%")
        slider_key = f"slider_{j}"
        if slider_key not in st.session_state:
            st.session_state[slider_key] = int(s["value"])
        slider_val = int(st.session_state[slider_key])

        col.markdown('<span class="dash-filter-slider" aria-hidden="true"></span>', unsafe_allow_html=True)
        box = col.container(border=True)
        label_col, track_col, value_col = box.columns([0.18, 0.68, 0.14], vertical_alignment="center")
        label_col.markdown(_filter_slider_label(s["key"].upper()), unsafe_allow_html=True)
        track_col.slider(
            "\u200b",
            min_value=int(s["min"]),
            max_value=int(s["max"]),
            value=slider_val,
            step=1,
            format="",
            key=slider_key,
            label_visibility="collapsed",
        )
        value_col.markdown(_filter_slider_value(slider_val, suffix), unsafe_allow_html=True)

    live = html.escape(data["live_label"])
    cols[-2].markdown(
        f'<div class="figma-filters-live"><span class="dot"></span>{live}</div>',
        unsafe_allow_html=True,
    )

    with cols[-1]:
        st.markdown('<div class="figma-filters-actions"></div>', unsafe_allow_html=True)
        if st.button("▶  Start simulation", type="primary", use_container_width=True, key="dash_start_sim"):
            on_start_simulation()


def render_table_header(title: str, meta: str) -> str:
    """Title row + horizontal meta chips (PT10 · EA2 · 2026 · …)."""
    parts = [p.strip() for p in meta.replace("·", "|").split("|") if p.strip()]
    if not parts:
        parts = [meta.strip()] if meta.strip() else []
    meta_items = "".join(
        f'<span class="dash-table-meta-item">{html.escape(part)}</span>' for part in parts
    )
    return f"""
    <div class="dash-table-header">
      <div class="dash-table-title-row">
        <span class="dash-table-title">{html.escape(title)}</span>
        <span class="dash-table-databricks"> · From Databricks</span>
      </div>
      <div class="dash-table-meta">{meta_items}</div>
    </div>
    <style>
    .dash-table-header {{ margin: 0; padding: 0; }}
    .dash-table-title-row {{ line-height: 1.3; }}
    .dash-table-title {{ font-size: 18px; font-weight: 700; color: #111827; }}
    .dash-table-databricks {{ font-size: 14px; font-weight: 600; color: #2563eb; }}
    .dash-table-meta {{
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      align-items: center;
      gap: 0;
      margin-top: 6px;
      font-size: 12px;
      color: #6b7280;
      line-height: 1.4;
    }}
    .dash-table-meta-item {{
      display: inline-flex;
      align-items: center;
      white-space: nowrap;
    }}
    .dash-table-meta-item + .dash-table-meta-item::before {{
      content: "·";
      margin: 0 8px;
      color: #9ca3af;
      font-weight: 600;
    }}
    </style>
    """
