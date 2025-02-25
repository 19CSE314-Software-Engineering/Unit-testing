import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MeasureControl, MousePosition, MiniMap, Fullscreen, Draw
import pandas as pd
from datetime import datetime

# Initialize session state
if 'selected_state' not in st.session_state:
    st.session_state.selected_state = None

# Australian States Data with GeoJSON coordinates

states_data = {
    "New South Wales": {
        "status": "Operational",
        "description": "State administrative center",
        "last_updated": "2024-02-13",
        "capacity": 8166000,
        "water_level": "78%",
        "in_charge_name": "John Smith",
        "in_charge_id": "NSW001",
        "coordinates": [
            [-37.5, 141.0], [-33.98, 141.0], [-29.0, 141.0],
            [-29.0, 153.0], [-37.5, 150.0], [-37.5, 141.0]
        ]
    },
    "Victoria": {
        "status": "Open",
        "description": "State infrastructure hub",
        "last_updated": "2024-02-13",
        "capacity": 6681000,
        "water_level": "85%",
        "in_charge_name": "Emily Johnson",
        "in_charge_id": "VIC002",
        "coordinates": [
            [-39.2, 141.0], [-34.0, 141.0], [-34.0, 150.0],
            [-39.2, 146.0], [-39.2, 141.0]
        ]
    },
    "Queensland": {
        "status": "Operational",
        "description": "Northern state facilities",
        "last_updated": "2024-02-13",
        "capacity": 5265000,
        "water_level": "65%",
        "in_charge_name": "Michael Brown",
        "in_charge_id": "QLD003",
        "coordinates": [
            [-29.0, 141.0], [-10.0, 141.0], [-10.0, 154.0],
            [-29.0, 154.0], [-29.0, 141.0]
        ]
    },
    "Western Australia": {
        "status": "Under Maintenance",
        "description": "Western state infrastructure",
        "last_updated": "2024-02-13",
        "capacity": 2667000,
        "water_level": "50%",
        "in_charge_name": "Sarah Davis",
        "in_charge_id": "WA004",
        "coordinates": [
            [-35.0, 129.0], [-14.0, 129.0], [-14.0, 118.0],
            [-35.0, 115.0], [-35.0, 129.0]
        ]
    },
    "South Australia": {
        "status": "Open",
        "description": "Southern state facilities",
        "last_updated": "2024-02-13",
        "capacity": 1771000,
        "water_level": "92%",
        "in_charge_name": "David Wilson",
        "in_charge_id": "SA005",
        "coordinates": [
            [-38.0, 129.0], [-26.0, 129.0], [-26.0, 141.0],
            [-38.0, 141.0], [-38.0, 129.0]
        ]
    },
    "Tasmania": {
        "status": "Operational",
        "description": "Island state infrastructure",
        "last_updated": "2024-02-13",
        "capacity": 571000,
        "water_level": "80%",
        "in_charge_name": "Emma White",
        "in_charge_id": "TAS006",
        "coordinates": [
            [-43.0, 145.0], [-40.0, 145.0], [-40.0, 148.5],
            [-43.0, 148.5], [-43.0, 145.0]
        ]
    },
    "Northern Territory": {
        "status": "Open",
        "description": "Northern territory facilities",
        "last_updated": "2024-02-13",
        "capacity": 247000,
        "water_level": "70%",
        "in_charge_name": "Liam Taylor",
        "in_charge_id": "NT007",
        "coordinates": [
            [-26.0, 129.0], [-11.0, 129.0], [-11.0, 138.0],
            [-26.0, 138.0], [-26.0, 129.0]
        ]
    }
}




# Color based on status
def get_color(status):
    return {
        "Operational": "green",
        "Closed": "red",
        "Open": "blue",
        "Under Maintenance": "orange"
    }.get(status, "gray")

# Streamlit UI Configuration
st.set_page_config(layout="wide", page_title="Australian Infrastructure Dashboard", page_icon="🦘")

