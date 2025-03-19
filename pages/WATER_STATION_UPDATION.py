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
st.set_page_config(page_title="Tank Management", page_icon="💧", layout="wide")
st.title("💧 Water Tank Management")

add_logout_button()


# Navigation Buttons
st.divider()
st.write("🔗 **Navigation**")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("📊 View Substation Statistics"):
        st.switch_page("pages/WATER_STATION_STATISTICS.py")

with col_nav2:
    if st.button("🗺 View Substation Mapping"):
        st.switch_page("pages/WATER_STATION_MAPPING.py")

with col_nav3:
    if st.button("🗺 View Substation Updation"):
        st.switch_page("pages/WATER_STATION_UPDATION.py")

st.divider()

# Simulate employee authentication (Replace with actual authentication logic)
if "employee_id" not in st.session_state:
    st.error("User is not authenticated.")
    st.stop()

employee_id = st.session_state["employee_id"]

# Fetch the assigned water tank details
tank_response = (
    supabase.table("tank_details")
    .select("tank_id, state_name, status, description, last_updated, capacity, water_level")
    .eq("in_charge_id", employee_id)
    .execute()
)

if tank_response and hasattr(tank_response, "data") and tank_response.data:
    tank_details = tank_response.data
else:
    tank_details = []

if not tank_details:
    st.warning("You are not assigned to any water tank.")
else:
    tank = tank_details[0]  # Assuming one tank per employee
    st.subheader(f"🚰 Water Tank in {tank['state_name']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔹 Status:**", tank.get("status", "N/A"))
        st.write("**📌 Description:**", tank.get("description", "N/A"))
        st.write("**📅 Last Updated:**", tank.get("last_updated", "N/A"))
    
    with col2:
        st.write("**📏 Capacity:**", f"{tank.get('capacity', 'N/A')} liters")
        water_level = st.text_input("💦 Water Level (%)", value=tank.get("water_level", "N/A"))
        
        if st.button("✅ Update Water Level"):
            try:
                update_response = (
                    supabase.table("tank_details")
                    .update({"water_level": water_level, "last_updated": datetime.date.today().isoformat()})
                    .eq("tank_id", tank["tank_id"])
                    .execute()
                )
                if update_response and hasattr(update_response, "data") and update_response.data:
                    st.success("✔ Water level updated successfully!")
                else:
                    st.error("❌ Failed to update water level.")
            except Exception as e:
                st.error(f"⚠ Error: {str(e)}")