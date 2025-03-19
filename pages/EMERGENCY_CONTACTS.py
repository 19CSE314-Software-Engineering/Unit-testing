import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from utils import add_logout_button 


# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to fetch emergency contacts for a city
def fetch_emergency_contacts(city_name):
    try:
        response = supabase.table("emergency_contacts").select("*, employees(name)").eq("city_name", city_name).execute()
        if response.data:
            return response.data
        return []
    except Exception as e:
        st.error(f"Error fetching contacts: {e}")
        return []

# Streamlit UI Setup
st.set_page_config(page_title="Emergency Contacts", layout="wide")
st.title("🚨 Emergency Contact Directory")
st.write("Find emergency contacts for different services in your city.")

# Search bar for city
city_name = st.text_input("Enter your city name:", "")

if city_name:
    contacts = fetch_emergency_contacts(city_name)
    if contacts:
        st.subheader(f"Emergency Contacts for {city_name}")
        for contact in contacts:
            with st.expander(f"{contact['service_type']} - {contact['contact_number']}"):
                st.write(f"**Status:** {contact['status']}")
                st.write(f"**In-Charge:** {contact['employees']['name'] if 'employees' in contact else 'Not Assigned'}")
    else:
        st.warning("No emergency contacts found for this city.")
