# Logistics Cost Simulator (LCS) — Code & Requirements Guide

This document explains **what the app is for**, **how it is structured**, and **how the main flows work** — especially the **Simulate** page (`simulate_ui.py`), which is the largest and most complex part of the codebase.

---

## 1. What is this app?

**Electrolux Logistics Cost Simulator (LCS)** is a Streamlit web app that lets logistics controllers:

1. **View a dashboard** of cost KPIs, simulation results, country progress, deadlines, and activity.
2. **Run cost simulations** by entering parameters (Direct Delivery %, inflation, process costs) and starting a simulation.
3. **Manage users** (admin-only).

### Origin & goal

- This repo is a **Streamlit port** of an earlier **Flask prototype**.
- It uses the **same SQLite database** (`app.db`) and aims for **visual parity with Figma designs**.
- It is a **prototype / demo** — most numbers come from seeded DB data; the simulation engine stores snapshots in session state rather than calling a real backend.

### Users & roles

| Role        | Access                                      |
|-------------|---------------------------------------------|
| Controller  | Dashboard + Simulate                        |
| Admin       | Dashboard + Simulate + Admin (user mgmt)    |

Default logins (after `python seed.py`):

| Email                          | Password        | Admin |
|--------------------------------|-----------------|-------|
| `nanda.kishore@electrolux.com` | `electrolux123` | yes   |
| `demo@electrolux.com`          | `demo`          | no    |

---

## 2. High-level architecture

```
streamlit_app.py          ← Entry point: auth gate, top nav, page routing
    │
    ├── login_page.py     ← Unauthenticated users only
    │
    └── (authenticated)
            ├── navbar.py           ← Top navigation bar
            ├── dashboard_page.py   ← KPIs, table, panels
            ├── simulate_page.py    ← Thin orchestrator
            │       └── simulate_ui.py   ← All Simulate UI + logic (~3000 lines)
            └── admin_page.py       ← Add/toggle users

db_st.py                  ← SQLite read/write layer (cached connection)
app.db                    ← All page content + users (seeded by seed.py)
schema.sql + seed.py      ← DB structure and demo data
```

### Request lifecycle (Streamlit rerun model)

Every user interaction triggers a **full script rerun**:

1. `streamlit_app.py` checks `st.session_state["user"]`.
2. If not logged in → `login_page.render()` and `st.stop()`.
3. If logged in → `top_navigation()` then render page from `st.session_state.page`.
4. Each page calls `db_st.get_*_data()` and renders widgets.
5. Button clicks update `st.session_state` and call `st.rerun()`.

**Auth state:** `st.session_state["user"]` is a dict: `{ email, name, role, is_admin, initials }`.

**Page routing:** `st.session_state.page` is one of `"dashboard" | "simulate" | "admin"`.

---

## 3. Project layout (files you will touch most)

| Path | Purpose |
|------|---------|
| `streamlit_app.py` | App entry, hides sidebar, routes pages |
| `db_st.py` | All DB queries; builds simulate parameter groups |
| `schema.sql` | Table definitions |
| `seed.py` | Rebuilds `app.db` with demo data |
| `pages_st/login_page.py` | Split-screen login (email/password + Databricks SSO banner) |
| `pages_st/dashboard_page.py` | Dashboard layout |
| `pages_st/simulate_page.py` | Simulate page shell (loads data, calls `simulate_ui`) |
| `pages_st/Common_Pages/simulate_ui.py` | Simulate UI, CSS, session logic, calculations |
| `pages_st/Common_Pages/dashboard_ui.py` | Dashboard HTML/CSS components |
| `pages_st/Common_Pages/navbar.py` | Electrolux top nav |
| `pages_st/Common_Pages/filter_bar.py` | Shared CONTEXT filter row |
| `pages_st/Common_Pages/filter_select.py` | Styled dropdown component |
| `pages_st/_shared.py` | Global fonts/CSS for authenticated pages |
| `pages_st/admin_page.py` | User management |

