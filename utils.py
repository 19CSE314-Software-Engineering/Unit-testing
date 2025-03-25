# utils.py
import streamlit as st
import time
from streamlit_extras.switch_page_button import switch_page
from supabase import Client
from datetime import date

# Existing functions (from previous work)
def logout():
    supabase = st.session_state.get("supabase")
    if supabase:
        supabase.auth.sign_out()
    st.session_state.clear()
    st.success("Logged out successfully! ")
    time.sleep(2)
    switch_page("main")

def add_logout_button():
    with st.sidebar:
        st.button("Logout", on_click=logout)

def create_employee(
    supabase: Client,
    name: str,
    email: str,
    dob: date,
    contact_number: str,
    gender: str,
    dept_id: int,
    position_id: int,
    default_password: str = "abcdef"
) -> tuple[bool, str]:
    if not name or not email:
        return False, "Name and email are required."
    try:
        auth_response = supabase.auth.sign_up(
            {"email": email, "password": default_password}
        )
        if not auth_response or not auth_response.user:
            return False, "User authentication creation failed."
        employee_response = (
            supabase.table("employees")
            .insert({
                "name": name,
                "email": email,
                "dob": dob.strftime("%Y-%m-%d"),
                "contact_number": contact_number,
                "gender": gender,
                "dept_id": dept_id,
                "position_id": position_id
            })
            .execute()
        )
        if employee_response.data:
            return True, "Employee created successfully!"
        else:
            return False, "Failed to add employee to database."
    except Exception as e:
        return False, f"Error: {str(e)}"

def process_employee_data(employees: list) -> list:
    processed_employees = []
    for emp in employees:
        processed_emp = emp.copy()
        if "department" in processed_emp and processed_emp["department"]:
            processed_emp["department"] = processed_emp["department"]["dept_name"]
        if "positions" in processed_emp and processed_emp["positions"]:
            processed_emp["positions"] = processed_emp["positions"]["position_name"]
        processed_employees.append(processed_emp)
    return processed_employees

def create_department(supabase: Client, dept_name: str) -> tuple[bool, str]:
    if not dept_name:
        return False, "Enter a department name."
    dept_data = {"dept_name": dept_name}
    response = supabase.table("department").insert(dept_data).execute()
    if response.data:
        return True, "Department added successfully!"
    else:
        return False, "Failed to add department."

def submit_complaint(
    supabase: Client,
    email: str,
    name: str,
    phone_number: str,
    category: str,
    description: str
) -> tuple[bool, str]:
    if not email or not name or not description:
        return False, "Email, name, and description are required."
    data = {
        "email": email,
        "name": name,
        "phone_number": phone_number,
        "category": category,
        "description": description
    }
    response = supabase.table("customer_complaints").insert(data).execute()
    if response.data:
        return True, "Complaint submitted successfully!"
    else:
        return False, "Failed to submit complaint."

def fetch_complaints_by_email(supabase: Client, email: str) -> list:
    response = supabase.table("customer_complaints").select("category, description, status, created_at").eq("email", email).execute()
    return response.data if response.data else []

def fetch_notifications(supabase: Client) -> list:
    response = supabase.table("notifications").select("notification, created_at").order("created_at", desc=True).execute()
    return response.data if response.data else []

def fetch_welfare_schemes(supabase: Client) -> list:
    response = supabase.table("welfare_schemes").select("*").execute()
    return response.data if response.data else []

def check_eligibility(scheme: dict, age: int, income: float, employment_status: str) -> bool:
    eligibility_criteria = scheme["eligibility_criteria"].lower()
    return (
        ("age" in eligibility_criteria and str(age) in eligibility_criteria) or
        ("income" in eligibility_criteria and str(int(income)) in eligibility_criteria) or
        ("employment" in eligibility_criteria and employment_status.lower() in eligibility_criteria)
    )

def apply_for_scheme(
    supabase: Client,
    name: str,
    age: int,
    income: float,
    employment_status: str,
    crisis_type: str,
    scheme_id: int
) -> tuple[bool, str]:
    if not name:
        return False, "Name is required."
    data = {
        "name": name,
        "age": int(age),
        "income": int(income),
        "employment_status": employment_status,
        "crisis_type": crisis_type,
        "scheme_id": scheme_id
    }
    response = supabase.table("citizen_applications").insert(data).execute()
    if response.data:
        return True, "Application submitted successfully!"
    else:
        return False, "Failed to submit application."

def fetch_crisis_reports(supabase: Client, employee_id: int) -> list:
    response = supabase.table("crisis_reports").select("*").eq("in_charge_id", employee_id).execute()
    return response.data if response.data else []

