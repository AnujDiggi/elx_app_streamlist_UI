"""Shared filter bar (dashboard + simulate) — uses filter_select dropdowns."""
from __future__ import annotations

import html
from collections.abc import Callable
from typing import Any

import streamlit as st

from pages_st.Common_Pages.filter_select import filter_select, inject_filter_select_css

_CSS_INJECTED = False
_BC = ".block-container:has(.dash-filters-marker)"


def inject_filter_bar_css() -> None:
    """Inject full-bleed filter bar + slider styles (once per session)."""
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return
    _CSS_INJECTED = True
    inject_filter_select_css()
    st.markdown(
        f"""
        <style>
        .dash-filters-marker {{
            display: none !important;
            height: 0 !important;
            width: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}

        section.main:has(.dash-filters-marker),
        [data-testid="stAppViewContainer"]:has(.dash-filters-marker),
        [data-testid="stMainBlockContainer"]:has(.dash-filters-marker) {{
            overflow-x: visible !important;
            max-width: 100% !important;
        }}

        [data-testid="stElementContainer"]:has(.dash-filters-marker) {{
            background: #ffffff !important;
            box-sizing: border-box !important;
            width: 100vw !important;
            max-width: 100vw !important;
            margin-left: calc(50% - 50vw) !important;
            margin-right: calc(50% - 50vw) !important;
            padding: 0 !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) {{
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
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) > [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            overflow: visible !important;
            background: transparent !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) [data-testid="stVerticalBlock"],
        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) [data-testid="stVerticalBlock"] > div {{
            margin: 0 !important;
            padding: 0 !important;
            justify-content: center !important;
            align-items: center !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) {{
            min-width: 168px !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) {{
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
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stHorizontalBlock"] {{
            align-items: center !important;
            gap: 4px !important;
            min-height: 38px !important;
            height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"] {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            min-height: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"]:nth-child(2) {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            padding-right: 2px !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="column"]:nth-child(3) {{
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: 40px !important;
            min-width: 32px !important;
            padding-left: 0 !important;
            justify-content: flex-end !important;
        }}

        {_BC} .dash-filter-slider-name {{
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #545f6f !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            margin: 0 !important;
        }}

        {_BC} .dash-filter-slider-val {{
            font-size: 13px !important;
            font-weight: 700 !important;
            color: #011e41 !important;
            white-space: nowrap !important;
            line-height: 1 !important;
            margin: 0 !important;
            text-align: right !important;
            display: block !important;
            width: 100% !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stSlider"] {{
            padding: 0 !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
            width: 100% !important;
            min-height: 0 !important;
            max-height: 20px !important;
            overflow: hidden !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stElementContainer"]:has([data-testid="stSlider"]) {{
            overflow: hidden !important;
            max-height: 22px !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stThumbValue"],
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stThumbValue"] *,
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [class*="st-key-slider_"] [data-testid="stThumbValue"],
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stThumbValue"],
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stThumbValue"] * {{
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
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stWidgetLabel"],
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stTickBarMin"],
        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) [data-testid="stTickBarMax"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
            opacity: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] {{
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] > div {{
            background: #e4eaf2 !important;
            height: 4px !important;
            border-radius: 999px !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] > div > div {{
            background: #011e41 !important;
            border-radius: 999px !important;
        }}

        {_BC} [data-testid="column"]:has(.dash-filter-slider) [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stSlider"]) div[data-baseweb="slider"] [role="slider"] {{
            background: #011e41 !important;
            border: 2px solid #011e41 !important;
            width: 14px !important;
            height: 14px !important;
            box-shadow: none !important;
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) .figma-filters-title {{
            font-size: 11px;
            font-weight: 700;
            color: #6b7280;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            white-space: nowrap;
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) .figma-filters-vdiv {{
            width: 1px;
            height: 40px;
            background: #e4eaf2;
            margin: 0 auto;
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) .figma-filters-live {{
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
        }}

        [data-testid="stHorizontalBlock"]:has(.dash-filters-marker) .figma-filters-live .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            flex-shrink: 0;
        }}

        {_BC} [data-testid="column"]:has(.figma-filters-actions) {{
            min-width: 160px !important;
            flex-shrink: 0 !important;
        }}

        {_BC} [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button,
        {_BC} [class*="st-key-dash_start_sim"] button,
        {_BC} [class*="st-key-sim_start_sim"] button {{
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
        }}

        {_BC} [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button:hover,
        {_BC} [class*="st-key-dash_start_sim"] button:hover,
        {_BC} [class*="st-key-sim_start_sim"] button:hover {{
            background: #013060 !important;
            color: #ffffff !important;
        }}

        {_BC} [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button:focus,
        {_BC} [class*="st-key-dash_start_sim"] button:focus,
        {_BC} [class*="st-key-sim_start_sim"] button:focus {{
            background: #011e41 !important;
            color: #ffffff !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _filter_slider_label(name: str) -> str:
    return f'<span class="dash-filter-slider-name">{html.escape(name)}</span>'


def _filter_slider_value(value: int, suffix: str) -> str:
    return f'<span class="dash-filter-slider-val">{html.escape(f"{value}{suffix}")}</span>'


def render_filter_bar(
    data: dict[str, Any],
    on_start_simulation: Callable[[], None] | None = None,
    *,
    key_prefix: str = "filter",
    show_sliders: bool = True,
    show_action: bool = True,
    title: str = "Filters:",
) -> None:
    """Filter bar under navbar — same layout on dashboard and simulate."""
    filters: list[dict[str, str]] = data["filters"]
    sliders: list[dict[str, Any]] = data.get("sliders", []) if show_sliders else []
    n_filters = len(filters)
    n_sliders = len(sliders)
    has_action = show_action and on_start_simulation is not None

    ratios: list[float] = [0.6] + [0.82] * n_filters
    if n_sliders:
        ratios.append(0.03)
        ratios.extend([1.25] * n_sliders)
    if has_action:
        ratios.extend([1.35, 1.55])
    else:
        ratios.append(1.35)

    cols = st.columns(ratios, vertical_alignment="center")

    cols[0].markdown(
        '<span class="dash-filters-marker" aria-hidden="true"></span>'
        f'<div class="figma-filters-title">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )

    for i, f in enumerate(filters):
        filter_select(
            f["key"],
            f"{key_prefix}_{i}",
            preset=f["key"],
            default=f["value"],
            parent=cols[1 + i],
        )

    idx = 1 + n_filters
    if n_sliders:
        cols[idx].markdown('<div class="figma-filters-vdiv"></div>', unsafe_allow_html=True)
        idx += 1
        for j, s in enumerate(sliders):
            col = cols[idx + j]
            slider_key = f"slider_{j}" if key_prefix == "filter" else f"{key_prefix}_slider_{j}"
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
            value_col.markdown(_filter_slider_value(slider_val, s["suffix"] or ""), unsafe_allow_html=True)
        idx += n_sliders

    live = html.escape(data["live_label"])
    cols[idx].markdown(
        f'<div class="figma-filters-live"><span class="dot"></span>{live}</div>',
        unsafe_allow_html=True,
    )

    if has_action:
        btn_key = f"{key_prefix}_start_sim"
        with cols[idx + 1]:
            st.markdown('<div class="figma-filters-actions"></div>', unsafe_allow_html=True)
            if st.button("▶  Start simulation", type="primary", use_container_width=True, key=btn_key):
                on_start_simulation()


def render_context_filter_bar(data: dict[str, Any], *, page_marker: bool = True) -> dict[str, str]:
    """Simulate CONTEXT row (Figma) — labeled filter_select dropdowns + live chip."""
    from pages_st.Common_Pages.filter_select import render_simulate_context_bar

    rows: list[dict[str, str]] = list(data.get("context") or [])
    if not rows and data.get("filters"):
        rows = [{"key": f["key"], "value": f["value"]} for f in data["filters"]]
    if not rows:
        return {}
    return render_simulate_context_bar(rows, data["live_label"], page_marker=page_marker)
