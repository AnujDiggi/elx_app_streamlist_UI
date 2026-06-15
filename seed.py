"""Seed app.db from the original hardcoded dicts.

Re-run safe: deletes the existing app.db, executes schema.sql, then inserts
every row. Run with `python seed.py`.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

HERE = Path(__file__).parent
DB_PATH = HERE / "app.db"
SCHEMA_PATH = HERE / "schema.sql"


# ---------------------------------------------------------------------------
# Seed payloads — copied verbatim from the original app.py literals so the
# database matches the pre-cutover UI exactly.
# ---------------------------------------------------------------------------

# (password, name, role, is_admin)
USERS: dict[str, tuple[str, str, str, int]] = {
    "nanda.kishore@electrolux.com": ("electrolux123", "Nanda Kishore", "Controller", 1),
    "demo@electrolux.com":          ("demo",          "Demo User",     "Controller", 0),
}

DASHBOARD_META = {
    "live_label": "Live · Databricks Delta Lake",
    "hero_tag":   "Databricks Delta Lake · Live data",
    "hero_title": "Simulation data loaded — EA1 2026 · BC04 · FR10 France",
    "hero_sub":   "6,240,000 rows fetched · Global P&L Actuals (Jan–Dec 2025) + FADP Forecast (Apr–Sep 2026) · Refreshed: 21 May 2026 08:00",
}

DASHBOARD_FILTERS = [
    {"key": "Area",     "value": "FR10"},
    {"key": "Period",   "value": "EA2 · 2026"},
    {"key": "FADP",     "value": "BC04"},
    {"key": "Category", "value": "All"},
    {"key": "Bucket",   "value": "All buckets"},
]

DASHBOARD_SLIDERS = [
    {"key": "DD%",   "min": 0, "max": 100, "value": 45, "suffix": "%"},
    {"key": "Infl.", "min": 0, "max": 20,  "value": 3,  "suffix": "%"},
]

DASHBOARD_HERO_STATS = [
    {"num": "6.2M",  "label": "Rows loaded"},
    {"num": "18mo",  "label": "Forecast range"},
    {"num": "BC04",  "label": "FADP version"},
]

DASHBOARD_KPIS = [
    {"tone": "red",    "label": "Total cost Δ (FR10)", "value": "+€ 158,900",
     "value_class": "neg",     "badge_class": "up-red",     "badge_arrow": "up",   "badge_text": "+6.0%",   "meta": "vs baseline"},
    {"tone": "red2",   "label": "STC impact",          "value": "+€ 112,300",
     "value_class": "neg",     "badge_class": "up-red",     "badge_arrow": "up",   "badge_text": "+9.1%",   "meta": "secondary transport"},
    {"tone": "green",  "label": "PTC savings",         "value": "−€ 8,400",
     "value_class": "pos",     "badge_class": "down-green", "badge_arrow": "down", "badge_text": "−1.0%",   "meta": "primary transport"},
    {"tone": "yellow", "label": "Project costs",       "value": "€ 45,000",
     "value_class": "neutral", "badge_class": "warn",       "badge_arrow": None,   "badge_text": "3 items", "meta": "this cycle"},
    {"tone": "blue",   "label": "Simulation status",   "value": "In Progress",
     "value_class": "neutral in-progress", "badge_class": "info", "badge_arrow": None, "badge_text": "5/8 params", "meta": "entered"},
]

DASHBOARD_TABLE_META = {
    "title": "Simulation Result Table",
    "meta":  "PT10 · EA2 · 2026 · BC05 · DD% 15% · Inflation 3%",
    "showing": "1-10",
    "total": 20,
    "active_page": 1,
    "pages": "1,2",
}

DASHBOARD_TABLE_ROWS = [
    {"category": "Secondary Transport", "dot": "red", "bucket": "STC",
     "actual": "1,240,500", "forecast": "1,280,000", "simulation": "1,352,800",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+112,300", "delta_dir": "up", "delta_pct": "+9.1%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Primary Transport", "dot": "blue", "bucket": "PTC",
     "actual": "870,200", "forecast": "895,000", "simulation": "861,800",
     "actual_class": None, "forecast_class": None,
     "delta_text": "−8,400", "delta_dir": "down", "delta_pct": "−1.0%", "delta_pct_class": "delta-green",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "SWC Variable", "dot": "green", "bucket": "SWC Var",
     "actual": "340,000", "forecast": "350,000", "simulation": "350,000",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+10,000", "delta_dir": "warn", "delta_pct": "+2.9%", "delta_pct_class": "delta-red",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "SWC Fixed", "dot": "green-dark", "bucket": "SWC Fix",
     "actual": "190,000", "forecast": "190,000", "simulation": "190,000",
     "actual_class": None, "forecast_class": None,
     "delta_text": "0", "delta_dir": "zero", "delta_pct": "0.0%", "delta_pct_class": "delta-grey",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Project Costs", "dot": "orange", "bucket": "Project",
     "actual": "—", "forecast": "—", "simulation": "45,000",
     "actual_class": "delta-grey", "forecast_class": "delta-grey",
     "delta_text": "+45000", "delta_dir": "warn", "delta_pct": "N/A", "delta_pct_class": "delta-grey",
     "source": "Controller", "status": "Project", "status_class": "project"},
    {"category": "SWC Obs. Fixed", "dot": "grey", "bucket": "SWC Obs",
     "actual": "62,000", "forecast": "62,000", "simulation": "62,000",
     "actual_class": None, "forecast_class": None,
     "delta_text": "0", "delta_dir": "zero", "delta_pct": "0.0%", "delta_pct_class": "delta-grey",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Warehouse Handling", "dot": "orange", "bucket": "WH",
     "actual": "128,400", "forecast": "130,000", "simulation": "134,200",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+5,800", "delta_dir": "up", "delta_pct": "+4.5%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Customs & Duties", "dot": "blue", "bucket": "CUS",
     "actual": "54,300", "forecast": "55,000", "simulation": "52,100",
     "actual_class": None, "forecast_class": None,
     "delta_text": "−2,200", "delta_dir": "down", "delta_pct": "−4.0%", "delta_pct_class": "delta-green",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Linehaul", "dot": "red", "bucket": "LH",
     "actual": "412,000", "forecast": "420,000", "simulation": "438,500",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+26,500", "delta_dir": "up", "delta_pct": "+6.4%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Last Mile", "dot": "green", "bucket": "LM",
     "actual": "215,600", "forecast": "218,000", "simulation": "219,400",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+3,800", "delta_dir": "up", "delta_pct": "+1.8%", "delta_pct_class": "delta-red",
     "source": "Databricks", "status": "Simulated", "status_class": "simulated"},
    {"category": "Reverse Logistics", "dot": "grey", "bucket": "REV",
     "actual": "38,200", "forecast": "40,000", "simulation": "41,500",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+3,300", "delta_dir": "up", "delta_pct": "+8.6%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Packaging", "dot": "orange", "bucket": "PKG",
     "actual": "96,800", "forecast": "98,000", "simulation": "97,200",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+400", "delta_dir": "up", "delta_pct": "+0.4%", "delta_pct_class": "delta-red",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Fuel Surcharge", "dot": "red", "bucket": "FUEL",
     "actual": "72,100", "forecast": "75,000", "simulation": "81,300",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+9,200", "delta_dir": "up", "delta_pct": "+12.8%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Insurance", "dot": "blue", "bucket": "INS",
     "actual": "18,500", "forecast": "19,000", "simulation": "19,000",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+500", "delta_dir": "up", "delta_pct": "+2.7%", "delta_pct_class": "delta-red",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Cross-dock", "dot": "green-dark", "bucket": "XD",
     "actual": "44,000", "forecast": "45,500", "simulation": "43,800",
     "actual_class": None, "forecast_class": None,
     "delta_text": "−200", "delta_dir": "down", "delta_pct": "−0.5%", "delta_pct_class": "delta-green",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Hub Operations", "dot": "green", "bucket": "HUB",
     "actual": "156,000", "forecast": "160,000", "simulation": "162,400",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+6,400", "delta_dir": "up", "delta_pct": "+4.1%", "delta_pct_class": "delta-red",
     "source": "Databricks", "status": "Simulated", "status_class": "simulated"},
    {"category": "Returns Processing", "dot": "grey", "bucket": "RET",
     "actual": "29,400", "forecast": "30,000", "simulation": "30,600",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+1,200", "delta_dir": "up", "delta_pct": "+4.1%", "delta_pct_class": "delta-red",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Toll Fees", "dot": "orange", "bucket": "TOLL",
     "actual": "11,800", "forecast": "12,000", "simulation": "12,900",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+1,100", "delta_dir": "up", "delta_pct": "+9.3%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Project", "status_class": "project"},
    {"category": "Detention", "dot": "red", "bucket": "DET",
     "actual": "8,200", "forecast": "8,500", "simulation": "9,100",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+900", "delta_dir": "up", "delta_pct": "+11.0%", "delta_pct_class": "delta-red",
     "source": "Controller", "status": "Simulated", "status_class": "simulated"},
    {"category": "Demurrage", "dot": "blue", "bucket": "DEM",
     "actual": "5,600", "forecast": "6,000", "simulation": "5,950",
     "actual_class": None, "forecast_class": None,
     "delta_text": "+350", "delta_dir": "up", "delta_pct": "+6.3%", "delta_pct_class": "delta-red",
     "source": "Actuals", "status": "Baseline", "status_class": "baseline"},
    {"category": "Seasonal Peak", "dot": "orange", "bucket": "PEAK",
     "actual": "—", "forecast": "25,000", "simulation": "28,400",
     "actual_class": "delta-grey", "forecast_class": None,
     "delta_text": "+28,400", "delta_dir": "up", "delta_pct": "N/A", "delta_pct_class": "delta-grey",
     "source": "Controller", "status": "Project", "status_class": "project"},
]

COUNTRIES = [
    {"flag": "🇫🇷", "code": "FR10", "name": "France",   "pct": 100, "bar_class": "full",    "bar_width": 100, "status": "ok"},
    {"flag": "🇪🇸", "code": "ES10", "name": "Spain",    "pct": 62,  "bar_class": "partial", "bar_width": 62,  "status": "warn"},
    {"flag": "🇮🇹", "code": "IT16", "name": "Italy",    "pct": 100, "bar_class": "full",    "bar_width": 100, "status": "ok"},
    {"flag": "🇵🇹", "code": "PT10", "name": "Portugal", "pct": 0,   "bar_class": "zero",    "bar_width": 2,   "status": "danger"},
]

DEADLINES = [
    {"day": "24", "month": "MAY", "title": "PT10 submission — not started", "meta": "EA1 2026 · BC04", "urgent": True,  "chip": "3 days",  "chip_class": ""},
    {"day": "12", "month": "MAY", "title": "ES10 mid-cycle review",         "meta": "EA1 2026 · BC04", "urgent": True,  "chip": "3 days",  "chip_class": ""},
    {"day": "15", "month": "JUN", "title": "IT16 final version due",        "meta": "EA1 2026 · BC04", "urgent": False, "chip": "23 days", "chip_class": "ok"},
]

# meta_template strings may contain a {user_name} placeholder, resolved at read time.
ACTIVITIES = [
    {"icon": "check",    "tone": "green",  "title": "FR10 version submitted — EA1 BC04",
     "meta_template": "Today 14:32 · {user_name}", "meta_warn": False},
    {"icon": "download", "tone": "blue",   "title": "PT10 submission — not started",
     "meta_template": "EA1 2026 · BC04",            "meta_warn": True},
    {"icon": "bolt",     "tone": "yellow", "title": "Baseline data refreshed from Delta Lake",
     "meta_template": "Yesterday 08:00 · System",   "meta_warn": False},
]

SIMULATE_META = {
    "live_label":      "Live · Databricks Delta Lake",
    "params_title":    "Enter Simulation Parameters",
    "params_sub":      "Parameters feed directly into the Databricks simulation engine",
    "expander_text":   "+ Show all 16 categories",
    "progress_label":  "Parameters completed",
    "progress_count":  "7/8",
    "progress_pct":    87.5,
    "status_summary":  "7/8 done",
    "warn_message":    "Complete remaining project costs to enable version submission.",
    "impact_headline": "+€ 158,900",
    "impact_sub":      "+6.0% vs baseline · FR10 · EA1",
    "impact_note":     'Updates as you change parameters. Hit "Run simulation" to calculate from Databricks.',
}

SIMULATE_CONTEXT = [
    {"key": "Area",     "value": "FR10"},
    {"key": "Period",   "value": "Jan"},
    {"key": "FADP",     "value": "BC04"},
    {"key": "Scenario", "value": "Base Case"},
]

SIMULATE_STEPS = [
    {"label": "Select Context",   "state": "done"},
    {"label": "Enter Parameters", "state": "current"},
    {"label": "Run Simulation",   "state": ""},
    {"label": "Review Results",   "state": ""},
    {"label": "Submit Version",   "state": ""},
]

SIMULATE_CONTEXT_PILLS = [
    "🇫🇷 FR10 — France",
    "📅 EA1 · 2026",
    "📊 FADP BC04",
    "☁ 6.2M rows",
]

# Each group: dict with `tags` (list) and `fields` (list of dicts; each field may have `name_tags`).

def _seed_process_cost_fields() -> list[dict]:
    return []


SIMULATE_PARAM_GROUPS = [
    {
        "icon": "🚚",
        "title": "Direct Delivery",
        "description": "Controls split between direct and indirect delivery routes",
        "expanded": True,
        "tags": [{"text": "DD%", "class": "dd"}, {"text": "4 fields", "class": "fields"}],
        "fields": [
            {"name": "France (FR10)",
             "description": "",
             "dd_change": 10,
             "value": 0, "min": 0, "max": 100, "step": None, "suffix": "%",
             "name_tags": []},
            {"name": "Spain (ES10)",
             "description": "",
             "dd_change": 30,
             "value": 0, "min": 0, "max": 100, "step": None, "suffix": "%",
             "name_tags": []},
            {"name": "Italy (IT16)",
             "description": "",
             "dd_change": 5,
             "value": 0, "min": 0, "max": 100, "step": None, "suffix": "%",
             "name_tags": []},
            {"name": "Portugal (PT10)",
             "description": "",
             "dd_change": 0,
             "value": 0, "min": 0, "max": 100, "step": None, "suffix": "%",
             "name_tags": []},
        ],
    },
    {
        "icon": "📈",
        "title": "Inflation Rates",
        "description": "Fuel and non-fuel cost inflation for secondary and primary transport",
        "expanded": True,
        "tags": [
            {"text": "STC", "class": "stc"},
            {"text": "PTC", "class": "ptc"},
            {"text": "6 fields", "class": "fields"},
        ],
        "fields": [
            {"name": "inflation",
             "description": "",
             "infl_role": "input",
             "infl_baseline": 13.0,
             "impact": [],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": []},
            {"name": "PTC impact",
             "description": "",
             "infl_role": "impact",
             "infl_baseline": 95.0,
             "impact": [0, 0, 25, 70, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "PTC", "class": "ptc"}]},
            {"name": "STC impact",
             "description": "",
             "infl_role": "impact",
             "infl_baseline": 100.0,
             "impact": [30, 70, 0, 0, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "STC", "class": "stc"}]},
            {"name": "SWC var impact",
             "description": "",
             "infl_role": "impact",
             "infl_baseline": 100.0,
             "impact": [0, 0, 0, 0, 100, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
            {"name": "SWC fixed impact",
             "description": "",
             "infl_role": "impact",
             "infl_baseline": 100.0,
             "impact": [0, 0, 0, 0, 0, 100],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
            {"name": "SWC Obs. fix. Impact",
             "description": "",
             "infl_role": "impact",
             "infl_baseline": 0.0,
             "impact": [0, 0, 0, 0, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
            {"name": "PTC",
             "description": "",
             "infl_role": "calculated",
             "infl_baseline": 2.7,
             "impact": [0, 0, 25, 70, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "PTC", "class": "ptc"}]},
            {"name": "STC",
             "description": "",
             "infl_role": "calculated",
             "infl_baseline": 2.7,
             "impact": [30, 70, 0, 0, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "STC", "class": "stc"}]},
            {"name": "SWC var",
             "description": "",
             "infl_role": "calculated",
             "infl_baseline": -1.0,
             "impact": [0, 0, 0, 0, 100, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
            {"name": "SWC fixed",
             "description": "",
             "infl_role": "calculated",
             "infl_baseline": 2.0,
             "impact": [0, 0, 0, 0, 0, 100],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
            {"name": "SWC Obs. fix.",
             "description": "",
             "infl_role": "calculated",
             "infl_baseline": 0.0,
             "impact": [0, 0, 0, 0, 0, 0],
             "value": 0, "min": None, "max": None, "step": 0.1, "suffix": "%",
             "name_tags": [{"text": "SWC", "class": "swc"}]},
        ],
    },
    {
        "icon": "💼",
        "title": "Process cost",
        "description": "One-time and planned initiative costs for this planning cycle",
        "expanded": False,
        "tags": [
            {"text": "PTC", "class": "ptc"},
            {"text": "STC", "class": "stc"},
            {"text": "16 rows", "class": "fields"},
        ],
        "fields": _seed_process_cost_fields(),
    },
]

SIMULATE_SUMMARY_ROWS = [
    {"name": "Current", "sq": "red", "value": "€42.3k", "value_class": "red"},
    {"name": "Baseline", "sq": "blue", "value": "€30.5k", "value_class": "green"},
    {"name": "Difference", "sq": "orange", "value": "+€12.3k", "value_class": "red"},
    {"name": "Difference%", "sq": "blue", "value": "41.5%", "value_class": "neutral"},
]

SIMULATE_IMPACT_ROWS = [
    {"name": "STC impact",      "sq": "red",    "value": "+€ 112,300", "value_class": "red"},
    {"name": "PTC savings",     "sq": "blue",   "value": "−€ 8,400",   "value_class": "green"},
    {"name": "SWC impact",      "sq": "green",  "value": "+€ 10,000",  "value_class": "red"},
    {"name": "Project costs",   "sq": "orange", "value": "€ 87,500",   "value_class": "neutral"},
]

SIMULATE_STATUS_ROWS = [
    {"name": "DD% (4 fields)",        "pill": "done",    "pill_text": "Done"},
    {"name": "Inflation (6 fields)", "pill": "done",    "pill_text": "Done"},
    {"name": "Process cost",         "pill": "partial", "pill_text": "0 / 14"},
]

SIMULATE_CTX_ROWS = [
    {"label": "Planning Area",  "value": "FR10"},
    {"label": "Period",         "value": "EA1 · 2026"},
    {"label": "FADP Version",   "value": "BC04"},
    {"label": "Baseline rows",  "value": "6.2M"},
    {"label": "Last refreshed", "value": "21 May 08:00"},
]


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------

def seed() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

        # Users
        conn.executemany(
            "INSERT INTO users (email, password_hash, name, role, is_admin) VALUES (?, ?, ?, ?, ?)",
            [(email, generate_password_hash(pw), name, role, is_admin)
             for email, (pw, name, role, is_admin) in USERS.items()],
        )

        # Dashboard singletons
        conn.execute(
            "INSERT INTO dashboard_meta (id, live_label, hero_tag, hero_title, hero_sub) VALUES (1, ?, ?, ?, ?)",
            (DASHBOARD_META["live_label"], DASHBOARD_META["hero_tag"],
             DASHBOARD_META["hero_title"], DASHBOARD_META["hero_sub"]),
        )
        conn.execute(
            'INSERT INTO dashboard_table_meta (id, title, "meta", showing, total, active_page, pages) VALUES (1, ?, ?, ?, ?, ?, ?)',
            (DASHBOARD_TABLE_META["title"], DASHBOARD_TABLE_META["meta"],
             DASHBOARD_TABLE_META["showing"], DASHBOARD_TABLE_META["total"],
             DASHBOARD_TABLE_META["active_page"], DASHBOARD_TABLE_META["pages"]),
        )

        # Dashboard lists
        conn.executemany(
            'INSERT INTO dashboard_filters ("key", "value", sort_order) VALUES (?, ?, ?)',
            [(f["key"], f["value"], i) for i, f in enumerate(DASHBOARD_FILTERS)],
        )
        conn.executemany(
            'INSERT INTO dashboard_sliders ("key", min_value, max_value, "value", suffix, sort_order) VALUES (?, ?, ?, ?, ?, ?)',
            [(s["key"], s["min"], s["max"], s["value"], s["suffix"], i)
             for i, s in enumerate(DASHBOARD_SLIDERS)],
        )
        conn.executemany(
            "INSERT INTO dashboard_hero_stats (num, label, sort_order) VALUES (?, ?, ?)",
            [(s["num"], s["label"], i) for i, s in enumerate(DASHBOARD_HERO_STATS)],
        )
        conn.executemany(
            'INSERT INTO dashboard_kpis (tone, label, "value", value_class, badge_class, badge_arrow, badge_text, "meta", sort_order)'
            ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            [(k["tone"], k["label"], k["value"], k["value_class"], k["badge_class"],
              k["badge_arrow"], k["badge_text"], k["meta"], i)
             for i, k in enumerate(DASHBOARD_KPIS)],
        )
        conn.executemany(
            "INSERT INTO dashboard_table_rows ("
            "category, dot, bucket, actual, forecast, simulation, actual_class, forecast_class,"
            " delta_text, delta_dir, delta_pct, delta_pct_class, source, status, status_class, sort_order"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [(r["category"], r["dot"], r["bucket"], r["actual"], r["forecast"], r["simulation"],
              r.get("actual_class"), r.get("forecast_class"),
              r["delta_text"], r["delta_dir"], r["delta_pct"], r["delta_pct_class"],
              r["source"], r["status"], r["status_class"], i)
             for i, r in enumerate(DASHBOARD_TABLE_ROWS)],
        )
        conn.executemany(
            "INSERT INTO countries (flag, code, name, pct, bar_class, bar_width, status, sort_order)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(c["flag"], c["code"], c["name"], c["pct"], c["bar_class"], c["bar_width"], c["status"], i)
             for i, c in enumerate(COUNTRIES)],
        )
        conn.executemany(
            'INSERT INTO deadlines (day, month, title, "meta", urgent, chip, chip_class, sort_order)'
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(d["day"], d["month"], d["title"], d["meta"], int(d["urgent"]),
              d["chip"], d["chip_class"], i)
             for i, d in enumerate(DEADLINES)],
        )
        conn.executemany(
            "INSERT INTO activities (icon, tone, title, meta_template, meta_warn, sort_order)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [(a["icon"], a["tone"], a["title"], a["meta_template"], int(a["meta_warn"]), i)
             for i, a in enumerate(ACTIVITIES)],
        )

        # Simulate singleton
        conn.execute(
            "INSERT INTO simulate_meta ("
            "id, live_label, params_title, params_sub, expander_text,"
            " progress_label, progress_count, progress_pct,"
            " status_summary, warn_message,"
            " impact_headline, impact_sub, impact_note"
            ") VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (SIMULATE_META["live_label"], SIMULATE_META["params_title"], SIMULATE_META["params_sub"],
             SIMULATE_META["expander_text"],
             SIMULATE_META["progress_label"], SIMULATE_META["progress_count"], SIMULATE_META["progress_pct"],
             SIMULATE_META["status_summary"], SIMULATE_META["warn_message"],
             SIMULATE_META["impact_headline"], SIMULATE_META["impact_sub"], SIMULATE_META["impact_note"]),
        )

        # Simulate lists
        conn.executemany(
            'INSERT INTO simulate_context ("key", "value", sort_order) VALUES (?, ?, ?)',
            [(c["key"], c["value"], i) for i, c in enumerate(SIMULATE_CONTEXT)],
        )
        conn.executemany(
            "INSERT INTO simulate_steps (label, state, sort_order) VALUES (?, ?, ?)",
            [(s["label"], s["state"], i) for i, s in enumerate(SIMULATE_STEPS)],
        )
        conn.executemany(
            'INSERT INTO simulate_context_pills ("text", sort_order) VALUES (?, ?)',
            [(p, i) for i, p in enumerate(SIMULATE_CONTEXT_PILLS)],
        )

        # Param groups + nested tags/fields/name_tags
        for g_idx, g in enumerate(SIMULATE_PARAM_GROUPS):
            cur = conn.execute(
                "INSERT INTO simulate_param_groups (icon, title, description, expanded, sort_order)"
                " VALUES (?, ?, ?, ?, ?)",
                (g["icon"], g["title"], g["description"], int(g["expanded"]), g_idx),
            )
            group_id = cur.lastrowid
            conn.executemany(
                'INSERT INTO simulate_param_group_tags (group_id, "text", "class", sort_order) VALUES (?, ?, ?, ?)',
                [(group_id, t["text"], t["class"], i) for i, t in enumerate(g["tags"])],
            )
            for f_idx, f in enumerate(g["fields"]):
                cur = conn.execute(
                    "INSERT INTO simulate_param_fields ("
                    "group_id, name, description, \"value\", min_value, max_value, step, suffix, sort_order"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (group_id, f["name"], f["description"], f["value"],
                     f["min"], f["max"], f["step"], f["suffix"], f_idx),
                )
                field_id = cur.lastrowid
                conn.executemany(
                    'INSERT INTO simulate_param_field_name_tags (field_id, "text", "class", sort_order) VALUES (?, ?, ?, ?)',
                    [(field_id, t["text"], t["class"], i) for i, t in enumerate(f["name_tags"])],
                )

        conn.executemany(
            'INSERT INTO simulate_impact_rows (name, sq, "value", value_class, sort_order) VALUES (?, ?, ?, ?, ?)',
            [(r["name"], r["sq"], r["value"], r["value_class"], i)
             for i, r in enumerate(SIMULATE_IMPACT_ROWS)],
        )
        conn.executemany(
            "INSERT INTO simulate_status_rows (name, pill, pill_text, sort_order) VALUES (?, ?, ?, ?)",
            [(r["name"], r["pill"], r["pill_text"], i) for i, r in enumerate(SIMULATE_STATUS_ROWS)],
        )
        conn.executemany(
            'INSERT INTO simulate_ctx_rows (label, "value", sort_order) VALUES (?, ?, ?)',
            [(r["label"], r["value"], i) for i, r in enumerate(SIMULATE_CTX_ROWS)],
        )

        conn.commit()
    finally:
        conn.close()

    print(
        f"Seeded {DB_PATH.name}: "
        f"{len(USERS)} users, {len(DASHBOARD_KPIS)} kpis, "
        f"{len(DASHBOARD_TABLE_ROWS)} table rows, {len(COUNTRIES)} countries, "
        f"{len(DEADLINES)} deadlines, {len(ACTIVITIES)} activities, "
        f"{len(SIMULATE_PARAM_GROUPS)} param groups, "
        f"{sum(len(g['fields']) for g in SIMULATE_PARAM_GROUPS)} param fields."
    )


if __name__ == "__main__":
    seed()
