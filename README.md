# Logistics Cost Simulator (LCS) — Streamlit build

Self-contained Streamlit port of the Electrolux Logistics Cost Simulator
prototype. Same data (SQLite `app.db`) and same screens as the Flask build,
each section rendered through its native Streamlit widget.

## Layout

```
streamlit_elx_app/
  streamlit_app.py          # entry point — auth + st.navigation
  db_st.py                  # SQLite data layer (auth, dashboard, simulate, admin)
  schema.sql                # DB schema (executed by seed.py)
  seed.py                   # rebuilds app.db with demo data
  requirements.txt
  app.db                    # created by `python seed.py` (or shipped pre-seeded)
  pages_st/
    login_page.py           # /login   — email + password, Databricks SSO banner
    dashboard_page.py       # /dashboard — filters, KPIs, results table, panels
    simulate_page.py        # /simulate  — context bar, stepper, parameter form
    admin_page.py           # /admin     — add user + toggle admin (admin-only)
    _shared.py              # topbar + global CSS shared by auth'd pages
  static/images/elx-icon.png
```

## Setup

```powershell
# 1) Create + activate a venv (Python 3.10+)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2) Install deps
pip install -r requirements.txt

# 3) Seed the database (only needed if app.db is missing)
python seed.py

# 4) Run
streamlit run streamlit_app.py
```

## Default credentials

| Email                            | Password       | Admin |
|----------------------------------|----------------|-------|
| `nanda.kishore@electrolux.com`   | `electrolux123`| yes   |
| `demo@electrolux.com`            | `demo`         | no    |

## Widget mapping

Each UI section maps to a specific native Streamlit widget — these mappings
are visible as badges in the original Flask templates and preserved here:

| Section                       | Widget                                    |
|-------------------------------|-------------------------------------------|
| Context / filter dropdowns    | `st.selectbox`                            |
| DD% / Inflation sliders       | `st.slider`                               |
| Parameter inputs              | `st.number_input`                         |
| Collapsible parameter groups  | `st.expander`                             |
| Run simulation / form submits | `st.form_submit_button`                   |
| Simulation result table       | `st.dataframe`                            |
| KPI / hero stats              | `st.metric`                               |
| Excel export                  | `st.download_button`                      |
| Status alerts                 | `st.warning` / `st.success` / `st.info`   |
| Country progress              | `st.progress`                             |



.\myenv\Scripts\activate