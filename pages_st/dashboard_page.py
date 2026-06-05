"""Dashboard page — layout aligned with Electrolux mockup."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

import db_st
from pages_st.Common_Pages.dashboard_ui import (
    dash_spacer,
    inject_dashboard_css,
    render_activity_panel,
    render_country_panel,
    render_deadlines_panel,
    render_filter_bar,
    render_hero_stats,
    render_hero_tag_title,
    render_simulation_table,
    render_table_header,
)
from pages_st.Common_Pages.kpi_card import kpi_card_from_row
from pages_st.table_pagination import get_table_page, paginate_table_rows


def _go_simulate() -> None:
    st.session_state.page = "simulate"
    st.rerun()


def render() -> None:
    user = st.session_state["user"]
    data = db_st.get_dashboard_data(user["name"])

    inject_dashboard_css()
    st.markdown('<div id="dashboard-page"></div>', unsafe_allow_html=True)

    render_filter_bar(data, _go_simulate)
    

    # ----- Hero banner -----
    st.markdown('<span class="dash-hero-marker"></span>', unsafe_allow_html=True)
    hero_left, hero_stats, hero_btn = st.columns([4.2, 4.3, 1.5], vertical_alignment="center")

    with hero_left:
        st.markdown(render_hero_tag_title(data["hero"]), unsafe_allow_html=True)
    with hero_stats:
        st.markdown(render_hero_stats(data["hero"]["stats"]), unsafe_allow_html=True)
    with hero_btn:
        st.markdown('<div class="dash-hero-open"></div>', unsafe_allow_html=True)
        if st.button("Open simulator  →", use_container_width=True, key="dash_open_sim"):
            _go_simulate()

    dash_spacer()

    # ----- KPI cards -----
    st.markdown('<span class="dash-kpi-marker"></span>', unsafe_allow_html=True)
    kpi_cols = st.columns(len(data["kpis"]), gap="large")
    for kpi, col in zip(data["kpis"], kpi_cols):
        with col:
            kpi_card_from_row(kpi)

    dash_spacer()

    # ----- Simulation result table -----
    st.markdown('<span class="dash-section-table"></span>', unsafe_allow_html=True)
    all_table_rows = data["table"]["rows"]
    page_rows, _current_page, pagination = paginate_table_rows(
        all_table_rows,
        get_table_page(),
    )

    table_df = pd.DataFrame(
        [
            {
                "Cost category": r["category"],
                "Bucket": r["bucket"],
                "Actual (EUR)": r["actual"],
                "Forecast (EUR)": r["forecast"],
                "Simulation (EUR)": r["simulation"],
                "Δ vs baseline": r["delta_text"],
                "Δ %": r["delta_pct"],
                "Source": r["source"],
                "Status": r["status"],
            }
            for r in all_table_rows
        ]
    )

    csv_buf = io.StringIO()
    table_df.to_csv(csv_buf, index=False)

    header_left, header_right = st.columns([5.5, 2.5], vertical_alignment="center")

    with header_left:
        st.markdown(
            '<span class="dash-table-toolbar-marker" aria-hidden="true"></span>'
            + render_table_header(data["table"]["title"], data["table"]["meta"]),
            unsafe_allow_html=True,
        )

    with header_right:
        btn_export, btn_submit = st.columns(2, gap="small", vertical_alignment="center")
        with btn_export:
            st.download_button(
                "⬇  Export CSV",
                data=csv_buf.getvalue(),
                file_name="simulation_result.csv",
                mime="text/csv",
                use_container_width=True,
                key="dash_export_csv",
            )
        with btn_submit:
            st.button("✓  Submit", type="primary", use_container_width=True, key="dash_submit")

    st.markdown(
        render_simulation_table(page_rows, pagination),
        unsafe_allow_html=True,
    )

    dash_spacer()

    # ----- Bottom panels -----
    st.markdown('<span class="dash-panels-marker"></span>', unsafe_allow_html=True)
    panel_country, panel_deadline, panel_activity = st.columns(
        3, gap="small", vertical_alignment="top"
    )

    with panel_country:
        st.markdown(render_country_panel(data["countries"]), unsafe_allow_html=True)
    with panel_deadline:
        st.markdown(render_deadlines_panel(data["deadlines"]), unsafe_allow_html=True)
    with panel_activity:
        st.markdown(render_activity_panel(data["activities"]), unsafe_allow_html=True)
