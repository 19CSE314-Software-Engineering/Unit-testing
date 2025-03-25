import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from streamlit_extras.switch_page_button import switch_page
import time
from utils import add_logout_button

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ensure only Mayor can access
if "role" not in st.session_state or st.session_state["role"] != "Mayor":
    st.error("Access Denied. Only the Mayor can access this page.")
    time.sleep(2)
    switch_page("main")

st.set_page_config(layout="wide", page_title="Mayor - Complaints Dashboard", page_icon="📢")
st.title("📢 Mayor's Complaints Dashboard")

# Sidebar Logout Button
add_logout_button()

# Function to fetch complaints with assigned employee details
def fetch_complaints():
    try:
        response = (
            supabase.table("customer_complaints")
            .select("id, created_at, name, phone_number, category, description, status, email, assign, employees(name, email)")
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching complaints: {e}")
        return []

# Fetch complaints
complaints = fetch_complaints()

# Filter Complaints by Status
status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Resolved"])

if complaints:
    for complaint in complaints:
        if status_filter != "All" and complaint["status"] != status_filter:
            continue  # Skip complaints that don’t match the filter

        # Extract assigned employee details (if available)
        assigned_employee = complaint["employees"] if complaint["assign"] else None
        assigned_name = assigned_employee["name"] if assigned_employee else "Not Assigned"
        assigned_email = assigned_employee["email"] if assigned_employee else "Not Assigned"

        with st.expander(f"Complaint ID {complaint['id']}: {complaint['category']}"):
            st.write(f"**Created At:** {complaint['created_at']}")
            st.write(f"**Name:** {complaint['name']}")
            st.write(f"**Phone Number:** {complaint['phone_number']}")
            st.write(f"**Email:** {complaint['email']}")
            st.write(f"**Category:** {complaint['category']}")
            st.write(f"**Description:** {complaint['description']}")
            st.write(f"**Status:** {complaint['status'] if complaint['status'] else 'Not Assigned'}")
            st.write(f"**Assigned To:** {assigned_name} ({assigned_email})")

else:
    st.warning("No complaints found.")