---

## 4. Data layer (`db_st.py`)

### Connection

- SQLite file: `app.db` (next to `db_st.py`).
- Connection is cached with `@st.cache_resource` (one connection per Streamlit process).

### Main functions

| Function | Returns | Used by |
|----------|---------|---------|
| `authenticate(email, password)` | User dict or `None` | Login |
| `get_dashboard_data(user_name)` | Filters, KPIs, table, countries, etc. | Dashboard |
| `get_simulate_data()` | Context, steps, param groups, impact, status | Simulate |
| `list_users()`, `create_user()`, `set_admin()` | Admin CRUD | Admin |

### Simulate data shape (`get_simulate_data()`)

```python
{
    "context":        [{"key": "...", "value": "..."}],   # top CONTEXT bar
    "live_label":     "...",
    "steps":          [{"label": "...", "state": "done|..."}],
    "params_title":   "...",
    "params_sub":     "...",
    "param_groups":   [ ... ],   # see below
    "impact":         {"headline", "sub", "note", "rows": [...]},
    "summary":        {"title", "badge", "rows": [...]},
    "status_rows":    [...],
    "ctx_rows":       [...],
    ...
}
```

### Parameter groups (business content)

Groups are loaded from `simulate_param_groups` in the DB, but **three groups are built in code** with special logic:

| DB title | UI title | Fields | Logic location |
|----------|----------|--------|----------------|
| Delivery Mix / Direct Delivery | **Direct Delivery** | 4 countries (FR, ES, IT, PT) | `db_st._delivery_mix_fields()` + `simulate_ui._compute_delivery_mix()` |
| Inflation Rates | **Inflation Rates** | inflation input + 5 impacts + 5 calculated rows | `db_st._inflation_rates_fields()` + `simulate_ui._compute_inflation_rates()` |
| Process cost / Project Costs | **Process cost** | PTC / STC / SWC sections (14 inputs) | `db_st._process_cost_fields()` |

**Excluded:** `Warehouse Costs (SWC)` is filtered out in `get_simulate_data()`.

Each **generic** group field dict looks like:

```python
{
    "name": "...",
    "name_tags": [{"text": "PTC", "class": "ptc"}],
    "desc": "...",
    "value": 0,
    "min": 0, "max": 100,
    "step": None,      # None → integer field
    "suffix": "%",
}
```

Process-cost fields may have `"field_role": "section"` for subsection headers (not inputs).

---

## 5. Page-by-page requirements

### 5.1 Login (`login_page.py`)

**Requirements:**
- Figma split-screen layout (brand panel + form).
- Email + password sign-in against `users` table.
- Databricks SSO info banner (informational; not wired to real SSO).
- On success → set `st.session_state["user"]` and rerun.

### 5.2 Dashboard (`dashboard_page.py` + `dashboard_ui.py`)

**Requirements:**
- **Filter bar** at top (Business Area, Commercial Area, etc.) + link to open simulator.
- **Hero banner** with tag, title, stats, “Open simulator →” button.
- **KPI cards** (tone, value, badge, meta).
- **Simulation results table** with pagination and CSV export.
- **Bottom panels:** country progress, deadlines, activity feed.

Data is **read-only** from SQLite; Export/Submit buttons are UI placeholders (Submit does not persist).

### 5.3 Simulate (`simulate_page.py` + `simulate_ui.py`)

**Requirements (Figma-aligned):**