def update_crisis_report(supabase: Client, crisis_id: int, severity: int, description: str) -> tuple[bool, str]:
    if severity < 1 or severity > 5:
        return False, "Severity must be between 1 and 5."
    if not description:
        return False, "Description cannot be empty."
    response = supabase.table("crisis_reports").update({
        "severity": severity,
        "description": description,
    }).eq("crisis_id", crisis_id).execute()
    if response.data:
        return True, "Crisis updated successfully!"
    else:
        return False, "Failed to update crisis."

def delete_crisis_report(supabase: Client, crisis_id: int) -> tuple[bool, str]:
    response = supabase.table("crisis_reports").delete().eq("crisis_id", crisis_id).execute()
    if response.data:
        return True, "Crisis resolved and removed."
    else:
        return False, "Failed to resolve crisis."

def post_news_update(
    supabase: Client,
    title: str,
    content: str,
    crisis_id: int = None,
    posted_by: str = None
) -> tuple[bool, str]:
    if not title or not content:
        return False, "Title and content are required."
    new_entry = {
        "title": title,
        "content": content,
        "crisis_id": crisis_id,
        "posted_by": posted_by
    }
    response = supabase.table("crisis_newsboard").insert(new_entry).execute()
    if response.data:
        return True, "News update posted successfully!"
    else:
        return False, "Failed to post news update."

def fetch_recent_news_updates(supabase: Client, limit: int = 10) -> list:
    response = supabase.table("crisis_newsboard").select("*").order("id", desc=True).limit(limit).execute()
    return response.data if response.data else []

def fetch_electricity_employees(supabase: Client) -> list:
    response = supabase.table("employees").select("id, name").eq("dept_id", 2).execute()
    return response.data if response.data else []

def fetch_substation_locations(supabase: Client) -> list:
    response = supabase.table("electricity_substations").select("substation_id, state_name").execute()
    return response.data if response.data else []

def assign_employee_to_substation(supabase: Client, employee_id: int, substation_id: int) -> tuple[bool, str]:
    response = supabase.table("electricity_substations").update({"in_charge_id": employee_id}).eq("substation_id", substation_id).execute()
    if response.data:
        return True, "Employee assigned successfully!"
    else:
        return False, "Failed to assign employee."

def fetch_electricity_complaints(supabase: Client) -> list:
    response = supabase.table("customer_complaints").select("id, created_at, name, phone_number, category, description, status, email, assign").eq("category", "Electricity").execute()
    return response.data if response.data else []

def update_electricity_complaint(supabase: Client, complaint_id: int, status: str, employee_id: int) -> tuple[bool, str]:
    if status not in ["Pending", "In Progress", "Resolved"]:
        return False, "Invalid status."
    response = supabase.table("customer_complaints").update({"status": status, "assign": employee_id}).eq("id", complaint_id).execute()
    if response.data:
        return True, "Complaint updated successfully!"
    else:
        return False, "Failed to update complaint."

def set_user_password(supabase: Client, email: str, password: str) -> tuple[bool, str]:
    if not email.strip() or not password.strip():
        return False, "Both email and password are required!"
    try:
        user_query = supabase.auth.admin.list_users()
        user_id = None
        for user in user_query.users:
            if user.email == email:
                user_id = user.id
                break
        if user_id is None:
            return False, "User not found! Please check the email."
        supabase.auth.admin.update_user_by_id(user_id, {"password": password})
        return True, "Password set successfully! You can now log in."
    except Exception as e:
        return False, f"Error: {str(e)}"

def fetch_all_complaints(supabase: Client) -> list:
    response = (
        supabase.table("customer_complaints")
        .select("id, created_at, name, phone_number, category, description, status, email, assign, employees(name, email)")
        .execute()
    )
    return response.data if response.data else []

def filter_complaints_by_status(complaints: list, status: str) -> list:
    if status == "All":
        return complaints
    return [complaint for complaint in complaints if complaint["status"] == status]

def fetch_waste_employees(supabase: Client) -> list:
    response = supabase.table("employees").select("id, name").eq("dept_id", 5).execute()
    return response.data if response.data else []

def fetch_waste_facilities(supabase: Client) -> list:
    response = supabase.table("waste_facilities").select("facility_id, state_name").execute()
    return response.data if response.data else []

def assign_employee_to_waste_facility(supabase: Client, employee_id: int, facility_id: int) -> tuple[bool, str]:
    response = supabase.table("waste_facilities").update({"in_charge_id": employee_id}).eq("facility_id", facility_id).execute()
    if response.data:
        return True, "Employee assigned successfully!"
    else:
        return False, "Failed to assign employee."

def fetch_waste_complaints(supabase: Client) -> list:
    response = supabase.table("customer_complaints").select("id, created_at, name, phone_number, category, description, status, email, assign").eq("category", "waste").execute()
    return response.data if response.data else []

