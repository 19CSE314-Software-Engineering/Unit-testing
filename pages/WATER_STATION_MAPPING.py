import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch tank details from the database
def fetch_tank_data():
    try:
        response = supabase.table("tank_details").select("*, employees(name, id)").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching tank data: {e}")
        return []

# Function to parse water level
def parse_water_level(water_level):
    if isinstance(water_level, str) and water_level.endswith("%"):
        return float(water_level[:-1])  # Remove '%' and convert to float
    elif isinstance(water_level, (int, float)):  # If already a number
        return float(water_level)
    return None  # Invalid data

# Function to determine color based on water level
def get_color(water_level):
    if water_level is None:
        return "gray"  # Default color if conversion fails
    if water_level < 30:
        return "red"  # Low water level
    elif water_level < 70:
        return "yellow"  # Medium water level
    else:
        return "green"  # High water level

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Australian Infrastructure Dashboard", page_icon="🦘")

st.title("🦘 Australian Infrastructure Dashboard")
st.write("Real-time monitoring and management of tank facilities")

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


# Fetch data from Supabase
tank_data = fetch_tank_data()

# Create main map
m = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron")

# Add tank polygons
for tank in tank_data:
    try:
        coordinates = tank["coordinates"]  # Directly use the list
        water_level = parse_water_level(tank["water_level"])  # Convert water level properly
        if water_level is None:
            continue  # Skip if water level is invalid
        color = get_color(water_level)  # Get color based on water level

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
                    <h4 style='color:{color}; margin-bottom:10px'>{tank['state_name']}</h4>
                    <p><b>Water Level:</b> {water_level}%</p>
                    <p><b>Capacity:</b> {tank['capacity']:,}</p>
                    <p><b>In charge:</b> {tank['employees']['name'] if 'employees' in tank else 'Unknown'}</p>
                    <p><small>Last Updated: {tank['last_updated']}</small></p>
                </div>
                """,
                max_width=300
            )
        )
        polygon.add_to(m)
    except Exception as e:
        st.warning(f"Error rendering tank {tank.get('tank_id', 'Unknown')}: {e}")

Fullscreen().add_to(m)

# Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("📊 Water Level Overview")
    level_counts = {"Low (<30%)": 0, "Medium (30%-70%)": 0, "High (>70%)": 0}

    for tank in tank_data:
        water_level = parse_water_level(tank["water_level"])  # Convert water level properly
        if water_level is None:
            continue  # Skip if water level is invalid
        if water_level < 30:
            level_counts["Low (<30%)"] += 1
        elif water_level < 70:
            level_counts["Medium (30%-70%)"] += 1
        else:
            level_counts["High (>70%)"] += 1

    cols = st.columns(3)
    colors = ["red", "yellow", "green"]

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