```
┌─────────────────────────────────────────────────────────────┐
│  TOP NAVBAR (navbar.py)                                      │
├─────────────────────────────────────────────────────────────┤
│  CONTEXT filter bar (Business Area, Country, Period, …)      │
├──────────────────────────────────┬──────────────────────────┤
│  MAIN PANEL (75%)                │  SIDEBAR (330px)         │
│  ┌────────────────────────────┐  │  • Live Impact card      │
│  │ Panel header (dark blue)   │  │  • Submission history    │
│  │ Title + 5 scope dropdowns  │  │    cards per Save        │
│  ├────────────────────────────┤  │                          │
│  │ Accordion parameter groups │  │                          │
│  │  • Direct Delivery         │  │                          │
│  │  • Inflation Rates         │  │                          │
│  │  • Process cost            │  │                          │
│  ├────────────────────────────┤  │                          │
│  │ Footer: progress + Reset   │  │                          │
│  │         Start Simulation   │  │                          │
│  └────────────────────────────┘  │                          │
└──────────────────────────────────┴──────────────────────────┘
```

**User workflow:**

1. Optionally change **CONTEXT** and **panel header** filters (session-only; not saved to DB).
2. Expand a parameter group (accordion).
3. Enter **% values** in text inputs (styled as chips).
4. Click **Save** on a section → locks fields, runs section calculations, adds a card to the right sidebar.
5. Click **Start Simulation** → captures all current values into a snapshot; marks simulation as run.
6. Click **Reset** → clears all simulate session state.

**Important:** Saving all sections is **optional**. Start Simulation uses **whatever is currently in the form**.

### 5.4 Admin (`admin_page.py`)

**Requirements:**
- Only for `is_admin=True`.
- Add user form (email, name, password, role, admin checkbox).
- List users with Make admin / Revoke admin (cannot change self).

---

## 6. Simulate page — deep dive

### 6.1 Render order (`simulate_page.py`)

```python
def render():
    data = db_st.get_simulate_data()
    groups = data["param_groups"]
    init_simulate_state(groups)      # session keys + pending reset
    inject_css()                     # global simulate styles (once)
    inject_simulate_layout_css()     # layout per run
    render_simulate_context_bar(data)  # under navbar
    _render_main_section(data, groups) # form + sidebar
    inject_paint_js()                # DOM fixes after widgets mount
```

### 6.2 Key functions in `simulate_ui.py`

| Function | Role |
|----------|------|
| `init_simulate_state()` | Initialize saved flags, handle reset |
| `render_simulate_context_bar()` | Top CONTEXT row |
| `render_parameter_panel_header()` | Dark header + 5 filter dropdowns |
| `render_parameter_group()` | One accordion card (bordered container) |
| `render_parameter_group_header()` | Title, tags, Save, expand/collapse |
| `render_parameter_group_fields()` | Input rows or section headers |
| `render_action_bar()` | Progress bar, Reset, Start Simulation |
| `render_simulate_sidebar()` | Live impact + submission history |
| `_on_save_group()` | Save handler + calculations |
| `_on_start_simulation()` | Snapshot all field values |

### 6.3 Session state keys

| Key | Meaning |
|-----|---------|
| `sim_saved_{i}` | Group `i` has been saved (fields locked) |
| `sim_open_{i}` | Group `i` accordion open/closed |
| `sim_f_{gi}_{fi}` | Text input value for field |
| `sim_saved_display_{gi}_{fi}` | Frozen display string after save |
| `sim_dm_calc_{gi}` | Delivery mix calculation rows |
| `sim_infl_calc_{gi}` | Inflation calculation rows |
| `simulation_run` | `True` after Start Simulation |
| `simulation_snapshot` | List of all param values at run time |
| `sim_submission_history` | List of per-section save snapshots |
| `sim_reset_requested` | Triggers full reset on next init |

### 6.4 Business calculations

#### Direct Delivery (DD%)

Per country field:

```
effective_dd = clamp(0, 100, dd_change + user_input)
```

Baseline `dd_change` per country (from `db_st`):

| Country | Code | dd_change |
|---------|------|-----------|
| France  | FR10 | 10        |
| Spain   | ES10 | 30        |
| Italy   | IT16 | 5         |
| Portugal| PT10 | 0         |

#### Inflation Rates

