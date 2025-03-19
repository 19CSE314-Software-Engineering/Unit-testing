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

# Ensure only Electricity Admin can access
if "role" not in st.session_state or st.session_state["role"] != "Electricity Admin":
    st.error("Access Denied. Only Electricity Admins can access this page.")
    time.sleep(2)
    switch_page("main")

st.set_page_config(layout="wide", page_title="Admin - Electricity Management", page_icon="⚡")
st.title("⚡ Admin Panel - Electricity Management")

# Sidebar Logout Button
add_logout_button()

# Function to fetch employees
def fetch_employees():
    try:
        response = supabase.table("employees").select("id, name").eq("dept_id", 2).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching employees: {e}")
        return []

# Function to fetch substation locations
def fetch_substation_locations():
    try:
        response = supabase.table("electricity_substations").select("substation_id, state_name").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching substation locations: {e}")
        return []

# Function to assign employee to a substation
def assign_employee(employee_id, substation_id):
    try:
        response = supabase.table("electricity_substations").update({"in_charge_id": employee_id}).eq("substation_id", substation_id).execute()
        if response.data:
            st.success("Employee assigned successfully!")
        else:
            st.error("Failed to assign employee.")
    except Exception as e:
        st.error(f"Error assigning employee: {e}")

# Function to fetch complaints for Electricity department
def fetch_complaints():
    try:
        response = supabase.table("customer_complaints").select("id, created_at, name, phone_number, category, description, status, email, assign").eq("category", "Electricity").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching complaints: {e}")
        return []

# Function to update complaint status and assignment
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
    st.header("Assign Employees to Electricity Substations")
    employees = fetch_employees()
    substation_locations = fetch_substation_locations()
    
    if employees and substation_locations:
        employee_options = {emp["name"]: emp["id"] for emp in employees}
        substation_options = {substation["state_name"]: substation["substation_id"] for substation in substation_locations}
        
        selected_employee = st.selectbox("Select Employee", list(employee_options.keys()))
        selected_substation = st.selectbox("Select Substation Location", list(substation_options.keys()))
        
        if st.button("Assign Employee"):
            assign_employee(employee_options[selected_employee], substation_options[selected_substation])
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
                
                # Status selection
                status_options = ["Pending", "In Progress", "Resolved"]
                selected_status = st.selectbox(f"Update Status", status_options, index=status_options.index(complaint["status"]) if complaint["status"] in status_options else 0, key=f"status_{complaint['id']}")
                
                # Assign employee (show name instead of index)
                selected_employee = st.selectbox(
                    f"Assign Employee",
                    employees,
                    index=employees.index(complaint["assign"]) if complaint["assign"] in employees else 0,
                    key=f"employee_{complaint['id']}"
                ) if employees else None
                
                if st.button(f"Update", key=f"update_{complaint['id']}"):
                    update_complaint(complaint['id'], selected_status, selected_employee)
    else:
        st.warning("No complaints found.")