def update_waste_complaint(supabase: Client, complaint_id: int, status: str, employee_id: int) -> tuple[bool, str]:
    if status not in ["Pending", "In Progress", "Resolved"]:
        return False, "Invalid status."
    response = supabase.table("customer_complaints").update({"status": status, "assign": employee_id}).eq("id", complaint_id).execute()
    if response.data:
        return True, "Complaint updated successfully!"
    else:
        return False, "Failed to update complaint."

def fetch_waste_facility_data(supabase: Client) -> list:
    response = supabase.table("waste_facilities").select("*, employees(name, id)").execute()
    return response.data if response.data else []

def get_waste_level_color(waste_level: float, total_capacity: float) -> str:
    if waste_level is None or total_capacity is None or total_capacity == 0:
        return "gray"
    per = (waste_level / total_capacity) * 100
    if per < 30:
        return "green"
    elif per < 70:
        return "yellow"
    else:
        return "red"

def count_waste_levels(waste_data: list) -> dict:
    level_counts = {"Low (<30%)": 0, "Medium (30%-70%)": 0, "High (>70%)": 0}
    for site in waste_data:
        waste_level = site["waste_level"]
        total_capacity = site["capacity"]
        if waste_level is None or total_capacity is None or total_capacity == 0:
            continue
        per = (waste_level / total_capacity) * 100
        if per < 30:
            level_counts["Low (<30%)"] += 1
        elif per < 70:
            level_counts["Medium (30%-70%)"] += 1
        else:
            level_counts["High (>70%)"] += 1
    return level_counts

def fetch_waste_levels_data(supabase: Client) -> list:
    response = supabase.table("waste_facilities").select("state_name, waste_level").execute()
    return response.data if response.data else []

def parse_waste_level_value(waste_level) -> float:
    if isinstance(waste_level, str) and waste_level.endswith("%"):
        return float(waste_level[:-1])
    elif isinstance(waste_level, (int, float)):
        return float(waste_level)
    return None

def fetch_assigned_waste_facility(supabase: Client, employee_id: int) -> list:
    response = (
        supabase.table("waste_facilities")
        .select("facility_id, state_name, status, description, last_updated, capacity, waste_level")
        .eq("in_charge_id", employee_id)
        .execute()
    )
    return response.data if response.data else []

def update_waste_facility_level(supabase: Client, facility_id: int, waste_level: str, last_updated: str) -> tuple[bool, str]:
    try:
        waste_level_float = float(waste_level)
        if waste_level_float < 0 or waste_level_float > 100:
            return False, "Waste level must be between 0 and 100."
        
        response = (
            supabase.table("waste_facilities")
            .update({"waste_level": waste_level_float, "last_updated": last_updated})
            .eq("facility_id", facility_id)
            .execute()
        )
        if response.data:
            return True, "Waste level updated successfully!"
        else:
            return False, "Failed to update waste level."
    except ValueError:
        return False, "Waste level must be a valid number."
    except Exception as e:
        return False, f"Error: {str(e)}"

# New functions for CRISIS_MAP.py
def fetch_crisis_map_data(supabase: Client) -> list:
    """
    Fetch crisis data for the map.
    
    Args:
        supabase: Supabase client instance
    
    Returns:
        List of crisis reports
    """
    response = supabase.table("crisis_reports").select("*").execute()
    return response.data if response.data else []

def fetch_facility_data(supabase: Client) -> list:
    """
    Fetch facility data for the map.
    
    Args:
        supabase: Supabase client instance
    
    Returns:
        List of facilities
    """
    response = supabase.table("facilities").select("facility_name, facility_type, latitude, longitude, contact_info").execute()
    return response.data if response.data else []

def filter_crises_by_location(crisis_data: list, location_query: str) -> list:
    """
    Filter crises by location (state name).
    
    Args:
        crisis_data: List of crisis data
        location_query: State name to filter by
    
    Returns:
        Filtered list of crises
    """
    if not location_query:
        return crisis_data
    return [crisis for crisis in crisis_data if crisis["state_name"].lower() == location_query.lower()]

def count_crises_by_type(crisis_data: list) -> dict:
    """
    Count crises by type for the overview section.
    
    Args:
        crisis_data: List of crisis data
    
    Returns:
        Dictionary with counts for each crisis type
    """
    crisis_counts = {"Fire": 0, "Flood": 0, "Earthquake": 0, "Power Outage": 0, "Other": 0}
    for crisis in crisis_data:
        crisis_type = crisis["crisis_type"]
        if crisis_type in crisis_counts:
            crisis_counts[crisis_type] += 1
        else:
            crisis_counts["Other"] += 1
    return crisis_counts