Uses a fixed **inflation vector**: `(2.0, 3.0, 5.0, 2.0, -1.0, 2.0)` and per-row **impact weights** (PTC, STC, SWC var, etc.).

For each impact row:

```
cell[i] = inflation_vector[i] * impact[i] / 100
baseline = sum(cells)
effective_total = baseline + user_input
```

Calculated rows (PTC, STC, SWC var, …) derive their user input from the matching impact row.

#### Process cost

14 percentage inputs grouped under **PTC**, **STC**, and **SWC Variable** section headers. No auto-calculation — values pass through to snapshots as entered.

### 6.5 Field input behavior

- Fields use `st.text_input` (not `st.number_input`) for Figma chip styling.
- `_parse_field_text()` validates and clamps integers (0–100 when `max` set).
- After **Save**, inputs render as **read-only chips** (`locked = _group_is_saved(index)`).
- `_FIELD_WIDGET_VERSION` bumps reset widget keys when input behavior changes.

### 6.6 Styling approach

Simulate uses **heavy CSS injection** because Streamlit’s default layout does not match Figma:

- **Design tokens** at top of `simulate_ui.py` (`_PRIMARY`, `_PANEL_HEADER_BG`, etc.).
- **Marker spans** (e.g. `.sim-main-panel-marker`) let CSS target Streamlit containers via `:has()`.
- **`inject_paint_js()`** runs JavaScript after render to fix number-input layout on first paint.
- **Keyed containers** (`st.container(key="sim_main_content")`) for stable CSS selectors.

Same pattern exists in `dashboard_ui.py` and `navbar.py`.

---

## 7. Shared components

### Top navigation (`navbar.py`)

- Electrolux logo + page links (Dashboard, Simulate, Admin if admin).
- Placeholder links: History, Export, Reports (disabled).
- Controller / Management mode toggle (session: `nav_user_mode`).
- Scope pill, notification bell, profile + sign out.

### Filter bar (`filter_bar.py` + `filter_select.py`)

- Used on Dashboard and Simulate CONTEXT rows.
- `filter_select()` renders a labeled dropdown with Figma styling.
- Panel header on Simulate uses 5 presets: Business Area, Commercial Area, Country, Period, Company.

### Global CSS (`_shared.py`)

- Loads Manrope + Inter fonts.
- Sets page background `#F1F3FB`.
- Shared button/input overrides.

---

## 8. Database tables (quick reference)

### Auth
- `users` — email, password_hash, name, role, is_admin

### Dashboard
- `dashboard_meta`, `dashboard_table_meta` — singleton config
- `dashboard_filters`, `dashboard_sliders`, `dashboard_hero_stats`, `dashboard_kpis`
- `dashboard_table_rows`, `countries`, `deadlines`, `activities`

### Simulate
- `simulate_meta` — titles, progress labels, impact headline
- `simulate_context`, `simulate_steps`, `simulate_context_pills`
- `simulate_param_groups`, `simulate_param_group_tags`, `simulate_param_fields`, `simulate_param_field_name_tags`
- `simulate_impact_rows`, `simulate_status_rows`, `simulate_ctx_rows`

Regenerate: `python seed.py`

---

## 9. Widget mapping (Flask → Streamlit)

| UI section | Streamlit widget |
|------------|------------------|
| Context / filter dropdowns | `st.selectbox` (via `filter_select`) |
| DD% / parameter inputs | `st.text_input` (chip-styled) |
| Collapsible groups | bordered `st.container` + toggle button |
| Run simulation | `st.button` |
| KPI / hero stats | `st.metric` / custom HTML |
| Result table | `st.dataframe` / HTML table |
| Excel/CSV export | `st.download_button` |
| Alerts | `st.warning` / `st.success` / `st.info` |
| Country progress | `st.progress` / custom HTML |

---

## 10. Packages & dependencies

Everything you need to install is in `requirements.txt`. The app also relies on **Python standard library** modules (no extra install).

