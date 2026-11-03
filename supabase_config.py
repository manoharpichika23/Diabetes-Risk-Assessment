import os
import streamlit as st
from supabase import create_client


def get_config(key):
    # Read from Render environment variables
    value = os.getenv(key)

    if value:
        return value

    # Read from local Streamlit secrets
    try:
        return st.secrets[key]
    except Exception:
        raise ValueError(f"{key} is not configured")


# Get Supabase credentials
SUPABASE_URL = get_config("SUPABASE_URL")
SUPABASE_KEY = get_config("SUPABASE_KEY")

# Create Supabase connection
supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase connection initialized successfully!")