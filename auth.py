import streamlit as st
from supabase import create_client


def get_auth_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )


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