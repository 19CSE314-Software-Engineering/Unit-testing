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

# Function to fetch waste collection site details from the database
def fetch_waste_data():
    try:
        response = supabase.table("waste_sites").select("*, employees(name, id)").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching waste site data: {e}")
        return []

# Function to determine color based on waste level
def get_color(waste_level):
    if waste_level is None:
        return "gray"  # Default color if conversion fails
    if waste_level < 30:
        return "green"  # Low waste level
    elif waste_level < 70:
        return "yellow"  # Medium waste level
    else:
        return "red"  # High waste level (Needs immediate attention)

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Waste Management Dashboard", page_icon="🗑️")

st.title("🗑️ Waste Management Dashboard")
st.write("Real-time monitoring and management of waste collection sites.")

# Fetch data from Supabase
waste_data = fetch_waste_data()

# Create main map
m = folium.Map(location=[-25.2744, 133.7751], zoom_start=4, tiles="CartoDB positron")

# Add waste site markers
for site in waste_data:
    try:
        coordinates = site["coordinates"]  # Directly use the list
        waste_level = site["waste_level"]  # Waste level percentage
        if waste_level is None:
            continue  # Skip if waste level is invalid
        color = get_color(waste_level)  # Get color based on waste level

        folium.Marker(
            location=coordinates,
            icon=folium.Icon(color=color, icon="trash"),
            popup=folium.Popup(
                f"""
                <div style='width:250px'>
                    <h4 style='color:{color}; margin-bottom:10px'>{site['location_name']}</h4>
                    <p><b>Waste Level:</b> {waste_level}%</p>
                    <p><b>Capacity:</b> {site['capacity']:,} kg</p>
                    <p><b>In charge:</b> {site['employees']['name'] if 'employees' in site else 'Unknown'}</p>
                    <p><small>Last Updated: {site['last_updated']}</small></p>
                </div>
                """,
                max_width=300
            )
        ).add_to(m)
    except Exception as e:
        st.warning(f"Error rendering waste site {site.get('site_id', 'Unknown')}: {e}")

Fullscreen().add_to(m)

# Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("📊 Waste Level Overview")
    level_counts = {"Low (<30%)": 0, "Medium (30%-70%)": 0, "High (>70%)": 0}

    for site in waste_data:
        waste_level = site["waste_level"]
        if waste_level is None:
            continue  # Skip if waste level is invalid
        if waste_level < 30:
            level_counts["Low (<30%)"] += 1
        elif waste_level < 70:
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
