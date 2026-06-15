"""Bits shared by every authenticated page: a small header strip + the
global CSS that the Streamlit-port screens lean on."""
from __future__ import annotations

import streamlit as st


# Manrope + Inter are loaded as graceful fallbacks for users who don't have
# the proprietary Electrolux Sans corporate font installed locally. These two
# match what the Flask templates load (see templates/base.html).
GLOBAL_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>

/* ------------------------------------------------ */
/* FONT */
/* ------------------------------------------------ */

html,
body,
[class*="st-"],
[data-testid],
button,
input,
textarea,
select,
label,
p,
span,
div,
h1,
h2,
h3,
h4,
h5,
h6,
li,
a,
code,
td,
th {

    font-family:
        'Electrolux Sans', 'Manrope', 'Inter', sans-serif !important;
}

/* ------------------------------------------------ */
/* KEEP MATERIAL ICONS */
/* ------------------------------------------------ */

.material-icons,
.material-symbols-rounded,
.material-symbols-outlined,
[class*="material-symbols"],
[class*="material-icons"],
[data-testid="stIconMaterial"] {

    font-family:
        'Material Symbols Rounded',
        'Material Icons',
        'Material Symbols Outlined' !important;
}

/* ------------------------------------------------ */
/* PAGE */
/* ------------------------------------------------ */

html,
body,
.stApp{
    background:#F1F3FB !important;
}

/* remove default streamlit spacing */

