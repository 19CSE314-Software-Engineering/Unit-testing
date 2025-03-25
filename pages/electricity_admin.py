# electricity_admin.py
import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from streamlit_extras.switch_page_button import switch_page
import time
from utils import add_logout_button, fetch_electricity_employees, fetch_substation_locations, assign_employee_to_substation, fetch_electricity_complaints, update_electricity_complaint

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Store Supabase client in session state for use in utils
st.session_state["supabase"] = supabase

# Ensure only Electricity Admin can access
if "role" not in st.session_state or st.session_state["role"] != "Electricity Admin":
    st.error("Access Denied. Only Electricity Admins can access this page.")
    time.sleep(2)
    switch_page("main")

st.set_page_config(layout="wide", page_title="Admin - Electricity Management", page_icon="⚡")
st.title("⚡ Admin Panel - Electricity Management")

# Sidebar Logout Button
add_logout_button()

# UI with Tabs
tab1, tab2 = st.tabs(["Assign Employees", "View Complaints"])

with tab1:
    st.header("Assign Employees to Electricity Substations")
    employees = fetch_electricity_employees(supabase)
    substation_locations = fetch_substation_locations(supabase)
    
    if employees and substation_locations:
        employee_options = {emp["name"]: emp["id"] for emp in employees}
        substation_options = {substation["state_name"]: substation["substation_id"] for substation in substation_locations}
        
        selected_employee = st.selectbox("Select Employee", list(employee_options.keys()))
        selected_substation = st.selectbox("Select Substation Location", list(substation_options.keys()))
        
        if st.button("Assign Employee"):
            success, message = assign_employee_to_substation(
                supabase=supabase,
                employee_id=employee_options[selected_employee],
                substation_id=substation_options[selected_substation]
            )
            if success:
                st.success(message)
            else:
                st.error(message)
    else:
        st.warning("No employees or locations found.")

with tab2:
    st.header("View and Manage Complaints")
    complaints = fetch_electricity_complaints(supabase)
    employees = fetch_electricity_employees(supabase)
    
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
                selected_status = st.selectbox(
                    f"Update Status",
                    status_options,
                    index=status_options.index(complaint["status"]) if complaint["status"] in status_options else 0,
                    key=f"status_{complaint['id']}"
                )
                
                # Create a dictionary to map employee names to their IDs
                employee_options = {emp["name"]: emp["id"] for emp in employees} if employees else {}

                # Reverse mapping to find the selected employee's name from the stored ID
                assigned_employee_id = complaint["assign"]
                assigned_employee_name = next((name for name, emp_id in employee_options.items() if emp_id == assigned_employee_id), None)

                # Assign Employee using Employee Name but store Employee ID
                selected_employee_name = st.selectbox(
                    f"Assign Employee",
                    list(employee_options.keys()),
                    index=list(employee_options.keys()).index(assigned_employee_name) if assigned_employee_name in employee_options else 0,
                    key=f"employee_{complaint['id']}"
                ) if employees else None

                # Get the selected employee's ID
                selected_employee_id = employee_options[selected_employee_name] if selected_employee_name else None
                
                if st.button(f"Update", key=f"update_{complaint['id']}"):
                    success, message = update_electricity_complaint(
                        supabase=supabase,
                        complaint_id=complaint['id'],
                        status=selected_status,
                        employee_id=selected_employee_id
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        st.warning("No complaints found.")