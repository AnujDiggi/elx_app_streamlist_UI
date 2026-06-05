-- nanda_app SQLite schema
-- Regenerate the DB with `python seed.py` — this file is executed via executescript().

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Auth
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    email         TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    name          TEXT NOT NULL,
    role          TEXT NOT NULL,
    is_admin      INTEGER NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- Dashboard — singletons
-- ---------------------------------------------------------------------------
CREATE TABLE dashboard_meta (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    live_label TEXT,
    hero_tag   TEXT,
    hero_title TEXT,
    hero_sub   TEXT
);

CREATE TABLE dashboard_table_meta (
    id          INTEGER PRIMARY KEY CHECK (id = 1),
    title       TEXT,
    "meta"      TEXT,
    showing     TEXT,
    total       INTEGER,
    active_page INTEGER,
    pages       TEXT  -- comma-joined, e.g. "1,2,3"
);

-- ---------------------------------------------------------------------------
-- Dashboard — list tables
-- ---------------------------------------------------------------------------
CREATE TABLE dashboard_filters (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    "key"      TEXT NOT NULL,
    "value"    TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dashboard_sliders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    "key"      TEXT NOT NULL,
    min_value  REAL NOT NULL,
    max_value  REAL NOT NULL,
    "value"    REAL NOT NULL,
    suffix     TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dashboard_hero_stats (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    num        TEXT NOT NULL,
    label      TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE dashboard_kpis (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    tone        TEXT,
    label       TEXT,
    "value"     TEXT,
    value_class TEXT,
    badge_class TEXT,
    badge_arrow TEXT,
    badge_text  TEXT,
    "meta"      TEXT,
    sort_order  INTEGER NOT NULL
);

CREATE TABLE dashboard_table_rows (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT,
    dot             TEXT,
    bucket          TEXT,
    actual          TEXT,
    forecast        TEXT,
    simulation      TEXT,
    actual_class    TEXT,
    forecast_class  TEXT,
    delta_text      TEXT,
    delta_dir       TEXT,
    delta_pct       TEXT,
    delta_pct_class TEXT,
    source          TEXT,
    status          TEXT,
    status_class    TEXT,
    sort_order      INTEGER NOT NULL
);

CREATE TABLE countries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    flag       TEXT,
    code       TEXT NOT NULL,
    name       TEXT NOT NULL,
    pct        INTEGER,
    bar_class  TEXT,
    bar_width  INTEGER,
    status     TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE deadlines (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    day        TEXT,
    month      TEXT,
    title      TEXT,
    "meta"     TEXT,
    urgent     INTEGER NOT NULL DEFAULT 0,
    chip       TEXT,
    chip_class TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE activities (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    icon          TEXT,
    tone          TEXT,
    title         TEXT,
    meta_template TEXT,  -- may include {user_name} placeholder
    meta_warn     INTEGER NOT NULL DEFAULT 0,
    sort_order    INTEGER NOT NULL
);

-- ---------------------------------------------------------------------------
-- Simulate — singleton (folds progress + impact scalar fields in)
-- ---------------------------------------------------------------------------
CREATE TABLE simulate_meta (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    live_label      TEXT,
    params_title    TEXT,
    params_sub      TEXT,
    expander_text   TEXT,
    progress_label  TEXT,
    progress_count  TEXT,
    progress_pct    REAL,
    status_summary  TEXT,
    warn_message    TEXT,
    impact_headline TEXT,
    impact_sub      TEXT,
    impact_note     TEXT
);

-- ---------------------------------------------------------------------------
-- Simulate — list tables
-- ---------------------------------------------------------------------------
CREATE TABLE simulate_context (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    "key"      TEXT NOT NULL,
    "value"    TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_steps (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    label      TEXT NOT NULL,
    state      TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_context_pills (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    "text"     TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_param_groups (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    icon        TEXT,
    title       TEXT,
    description TEXT,
    expanded    INTEGER NOT NULL DEFAULT 0,
    sort_order  INTEGER NOT NULL
);

CREATE TABLE simulate_param_group_tags (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id   INTEGER NOT NULL REFERENCES simulate_param_groups(id) ON DELETE CASCADE,
    "text"     TEXT NOT NULL,
    "class"    TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_param_fields (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id    INTEGER NOT NULL REFERENCES simulate_param_groups(id) ON DELETE CASCADE,
    name        TEXT,
    description TEXT,
    "value"     REAL,
    min_value   REAL,
    max_value   REAL,
    step        REAL,
    suffix      TEXT,
    sort_order  INTEGER NOT NULL
);

CREATE TABLE simulate_param_field_name_tags (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    field_id   INTEGER NOT NULL REFERENCES simulate_param_fields(id) ON DELETE CASCADE,
    "text"     TEXT NOT NULL,
    "class"    TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_impact_rows (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT,
    sq          TEXT,
    "value"     TEXT,
    value_class TEXT,
    sort_order  INTEGER NOT NULL
);

CREATE TABLE simulate_status_rows (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT,
    pill       TEXT,
    pill_text  TEXT,
    sort_order INTEGER NOT NULL
);

CREATE TABLE simulate_ctx_rows (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    label      TEXT,
    "value"    TEXT,
    sort_order INTEGER NOT NULL
);
