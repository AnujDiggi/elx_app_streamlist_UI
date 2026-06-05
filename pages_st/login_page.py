"""Electrolux login page — Figma split-screen layout."""
from __future__ import annotations

import base64
import os

import streamlit as st
import streamlit.components.v1 as components

import db_st

try:
    st.set_page_config(
        page_title="Electrolux Login",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
except st.errors.StreamlitAPIException:
    pass

_PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_PAGES_DIR, "assets")
_ICON_PATH = os.path.join(_ASSETS, "elex_logo.png")
if not os.path.exists(_ICON_PATH):
    _ICON_PATH = os.path.join(os.path.dirname(_PAGES_DIR), "static", "images", "elx-icon.png")

_SVG_PATH = os.path.join(_ASSETS, "leftPannel.svg")
_DATABRICKS_PATH = os.path.join(_ASSETS, "databricksIcon.svg")
_UNION_PATH = os.path.join(_ASSETS, "Union.svg")
_CHECK_PATH = os.path.join(_ASSETS, "check.png")


def _b64(path: str) -> str:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


_SVG_B64 = _b64(_SVG_PATH)
_LOGO_B64 = _b64(_ICON_PATH)
_DATABRICKS_B64 = _b64(_DATABRICKS_PATH)
_UNION_B64 = _b64(_UNION_PATH)
_CHECK_B64 = _b64(_CHECK_PATH)

_FEATURE_ICONS = {
    "chart": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        '<rect x="3" y="10" width="4" height="11" rx="1" fill="#7dd3fc"/>'
        '<rect x="10" y="6" width="4" height="15" rx="1" fill="#38bdf8"/>'
        '<rect x="17" y="2" width="4" height="19" rx="1" fill="#0ea5e9"/>'
        "</svg>"
    ),
    "lock": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        '<rect x="5" y="10" width="14" height="11" rx="2" fill="#fbbf24"/>'
        '<path d="M8 10V8a4 4 0 118 0v2" stroke="#fbbf24" stroke-width="2.5"/>'
        "</svg>"
    ),
    "powerbi": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        '<path d="M4 18V8l6 4 4-6 6 10" stroke="#f472b6" stroke-width="2.2" stroke-linecap="round"/>'
        "</svg>"
    ),
    "globe": (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
        '<circle cx="12" cy="12" r="9" stroke="#86efac" stroke-width="1.8"/>'
        '<path d="M3 12h18M12 3c2.5 3 2.5 15 0 18M12 3c-2.5 3-2.5 15 0 18" stroke="#86efac" stroke-width="1.5"/>'
        "</svg>"
    ),
}


