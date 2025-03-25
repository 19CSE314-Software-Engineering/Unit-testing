# ADMIN_DASHBOARD.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import datetime
import time
from utils import add_logout_button, create_employee, process_employee_data, create_department

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.postgrest.auth(SUPABASE_KEY)

# Store Supabase client in session state for use in utils
st.session_state["supabase"] = supabase

# Streamlit UI
st.set_page_config(page_title="Admin Dashboard", page_icon="🔐", layout="wide")

if "role" not in st.session_state or st.session_state["role"] != "Admin":
    st.error("Access Denied. Only Electricity Admins can access this page.")
    time.sleep(2)
    switch_page("main")  # Redirect to Home page

st.title("Admin Dashboard")

add_logout_button()

# Tabs for Employee Management
tab1, tab2, tab3 = st.tabs(["Create Employee", "View Employees", "Create Department & Position"])

### **🔹 Tab 1: Create Employee**
with tab1:
    st.subheader("Create New Employee")

    # Fetch departments
    dept_response = supabase.table("department").select("dept_id, dept_name").execute()
    departments = dept_response.data if dept_response.data else []
    
    if not departments:
        st.warning("No departments available. Please add departments first.")
    else:
        # Dropdown for departments
        dept_options = {dept["dept_name"]: dept["dept_id"] for dept in departments}
        selected_dept_name = st.selectbox("Select Department", list(dept_options.keys()))
        selected_dept_id = dept_options[selected_dept_name]

        # Fetch positions for selected department
        position_response = (
            supabase.table("positions")
            .select("position_id, position_name")
            .eq("dept_id", selected_dept_id)
            .execute()
        )
        positions = position_response.data if position_response.data else []

        if not positions:
            st.warning("No positions available for this department.")
        else:
            # Dropdown for positions
            position_options = {pos["position_name"]: pos["position_id"] for pos in positions}
            selected_position_name = st.selectbox("Select Position", list(position_options.keys()))
            selected_position_id = position_options[selected_position_name]

            # Employee details input
            name = st.text_input("Full Name")
            email = st.text_input("Email (Must be Unique)")
            dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date(2025, 12, 31))
            contact_number = st.text_input("Contact Number")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            default_password = "abcdef"

            # Button to create employee
            if st.button("Create Employee"):
                success, message = create_employee(
                    supabase=supabase,
                    name=name,
                    email=email,
                    dob=dob,
                    contact_number=contact_number,
                    gender=gender,
                    dept_id=selected_dept_id,
                    position_id=selected_position_id,
                    default_password=default_password
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

### **🔹 Tab 2: View Employees**
with tab2:
    st.subheader("Employee List")

    # Fetch all employees with department and position names
    employee_response = (
        supabase.table("employees")
        .select("id, name, email, gender, dob, department(dept_name), positions(position_name), created_at")
        .execute()
    )

    employees = employee_response.data if employee_response.data else []

    if not employees:
        st.info("No employees found.")
    else:
        # Process the data using the new function
        processed_employees = process_employee_data(employees)
        
        # Convert to DataFrame and display
        df = pd.DataFrame(processed_employees)
        df.rename(columns={"department": "Department", "positions": "Position"}, inplace=True)
        st.dataframe(df, hide_index=True)

### **🔹 Tab 3: Create Department & Position**
with tab3:
    st.subheader("Root Admin Panel")

    st.write("### Manage Departments")
    new_dept_name = st.text_input("New Department Name")

    if st.button("Create Department"):
        success, message = create_department(supabase, new_dept_name)
        if success:
            st.success(message)
        else:
            st.error(message)

    st.write("### Manage Positions")
    # Fetch departments again for position creation
    dept_response = supabase.table("department").select("dept_id, dept_name").execute()
    departments = dept_response.data if dept_response.data else []

    if departments:
        dept_options = {dept["dept_name"]: dept["dept_id"] for dept in departments}
        selected_dept_for_position = st.selectbox("Select Department for Position", list(dept_options.keys()))
        selected_dept_id = dept_options[selected_dept_for_position]

        new_position_name = st.text_input("New Position Name")
        
        if st.button("Create Position"):
            if new_position_name:
                position_data = {"position_name": new_position_name, "dept_id": selected_dept_id}
                response = supabase.table("positions").insert(position_data).execute()
                
                if response.data:
                    st.success("Position added successfully!")
                else:
                    st.error("Failed to add position.")
            else:
                st.warning("Enter a position name.")
    else:
        st.warning("No departments found. Please create a department first.")