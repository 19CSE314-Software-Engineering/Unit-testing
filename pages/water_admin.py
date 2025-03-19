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

# Fetch employees
def fetch_employees():
    try:
        response = supabase.table("employees").select("id, name").eq("dept_id", 1).execute()

        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching employees: {e}")
        return []

# Fetch tank locations
def fetch_tank_locations():
    try:
        response = supabase.table("tank_details").select("tank_id, state_name").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching tank locations: {e}")
        return []

# Assign employee to a location
def assign_employee(employee_id, tank_id):
    try:
        response = supabase.table("tank_details").update({"in_charge_id": employee_id}).eq("tank_id", tank_id).execute()
        if response.data:
            st.success("Employee assigned successfully!")
        else:
            st.error("Failed to assign employee.")
    except Exception as e:
        st.error(f"Error assigning employee: {e}")

# Streamlit UI


if "role" not in st.session_state or st.session_state["role"] != "Water Admin":
    st.error("Access Denied. Only Water Admins can access this page.")
    time.sleep(2)
    switch_page("main") # Redirect to Home page




st.set_page_config(layout="wide", page_title="Admin - Assign Employees", page_icon="🛠")
st.title("🛠 Admin Panel - Assign Employees to Locations")

st.header("Assign Employees to Water Stations")


add_logout_button()


employees = fetch_employees()
tank_locations = fetch_tank_locations()

if employees and tank_locations:
    employee_options = {emp["name"]: emp["id"] for emp in employees}
    tank_options = {tank["state_name"]: tank["tank_id"] for tank in tank_locations}
    
    selected_employee = st.selectbox("Select Employee", list(employee_options.keys()))
    selected_tank = st.selectbox("Select Tank Location", list(tank_options.keys()))
    
    if st.button("Assign Employee"):
        assign_employee(employee_options[selected_employee], tank_options[selected_tank])
else:
    st.warning("No employees or locations found.")