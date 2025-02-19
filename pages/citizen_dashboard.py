import streamlit as st
import supabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase connection setup using .env file
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Citizen Dashboard", page_icon="🏛", layout="wide")

# Welcome Text
st.title("🏛 Citizen Dashboard")
st.write("Welcome to the Citizen Dashboard! Here you can submit complaints, view their status, and check notifications.")

# Tabs for Navigation
tab1, tab2, tab3 = st.tabs(["📝 Create Complaint", "📋 View Complaints", "🔔 Notifications"])

### TAB 1: Create Complaint Form
with tab1:
    st.subheader("📝 Submit a Complaint")
    st.write("If you have any complaints, please fill out the form below.")
    st.write("Please provide the necessary details below.")

    # Form inputs with styling
    with st.form(key="complaint_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("📧 Email", placeholder="Enter your email")
            name = st.text_input("👤 Name", placeholder="Enter your name")
            phone_number = st.text_input("📞 Phone Number", placeholder="Enter your phone number")

        with col2:
            category = st.selectbox("📂 Category", ["Service", "Infrastructure", "Billing", "Others"])
            description = st.text_area("📝 Complaint Description", placeholder="Describe your issue", height=150)

        submit_button = st.form_submit_button("🚀 Submit Complaint")
    
    if submit_button:
        # Insert into Supabase table
        data = {
            "email": email,
            "name": name,
            "phone_number": phone_number,
            "category": category,
            "description": description
        }
        response = client.table("customer_complaints").insert(data).execute()
        
        if response.data:
            st.success("✅ Complaint submitted successfully!")
        else:
            st.error(f"❌ Failed to submit complaint: {response.error_message}")

### TAB 2: View Complaint Status with Status & Timestamp
with tab2:
    st.subheader("📋 Your Complaints")
    st.write("View the status of your previously submitted complaints.")
    email = st.text_input("📧 Enter your email to view complaints", key="status_email")

    if st.button("🔍 Fetch Complaints"):
        if email:
            # Fetch complaints from Supabase
            response = client.table("customer_complaints").select("category, description, status, created_at").eq("email", email).execute()
            
            if response.data:
                st.write("Your Complaints:")
                st.table(response.data)
            else:
                st.warning("⚠️ No complaints found for this email.")
        else:
            st.error("❌ Please enter an email.")

### TAB 3: View Notifications
with tab3:
    st.subheader("🔔 Notifications")
    
    # Fetch notifications from Supabase
    response = client.table("notifications").select("notification, created_at").execute()
    
    if response.data:
        st.write("Latest Notifications:")
        st.table(response.data)
    else:
        st.info("ℹ️ No notifications available at the moment.")
