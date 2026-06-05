"""Reusable KPI card matching the dashboard design (HTML via st.markdown)."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

# tone → top border, main value, badge text, badge background
_THEMES: dict[str, dict[str, str]] = {
    "red": {
        "border": "#ef4444",
        "value": "#ef4444",
        "badge_fg": "#dc2626",
        "badge_bg": "#fee2e2",
    },
    "red2": {
        "border": "#ef4444",
        "value": "#ef4444",
        "badge_fg": "#dc2626",
        "badge_bg": "#fee2e2",
    },
    "green": {
        "border": "#16a34a",
        "value": "#16a34a",
        "badge_fg": "#15803d",
        "badge_bg": "#dcfce7",
    },
    "yellow": {
        "border": "#f59e0b",
        "value": "#d97706",
        "badge_fg": "#b45309",
        "badge_bg": "#fef3c7",
    },
    "orange": {
        "border": "#f59e0b",
        "value": "#d97706",
        "badge_fg": "#b45309",
        "badge_bg": "#fef3c7",
    },
    "blue": {
        "border": "#3b82f6",
        "value": "#1e40af",
        "badge_fg": "#1d4ed8",
        "badge_bg": "#dbeafe",
    },
}

_DEFAULT_THEME = _THEMES["red"]


def _arrow_prefix(badge_arrow: str | None) -> str:
    if badge_arrow == "up":
        return "↑ "
    if badge_arrow == "down":
        return "↓ "
    return ""


def kpi_card(
    title: str,
    value: str,
    badge_text: str,
    meta: str,
    *,
    tone: str = "red",
    badge_arrow: str | None = None,
) -> None:
    """Render one KPI card inside the current Streamlit container/column."""
    theme = _THEMES.get(tone, _DEFAULT_THEME)
    border = theme["border"]
    value_color = theme["value"]
    badge_fg = theme["badge_fg"]
    badge_bg = theme["badge_bg"]

    safe_title = html.escape(title)
    safe_value = html.escape(value)
    safe_badge = html.escape(f"{_arrow_prefix(badge_arrow)}{badge_text}")
    safe_meta = html.escape(meta)

    st.markdown(
        f"""
<div class="elx-kpi-card" style="
    background:#ffffff;
    border-radius:10px;
    border-top:3px solid {border};
    padding:16px 18px 14px;
    min-height:118px;
    box-shadow:0 1px 4px rgba(15,23,42,0.08);
    display:flex;
    flex-direction:column;
    box-sizing:border-box;
">
  <div style="
    font-size:11px;
    font-weight:600;
    letter-spacing:0.04em;
    color:#6b7280;
    text-transform:uppercase;
    line-height:1.3;
    margin-bottom:10px;
  ">{safe_title}</div>

  <div style="
    font-size:28px;
    font-weight:700;
    color:{value_color};
    line-height:1.15;
    margin-bottom:12px;
    flex:1;
  ">{safe_value}</div>

  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;">
    <span style="
      display:inline-block;
      background:{badge_bg};
      color:{badge_fg};
      padding:4px 10px;
      border-radius:999px;
      font-size:12px;
      font-weight:600;
      line-height:1.2;
      white-space:nowrap;
    ">{safe_badge}</span>
    <span style="
      font-size:12px;
      color:#9ca3af;
      line-height:1.2;
    ">{safe_meta}</span>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def kpi_card_from_row(row: dict[str, Any]) -> None:
    """Render from a ``dashboard_kpis`` / ``get_dashboard_data()['kpis']`` row."""
    kpi_card(
        title=row["label"],
        value=row["value"],
        badge_text=row["badge_text"],
        meta=row["meta"],
        tone=row.get("tone", "red"),
        badge_arrow=row.get("badge_arrow"),
    )
