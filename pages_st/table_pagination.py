"""Dashboard simulation table — pagination logic only (UI stays in dashboard_ui)."""
from __future__ import annotations

import math
from typing import Any

TABLE_PAGE_SIZE = 10
TABLE_PAGE_QP = "table_page"


def get_table_page(default: int = 1) -> int:
    """Current page from URL query (``?table_page=2``)."""
    import streamlit as st

    raw = st.query_params.get(TABLE_PAGE_QP)
    if raw is None:
        return default
    try:
        return max(1, int(raw))
    except (TypeError, ValueError):
        return default


def paginate_table_rows(
    rows: list[dict[str, Any]],
    page: int,
    page_size: int = TABLE_PAGE_SIZE,
) -> tuple[list[dict[str, Any]], int, dict[str, Any]]:
    """Slice *rows* for *page* and build the pagination dict for ``render_simulation_table``."""
    total = len(rows)
    total_pages = max(1, math.ceil(total / page_size)) if total else 1
    current = max(1, min(int(page), total_pages))
    start = (current - 1) * page_size
    end = min(start + page_size, total)
    page_rows = rows[start:end]
    showing = f"{start + 1}-{end}" if total else "0"

    pagination = {
        "showing": showing,
        "total": total,
        "pages": list(range(1, total_pages + 1)),
        "active": current,
        "link_pages": True,
        "page_param": TABLE_PAGE_QP,
    }
    return page_rows, current, pagination
