"""Streamlit-friendly read layer for nanda_app.

Mirrors the functions in db.py but uses a plain sqlite3 connection cached by
Streamlit instead of Flask's `g`. Returns the exact same dict shapes so each
Streamlit page can be a near drop-in renderer of the same data.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import streamlit as st
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = Path(__file__).parent / "app.db"


@st.cache_resource
def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _rows(sql: str, *params: Any) -> list[sqlite3.Row]:
    return _conn().execute(sql, params).fetchall()


def _one(sql: str, *params: Any) -> sqlite3.Row | None:
    return _conn().execute(sql, params).fetchone()


def _one_required(sql: str, *params: Any) -> sqlite3.Row:
    row = _conn().execute(sql, params).fetchone()
    if row is None:
        raise RuntimeError(f"Expected one row but got none: {sql}")
    return row


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (parts[0][:2] if parts else "?").upper()


# ---------------------------------------------------------------------------
# Auth + admin
# ---------------------------------------------------------------------------

def authenticate(email: str, password: str) -> dict | None:
    row = _one(
        "SELECT email, password_hash, name, role, is_admin FROM users WHERE email = ?",
        email,
    )
    if row is None or not check_password_hash(row["password_hash"], password):
        return None
    return {
        "email":    row["email"],
        "name":     row["name"],
        "role":     row["role"],
        "is_admin": bool(row["is_admin"]),
        "initials": _initials(row["name"]),
    }


def list_users() -> list[dict]:
    rows = _rows(
        "SELECT email, name, role, is_admin FROM users ORDER BY name COLLATE NOCASE"
    )
    return [
        {
            "email":    r["email"],
            "name":     r["name"],
            "role":     r["role"],
            "is_admin": bool(r["is_admin"]),
        }
        for r in rows
    ]


def create_user(email: str, name: str, password: str, role: str, is_admin: bool) -> bool:
    try:
        _conn().execute(
            "INSERT INTO users (email, password_hash, name, role, is_admin) VALUES (?, ?, ?, ?, ?)",
            (email, generate_password_hash(password), name, role, 1 if is_admin else 0),
        )
        _conn().commit()
        return True
    except sqlite3.IntegrityError:
        return False


def set_admin(email: str, is_admin: bool) -> None:
    _conn().execute(
        "UPDATE users SET is_admin = ? WHERE email = ?",
        (1 if is_admin else 0, email),
    )
    _conn().commit()


def _load_filter_bar_rows() -> tuple[list[dict], list[dict]]:
    filters = [{"key": r["key"], "value": r["value"]}
               for r in _rows('SELECT "key", "value" FROM dashboard_filters ORDER BY sort_order')]
    sliders = [{"key": r["key"], "min": r["min_value"], "max": r["max_value"],
                "value": r["value"], "suffix": r["suffix"]}
               for r in _rows('SELECT "key", min_value, max_value, "value", suffix FROM dashboard_sliders ORDER BY sort_order')]
    return filters, sliders


def get_dashboard_data(user_name: str) -> dict:
    meta = _one_required(
        "SELECT live_label, hero_tag, hero_title, hero_sub FROM dashboard_meta WHERE id = 1"
    )
    table_meta = _one_required(
        'SELECT title, "meta", showing, total, active_page, pages FROM dashboard_table_meta WHERE id = 1'
    )

    filters, sliders = _load_filter_bar_rows()

    hero_stats = [{"num": r["num"], "label": r["label"]}
                  for r in _rows("SELECT num, label FROM dashboard_hero_stats ORDER BY sort_order")]

    kpis = [{"tone": r["tone"], "label": r["label"], "value": r["value"],
             "value_class": r["value_class"], "badge_class": r["badge_class"],
             "badge_arrow": r["badge_arrow"], "badge_text": r["badge_text"], "meta": r["meta"]}
            for r in _rows('SELECT tone, label, "value", value_class, badge_class, badge_arrow, badge_text, "meta"'
                           " FROM dashboard_kpis ORDER BY sort_order")]

    table_rows = []
    for r in _rows(
        "SELECT category, dot, bucket, actual, forecast, simulation, actual_class, forecast_class,"
        " delta_text, delta_dir, delta_pct, delta_pct_class, source, status, status_class"
        " FROM dashboard_table_rows ORDER BY sort_order"
    ):
        row = {
            "category": r["category"], "dot": r["dot"], "bucket": r["bucket"],
            "actual": r["actual"], "forecast": r["forecast"], "simulation": r["simulation"],
            "delta_text": r["delta_text"], "delta_dir": r["delta_dir"],
            "delta_pct": r["delta_pct"], "delta_pct_class": r["delta_pct_class"],
            "source": r["source"], "status": r["status"], "status_class": r["status_class"],
        }
        if r["actual_class"] is not None:
            row["actual_class"] = r["actual_class"]
        if r["forecast_class"] is not None:
            row["forecast_class"] = r["forecast_class"]
        table_rows.append(row)

    countries = [{"flag": r["flag"], "code": r["code"], "name": r["name"], "pct": r["pct"],
                  "bar_class": r["bar_class"], "bar_width": r["bar_width"], "status": r["status"]}
                 for r in _rows("SELECT flag, code, name, pct, bar_class, bar_width, status FROM countries ORDER BY sort_order")]

    deadlines = [{"day": r["day"], "month": r["month"], "title": r["title"], "meta": r["meta"],
                  "urgent": bool(r["urgent"]), "chip": r["chip"], "chip_class": r["chip_class"]}
                 for r in _rows('SELECT day, month, title, "meta", urgent, chip, chip_class FROM deadlines ORDER BY sort_order')]

    activities = []
    for r in _rows("SELECT icon, tone, title, meta_template, meta_warn FROM activities ORDER BY sort_order"):
        a = {
            "icon":  r["icon"],
            "tone":  r["tone"],
            "title": r["title"],
            "meta":  r["meta_template"].format(user_name=user_name),
        }
        if r["meta_warn"]:
            a["meta_warn"] = True
        activities.append(a)

    pages = [int(p) for p in (table_meta["pages"] or "").split(",") if p]

    return {
        "filters":    filters,
        "sliders":    sliders,
        "live_label": meta["live_label"],
        "hero": {
            "tag":   meta["hero_tag"],
            "title": meta["hero_title"],
            "sub":   meta["hero_sub"],
            "stats": hero_stats,
        },
        "kpis": kpis,
        "table": {
            "title": table_meta["title"],
            "meta":  table_meta["meta"],
            "rows":  table_rows,
            "pagination": {
                "showing": table_meta["showing"],
                "total":   table_meta["total"],
                "pages":   pages,
                "active":  table_meta["active_page"],
            },
        },
        "countries":  countries,
        "deadlines":  deadlines,
        "activities": activities,
    }


# ---------------------------------------------------------------------------
# Simulate
# ---------------------------------------------------------------------------

_SIM_GROUPS_WITHOUT_FIELD_DESC = frozenset({
    "Delivery Mix", "Direct Delivery", "Inflation Rates", "Process cost", "Project Costs (EUR)",
})
_SIM_EXCLUDED_GROUPS = frozenset({"Warehouse Costs (SWC)"})
_SIM_GROUP_TITLE_ALIASES = {
    "Project Costs (EUR)": "Process cost",
    "Delivery Mix": "Direct Delivery",
}
_DIRECT_DELIVERY_DB_TITLES = frozenset({"Delivery Mix", "Direct Delivery"})
_DELIVERY_MIX_ENTRIES: tuple[tuple[str, str], ...] = (
    ("France (FR10)", "FR10"),
    ("Spain (ES10)", "ES10"),
    ("Italy (IT16)", "IT16"),
    ("Portugal (PT10)", "PT10"),
)
_DELIVERY_MIX_DD_CHANGE = {"FR10": 10, "ES10": 30, "IT16": 5, "PT10": 0}


def _delivery_mix_fields() -> list[dict]:
    return [
        {
            "name": label,
            "name_tags": [],
            "desc": "",
            "dd_change": _DELIVERY_MIX_DD_CHANGE[code],
            "value": 0,
            "min": 0,
            "max": 100,
            "step": None,
            "suffix": "%",
        }
        for label, code in _DELIVERY_MIX_ENTRIES
    ]


_PROCESS_COST_DB_TITLES = frozenset({"Process cost", "Project Costs (EUR)"})
_PROCESS_COST_COLUMNS: tuple[str, ...] = (
    "PTC",
    "STC",
    "SWC Var",
    "SWC Fixed",
    "SWC Obs. fix.",
)
_PROCESS_COST_MATRIX_ROWS: tuple[dict, ...] = (
    {"key": "new_setup", "label": "New set-up / business", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "primary_freight_price", "label": "Primary/direct freight price", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "primary_freight_eff", "label": "Primary/direct freight eff.", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "ocean", "label": "Ocean", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "secondary_freight_price", "label": "Secondary freight price", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "secondary_freight_eff", "label": "Secondary freight eff.", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "d2c_freight_eff", "label": "D2C freight efficiency", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "direct_del_effect", "label": "Direct del effect", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "indirect_labour", "label": "Indirect labour price", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "other_price_wh_var", "label": "Other price WH VAR", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "whse_var_eff", "label": "Whse var efficiency", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "new_stock_policy", "label": "New stock policy", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "other_variable", "label": "Other variable", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "other", "label": "other", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "stk", "label": "STK", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
    {"key": "op_exch_rates", "label": "Op.exch.rates", "company": "FR10", "defaults": (0, 0, 0, 0, 0)},
)


def get_process_cost_matrix_config() -> dict:
    """Column headers and row specs for the process cost matrix UI."""
    return {
        "company_label": "Company",
        "category_label": "Process Changes Cat.",
        "columns": _PROCESS_COST_COLUMNS,
        "input_rows": _PROCESS_COST_MATRIX_ROWS,
    }


def _process_cost_fields() -> list[dict]:
    """Matrix UI replaces legacy section fields — keep empty for compatibility."""
    return []


_INFLATION_VECTOR = (2.0, 3.0, 5.0, 2.0, -1.0, 2.0)
_INFLATION_IMPACT_WEIGHTS = {
    "PTC": (0, 0, 25, 70, 0, 0),
    "STC": (30, 70, 0, 0, 0, 0),
    "SWC var": (0, 0, 0, 0, 100, 0),
    "SWC fixed": (0, 0, 0, 0, 0, 100),
    "SWC Obs. fix.": (0, 0, 0, 0, 0, 0),
}
_INFLATION_COLUMNS = (
    "Secondary TPT, Fuel",
    "Secondary TPT, Others",
    "Primary Fuel",
    "Primary Others",
    "Sales Warehouse",
    "Sales Warehouse Fixed",
)
_INFLATION_MATRIX_INPUT_ROWS: tuple[dict, ...] = (
    {"key": "inflation", "label": "Inflation", "defaults": _INFLATION_VECTOR, "name_tags": []},
    {
        "key": "ptc_impact",
        "label": "PTC Impact",
        "defaults": _INFLATION_IMPACT_WEIGHTS["PTC"],
        "name_tags": [{"text": "PTC", "class": "ptc"}],
    },
    {
        "key": "stc_impact",
        "label": "STC Impact",
        "defaults": _INFLATION_IMPACT_WEIGHTS["STC"],
        "name_tags": [{"text": "STC", "class": "stc"}],
    },
    {
        "key": "swc_var_impact",
        "label": "SWC Var Impact",
        "defaults": _INFLATION_IMPACT_WEIGHTS["SWC var"],
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
    {
        "key": "swc_fixed_impact",
        "label": "SWC Fixed Impact",
        "defaults": _INFLATION_IMPACT_WEIGHTS["SWC fixed"],
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
    {
        "key": "swc_obs_impact",
        "label": "SWC Obs. Fix. Impact",
        "defaults": _INFLATION_IMPACT_WEIGHTS["SWC Obs. fix."],
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
)
_INFLATION_MATRIX_CALC_ROWS: tuple[dict, ...] = (
    {
        "key": "ptc",
        "label": "PTC",
        "impact_key": "ptc_impact",
        "name_tags": [{"text": "PTC", "class": "ptc"}],
    },
    {
        "key": "stc",
        "label": "STC",
        "impact_key": "stc_impact",
        "name_tags": [{"text": "STC", "class": "stc"}],
    },
    {
        "key": "swc_var",
        "label": "SWC Var",
        "impact_key": "swc_var_impact",
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
    {
        "key": "swc_fixed",
        "label": "SWC Fixed",
        "impact_key": "swc_fixed_impact",
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
    {
        "key": "swc_obs",
        "label": "SWC Obs. Fix.",
        "impact_key": "swc_obs_impact",
        "name_tags": [{"text": "SWC", "class": "swc"}],
    },
)


def get_inflation_matrix_config() -> dict:
    """Column headers and input/calculated row specs for the inflation matrix UI."""
    return {
        "columns": _INFLATION_COLUMNS,
        "input_rows": _INFLATION_MATRIX_INPUT_ROWS,
        "calc_rows": _INFLATION_MATRIX_CALC_ROWS,
    }


def _inflation_baseline_total(impact: tuple[int, ...]) -> float:
    cells = [round(_INFLATION_VECTOR[i] * impact[i] / 100, 1) for i in range(len(_INFLATION_VECTOR))]
    return round(sum(cells), 1)


def _impact_row_total(impact: tuple[int, ...]) -> float:
    return float(sum(impact))


def _inflation_field_spec(
    name: str,
    *,
    role: str,
    baseline: float,
    impact: tuple[int, ...] = (),
    name_tags: list[dict] | None = None,
) -> dict:
    return {
        "name": name,
        "name_tags": name_tags or [],
        "desc": "",
        "infl_role": role,
        "infl_baseline": baseline,
        "impact": list(impact),
        "value": 0.0,
        "min": None,
        "max": None,
        "step": 0.1,
        "suffix": "%",
    }


def _simulation_summary_rows() -> list[dict]:
    return [
        {"name": "Current", "sq": "red", "value": "€42.3k", "value_class": "red"},
        {"name": "Baseline", "sq": "blue", "value": "€30.5k", "value_class": "green"},
        {"name": "Difference", "sq": "orange", "value": "+€12.3k", "value_class": "red"},
        {"name": "Difference%", "sq": "blue", "value": "41.5%", "value_class": "neutral"},
    ]


def _inflation_rates_fields() -> list[dict]:
    ptc_w = _INFLATION_IMPACT_WEIGHTS["PTC"]
    stc_w = _INFLATION_IMPACT_WEIGHTS["STC"]
    swc_var_w = _INFLATION_IMPACT_WEIGHTS["SWC var"]
    swc_fix_w = _INFLATION_IMPACT_WEIGHTS["SWC fixed"]
    swc_obs_w = _INFLATION_IMPACT_WEIGHTS["SWC Obs. fix."]
    return [
        _inflation_field_spec(
            "inflation",
            role="input",
            baseline=round(sum(_INFLATION_VECTOR), 1),
        ),
        _inflation_field_spec(
            "PTC impact",
            role="impact",
            baseline=_impact_row_total(ptc_w),
            impact=ptc_w,
            name_tags=[{"text": "PTC", "class": "ptc"}],
        ),
        _inflation_field_spec(
            "STC impact",
            role="impact",
            baseline=_impact_row_total(stc_w),
            impact=stc_w,
            name_tags=[{"text": "STC", "class": "stc"}],
        ),
        _inflation_field_spec(
            "SWC var impact",
            role="impact",
            baseline=_impact_row_total(swc_var_w),
            impact=swc_var_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
        _inflation_field_spec(
            "SWC fixed impact",
            role="impact",
            baseline=_impact_row_total(swc_fix_w),
            impact=swc_fix_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
        _inflation_field_spec(
            "SWC Obs. fix. Impact",
            role="impact",
            baseline=_impact_row_total(swc_obs_w),
            impact=swc_obs_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
        _inflation_field_spec(
            "PTC",
            role="calculated",
            baseline=_inflation_baseline_total(ptc_w),
            impact=ptc_w,
            name_tags=[{"text": "PTC", "class": "ptc"}],
        ),
        _inflation_field_spec(
            "STC",
            role="calculated",
            baseline=_inflation_baseline_total(stc_w),
            impact=stc_w,
            name_tags=[{"text": "STC", "class": "stc"}],
        ),
        _inflation_field_spec(
            "SWC var",
            role="calculated",
            baseline=_inflation_baseline_total(swc_var_w),
            impact=swc_var_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
        _inflation_field_spec(
            "SWC fixed",
            role="calculated",
            baseline=_inflation_baseline_total(swc_fix_w),
            impact=swc_fix_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
        _inflation_field_spec(
            "SWC Obs. fix.",
            role="calculated",
            baseline=_inflation_baseline_total(swc_obs_w),
            impact=swc_obs_w,
            name_tags=[{"text": "SWC", "class": "swc"}],
        ),
    ]


def get_simulate_data() -> dict:
    meta = _one_required(
        "SELECT live_label, params_title, params_sub, expander_text,"
        " progress_label, progress_count, progress_pct,"
        " status_summary, warn_message,"
        " impact_headline, impact_sub, impact_note"
        " FROM simulate_meta WHERE id = 1"
    )

    context = [{"key": r["key"], "value": r["value"]}
               for r in _rows('SELECT "key", "value" FROM simulate_context ORDER BY sort_order')]

    steps = [{"label": r["label"], "state": r["state"]}
             for r in _rows("SELECT label, state FROM simulate_steps ORDER BY sort_order")]

    context_pills = [r["text"]
                     for r in _rows('SELECT "text" FROM simulate_context_pills ORDER BY sort_order')]

    param_groups = []
    for g_row in _rows(
        "SELECT id, icon, title, description, expanded FROM simulate_param_groups ORDER BY sort_order"
    ):
        if g_row["title"] in _SIM_EXCLUDED_GROUPS:
            continue
        gid = g_row["id"]
        hide_field_desc = g_row["title"] in _SIM_GROUPS_WITHOUT_FIELD_DESC
        if g_row["title"] in _DIRECT_DELIVERY_DB_TITLES:
            tags = [{"text": "DD%", "class": "dd"}, {"text": "4 fields", "class": "fields"}]
            fields = _delivery_mix_fields()
        elif g_row["title"] == "Inflation Rates":
            tags = [
                {"text": "STC", "class": "stc"},
                {"text": "PTC", "class": "ptc"},
                {"text": "6 fields", "class": "fields"},
            ]
            fields = _inflation_rates_fields()
        elif g_row["title"] in _PROCESS_COST_DB_TITLES:
            pc_config = get_process_cost_matrix_config()
            n_rows = len(pc_config["input_rows"])
            tags = [
                {"text": "PTC", "class": "ptc"},
                {"text": "STC", "class": "stc"},
                {"text": f"{n_rows} rows", "class": "fields"},
            ]
            fields = _process_cost_fields()
        else:
            tags = [{"text": t["text"], "class": t["class"]}
                    for t in _rows('SELECT "text", "class" FROM simulate_param_group_tags WHERE group_id = ? ORDER BY sort_order', gid)]
            fields = []
            for f_row in _rows(
                'SELECT id, name, description, "value", min_value, max_value, step, suffix'
                " FROM simulate_param_fields WHERE group_id = ? ORDER BY sort_order",
                gid,
            ):
                name_tags = [{"text": t["text"], "class": t["class"]}
                             for t in _rows('SELECT "text", "class" FROM simulate_param_field_name_tags WHERE field_id = ? ORDER BY sort_order', f_row["id"])]
                is_int_field = f_row["max_value"] is not None and f_row["step"] is None
                fields.append({
                    "name":      f_row["name"],
                    "name_tags": name_tags,
                    "desc":      "" if hide_field_desc else f_row["description"],
                    "value":     0 if is_int_field else 0.0,
                    "min":       f_row["min_value"],
                    "max":       f_row["max_value"],
                    "step":      f_row["step"],
                    "suffix":    f_row["suffix"],
                })
        title = _SIM_GROUP_TITLE_ALIASES.get(g_row["title"], g_row["title"])
        param_groups.append({
            "icon":     g_row["icon"],
            "title":    title,
            "desc":     g_row["description"],
            "tags":     tags,
            "expanded": bool(g_row["expanded"]),
            "fields":   fields,
        })

    impact_rows = [{"name": r["name"], "sq": r["sq"], "value": r["value"], "value_class": r["value_class"]}
                   for r in _rows('SELECT name, sq, "value", value_class FROM simulate_impact_rows ORDER BY sort_order')]

    status_rows = [{"name": r["name"], "pill": r["pill"], "pill_text": r["pill_text"]}
                   for r in _rows("SELECT name, pill, pill_text FROM simulate_status_rows ORDER BY sort_order")]

    ctx_rows = [{"label": r["label"], "value": r["value"]}
                for r in _rows('SELECT label, "value" FROM simulate_ctx_rows ORDER BY sort_order')]

    return {
        "context":        context,
        "live_label":     meta["live_label"],
        "steps":          steps,
        "params_title":   meta["params_title"],
        "params_sub":     meta["params_sub"],
        "context_pills":  context_pills,
        "param_groups":   param_groups,
        "expander_text":  meta["expander_text"],
        "progress": {
            "label": meta["progress_label"],
            "count": meta["progress_count"],
            "pct":   meta["progress_pct"],
        },
        "impact": {
            "headline": meta["impact_headline"],
            "sub":      meta["impact_sub"],
            "note":     meta["impact_note"],
            "rows":     impact_rows,
        },
        "summary": {
            "title": "Simulation Summary",
            "badge": "Real-time",
            "rows":  _simulation_summary_rows(),
        },
        "status_summary": meta["status_summary"],
        "status_rows":    status_rows,
        "warn_message":   meta["warn_message"],
        "ctx_rows":       ctx_rows,
    }
