"""Streamlit port of templates/admin.html.

Behaviour parity with Flask `/admin`, `/admin/add`, `/admin/<email>/toggle-admin`:
- only admins reach this page (the entry shell hides it for non-admins; this
  module also re-checks for safety)
- add user form: email/name/password/role + is_admin checkbox
- existing users: per-row "Make admin" / "Revoke admin" button, hidden for self
"""
from __future__ import annotations

import streamlit as st

import db_st


def _render_add_user_form() -> None:
    with st.container(border=True):
        st.markdown("#### Add user")
        with st.form("admin_add_user", clear_on_submit=True):
            email    = st.text_input("Email")
            name     = st.text_input("Name")
            password = st.text_input("Password", type="default")
            role     = st.text_input("Role", value="Controller")
            is_admin = st.checkbox("Make this user an admin", value=False)
            submitted = st.form_submit_button("Add user", type="primary")

        if submitted:
            cleaned_email = (email or "").strip().lower()
            cleaned_name  = (name or "").strip()
            cleaned_role  = (role or "").strip()
            if not (cleaned_email and cleaned_name and password and cleaned_role):
                st.error("All fields are required.")
                return
            if db_st.create_user(cleaned_email, cleaned_name, password, cleaned_role, is_admin):
                st.success(f"User {cleaned_email} added.")
                st.rerun()
            else:
                st.error("A user with that email already exists.")


def _render_user_table() -> None:
    me = st.session_state["user"]
    me_email = me["email"].lower()

    with st.container(border=True):
        st.markdown("#### Existing users")

        header = st.columns([3, 4, 2, 1, 2])
        header[0].markdown("**Name**")
        header[1].markdown("**Email**")
        header[2].markdown("**Role**")
        header[3].markdown("**Admin**")
        header[4].markdown("**Actions**")
        st.divider()

        for u in db_st.list_users():
            row = st.columns([3, 4, 2, 1, 2])
            row[0].write(u["name"])
            row[1].write(u["email"])
            row[2].write(u["role"])
            row[3].markdown("🛡️" if u["is_admin"] else "")

            if u["email"].lower() == me_email:
                row[4].caption("_(you)_")
                continue

            label = "Revoke admin" if u["is_admin"] else "Make admin"
            if row[4].button(label, key=f'toggle_{u["email"]}'):
                db_st.set_admin(u["email"], not u["is_admin"])
                if u["is_admin"]:
                    st.success(f'Revoked admin for {u["email"]}.')
                else:
                    st.success(f'Granted admin for {u["email"]}.')
                st.rerun()


def render() -> None:
    if not st.session_state.get("user", {}).get("is_admin"):
        st.error("Admin access required.")
        st.stop()

    st.markdown("# Admin")
    st.caption("Add users and manage admin access.")

    _render_add_user_form()
    _render_user_table()
