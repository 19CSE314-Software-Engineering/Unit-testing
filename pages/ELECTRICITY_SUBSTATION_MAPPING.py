import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch substation details from the database
def fetch_substation_data():
    try:
        response = supabase.table("electricity_substations").select("*, employees(name, id)").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching substation data: {e}")
        return []

# Function to parse electricity load
def parse_load(load):
    try:
        return float(load)
    except (TypeError, ValueError):
        return None  # Invalid data

# Function to determine color based on electricity load percentage
def get_color(load, capacity):
    if load is None or capacity is None or capacity == 0:
        return "gray"  # Default color if data is invalid
    percentage = (load / capacity) * 100
    if percentage < 30:
        return "green"  # Low load
    elif percentage < 70:
        return "yellow"  # Medium load
    else:
        return "red"  # High load

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Electricity Substation Dashboard", page_icon="⚡")

st.title("⚡ Electricity Substation Dashboard")
st.write("Real-time monitoring and management of electricity substations")



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


# Fetch data from Supabase
substation_data = fetch_substation_data()

# Create main map
m = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron")

# Add substation polygons
for substation in substation_data:

    try:
        coordinates = json.loads(substation["coordinates"]) if isinstance(substation["coordinates"], str) else substation["coordinates"]
  # Ensure coordinates are properly parsed
        load = parse_load(substation["electricity_load"])  # Convert load to float
        capacity = parse_load(substation["capacity"])  # Convert capacity to float
        if load is None or capacity is None:
            continue  # Skip if values are invalid
        color = get_color(load, capacity)  # Get color based on load percentage

        polygon = folium.Polygon(
            locations=coordinates,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.4,
            weight=2,
            popup=folium.Popup(
                f"""
                <div style='width:250px'>
                    <h4 style='color:{color}; margin-bottom:10px'>{substation['state_name']}</h4>
                    <p><b>Electricity Load:</b> {load} MW</p>
                    <p><b>Capacity:</b> {capacity} MW</p>
                    <p><b>In charge:</b> {substation['employees']['name'] if 'employees' in substation else 'Unknown'}</p>
                    <p><small>Last Updated: {substation['last_updated']}</small></p>
                </div>
                """,
                max_width=300
            )
        )
        polygon.add_to(m)
    except Exception as e:
        st.warning(f"Error rendering substation {substation.get('substation_id', 'Unknown')}: {e}")

Fullscreen().add_to(m)

# Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("📊 Electricity Load Overview")
    level_counts = {"Low (<30%)": 0, "Medium (30%-70%)": 0, "High (>70%)": 0}

    for substation in substation_data:
        load = parse_load(substation["electricity_load"])  # Convert load properly
        capacity = parse_load(substation["capacity"])
        if load is None or capacity is None or capacity == 0:
            continue  # Skip if values are invalid
        percentage = (load / capacity) * 100
        if percentage < 30:
            level_counts["Low (<30%)"] += 1
        elif percentage < 70:
            level_counts["Medium (30%-70%)"] += 1
        else:
            level_counts["High (>70%)"] += 1

    cols = st.columns(3)
    colors = ["green", "yellow", "red"]

    for i, (level, count) in enumerate(level_counts.items()):
        with cols[i]:
            st.markdown(f"""
                <div style='padding:10px; background-color:rgba(150,150,150,0.1);border-radius:5px;margin:5px 0;'>
                    <div style='font-size:14px;color:gray;'>{level}</div>
                    <div style='font-size:24px;font-weight:bold;color:{colors[i]}'>{count}</div>
                </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center'>
        <small>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}.</small>
    </div>
    """,
    unsafe_allow_html=True
)
