import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import datetime
from streamlit_extras.switch_page_button import switch_page

from utils import add_logout_button 

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase credentials are not set. Please check environment variables.")
    st.stop()

if "employee_id" not in st.session_state:
    st.error("User is not authenticated.")
    st.stop()

# Streamlit UI
st.set_page_config(page_title="Waste Management", page_icon="♻️", layout="wide")
st.title("♻️ Waste Management Dashboard")

add_logout_button()

# Navigation Buttons
st.divider()
st.write("🔗 **Navigation**")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("📊 View Waste Facility Statistics"):
        st.switch_page("pages/WASTE_FACILITY_STATISTICS.py")

with col_nav2:
    if st.button("🗺 View Facility Mapping"):
        st.switch_page("pages/WASTE_FACILITY_MAPPING.py")

with col_nav3:
    if st.button("🗺 Update Facility Data"):
        st.switch_page("pages/WASTE_FACILITY_UPDATION.py")

st.divider()

# Fetch the assigned waste facility details
employee_id = st.session_state["employee_id"]

facility_response = (
    supabase.table("waste_facilities")
    .select("facility_id, state_name, status, description, last_updated, capacity, waste_level")
    .eq("in_charge_id", employee_id)
    .execute()
)

if facility_response and hasattr(facility_response, "data") and facility_response.data:
    facility_details = facility_response.data
else:
    facility_details = []

if not facility_details:
    st.warning("You are not assigned to any waste facility.")
else:
    facility = facility_details[0]  # Assuming one facility per employee
    st.subheader(f"🚛 Waste Facility in {facility['state_name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔹 Status:**", facility.get("status", "N/A"))
        st.write("**📌 Description:**", facility.get("description", "N/A"))
        st.write("**📅 Last Updated:**", facility.get("last_updated", "N/A"))
    
    with col2:
        st.write("**📏 Capacity:**", f"{facility.get('capacity', 'N/A')} tons")
        waste_level = st.text_input("🗑 Waste Level (%)", value=facility.get("waste_level", "N/A"))
        
        if st.button("✅ Update Waste Level"):
            try:
                update_response = (
                    supabase.table("waste_facilities")
                    .update({"waste_level": waste_level, "last_updated": datetime.date.today().isoformat()})
                    .eq("facility_id", facility["facility_id"])
                    .execute()
                )
                if update_response and hasattr(update_response, "data") and update_response.data:
                    st.success("✔ Waste level updated successfully!")
                else:
                    st.error("❌ Failed to update waste level.")
            except Exception as e:
                st.error(f"⚠ Error: {str(e)}")
