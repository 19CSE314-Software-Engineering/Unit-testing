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




# Function to fetch tank water level data
def fetch_tank_water_levels():
    try:
        response = supabase.table("tank_details").select("state_name, water_level").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching water levels: {e}")
        return []

# Function to parse water level (handling both string and numeric formats)
def parse_water_level(water_level):
    if isinstance(water_level, str) and water_level.endswith("%"):
        return float(water_level[:-1])  # Remove '%' and convert to float
    elif isinstance(water_level, (int, float)):
        return float(water_level)
    return None  # Return None if invalid

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Water Management Dashboard", page_icon="💧")

st.title("💧 Water Management")

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




# -------------------------------
# Section: Water Levels in Tanks (Using Supabase)
# -------------------------------
st.header("📈 Water Levels at Different Tanks")

tank_data = fetch_tank_water_levels()

if tank_data:
    df_tanks = pd.DataFrame(tank_data)
    df_tanks["water_level"] = df_tanks["water_level"].apply(parse_water_level)
    df_tanks = df_tanks.dropna()  # Remove rows with invalid water levels

    fig = px.bar(df_tanks, x="state_name", y="water_level", color="water_level",
                 labels={"state_name": "Tank Location", "water_level": "Water Level (%)"},
                 title="Water Levels in Different Tanks")

    st.plotly_chart(fig, use_container_width=True)





# -------------------------------
# Section: Current Water Levels
# -------------------------------
st.header("📊 Current Water Levels")

# Example data (replace with your data source)
reservoir_levels = {
    "Reservoir A": 75,
    "Reservoir B": 92,
    "Reservoir C": 60,
}

for reservoir, level in reservoir_levels.items():
    st.write(f"{reservoir}: {level}% full")
    st.progress(level)

# -------------------------------
# Section: Water Usage Statistics
# -------------------------------
st.header("📉 Water Usage Statistics")

usage_data = {
    "Residential": 50000,  
    "Industrial": 30000,
    "Agriculture": 20000,
}

st.bar_chart(usage_data)  # Display usage data as a bar chart



# -------------------------------
# Section: Conservation Tips
# -------------------------------
st.header("💡 Conservation Tips")

st.write("- Reduce shower time.")
st.write("- Fix leaky faucets.")
st.write("- Water your garden efficiently.")
st.write("- Use water-saving appliances.")

# -------------------------------
# Section: Interactive Elements
# -------------------------------
if st.checkbox("Show Water Consumption Forecast"):
    st.write("Forecast data will be displayed here (replace with actual forecast logic).")

selected_reservoir = st.selectbox("Select a Reservoir", list(reservoir_levels.keys()))
st.write(f"Details for {selected_reservoir} will be displayed here.")

irrigation_amount = st.slider("Adjust Irrigation Amount (Liters)", 0, 1000, 500)
st.write(f"Irrigation amount set to: {irrigation_amount} Liters")
