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
        response = supabase.table("crisis_reports").select("*").execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching crisis data: {e}")
        return []

# Fetch news updates from the new "crisis_newsboard" table
def fetch_news_updates():
    try:
        response = supabase.table("crisis_newsboard").select("*, crisis_reports(name, state_name)").order("created_at", desc=True).limit(10).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching news updates: {e}")
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
facility_response = (
    supabase.table("facilities")
    .select("facility_name, facility_type, latitude, longitude, contact_info")
    .execute()
)

facility_data = facility_response.data if facility_response.data else []

for facility in facility_data:
    if "latitude" in facility and "longitude" in facility:
        folium.Marker(
            location=[facility["latitude"], facility["longitude"]],
            popup=f"<b>{facility['facility_name']}</b><br>Type: {facility['facility_type']}<br>Contact: {facility['contact_info']}",
            icon=folium.Icon(color="blue", icon="info-circle", prefix="fa"),
        ).add_to(m)

# Search functionality
location_query = st.text_input("Search for a location (State Name):")
if location_query:
    filtered_crises = [c for c in crisis_data if c["state_name"].lower() == location_query.lower()]
    print(filtered_crises)
    if filtered_crises:
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
    
    st.subheader("📰 Crisis Newsboard")

    news_updates = fetch_news_updates()

    if news_updates:
        for news in news_updates:
            crisis_name = news.get("crisis_reports", {}).get("name", "General Update")
            crisis_state = news.get("crisis_reports", {}).get("state_name", "")
            crisis_info = f" ({crisis_state})" if crisis_state else ""
          
            st.markdown(
                f"""
                <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;">
                    <h4 style="color: #d9534f;">{news['title']} - <span style="font-size: 14px; color: #555;">{crisis_name}{crisis_info}</span></h4>
                    <p style="color: #000">{news['content']}</p>
                    <p style="font-size: 12px; color: #888;"><strong>Posted by:</strong> {news['posted_by']} | <strong>🕒</strong> {news['created_at']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No recent crisis updates available.")
    # st.subheader("📰 Crisis Newsboard")
    # if crisis_data:

    #     if isinstance(crisis_data, list):
    #         for crisis in crisis_data:
    #             try:
    #                 st.markdown(
    #                     rf"""
    #                     <div style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;">
    #                         <h4 style="color: #d9534f;">{crisis.get('name', 'Unknown Crisis')} {crisis.get('state_name', 'Unknown State')}</h4>
    #                         <p><strong>Type:</strong> {crisis.get('crisis_type', 'N/A')} | <strong>Severity:</strong> {crisis.get('severity', 'N/A')}/5</p>
    #                         <p style="color: #5d5d5d;">{crisis.get('news_updates', 'No updates available.')}</p>
    #                     </div>
    #                     """,
    #                     unsafe_allow_html=True
    #                 )
    #             except Exception as e:
    #                 st.error(f"Error rendering crisis info: {e}")
    #     else:
    #         st.error("Crisis data is not in the expected format.")

    # else:
    #     st.write("No crisis updates available.")


st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center'>
        <small>Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M")}.</small>
    </div>
    """,
    unsafe_allow_html=True
)




# # Function to fetch crisis data
# def fetch_crisis_data():
#     try:
#         response = supabase.table("crisis_reports").select("*, employees(name, id)").execute()
#         return response.data if response.data else []
#     except Exception as e:
#         st.error(f"Error fetching crisis data: {e}")
#         return []

# Fetch crisis data
# crisis_data = fetch_crisis_data()

# Sidebar for searching a specific location
search_query = st.sidebar.text_input("🔍 Search by City or State", "")

# # Filter crisis based on search query
# filtered_crises = [crisis for crisis in crisis_data if search_query.lower() in crisis["state_name"].lower()]
