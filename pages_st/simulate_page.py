"""Simulate page — Figma layout (navbar from streamlit_app.top_navigation)."""
from __future__ import annotations

import streamlit as st

import db_st
from pages_st.Common_Pages.simulate_ui import (
    init_simulate_state,
    inject_css,
    inject_paint_js,
    inject_simulate_layout_css,
    process_pending_save,
    render_action_bar,
    render_parameter_group,
    render_parameter_panel_header,
    render_simulate_context_bar,
    render_simulate_sidebar,
    # dash_spacer,
    # render_stepper,
)


def _render_form_panel(data: dict, groups: list) -> None:
    with st.container(border=True):
        st.markdown('<span class="sim-main-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
        render_parameter_panel_header(data, groups)
        for idx, group in enumerate(groups):
            render_parameter_group(group, idx, groups)
        process_pending_save(groups)
        render_action_bar(data, groups)


def _render_main_section(data: dict, groups: list) -> None:
    """Section 3 — form panel + sidebar with 24px left/right inset."""
    try:
        section = st.container(key="sim_main_content")
    except TypeError:
        section = st.container()
    with section:
        st.markdown(
            '<span class="sim-content-section-marker" aria-hidden="true"></span>',
            unsafe_allow_html=True,
        )
        main_l, main_r = st.columns([3, 1], gap="small")
        with main_l:
            st.markdown('<span class="sim-main-panel-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
            _render_form_panel(data, groups)
        with main_r:
            render_simulate_sidebar(data, groups)


def render() -> None:
    data = db_st.get_simulate_data()
    groups = data["param_groups"]
    data["param_groups"] = groups

    init_simulate_state(groups)
    inject_css()
    inject_simulate_layout_css()

    # CONTEXT bar directly under navbar (not inside page_body wrapper).
    render_simulate_context_bar(data)

    try:
        page_body = st.container(key="sim_page_body")
    except TypeError:
        page_body = st.container()
    with page_body:
        st.markdown('<span class="sim-page-body-marker" aria-hidden="true"></span>', unsafe_allow_html=True)

        # render_stepper(data["steps"])
        # dash_spacer()
        _render_main_section(data, groups)

    # Run after all widgets mount so number-input layout paints correctly on first visit.
    inject_paint_js()
