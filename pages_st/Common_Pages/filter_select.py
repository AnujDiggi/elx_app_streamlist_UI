"""Reusable compact filter dropdown — single styled select (value only)."""
from __future__ import annotations

import html
from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator

_CSS_INJECTED = False
_SIM_CTX_CSS_INJECTED = False
_FILTER_H = 32
_FILTER_CTX_H = 36

PRESET_OPTIONS: dict[str, list[str]] = {
    "Area": ["FR10", "FR20", "EA1", "DE01"],
    "Period": ["Jan", "EA2 · 2026", "EA1 · 2025", "EA2 · 2027"],
    "FADP": ["BC04", "BC03", "BC05"],
    "Category": ["All", "STC", "PTC", "Warehouse"],
    "Bucket": ["All buckets", "Fixed", "Variable"],
    "Scenario": ["Base Case", "Optimistic", "Pessimistic"],
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
        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            height: {h}px !important;
            min-height: {h}px !important;
            max-height: {h}px !important;
            overflow: hidden !important;
            align-self: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) > div[data-testid="stVerticalBlock"] {{
            width: 100% !important;
            gap: 0 !important;
            justify-content: center !important;
            align-items: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) [data-testid="stWidgetLabel"] {{
            display: none !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) [data-testid="stSelectbox"] {{
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] {{
            width: 100% !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) div[data-baseweb="select"] > div {{
            background-color: #F8F9FC !important;
            border: 1px solid #D8DCE7 !important;
            border-radius: 6px !important;
            min-height: {h}px !important;
            height: {h}px !important;
            color: #011E41 !important;
            box-shadow: none !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) div[data-baseweb="select"] > div > div {{
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

        [data-testid="column"]:has(.elx-filter-dd):not(:has(.elx-filter-labeled)) div[data-baseweb="select"] span {{
            color: #011E41 !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-align: center !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] svg {{
            fill: #011E41 !important;
            color: #011E41 !important;
        }}

        [data-testid="column"]:has(.elx-filter-dd) .elx-filter-slot {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
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

        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) {{
            background: #ffffff !important;
            background-color: #ffffff !important;
            border-bottom: 1px solid #e4eaf2 !important;
            box-sizing: border-box !important;
            width: 100% !important;
            max-width: 100% !important;
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 10px 20px !important;
            flex-wrap: nowrap !important;
            align-items: flex-end !important;
            gap: 12px !important;
            overflow: visible !important;
        }}

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
        [data-testid="stHorizontalBlock"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx),
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) {{
            height: auto !important; min-height: 0 !important; max-height: none !important;
            min-width: 100px !important; flex: 0 1 130px !important;
            align-self: flex-end !important; overflow: visible !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-labeled) div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:has(.elx-filter-ctx) > [data-testid="stVerticalBlock"] {{
            width: 100% !important; gap: 4px !important; margin: 0 !important; padding: 0 !important;
            background: #ffffff !important;
        }}
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) .elx-filter-upper-lbl {{
            font-size: 10px; font-weight: 700; color: #6b7280;
            letter-spacing: 0.05em; text-transform: uppercase;
            margin: 0 0 0 2px; line-height: 1.1;
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
            border-radius: 6px !important;
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
        [data-testid="stElementContainer"]:has(.sim-ctx-marker) [data-testid="column"]:last-child {{
            display: flex !important; justify-content: flex-end !important;
            align-items: center !important; background: #ffffff !important;
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
            + [data-testid="stElementContainer"]:has(.sim-ctx-marker),
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
    """Figma CONTEXT row: CONTEXT | vdiv | labeled filter_select × N | live chip."""
    if not context_rows:
        return {}

    inject_simulate_context_css()

    n = len(context_rows)
    ratios = [0.48, 0.035] + [1.0] * n + [1.55]
    cols = st.columns(ratios, gap="small", vertical_alignment="center")

    # Marker inside columns row (same pattern as dashboard dash-filters-marker).
    page_id = ' id="simulate-page"' if page_marker else ""
    cols[0].markdown(
        f'<span{page_id} class="sim-ctx-marker" aria-hidden="true"></span>'
        '<div class="sim-ctx-title">CONTEXT:</div>',
        unsafe_allow_html=True,
    )
    cols[1].markdown('<div class="sim-ctx-vdiv" aria-hidden="true"></div>', unsafe_allow_html=True)

    results: dict[str, str] = {}
    presets = {"Area", "Period", "FADP", "Scenario"}
    for i, row in enumerate(context_rows):
        k = row["key"]
        results[k] = filter_select(
            k,
            f"sim_ctx_{k}",
            preset=k if k in presets else None,
            default=row["value"],
            parent=cols[2 + i],
            label_above=k.upper(),
            context_bar=True,
        )

    live = _format_live_chip_text(live_label)
    cols[-1].markdown(
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
    parent: DeltaGenerator | None = None,
    label_above: str | None = None,
    context_bar: bool = False,
) -> str:
    """One compact dropdown showing the selected value only (Figma top row).

    ``field_name`` is kept for API compatibility (used in presets). With
    ``label_above``, renders a small uppercase label over the control (simulate CONTEXT bar).

    Args:
        field_name: Preset key / logical name (e.g. ``"Category"``).
        key: Unique Streamlit session key.
        options: Values in the menu.
        preset: Named list in ``PRESET_OPTIONS``.
        default: Initial value.
        parent: Column/container to render into.

    Returns:
        Selected value string.
    """
    inject_filter_select_css()

    opts = resolve_options(options, preset=preset, default=default)
    if not opts:
        raise ValueError("filter_select requires options or a valid preset with a default")

    initial = default if default is not None else opts[0]
    if key not in st.session_state:
        st.session_state[key] = initial

    selected = str(st.session_state[key])
    if selected not in opts:
        opts = [selected, *opts]

    target = parent if parent is not None else st
    if context_bar or label_above:
        target.markdown('<span class="elx-filter-ctx elx-filter-labeled" aria-hidden="true"></span>', unsafe_allow_html=True)
    if label_above:
        target.markdown(
            f'<div class="elx-filter-upper-lbl">{html.escape(label_above)}</div>',
            unsafe_allow_html=True,
        )
    target.markdown('<span class="elx-filter-dd" aria-hidden="true"></span>', unsafe_allow_html=True)
    target.selectbox(
        "\u200b",
        options=opts,
        index=opts.index(selected),
        key=key,
        label_visibility="collapsed",
    )

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