### 10.1 Third-party packages (`requirements.txt`)

| Package | Version | What it is | Used for in this app |
|---------|---------|------------|----------------------|
| **streamlit** | `>=1.36,<2.0` | Web UI framework for Python data apps | **Core of the entire app** — pages, buttons, inputs, session state, layout, `st.download_button`, `st.html`, keyed containers. Run with `streamlit run streamlit_app.py`. |
| **pandas** | `>=2.0` | Data analysis library (tables, Series, DataFrame) | **Dashboard CSV export only** — builds a `DataFrame` from simulation table rows and writes CSV for `st.download_button` (`dashboard_page.py`). |
| **Werkzeug** | `>=3.0,<4.0` | WSGI utilities (from the Flask ecosystem) | **Password security only** — `generate_password_hash` / `check_password_hash` in `db_st.py` (login) and `seed.py` (demo user passwords). No Flask server is used. |
| **openpyxl** | `>=3.1` | Read/write Excel `.xlsx` files | **Listed in requirements but not imported in app code today.** Kept for planned Excel export (navbar “Export” is a placeholder) and parity with the original Flask build. |

Install all at once:

```powershell
pip install -r requirements.txt
```

### 10.2 Installed automatically (you don’t add these to `requirements.txt`)

These are pulled in when you install the packages above:

| Package | Brought in by | Role |
|---------|---------------|------|
| **numpy** | pandas | Fast arrays; pandas depends on it for `DataFrame` internals. |
| **python-dateutil**, **pytz**, **tzdata** | pandas | Date/time parsing and time zones (not used directly in app code). |
| **et-xmlfile** | openpyxl | Low-level XML for `.xlsx` files. |
| **markupsafe** | Werkzeug | Safe string escaping inside Werkzeug. |
| **altair**, **pillow**, **protobuf**, **pyarrow**, **tornado**, **click**, etc. | streamlit | Charts, images, server, CLI — used by Streamlit internally; this app mostly uses custom HTML/CSS instead of Altair charts. |

You do **not** need to import or configure these unless you add features that use them explicitly.

### 10.3 Python standard library (built-in)

| Module | Used in | Purpose |
|--------|---------|---------|
| **sqlite3** | `db_st.py`, `seed.py` | SQLite database (`app.db`) — users, dashboard, simulate seed data. |
| **pathlib** | `db_st.py`, `seed.py`, `navbar.py` | Resolve paths to `app.db`, assets, logos. |
| **typing** | Most modules | Type hints (`dict`, `Any`, `list`, etc.). |
| **html** | `simulate_ui.py`, `dashboard_ui.py`, `navbar.py`, `filter_select.py`, `kpi_card.py` | Escape user text before embedding in HTML (XSS safety). |
| **json** | `simulate_ui.py` | Serialize data for injected JavaScript (`inject_paint_js`). |
| **re** | `simulate_ui.py` | Text parsing in form/layout helpers. |
| **urllib.parse** | `simulate_ui.py` | Build/query URLs for scope-tree dropdown picks (`quote`, `unquote`). |
| **base64** | `login_page.py`, `navbar.py` | Embed PNG/SVG images inline in HTML (`data:image/...;base64,...`). |
| **os** | `login_page.py` | Asset file paths for login screen images. |
| **io** | `dashboard_page.py` | `io.StringIO` buffer for in-memory CSV before download. |
| **math** | `table_pagination.py` | Page count math for dashboard table pagination. |
| **inspect** | `filter_select.py` | Introspection for filter component wiring. |
| **collections.abc** | `filter_bar.py` | `Callable` type for callback parameters. |
| **__future__.annotations** | All modules | Postponed evaluation of type hints (Python 3.10+ style). |

### 10.4 Streamlit APIs used (subset of the `streamlit` package)

