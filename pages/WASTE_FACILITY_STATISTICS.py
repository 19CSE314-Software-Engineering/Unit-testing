import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch waste levels from Supabase
def fetch_waste_levels():
    try:
        response = supabase.table("waste_facilities").select("state_name, waste_level").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching waste levels: {e}")
        return []

# Function to parse waste level (handling both string and numeric formats)
def parse_waste_level(waste_level):
    if isinstance(waste_level, str) and waste_level.endswith("%"):
        return float(waste_level[:-1])  # Remove '%' and convert to float
    elif isinstance(waste_level, (int, float)):
        return float(waste_level)
    return None  # Return None if invalid

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Waste Management Dashboard", page_icon="♻️")

st.title("♻️ Waste Management")

# Navigation Buttons
st.divider()
st.write("🔗 **Navigation**")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("📊 View Facility Statistics"):
        st.switch_page("pages/WASTE_FACILITY_STATISTICS.py")

with col_nav2:
    if st.button("🗺 View Facility Mapping"):
        st.switch_page("pages/WASTE_FACILITY_MAPPING.py")

with col_nav3:
    if st.button("🗺 Update Facility Data"):
        st.switch_page("pages/WASTE_FACILITY_UPDATION.py")

st.divider()

# -------------------------------
# Section: Waste Levels in Facilities
# -------------------------------
st.header("📈 Waste Levels at Different Facilities")

waste_data = fetch_waste_levels()

if waste_data:
    df_waste = pd.DataFrame(waste_data)
    df_waste["waste_level"] = df_waste["waste_level"].apply(parse_waste_level)
    df_waste = df_waste.dropna()  # Remove rows with invalid waste levels

    fig = px.bar(df_waste, x="state_name", y="waste_level", color="waste_level",
                 labels={"state_name": "Facility Location", "waste_level": "Waste Level (%)"},
                 title="Waste Levels in Different Facilities")

    st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Section: Current Waste Levels
# -------------------------------
st.header("📊 Current Waste Levels")

# Example data (replace with your data source)
waste_levels = {
    "Landfill A": 85,
    "Recycling Plant B": 60,
    "Incinerator C": 45,
}

for site, level in waste_levels.items():
    st.write(f"{site}: {level}% capacity used")
    st.progress(level)

# -------------------------------
# Section: Waste Distribution Statistics
# -------------------------------
st.header("📉 Waste Distribution Statistics")

waste_distribution = {
    "Residential": 40000,  
    "Industrial": 35000,
    "Commercial": 25000,
    "Agricultural": 15000,
}

st.bar_chart(waste_distribution)  # Display waste data as a bar chart

# -------------------------------
# Section: Waste Reduction Tips
# -------------------------------
st.header("💡 Waste Reduction Tips")

st.write("- Reduce single-use plastics.")
st.write("- Compost organic waste.")
st.write("- Recycle paper, glass, and metal.")
st.write("- Donate usable items instead of discarding.")

# -------------------------------
# Section: Interactive Elements
# -------------------------------
if st.checkbox("Show Waste Forecast"):
    st.write("Forecast data will be displayed here (replace with actual forecast logic).")

selected_facility = st.selectbox("Select a Facility", list(waste_levels.keys()))
st.write(f"Details for {selected_facility} will be displayed here.")

waste_disposal_adjustment = st.slider("Adjust Waste Disposal Amount (Tons)", 0, 5000, 1000)
st.write(f"Disposal amount set to: {waste_disposal_adjustment} Tons")

# Fetch the assigned waste facility details
employee_id = st.session_state["employee_id"]

facility_response = (
    supabase.table("waste_facilities")
    .select("facility_id, state_name, status, description, last_updated, capacity, waste_level")
    .eq("in_charge_id", employee_id)
    .execute()
)
