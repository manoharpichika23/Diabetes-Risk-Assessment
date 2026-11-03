import os
import streamlit as st
from supabase import create_client


def get_config(key):
    # First check environment variables (Render)
    value = os.getenv(key)

    if value:
        return value

    # Then check Streamlit secrets (local system)
    try:
        return st.secrets[key]
    except Exception:
        raise ValueError(f"{key} is not configured")


def get_auth_client():
    supabase_url = get_config("SUPABASE_URL")
    supabase_key = get_config("SUPABASE_KEY")

    return create_client(supabase_url, supabase_key)


def register_user(email, password):
    supabase = get_auth_client()

    return supabase.auth.sign_up({
        "email": email,
        "password": password
    })


def login_user(email, password):
    supabase = get_auth_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    return supabase, response


def logout_user(supabase):
    supabase.auth.sign_out()