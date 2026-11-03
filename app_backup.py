import streamlit as st
from supabase import create_client


# Create a new Supabase client
def get_auth_client():

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


# USER REGISTRATION
def register_user(email, password):

    supabase = get_auth_client()

    response = supabase.auth.sign_up({
        "email": email,
        "password": password
    })

    return response


# USER LOGIN
def login_user(email, password):

    supabase = get_auth_client()

    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    return supabase, response


# USER LOGOUT
def logout_user(supabase):

    supabase.auth.sign_out()