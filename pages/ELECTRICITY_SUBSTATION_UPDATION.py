import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import datetime
from utils import add_logout_button 
from streamlit_extras.switch_page_button import switch_page


# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.error("Supabase credentials are missing. Please check environment variables.")
    st.stop()

# Check authentication
if "employee_id" not in st.session_state:
    st.error("User is not authenticated.")
    st.stop()

# Streamlit UI
st.set_page_config(page_title="Electricity Substation Management", page_icon="⚡", layout="wide")
st.title("Electricity Substation Management")

add_logout_button()

# Navigation Buttons
st.divider()
st.write("🔗 **Navigation**")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("📊 View Substation Statistics"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_STATISTICS.py")

with col_nav2:
    if st.button("🗺 View Substation Mapping"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_MAPPING.py")

with col_nav3:
    if st.button("🗺 View Substation Updation"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_UPDATION.py")

st.divider()






employee_id = st.session_state["employee_id"]

# Fetch assigned substation details
substation_response = (
    supabase.table("electricity_substations")
    .select("substation_id, name, state_name, status, description, last_updated, capacity, electricity_load")
    .eq("in_charge_id", employee_id)
    .execute()
)

if substation_response and hasattr(substation_response, "data") and substation_response.data:
    substation_details = substation_response.data
else:
    substation_details = []

if not substation_details:
    st.warning("You are not assigned to any electricity substation.")
else:
    substation = substation_details[0]  # Assuming one substation per employee
    st.subheader(f"Electricity Substation: {substation['name']} ({substation['state_name']})")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Status:**", substation.get("status", "N/A"))
        st.write("**Description:**", substation.get("description", "N/A"))
        st.write("**Last Updated:**", substation.get("last_updated", "N/A"))

    with col2:
        st.write("**Capacity:**", f"{substation.get('capacity', 'N/A')} MW")
        electricity_load = st.text_input("Electricity Load (MW)", value=substation.get("electricity_load", "N/A"))

        if st.button("Update Electricity Load"):
            try:
                update_response = (
                    supabase.table("electricity_substations")
                    .update({"electricity_load": electricity_load, "last_updated": datetime.date.today().isoformat()})
                    .eq("substation_id", substation["substation_id"])
                    .execute()
                )
                if update_response and hasattr(update_response, "data") and update_response.data:
                    st.success("Electricity load updated successfully!")
                else:
                    st.error("Failed to update electricity load.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
