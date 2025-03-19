import streamlit as st
import time
from streamlit_extras.switch_page_button import switch_page
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Logout function
def logout():
    supabase.auth.sign_out()  # Sign out from Supabase
    st.session_state.clear()  # Clear the user session
    st.success("Logged out successfully! ")
    time.sleep(2)  # Wait before redirecting
    switch_page("main")  # Redirect to the main page

# Function to add the logout button to all pages
def add_logout_button():
    with st.sidebar:
        st.button("Logout", on_click=logout)