| API | Where | Purpose |
|-----|-------|---------|
| `st.set_page_config` | `streamlit_app.py`, `login_page.py` | Title, wide layout, collapsed sidebar. |
| `st.session_state` | Everywhere | Auth user, page route, simulate form state, nav mode. |
| `st.markdown(..., unsafe_allow_html=True)` | All UI modules | Custom HTML + CSS markers for Figma styling. |
| `st.html` | `simulate_ui.py` | Render HTML fragments (newer Streamlit API). |
| `streamlit.components.v1` (`components.html`) | `login_page.py`, `simulate_ui.py`, `filter_select.py` | Inject HTML/JS iframes for layout fixes and custom widgets. |
| `st.columns`, `st.container` | All pages | Grid layout; keyed containers for CSS targeting. |
| `st.button`, `st.text_input`, `st.selectbox`, `st.form` | Pages | User actions and inputs. |
| `st.download_button` | `dashboard_page.py` | Export simulation table as CSV. |
| `st.cache_resource` | `db_st.py` | Cache single SQLite connection across reruns. |
| `st.rerun`, `st.stop` | `streamlit_app.py`, pages | Navigation and login gate. |
| `st.error`, `st.success`, `st.warning` | `admin_page.py`, login | Feedback messages. |

### 10.5 External assets (not pip packages)

Loaded from disk or CDN in HTML/CSS — no `pip install`:

| Asset | Source | Purpose |
|-------|--------|---------|
| **Google Fonts** (Manrope, Inter) | CDN link in `_shared.py` | Typography when Electrolux Sans is not installed locally. |
| **Material Symbols** | Streamlit / theme | Navbar icons (`:material/...` in older nav code). |
| **SVG/PNG** | `pages_st/assets/`, `static/images/` | Login panel art, Electrolux logo, Databricks icon. |

---

## 11. How to run & develop

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py          # if app.db missing
streamlit run streamlit_app.py
```

### Common development tasks

| Task | Where to change |
|------|-----------------|
| Add a new parameter group | `seed.py` + `schema.sql`; special logic in `db_st.get_simulate_data()` |
| Change DD% baselines | `db_st._DELIVERY_MIX_DD_CHANGE` |
| Change inflation vector/weights | `db_st._INFLATION_VECTOR`, `_INFLATION_IMPACT_WEIGHTS` |
| Adjust Simulate layout/CSS | `simulate_ui.py` → `inject_css`, `inject_simulate_layout_css` |
| Add a nav page | `streamlit_app.py` + new `pages_st/*_page.py` + `navbar._nav_menus()` |
| Change demo dashboard numbers | `seed.py` |

---

## 12. What is NOT implemented (prototype limits)

- **No real simulation backend** — “Start Simulation” stores a session snapshot; impact numbers come from seeded `simulate_impact_rows`.
- **Filters do not query DB** — dropdown changes are UI/session only.
- **History / Export / Reports** nav items are disabled placeholders.
- **Databricks SSO** is display-only on login.
- **Dashboard Submit** does not write to database.
- **Stepper** (`render_stepper`) exists but is commented out in `simulate_page.py`.

---

## 13. Mental model — read this first

1. **`streamlit_app.py`** = traffic cop (auth + which page).
2. **`db_st.py`** = what data exists (shape of dicts matters more than SQL).
3. **`simulate_page.py`** = thin glue (10 lines of real logic).
4. **`simulate_ui.py`** = everything users see and do on Simulate (UI + state + math).
5. **`st.session_state`** = the app’s memory between reruns; Simulate is stateful, Dashboard is mostly stateless reads.

If you are onboarding onto the Simulate screen, start with:

```
simulate_page.py  →  render() order
simulate_ui.py    →  init_simulate_state, render_parameter_group, _on_save_group, _on_start_simulation
db_st.py          →  get_simulate_data (what groups/fields exist)
```

---

*Last updated for the Streamlit build with custom top navigation (`streamlit_app.py` + `navbar.py`).*
