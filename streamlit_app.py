# """Multipage Streamlit entry point for nanda_app.

# Run with: `streamlit run streamlit_app.py`

# Mirrors the Flask app's surface:
#   /login   → Sign in (email/password + SSO info banner)
#   /        → redirect to /dashboard or /login depending on auth
#   /dashboard → Dashboard
#   /simulate  → Simulate
#   /admin     → Admin (admin-only, hidden from sidebar for non-admins)
#   /logout    → "Sign out" button in the topbar

# Auth state lives in `st.session_state["user"]`; pages re-read it on every run.
# """
# from __future__ import annotations

# import streamlit as st

# from pages_st import admin_page, dashboard_page, login_page, simulate_page
# from pages_st._shared import inject_global_css

# st.set_page_config(
#     page_title="Logistics Cost Simulator · Electrolux",
#     page_icon="📊",
#     layout="wide",
# )
# inject_global_css()

# user = st.session_state.get("user")

# if user is None:
#     # Single hidden-nav page until the user signs in.
#     nav = st.navigation(
#         [st.Page(login_page.render, title="Sign in", url_path="login",
#                  icon=":material/login:")],
#         position="hidden",
#     )
# else:
#     dashboard = st.Page(dashboard_page.render, title="Dashboard",
#                         url_path="dashboard", icon=":material/dashboard:",
#                         default=True)
#     simulate  = st.Page(simulate_page.render,  title="Simulate",
#                         url_path="simulate",  icon=":material/science:")
#     pages = [dashboard, simulate]
#     if user["is_admin"]:
#         pages.append(st.Page(admin_page.render, title="Admin",
#                              url_path="admin",
#                              icon=":material/admin_panel_settings:"))

#     # Expose page handles so dashboard buttons can `st.switch_page(...)`.
#     st.session_state["_pages"] = {"dashboard": dashboard, "simulate": simulate}

#     nav = st.navigation(pages)

# nav.run()



"""
Custom Streamlit entry point using Top Navigation
"""

from __future__ import annotations

import streamlit as st

from pages_st import (
    admin_page,
    dashboard_page,
    login_page,
    simulate_page,
)

from pages_st._shared import inject_global_css
from pages_st.Common_Pages.navbar import top_navigation

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Logistics Cost Simulator · Electrolux",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()

# --------------------------------------------------
# HIDE STREAMLIT SIDEBAR
# --------------------------------------------------

st.markdown(
    """
    <style>

    [data-testid="stSidebar"]{
        display:none;
    }

    [data-testid="collapsedControl"]{
        display:none;
    }

    #MainMenu{
        visibility:hidden;
    }

    footer{
        visibility:hidden;
    }

    header{
        visibility:hidden;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    section.main > div{
        padding-left:0 !important;
        padding-right:0 !important;
    }

    .stApp{
        overflow-x:clip !important;
        background:#F1F3FB !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# AUTH
# --------------------------------------------------

user = st.session_state.get("user")

# --------------------------------------------------
# LOGIN PAGE
# --------------------------------------------------

if user is None:
    login_page.render()
    st.stop()

# --------------------------------------------------
# PAGE ROUTING
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# --------------------------------------------------
# TOP NAVIGATION
# --------------------------------------------------

top_navigation()

# --------------------------------------------------
# PAGE RENDERING
# --------------------------------------------------

page = st.session_state.page

if page == "dashboard":
    dashboard_page.render()

elif page == "simulate":
    simulate_page.render()

elif page == "admin":

    if user.get("is_admin"):
        admin_page.render()
    else:
        st.error("You do not have access to this page.")

else:
    dashboard_page.render()