def _login_css() -> str:
    check_bg = f"url('data:image/png;base64,{_CHECK_B64}')" if _CHECK_B64 else "none"
    svg_bg = f"url('data:image/svg+xml;base64,{_SVG_B64}')"
    return f"""
<style>
[data-testid="stHeader"], [data-testid="stSidebar"], header, footer {{
    display: none !important;
}}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMainViewContainer"],
[data-testid="stMain"],
.block-container:has(#login-page-marker) {{
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.stApp:has(#login-page-marker) {{
    background: #F4F6F8 !important;
    height: 100vh !important;
}}

.block-container:has(#login-page-marker) {{
    max-width: 100% !important;
    padding: 0 !important;
}}

.block-container:has(#login-page-marker) [data-testid="stHorizontalBlock"] {{
    gap: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100vh !important;
    min-height: 100vh !important;
    width: 100% !important;
    flex-wrap: nowrap !important;
    align-items: stretch !important;
}}

/* ---- Left panel (Figma dark branding) ---- */
.block-container:has(#login-page-marker) [data-testid="column"]:has(.left-panel-wrapper) {{
    width: 50% !important;
    flex: 0 0 50% !important;
    min-width: 50% !important;
    max-width: 50% !important;
    height: 100vh !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
    background: #011E41 !important;
}}

.block-container:has(#login-page-marker) [data-testid="column"]:has(.left-panel-wrapper) [data-testid="stVerticalBlock"],
.block-container:has(#login-page-marker) [data-testid="column"]:has(.left-panel-wrapper) [data-testid="stElementContainer"],
.block-container:has(#login-page-marker) [data-testid="column"]:has(.left-panel-wrapper) [data-testid="stMarkdownContainer"],
.block-container:has(#login-page-marker) [data-testid="column"]:has(.left-panel-wrapper) .stMarkdown {{
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    gap: 0 !important;
    height: 100% !important;
}}

.left-panel-wrapper {{
    height: 100vh !important;
    min-height: 100vh !important;
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    padding: 56px 60px 44px 60px !important;
    box-sizing: border-box !important;
    background-color: #011E41 !important;
    background-image: {svg_bg} !important;
    background-repeat: no-repeat !important;
    background-size: cover !important;
    background-position: center center !important;
}}

.gold-bar {{
    width: 48px;
    height: 4px;
    background: #C5A059;
    margin-bottom: 22px;
    border-radius: 2px;
}}
.logo-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 44px;
}}
.logo-img {{
    height: 34px;
    width: auto;
    filter: brightness(0) invert(1);
}}
.logo-text {{
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
}}
.left-title {{
    font-size: 44px;
    font-weight: 700;
    line-height: 1.12;
    color: #ffffff;
    margin-bottom: 18px;
    max-width: 500px;
}}
.left-desc {{
    font-size: 15px;
    line-height: 1.55;
    color: rgba(255, 255, 255, 0.72);
    max-width: 440px;
    margin-bottom: 32px;
}}
.features-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    max-width: 540px;
}}
.feature-pill {{
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 999px;
    padding: 11px 16px;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.92);
    font-weight: 500;
}}
.feature-icon {{
    display: inline-flex;
    flex-shrink: 0;
}}
.stats-container {{
    display: flex;
    justify-content: space-between;
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 22px;
}}
.stat-col {{
    display: flex;
    flex-direction: column;
    gap: 3px;
    flex: 1;
}}
.stat-col:not(:last-child) {{
    border-right: 1px solid rgba(255, 255, 255, 0.15);
    margin-right: 14px;
    padding-right: 14px;
}}
.stat-num {{
    font-size: 21px;
    font-weight: 700;
    color: #ffffff;
}}
.stat-lbl {{
    font-size: 11px;
    color: rgba(255, 255, 255, 0.55);
}}

/* ---- Right panel background ---- */
.block-container:has(#login-page-marker) [data-testid="column"]:has([class*="st-key-login_right_shell"]) {{
    width: 50% !important;
    flex: 0 0 50% !important;
    min-width: 50% !important;
    max-width: 50% !important;
    height: 100vh !important;
    min-height: 100vh !important;
    background: #F4F6F8 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

.block-container:has(#login-page-marker) [data-testid="column"]:has([class*="st-key-login_right_shell"]) > [data-testid="stVerticalBlock"] {{
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
}}

/* Fixed center in right half — survives Streamlit flex overrides */
.block-container:has(#login-page-marker) [data-testid="stElementContainer"]:has([class*="st-key-login_right_shell"]),
.block-container:has(#login-page-marker) [class*="st-key-login_right_shell"] {{
    position: fixed !important;
    top: 50% !important;
    left: 75% !important;
    transform: translate(-50%, -50%) !important;
    width: 460px !important;
    max-width: calc(50vw - 48px) !important;
    z-index: 8 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.block-container:has(#login-page-marker) [data-testid="stElementContainer"]:has([class*="st-key-login_card"]),
.block-container:has(#login-page-marker) [class*="st-key-login_card"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stVerticalBlockBorderWrapper"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stVerticalBlockBorderWrapper"] > div,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stVerticalBlock"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stHorizontalBlock"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stElementContainer"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="column"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stMarkdownContainer"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] .stMarkdown {{
    background: #ffffff !important;
    background-color: #ffffff !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] {{
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid #e5e7eb !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 24px rgba(1, 30, 65, 0.08) !important;
    padding: 32px 36px 28px 36px !important;
    overflow: hidden !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stVerticalBlock"] {{
    gap: 10px !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] [data-testid="stElementContainer"] {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}}

.card-header {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 2px;
}}
.card-logo {{
    width: 42px;
    height: 42px;
    object-fit: contain;
}}
.card-title {{
    font-size: 22px !important;
    font-weight: 700 !important;
    color: #011E41 !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}}
.card-subtitle {{
    font-size: 14px !important;
    color: #6b7280 !important;
    margin: 2px 0 0 0 !important;
}}
.card-divider {{
    border: none !important;
    border-top: 1px solid #eef0f2 !important;
    margin: 10px 0 14px 0 !important;
}}

.sso-btn {{
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    border: 1px solid #FF4D4F !important;
    background: #ffffff !important;
    color: #FF4D4F !important;
    border-radius: 8px !important;
    padding: 11px 14px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    width: 100% !important;
    box-sizing: border-box !important;
}}
.sso-btn:hover {{
    background: #FFF5F5 !important;
}}
.sso-icon-text {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}}
.sso-icon, .sso-arrow {{
    width: 20px !important;
    height: 20px !important;
}}

.credentials-divider {{
    display: flex !important;
    align-items: center !important;
    margin: 14px 0 10px 0 !important;
    color: #9ca3af !important;
    font-size: 12px !important;
    width: 100% !important;
}}
.credentials-divider::before,
.credentials-divider::after {{
    content: '' !important;
    flex: 1 !important;
    border-bottom: 1px solid #e5e7eb !important;
}}
.credentials-divider::before {{ margin-right: .6em !important; }}
.credentials-divider::after {{ margin-left: .6em !important; }}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stTextInput"] {{
    width: 100% !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stTextInput"] label {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #011E41 !important;
    margin-bottom: 6px !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-baseweb="input"] {{
    border: 1px solid #D0D7E2 !important;
    border-radius: 8px !important;
    background: #f9fafb !important;
    min-height: 44px !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-baseweb="input"] > div {{
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-baseweb="input"] input {{
    border: none !important;
    background: transparent !important;
    padding: 0 14px !important;
    font-size: 14px !important;
    color: #374151 !important;
    box-shadow: none !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-baseweb="input"]:focus-within {{
    border-color: #011E41 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 2px rgba(1, 30, 65, 0.08) !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-baseweb="input"] button {{
    height: 44px !important;
    width: 44px !important;
    border: none !important;
    background: transparent !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-email"] input {{
    background-image: {check_bg} !important;
    background-repeat: no-repeat !important;
    background-position: right 12px center !important;
    background-size: 18px !important;
    padding-right: 40px !important;
}}

.password-label-row {{
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin: 4px 0 6px 0 !important;
    width: 100% !important;
}}
.input-label {{
    font-size: 14px !important;
    font-weight: 700 !important;
    color: #011E41 !important;
}}
.forgot-link {{
    font-size: 13px !important;
    color: #8c95a3 !important;
    text-decoration: none !important;
}}
.forgot-link:hover {{
    color: #011E41 !important;
    text-decoration: underline !important;
}}

.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"],
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] {{
    width: 100% !important;
    margin-top: 6px !important;
    background: transparent !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button {{
    width: 100% !important;
    background: #011E41 !important;
    background-color: #011E41 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    height: 46px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button:hover,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button:hover {{
    background: #0A3263 !important;
    background-color: #0A3263 !important;
    color: #ffffff !important;
}}
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button p,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button span,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] [data-testid="stMarkdownContainer"],
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button p,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button span,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] [data-testid="stMarkdownContainer"] {{
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

.access-info {{
    text-align: center !important;
    color: #8c95a3 !important;
    font-size: 12px !important;
    line-height: 1.55 !important;
    margin-top: 10px !important;
}}

.login-page-footer {{
    position: fixed !important;
    bottom: 22px !important;
    left: 75% !important;
    transform: translateX(-50%) !important;
    font-size: 11px !important;
    color: #a0aec0 !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    z-index: 20 !important;
    pointer-events: none !important;
}}

.block-container:has(#login-page-marker) [data-testid="stElementContainer"]:has(iframe[title="streamlit_components_v1.components.html"]) {{
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}
</style>
"""