# Custom CSS
st.markdown("""
    <style>
        .stButton>button {
            width: 100%;
        }
        .status-card {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# Dashboard Header
col1, col2, col3 = st.columns([3, 6, 3])
with col2:
    st.title("🦘 Australian Infrastructure Dashboard")
    st.write("Real-time monitoring and management of state facilities")

# Sidebar Configuration
st.sidebar.title("Dashboard Controls")

# Map Settings
st.sidebar.subheader("Map Settings")
map_style = st.sidebar.selectbox(
    "Map Style",
    ["CartoDB positron", "CartoDB dark_matter", "OpenStreetMap", "Stamen Terrain"]
)

# Filters
st.sidebar.subheader("Filters")
status_filter = st.sidebar.multiselect(
    "Filter by Status",
    ["Operational", "Closed", "Open", "Under Maintenance"],
    default=["Operational", "Closed", "Open", "Under Maintenance"]
)

# Create main map
m = folium.Map(
    location=[-25.2744, 133.7751],  # Center of Australia
    zoom_start=4,
    tiles=map_style
)

# Add state polygons
for state_name, state_data in states_data.items():
    if state_data["status"] in status_filter:
        # Create polygon for state
        polygon = folium.Polygon(
            locations=state_data["coordinates"],
            color=get_color(state_data["status"]),
            fill=True,
            fill_color=get_color(state_data["status"]),
            fill_opacity=0.4,
            weight=2,
            popup=folium.Popup(
                f"""
                <div style="width:250px">
                    <h4 style="color:{get_color(state_data['status'])}; margin-bottom:10px">{state_name}</h4>
                    <p><b>Status:</b> {state_data['status']}</p>
                    <p><b>Capacity:</b> {state_data['capacity']:,} </p>
                    <p><b>Water level:</b> {state_data['water_level']}</p>

                    <p><b>In charge:</b> {state_data['in_charge_name']}</p>

                    <p><small>Last Updated: {state_data['last_updated']}</small></p>
                </div>
                """,
                max_width=300
            )
        )
        polygon.add_to(m)

# Add Fullscreen control
Fullscreen().add_to(m)

# Add custom legend
legend_html = '''
<div style="position: fixed; 
     bottom: 50px; right: 50px; width: 200px;
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white;
     padding: 10px;
     border-radius: 5px;
     ">
     <h4 style="margin-bottom:10px"> State Status </h4>
     <div style="margin-bottom:5px">
         <i class="fa fa-square fa-1x" style="color:green"></i> Operational
     </div>
     <div style="margin-bottom:5px">
         <i class="fa fa-square fa-1x" style="color:red"></i> Closed
     </div>
     <div style="margin-bottom:5px">
         <i class="fa fa-square fa-1x" style="color:blue"></i> Open
     </div>
     <div style="margin-bottom:5px">
         <i class="fa fa-square fa-1x" style="color:orange"></i> Under Maintenance
     </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Create dashboard layout
col1, col2 = st.columns([2, 1])

# Map Column
with col1:
    st_folium(m, width=800, height=600)

# Information Panel Column
with col2:
    st.subheader("📊 Status Overview")
    
    # Status counts
    status_counts = {}
    for state_data in states_data.values():
        status_counts[state_data['status']] = status_counts.get(state_data['status'], 0) + 1
    
    # Display status metrics
    cols = st.columns(2)
    for i, (status, count) in enumerate(status_counts.items()):
        with cols[i % 2]:
            st.markdown(f"""
                <div style="padding:10px; background-color:rgba({','.join(map(str, [150,150,150,0.1]))});border-radius:5px;margin:5px 0;">
                    <div style="font-size:14px;color:gray;">{status}</div>
                    <div style="font-size:24px;font-weight:bold;color:{get_color(status)}">{count}</div>
                </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <small>Last updated: {}. For emergency support, call 000.</small>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M")),
    unsafe_allow_html=True
)