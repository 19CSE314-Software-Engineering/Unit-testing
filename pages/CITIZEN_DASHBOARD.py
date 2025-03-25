# CITIZEN_DASHBOARD.py
import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv
from utils import fetch_welfare_schemes, check_eligibility, apply_for_scheme, submit_complaint, fetch_complaints_by_email, fetch_notifications

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Citizen Dashboard", page_icon="🏛", layout="wide")

# Welcome Text
st.title("🏛 Citizen Dashboard")
st.write("Welcome to the Citizen Dashboard! Here you can submit complaints, view their status, and check notifications.")

# Tabs for Navigation
tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Complaint", "📋 View Complaints", "🔔 Notifications", "💰 Welfare Schemes"])

### TAB 1: Create Complaint Form
with tab1:
    st.subheader("📝 Submit a Complaint")
    st.write("If you have any complaints, please fill out the form below.")
    
    # Fetch distinct department names from department table
    response = supabase.table("department").select("dept_name").execute()
    if response.data:
        departments = list(set([dept["dept_name"] for dept in response.data if "dept_name" in dept]))
    else:
        departments = ["General"]
    
    with st.form(key="complaint_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("📧 Email", placeholder="Enter your email")
            name = st.text_input("👤 Name", placeholder="Enter your name")
            phone_number = st.text_input("📞 Phone Number", placeholder="Enter your phone number")

        with col2:
            category = st.selectbox("📂 Department", departments)
            description = st.text_area("📝 Complaint Description", placeholder="Describe your issue", height=150)

        submit_button = st.form_submit_button("🚀 Submit Complaint")
    
    if submit_button:
        success, message = submit_complaint(
            supabase=supabase,
            email=email,
            name=name,
            phone_number=phone_number,
            category=category,
            description=description
        )
        if success:
            st.success("✅ " + message)
        else:
            st.error("❌ " + message)

### TAB 2: View Complaint Status with Status & Timestamp
with tab2:
    st.subheader("📋 Your Complaints")
    email = st.text_input("📧 Enter your email to view complaints", key="status_email")

    if st.button("🔍 Fetch Complaints"):
        if email:
            complaints = fetch_complaints_by_email(supabase, email)
            if complaints:
                st.write("Your Complaints:")
                st.table(complaints)
            else:
                st.warning("⚠️ No complaints found for this email.")
        else:
            st.error("❌ Please enter an email.")

### TAB 3: View Notifications
with tab3:
    st.subheader("🔔 Notifications")
    notifications = fetch_notifications(supabase)
    
    if notifications:
        st.write("Latest Notifications:")
        st.table(notifications)
    else:
        st.info("ℹ️ No notifications available at the moment.")

### TAB 4: Welfare Schemes
with tab4:
    st.subheader("📜 Welfare Scheme Eligibility & Registration")

    # Fetch available welfare schemes
    schemes = fetch_welfare_schemes(supabase)

    st.subheader("📋 Available Welfare Schemes")
    for scheme in schemes:
        scheme_name = scheme["scheme_name"].encode("utf-8", "ignore").decode("utf-8")
        description = scheme["description"].encode("utf-8", "ignore").decode("utf-8")
        eligibility = scheme["eligibility_criteria"].encode("utf-8", "ignore").decode("utf-8")
        benefits = scheme["benefits"].encode("utf-8", "ignore").decode("utf-8")

        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;">
            <h4 style="color: #2c3e50;">{scheme_name}</h4>
            <p><strong>📖 Description:</strong> {description}</p>
            <p><strong>✅ Eligibility:</strong> {eligibility}</p>
            <p><strong>🎁 Benefits:</strong> {benefits}</p>
        </div>
        """, unsafe_allow_html=True)

    # Citizen Eligibility Check & Registration
    st.subheader("📝 Check Eligibility & Apply for a Scheme")
    citizen_name = st.text_input("👤 Full Name")
    age = st.number_input("🎂 Age", min_value=0, max_value=100, step=1)
    income = st.number_input("💵 Annual Income (in ₹)", min_value=0.0, step=1000.0)
    employment_status = st.selectbox("💼 Employment Status", ["Unemployed", "Employed", "Self-Employed"])
    crisis_type = st.selectbox("Affected Crisis Type", ["Flood", "Earthquake", "Fire", "Pandemic", "Industrial Accident", "Power Outage", "Economic Crisis", "Riot"])

    # Select scheme
    scheme_options = {scheme["scheme_name"]: scheme["scheme_id"] for scheme in schemes}
    selected_scheme_name = st.selectbox("📌 Select a Scheme", list(scheme_options.keys()))

    # Check eligibility
    selected_scheme = next((s for s in schemes if s["scheme_name"] == selected_scheme_name), None)
    if selected_scheme:
        is_eligible = check_eligibility(selected_scheme, age, income, employment_status)

        if is_eligible:
            st.success(f"🎉 Congratulations! You are eligible for {selected_scheme_name}!")
            if st.button("📩 Apply Now"):
                success, message = apply_for_scheme(
                    supabase=supabase,
                    name=citizen_name,
                    age=age,
                    income=income,
                    employment_status=employment_status,
                    crisis_type=crisis_type,
                    scheme_id=scheme_options[selected_scheme_name]
                )
                if success:
                    st.success("✅ " + message)
                else:
                    st.error("❌ " + message)
        else:
            st.error(f"❌ Sorry, you are not eligible for {selected_scheme_name}.")