.block-container{
    padding-top:0rem !important;
    padding-bottom:1rem !important;
    padding-left:0rem !important;
    padding-right:0rem !important;
    max-width:100% !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"],
section.main > div{
    padding-left:0 !important;
    padding-right:0 !important;
}

[data-testid="stMainBlockContainer"] > div{
    padding-left:0 !important;
    padding-right:0 !important;
}

/* remove header space */

[data-testid="stHeader"]{
    display:none !important;
}

/* remove top margin */

.main .block-container{
    margin-top:0 !important;
}

/* avoid horizontal scroll from full-bleed navbar */
.stApp{
    overflow-x:clip !important;
}

/* ------------------------------------------------ */
/* SIDEBAR */
/* ------------------------------------------------ */

[data-testid="stSidebar"]{
    display:none !important;
}

[data-testid="collapsedControl"]{
    display:none !important;
}

/* ------------------------------------------------ */
/* NAVBAR */
/* ------------------------------------------------ */

.navbar-container{
    background:#011E41;
    padding:5px 12px;
    margin:0;
}

.navbar-user{
    color:white;
    text-align:right;
    line-height:1.3;
}

.navbar-role{
    color:#C6D2E1;
    font-size:12px;
}

.navbar-divider{
    border:none;
    border-top:1px solid #18365D;
    margin:0;
}

/* ------------------------------------------------ */
/* BUTTONS */
/* ------------------------------------------------ */

div[data-testid="stButton"] button{

    border:none !important;
    background:transparent !important;
    color:white !important;

    font-size:14px !important;
    font-weight:500 !important;

    border-radius:6px !important;

    box-shadow:none !important;

    min-height:36px !important;
}

/* Dashboard filter bar — Start simulation (button is sibling of marker, not inside it) */
.block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button,
.block-container:has(#dashboard-page) [class*="st-key-dash_start_sim"] button{
    background:#011E41 !important;
    color:#ffffff !important;
    box-shadow:none !important;
}

.block-container:has(#dashboard-page) [data-testid="column"]:has(.figma-filters-actions) [data-testid="stButton"] button:hover,
.block-container:has(#dashboard-page) [class*="st-key-dash_start_sim"] button:hover{
    background:#013060 !important;
    color:#ffffff !important;
}

/* Login page — Sign in button */
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button{
    background:#011E41 !important;
    background-color:#011E41 !important;
    color:#ffffff !important;
    opacity:1 !important;
    box-shadow:none !important;
}
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button:hover,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button:hover{
    background:#0A3263 !important;
    background-color:#0A3263 !important;
    color:#ffffff !important;
}
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button p,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] button span,
.block-container:has(#login-page-marker) [class*="st-key-login_submit"] [data-testid="stMarkdownContainer"],
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button p,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] button span,
.block-container:has(#login-page-marker) [class*="st-key-login_card"] div[data-testid="stButton"] [data-testid="stMarkdownContainer"]{
    background:transparent !important;
    background-color:transparent !important;
    color:#ffffff !important;
}

div[data-testid="stButton"] button:hover{

    background:rgba(255,255,255,.08) !important;
    color:white !important;
}

/* Simulate page — Save / chevron (override global white navbar button styles) */
.block-container:has(#simulate-page) [class*="st-key-sim_save_"] button,
.block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button{
    background:#DCE8F2 !important;
    color:#000000 !important;
    border:1px solid #D4DBE6 !important;
    border-radius:8px !important;
    opacity:1 !important;
}

.block-container:has(#simulate-page) [class*="st-key-sim_save_"] button:hover,
.block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button:hover,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button:hover,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button:hover{
    background:#cfe0f0 !important;
    color:#000000 !important;
}

/* Simulate page — Reset / Start simulation footer */
.block-container:has(#simulate-page) [class*="st-key-sim_reset"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button{
    background:#ffffff !important;
    color:#011E41 !important;
    border:1px solid #E5E7EB !important;
    border-radius:0 !important;
    font-weight:600 !important;
    font-size:13px !important;
    min-height:42px !important;
    height:42px !important;
    box-shadow:none !important;
    opacity:1 !important;
}

.block-container:has(#simulate-page) [class*="st-key-sim_reset"] button:hover,
.block-container:has(#simulate-page) [class*="st-key-sim_reset"] button:focus,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button:hover,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-reset-col) div[data-testid="stButton"] button:focus{
    background:#f8fafc !important;
    color:#011E41 !important;
    border:1px solid #E5E7EB !important;
}

.block-container:has(#simulate-page) [class*="st-key-sim_start"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button{
    background:#011E41 !important;
    color:#ffffff !important;
    border:none !important;
    border-radius:0 !important;
    font-weight:600 !important;
    font-size:13px !important;
    min-height:42px !important;
    height:42px !important;
    box-shadow:none !important;
    opacity:1 !important;
}

.block-container:has(#simulate-page) [class*="st-key-sim_start"] button:hover,
.block-container:has(#simulate-page) [class*="st-key-sim_start"] button:focus,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button:hover,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-start-col) div[data-testid="stButton"] button:focus{
    background:#013060 !important;
    color:#ffffff !important;
    border:none !important;
}

/* Navbar mode toggle — must stay clickable (no invisible overlay) */
[class*="st-key-mode_ctrl"] button,
[class*="st-key-mode_mgmt"] button{
    pointer-events:auto !important;
    opacity:1 !important;
    cursor:pointer !important;
}

div[data-testid="stButton"] button:focus{
    border:none !important;
    box-shadow:none !important;
}

/* ------------------------------------------------ */
/* SELECT BOX */
/* ------------------------------------------------ */

div[data-baseweb="select"]{

    border-radius:8px !important;
}

/* ------------------------------------------------ */
/* INPUT */
/* ------------------------------------------------ */

input{

    border-radius:8px !important;
}

/* ------------------------------------------------ */
/* METRICS */
/* ------------------------------------------------ */

[data-testid="stMetric"]{

    background:white;

    border:1px solid #E4EAF2;

    border-radius:12px;

    padding:12px;
}

/* ------------------------------------------------ */
/* CONTAINERS */
/* ------------------------------------------------ */

[data-testid="stVerticalBlockBorderWrapper"]{

    border-radius:12px !important;

    border:1px solid #E4EAF2 !important;

    background:white !important;
}

/* Simulate — section cards must stay white (Streamlit bordered container tint) */
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap),
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) > div,
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stVerticalBlock"],
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stHorizontalBlock"],
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="column"]:not(:has(.sim-num-wrap)),
.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap) [data-testid="stElementContainer"]{
    background:#ffffff !important;
    background-color:#ffffff !important;
}

.block-container:has(#simulate-page) [class*="st-key-sim_grp_"]{
    background:#ffffff !important;
    background-color:#ffffff !important;
    border:1px solid #C3C3C3 !important;
    border-radius:0 !important;
}

.block-container:has(#simulate-page) [data-testid="stVerticalBlockBorderWrapper"]:has(.sim-param-group-wrap),
.block-container:has(#simulate-page) [class*="st-key-sim_grp_"]{
    border-radius:0 !important;
}

/* Simulate — parameter % chip row and section Save/chevron: 8px corners */
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stHorizontalBlock"],
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"],
.block-container:has(#simulate-page) [class*="st-key-sim_f_"] div[data-baseweb="input"],
.block-container:has(#simulate-page) [class*="st-key-sim_save_"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-save-col) div[data-testid="stButton"] button,
.block-container:has(#simulate-page) [class*="st-key-sim_toggle_"] button,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-toggle-col) div[data-testid="stButton"] button{
    border-radius:8px !important;
}
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-chip-row) div[data-baseweb="input"],
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-input-marker) div[data-baseweb="input"],
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-chip-row) [data-testid="stTextInput"] input,
.block-container:has(#simulate-page) [data-testid="column"]:has(.sim-pct-input-marker) [data-testid="stTextInput"] input{
    border:none !important;
    border-radius:0 !important;
    background:transparent !important;
    box-shadow:none !important;
}

.block-container:has(#simulate-page) [data-testid="column"]:has(.elx-filter-panel) div[data-baseweb="select"] > div,
.block-container:has(#simulate-page) [data-testid="column"]:has(.elx-filter-dd) div[data-baseweb="select"] > div,
.block-container:has(#simulate-page) [data-testid="column"]:has(.elx-filter-ctx) div[data-baseweb="select"] > div{
    border-radius:4px !important;
}

/* ------------------------------------------------ */
/* CHIPS */
/* ------------------------------------------------ */

.live-chip {

    display:inline-flex;
    align-items:center;
    gap:8px;

    padding:6px 12px;

    border-radius:999px;

    background:#ECFDF5;

    color:#065F46;

    font-size:12px;

    font-weight:600;
}

.live-chip .dot {

    width:8px;
    height:8px;

    border-radius:50%;

    background:#22C55E;

    display:inline-block;
}

.ctx-pill {

    display:inline-block;

    padding:4px 10px;

    margin-right:6px;

    border-radius:999px;

    background:#EFF3F8;

    color:#344054;

    font-size:12px;
}

/* ------------------------------------------------ */
/* STEPPER */
/* ------------------------------------------------ */

.step-box{

    text-align:center;

    font-size:13px;

    font-weight:600;
}

.step-active{

    color:#0B5ED7;
}

.step-done{

    color:#16A34A;
}

/* ------------------------------------------------ */
/* PARAM HEADER */
/* ------------------------------------------------ */

.param-header{
    background:#032B5A;
    color:white;
    padding:20px 24px;
    border-radius:12px 12px 0 0;

    display:flex;
    align-items:center;
    justify-content:space-between;
}

.param-title{
    font-size:18px;
    font-weight:700;
    margin:0;
    color:white;
}

.param-subtitle{
    font-size:13px;
    color:#B9C6D8;
    margin-top:4px;
    margin-bottom:12px;
}

.saved-chip{
    background:#0F8F4B;
    color:white;
    padding:8px 16px;
    border-radius:8px;
    font-size:13px;
    font-weight:600;
}

.context-chip{
    display:inline-block;
    background:#173A63;
    border:1px solid rgba(255,255,255,.1);

    color:white;

    padding:4px 10px;
    border-radius:6px;

    font-size:12px;
    font-weight:600;

    margin-right:6px;
}

.header-content-left {
    display: flex;
    flex-direction: column;
    gap: 6px
}

.small-data {
    color: #ffffff;
}

/* ------------------------------------------------ */
/* IMPACT VALUE */
/* ------------------------------------------------ */

.impact-value{

    font-size:46px;

    font-weight:700;

    color:#DC2626;
}

/* ------------------------------------------------ */
/* SUCCESS ALERT */
/* ------------------------------------------------ */

[data-testid="stAlert"]{

    border-radius:10px;
}


.stepper-container{
    background:white;
    border:1px solid #E4EAF2;
    border-radius:12px;
    padding:20px 30px;
    margin-bottom:20px;
}

.stepper{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    position:relative;
}

.stepper::before{
    content:"";
    position:absolute;
    top:14px;
    left:35px;
    right:35px;
    height:2px;
    background:#D8E0EA;
    z-index:1;
}

.stepper-progress{
    position:absolute;
    top:14px;
    left:35px;
    width:22%;
    height:2px;
    background:#198754;
    z-index:2;
}

.step-item{
    position:relative;
    z-index:3;
    text-align:center;
    width:20%;
}

.step-circle{
    width:28px;
    height:28px;
    border-radius:50%;
    margin:auto;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:13px;
    font-weight:700;
}

.step-done{
    background:#198754;
    color:white;
}

.step-active{
    background:#011E41;
    color:white;
}

.step-pending{
    background:white;
    border:2px solid #D8E0EA;
    color:#94A3B8;
}

.step-label{
    margin-top:10px;
    font-size:13px;
    font-weight:600;
}

.step-label.done{
    color:#198754;
}

.step-label.active{
    color:#011E41;
}

.step-label.pending{
    color:#64748B;
}


.st-emotion-cache-tn0cau {
    display: flex !important;
    flex-direction: column !important;

    justify-content: flex-start !important;
    align-items: stretch !important;

    gap: 0 !important;
    height: auto !important;
}

</style>
"""


def inject_global_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def topbar(scope_label: str = "FR10 · EA1 · BC04") -> None:
    """Render the user / scope / sign-out strip at the top of an auth'd page.

    The page-to-page nav is handled by `st.navigation` in the sidebar, so this
    strip is intentionally lighter than templates/_topbar.html.
    """
    user = st.session_state.get("user")
    if user is None:
        return

    brand_col, scope_col, user_col, signout_col = st.columns([3, 3, 3, 1])
    brand_col.markdown(
        '<div class="brand-row">⚡ <span>Electrolux</span></div>',
        unsafe_allow_html=True,
    )
    scope_col.markdown(
        f'<div class="live-chip"><span class="dot"></span>{scope_label}</div>',
        unsafe_allow_html=True,
    )
    user_col.markdown(f'**{user["name"]}**  \n_{user["role"]}_')
    if signout_col.button("Sign out", key="signout_btn"):
        st.session_state.pop("user", None)
        st.rerun()
    st.divider()
