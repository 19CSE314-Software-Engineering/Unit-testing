# CRISIS_MAP.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, Fullscreen
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
from utils import fetch_crisis_map_data, fetch_recent_news_updates, fetch_facility_data, filter_crises_by_location, count_crises_by_type

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit UI Setup
st.set_page_config(layout="wide", page_title="Crisis Management Dashboard", page_icon="⚠️")

st.title("⚠️ Crisis Management Dashboard")
st.write("Monitor and manage crises in real time.")

# Fetch crisis data
crisis_data = fetch_crisis_map_data(supabase)

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
            <p><b>In charge:</b> {crisis.get('in_charge_id', 'Unknown')}</p>
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

# Fetch Facilities
facility_data = fetch_facility_data(supabase)

for facility in facility_data:
    if "latitude" in facility and "longitude" in facility:
        folium.Marker(
            location=[facility["latitude"], facility["longitude"]],
            popup=f"<b>{facility['facility_name']}</b><br>Type: {facility['facility_type']}<br>Contact: {facility['contact_info']}",
            icon=folium.Icon(color="blue", icon="info-circle", prefix="fa"),
        ).add_to(m)

# Search functionality
location_query = st.text_input("Search for a location (State Name):")
filtered_crises = filter_crises_by_location(crisis_data, location_query)

if location_query and filtered_crises:
    crisis = filtered_crises[0]
    m.location = [crisis["coordinates"][0][1], crisis["coordinates"][0][0]]
    m.zoom_start = 10
    st.success(f"Showing crises for {location_query.title()}")

    for i in filtered_crises:
        st.markdown(f"""<h4 style="color: #d9534f;">{i["name"]}</h4>
                    """, unsafe_allow_html=True)
        st.write("Type:", i["crisis_type"])
        st.write("Description:", i["description"])
        st.write("Contact:", i["contact_info"])
elif location_query:
    st.warning("No crisis found for this location.")

# Dashboard Layout
col1, col2 = st.columns([2, 1])

with col1:
    st_folium(m, width=800, height=600)

with col2:
    st.subheader("📊 Crisis Overview")
    crisis_counts = count_crises_by_type(crisis_data)
    
    # Completely redesigned crisis count cards
    st.markdown("""
        <style>
        .crisis-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .crisis-card {
            flex: 1;
            min-width: 80px;
            background: rgba(40, 40, 40, 0.8);
            border-radius: 8px;
            padding: 12px 8px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 90px;
        }
        .crisis-type {
            font-size: 14px;
            color: #DDDDDD;
            margin-bottom: 8px;
        }
        .crisis-count {
            font-size: 28px;
            font-weight: bold;
        }
        </style>
        
        <div class="crisis-grid">
    """, unsafe_allow_html=True)
    
    colors = {"Fire": "#FF5252", "Flood": "#4B9BFF", "Earthquake": "#FFB74D", "Power Outage": "#9E9E9E", "Other": "#CE93D8"}
    
    for crisis_type, count in crisis_counts.items():
        st.markdown(f"""
            <div class="crisis-card">
                <div class="crisis-type">{crisis_type}</div>
                <div class="crisis-count" style="color: {colors[crisis_type]};">{count}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("📰 Crisis Newsboard")

    # Improved styling for the newsboard
    st.markdown("""
        <style>
        .news-container {
            margin-top: 10px;
        }
        .news-card {
            background: rgba(40, 40, 40, 0.8);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .news-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .news-title {
            color: #FF5252;
            font-size: 16px;
            font-weight: bold;
            margin: 0;
        }
        .news-crisis-info {
            color: #BBBBBB;
            font-size: 13px;
            margin-top: 3px;
        }
        .news-content {
            color: #DDDDDD;
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        .news-footer {
            color: #999999;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
        }
        </style>
        
        <div class="news-container">
    """, unsafe_allow_html=True)

    news_updates = fetch_recent_news_updates(supabase)

    if news_updates:
        for news in news_updates:
            crisis_name = news.get("crisis_reports", {}).get("name", "General Update")
            crisis_state = news.get("crisis_reports", {}).get("state_name", "")
            crisis_info = f" ({crisis_state})" if crisis_state else ""
          
            st.markdown(
                f"""
                <div class="news-card">
                    <div class="news-header">
                        <div>
                            <div class="news-title">{news['title']}</div>
                            <div class="news-crisis-info">{crisis_name}{crisis_info}</div>
                        </div>
                    </div>
                    <div class="news-content">{news['content']}</div>
                    <div class="news-footer">
                        <span><strong>Posted by:</strong> {news['posted_by']}</span>
                        <span>🕒 {news['created_at']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No recent crisis updates available.")

st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center'>
        <small>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}.</small>
    </div>
    """,
    unsafe_allow_html=True
)