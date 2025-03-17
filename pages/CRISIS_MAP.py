import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
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

# Function to fetch crisis data
def fetch_crisis_data():
    try:
        response = supabase.table("crisis_reports").select("*, employees(name)").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching crisis data: {e}")
        return []

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Crisis Management Dashboard", page_icon="⚠️")

st.title("⚠️ Crisis Management Dashboard")
st.write("Monitor and manage crises in real time.")

# Fetch crisis data
crisis_data = fetch_crisis_data()

# Create main map
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")

# Add heatmap data
heat_data = []
for crisis in crisis_data:
    try:
        coordinates = crisis["coordinates"]
        severity = crisis["severity"]
        heat_data.append([coordinates[0][1], coordinates[0][0], severity])

        popup_content = f"""
        <div style='width:250px'>
            <h4 style='color:red; margin-bottom:10px'>{crisis['name']}</h4>
            <p><b>Type:</b> {crisis['crisis_type']}</p>
            <p><b>Severity:</b> {crisis['severity']}</p>
            <p><b>Description:</b> {crisis['description']}</p>
            <p><b>In charge:</b> {crisis.get('employees', {}).get('name', 'Unknown')}</p>
            <p><b>Contact:</b> {crisis['contact_info']}</p>
            <p><small>Last Updated: {crisis['last_updated']}</small></p>
        </div>
        """
        folium.Marker(
            location=[coordinates[0][1], coordinates[0][0]],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color="red", icon="exclamation-triangle", prefix="fa"),
        ).add_to(m)
    except Exception as e:
        st.warning(f"Error rendering crisis {crisis.get('crisis_id', 'Unknown')}: {e}")

# Add heatmap layer
HeatMap(heat_data, radius=15, blur=10, min_opacity=0.5).add_to(m)
Fullscreen().add_to(m)

# Search functionality
location_query = st.text_input("Search for a location (State Name):")
if location_query:
    filtered_crises = [c for c in crisis_data if c["state_name"].lower() == location_query.lower()]
    if filtered_crises:
        crisis = filtered_crises[0]
        m.location = [crisis["coordinates"][0][1], crisis["coordinates"][0][0]]
        m.zoom_start = 10
        st.success(f"Showing crises for {location_query}")
        
        # Display crisis details
        st.subheader(f"Crisis Details for {location_query}")
        for crisis in filtered_crises:
            st.markdown(f"""
                **Name:** {crisis['name']}  
                **Type:** {crisis['crisis_type']}  
                **Severity:** {crisis['severity']}  
                **Description:** {crisis['description']}  
                **In charge:** {crisis.get('employees', {}).get('name', 'Unknown')}  
                **Contact:** {crisis['contact_info']}  
                **Last Updated:** {crisis['last_updated']}  
                ---
            """)
    else:
        st.warning("No crisis found for this location.")

# Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("📊 Crisis Overview")
    crisis_counts = {"Fire": 0, "Flood": 0, "Earthquake": 0, "Power Outage": 0, "Other": 0}
    for crisis in crisis_data:
        crisis_counts[crisis["crisis_type"]] += 1
    
    cols = st.columns(len(crisis_counts))
    colors = ["red", "blue", "orange", "gray", "purple"]
    
    for i, (crisis_type, count) in enumerate(crisis_counts.items()):
        with cols[i]:
            st.markdown(f"""
                <div style='padding:10px; background-color:rgba(150,150,150,0.1);border-radius:5px;margin:5px 0;'>
                    <div style='font-size:14px;color:gray;'>{crisis_type}</div>
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
