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

# Ensure only Water Admin can access
if "role" not in st.session_state or st.session_state["role"] != "Water Admin":
    st.error("Access Denied. Only Water Admins can access this page.")
    time.sleep(2)
    switch_page("main")

st.set_page_config(layout="wide", page_title="Admin - Water Management", page_icon="💧")
st.title("💧 Admin Panel - Water Management")

# Sidebar Logout Button
add_logout_button()

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

# Fetch complaints
def fetch_complaints():
    try:
        response = supabase.table("customer_complaints").select("id, created_at, name, phone_number, category, description, status, email, assign").eq("category", "Water").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching complaints: {e}")
        return []

# Update complaint status and assignment
def update_complaint(complaint_id, status, employee_name):
    try:
        response = supabase.table("customer_complaints").update({"status": status, "assign": employee_name}).eq("id", complaint_id).execute()
        if response.data:
            st.success("Complaint updated successfully!")
        else:
            st.error("Failed to update complaint.")
    except Exception as e:
        st.error(f"Error updating complaint: {e}")

# UI with Tabs
tab1, tab2 = st.tabs(["Assign Employees", "View Complaints"])

with tab1:
    st.header("Assign Employees to Water Stations")
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

with tab2:
    st.header("View and Manage Complaints")
    complaints = fetch_complaints()
    employees = fetch_employees()
    
    if complaints:
        for complaint in complaints:
            with st.expander(f"Complaint ID {complaint['id']}: {complaint['category']}"):
                st.write(f"**Created At:** {complaint['created_at']}")
                st.write(f"**Name:** {complaint['name']}")
                st.write(f"**Phone Number:** {complaint['phone_number']}")
                st.write(f"**Email:** {complaint['email']}")
                st.write(f"**Category:** {complaint['category']}")
                st.write(f"**Description:** {complaint['description']}")
                
                status_options = ["Pending", "In Progress", "Resolved"]
                selected_status = st.selectbox(f"Update Status", status_options, index=status_options.index(complaint["status"]) if complaint["status"] in status_options else 0, key=f"status_{complaint['id']}")
                
                selected_employee = st.selectbox(
                    f"Assign Employee",
                    [emp["name"] for emp in employees] if employees else [],
                    index=[emp["name"] for emp in employees].index(complaint["assign"]) if complaint["assign"] in [emp["name"] for emp in employees] else 0,
                    key=f"employee_{complaint['id']}"
                ) if employees else None
                
                if st.button(f"Update", key=f"update_{complaint['id']}"):
                    update_complaint(complaint['id'], selected_status, selected_employee)
    else:
        st.warning("No complaints found.")
