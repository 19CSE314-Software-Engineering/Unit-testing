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

# Ensure only Waste Admin can access
if "role" not in st.session_state or st.session_state["role"] != "Waste Admin":
    st.error("Access Denied. Only Waste Admins can access this page.")
    time.sleep(2)
    switch_page("main")

st.set_page_config(layout="wide", page_title="Admin - Waste Management", page_icon="🗑")
st.title("🗑 Admin Panel - Waste Management")

# Sidebar Logout Button
add_logout_button()

# Fetch employees
def fetch_employees():
    try:
        response = supabase.table("employees").select("id, name").eq("dept_id", 5).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching employees: {e}")
        return []

# Fetch waste collection locations
def fetch_waste_locations():
    try:
        response = supabase.table("waste_facilities").select("facility_id, state_name").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching waste locations: {e}")
        return []

# Assign employee to a waste site
def assign_employee(employee_id, site_id):
    try:
        response = supabase.table("waste_facilities").update({"in_charge_id": employee_id}).eq("facility_id", site_id).execute()
        if response.data:
            st.success("Employee assigned successfully!")
        else:
            st.error("Failed to assign employee.")
    except Exception as e:
        st.error(f"Error assigning employee: {e}")

# Fetch complaints
def fetch_complaints():
    try:
        response = supabase.table("customer_complaints").select("id, created_at, name, phone_number, category, description, status, email, assign").eq("category", "waste").execute()
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
    st.header("Assign Employees to Waste Collection Sites")
    employees = fetch_employees()
    waste_locations = fetch_waste_locations()

    if employees and waste_locations:
        employee_options = {emp["name"]: emp["id"] for emp in employees}
        site_options = {site["state_name"]: site["facility_id"] for site in waste_locations}
        
        selected_employee = st.selectbox("Select Employee", list(employee_options.keys()))
        selected_site = st.selectbox("Select Waste Collection Site", list(site_options.keys()))
        
        if st.button("Assign Employee"):
            assign_employee(employee_options[selected_employee], site_options[selected_site])
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
                
                employee_options = {emp["name"]: emp["id"] for emp in employees} if employees else {}
                assigned_employee_id = complaint["assign"]
                assigned_employee_name = next((name for name, emp_id in employee_options.items() if emp_id == assigned_employee_id), None)

                selected_employee_name = st.selectbox(
                    f"Assign Employee",
                    list(employee_options.keys()),
                    index=list(employee_options.keys()).index(assigned_employee_name) if assigned_employee_name in employee_options else 0,
                    key=f"employee_{complaint['id']}"
                ) if employees else None

                selected_employee_id = employee_options[selected_employee_name] if selected_employee_name else None
                
                if st.button(f"Update", key=f"update_{complaint['id']}"):
                    update_complaint(complaint['id'], selected_status, selected_employee_id)
    else:
        st.warning("No complaints found.")