def _feature_pill(icon_key: str, label: str) -> str:
    icon = _FEATURE_ICONS.get(icon_key, "")
    return f'<div class="feature-pill"><span class="feature-icon">{icon}</span>{label}</div>'


def render() -> None:
    if st.query_params.get("sso") == "true":
        user = db_st.authenticate("nanda.kishore@electrolux.com", "electrolux123")
        if user is not None:
            st.session_state["user"] = user
            st.query_params.clear()
            st.rerun()

    st.markdown('<span id="login-page-marker" aria-hidden="true"></span>', unsafe_allow_html=True)
    st.markdown(_login_css(), unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        features = "".join(
            [
                _feature_pill("chart", "Real-time cost simulation"),
                _feature_pill("lock", "Secure version control"),
                _feature_pill("powerbi", "Power BI integration"),
                _feature_pill("globe", "4 EMEA countries"),
            ]
        )
        st.markdown(
            f"""
            <div class="left-panel-wrapper">
              <div>
                <div class="gold-bar"></div>
                <div class="logo-row">
                  <img src="data:image/png;base64,{_LOGO_B64}" class="logo-img" alt="Electrolux" />
                  <span class="logo-text">Electrolux</span>
                </div>
                <div class="left-title">Smarter logistics<br/>decisions, faster.</div>
                <div class="left-desc">
                  The EMEA Logistics Cost Simulator replaces fragmented Excel models with a
                  centralised, interactive simulation platform.
                </div>
                <div class="features-grid">{features}</div>
              </div>
              <div class="stats-container">
                <div class="stat-col"><span class="stat-num">6M+</span><span class="stat-lbl">Records simulated</span></div>
                <div class="stat-col"><span class="stat-num">30</span><span class="stat-lbl">Concurrent users</span></div>
                <div class="stat-col"><span class="stat-num">4</span><span class="stat-lbl">EMEA countries</span></div>
                <div class="stat-col"><span class="stat-num">BC04</span><span class="stat-lbl">Current FADP</span></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        try:
            right_shell = st.container(key="login_right_shell")
        except TypeError:
            right_shell = st.container()

        with right_shell:
            try:
                login_card = st.container(border=True, key="login_card")
            except TypeError:
                login_card = st.container(border=True)

            with login_card:
                st.markdown(
                    f"""
                    <div class="card-header">
                      <img src="data:image/png;base64,{_LOGO_B64}" class="card-logo" alt="" />
                      <div>
                        <h2 class="card-title">Welcome back</h2>
                        <p class="card-subtitle">Sign in to Logistics Cost Simulator</p>
                      </div>
                    </div>
                    <hr class="card-divider" />
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <a href="?sso=true" class="sso-btn" target="_self">
                      <span class="sso-icon-text">
                        <img src="data:image/svg+xml;base64,{_DATABRICKS_B64}" class="sso-icon" alt="" />
                        Continue with Databricks SSO
                      </span>
                      <img src="data:image/svg+xml;base64,{_UNION_B64}" class="sso-arrow" alt="" />
                    </a>
                    <div class="credentials-divider"><span>or sign in with credentials</span></div>
                    """,
                    unsafe_allow_html=True,
                )

                st.text_input("Email Address", value="nanda.kishore@electrolux.com", key="email")

                st.markdown(
                    """
                    <div class="password-label-row">
                      <span class="input-label">Password</span>
                      <a href="#" class="forgot-link">Forgot password?</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                password = st.text_input("Password", type="password", label_visibility="collapsed", key="password")

                if st.button("Sign in", use_container_width=True, key="login_submit"):
                    email = st.session_state.get("email", "")
                    if email and password:
                        user = db_st.authenticate(email, password)
                        if user is not None:
                            st.session_state["user"] = user
                            st.rerun()
                        else:
                            st.error("Invalid email or password.")
                    else:
                        st.warning("Please enter email and password.")

                st.markdown(
                    """
                    <div class="access-info">
                      Access is managed by Databricks workspace.<br>
                      Contact your IT admin if you cannot sign in.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        '<div class="login-page-footer">LCS v1.0 · EMEA Supply Chain · Electrolux Group</div>',
        unsafe_allow_html=True,
    )

    components.html(
        f"""
        <script>
        (function () {{
          const doc = window.parent?.document || document;
          const svgBg = "url('data:image/svg+xml;base64,{_SVG_B64}')";
          function paint() {{
            doc.querySelectorAll(".left-panel-wrapper").forEach((el) => {{
              el.style.setProperty("background-color", "#011E41", "important");
              el.style.setProperty("background-image", svgBg, "important");
              el.style.setProperty("background-size", "cover", "important");
              el.style.setProperty("min-height", "100vh", "important");
            }});
            doc.querySelectorAll('[class*="st-key-login_right_shell"]').forEach((shell) => {{
              const host = shell.closest('[data-testid="stElementContainer"]') || shell;
              host.style.setProperty("position", "fixed", "important");
              host.style.setProperty("top", "50%", "important");
              host.style.setProperty("left", "75%", "important");
              host.style.setProperty("transform", "translate(-50%, -50%)", "important");
              host.style.setProperty("width", "460px", "important");
              host.style.setProperty("max-width", "calc(50vw - 48px)", "important");
              host.style.setProperty("z-index", "8", "important");
              host.style.setProperty("margin", "0", "important");
            }});
            doc.querySelectorAll('[class*="st-key-login_card"]').forEach((card) => {{
              const wrapper = card.querySelector('[data-testid="stVerticalBlockBorderWrapper"]') || card;
              wrapper.style.setProperty("background", "#ffffff", "important");
              wrapper.style.setProperty("background-color", "#ffffff", "important");
              card.querySelectorAll(
                '[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stElementContainer"], [data-testid="column"], [data-testid="stMarkdownContainer"], .stMarkdown'
              ).forEach((node) => {{
                if (node.closest('[data-testid="stButton"]')) return;
                node.style.setProperty("background", "#ffffff", "important");
                node.style.setProperty("background-color", "#ffffff", "important");
              }});
            }});
            doc.querySelectorAll('[class*="st-key-login_submit"] button').forEach((btn) => {{
              btn.style.setProperty("background", "#011E41", "important");
              btn.style.setProperty("background-color", "#011E41", "important");
              btn.style.setProperty("color", "#ffffff", "important");
              btn.querySelectorAll("p, span, [data-testid='stMarkdownContainer']").forEach((t) => {{
                t.style.setProperty("background", "transparent", "important");
                t.style.setProperty("color", "#ffffff", "important");
              }});
            }});
          }}
          paint();
          let n = 0;
          const t = setInterval(() => {{ paint(); if (++n > 16) clearInterval(t); }}, 120);
        }})();
        </script>
        """,
        height=0,
        width=0,
    )


if __name__ == "__main__":
    render()
