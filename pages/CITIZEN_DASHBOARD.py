import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

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
    
    with st.form(key="complaint_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input("📧 Email", placeholder="Enter your email")
            name = st.text_input("👤 Name", placeholder="Enter your name")
            phone_number = st.text_input("📞 Phone Number", placeholder="Enter your phone number")

        with col2:
            category = st.selectbox("📂 Category", ["Water", "Electricity", "Waste Management", "Others"])
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
        response = supabase.table("customer_complaints").insert(data).execute()
        
        if response.data:
            st.success("✅ Complaint submitted successfully!")
        else:
            st.error(f"❌ Failed to submit complaint.")

### TAB 2: View Complaint Status with Status & Timestamp
with tab2:
    st.subheader("📋 Your Complaints")
    email = st.text_input("📧 Enter your email to view complaints", key="status_email")

    if st.button("🔍 Fetch Complaints"):
        if email:
            response = supabase.table("customer_complaints").select("category, description, status, created_at").eq("email", email).execute()
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
    response = supabase.table("notifications").select("notification, created_at").order("created_at", desc=True).execute()
    
    if response.data:
        st.write("Latest Notifications:")
        st.table(response.data)
    else:
        st.info("ℹ️ No notifications available at the moment.")

### TAB 4: Welfare Schemes
with tab4:
    st.subheader("📜 Welfare Scheme Eligibility & Registration")

    # Fetch available welfare schemes
    def fetch_schemes():
        response = supabase.table("welfare_schemes").select("*").execute()
        return response.data if response.data else []

    schemes = fetch_schemes()

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
        eligibility_criteria = selected_scheme["eligibility_criteria"].lower()

        is_eligible = (
            ("age" in eligibility_criteria and str(age) in eligibility_criteria) or
            ("income" in eligibility_criteria and str(income) in eligibility_criteria) or
            ("employment" in eligibility_criteria and employment_status.lower() in eligibility_criteria)
        )

        if is_eligible:
            st.success(f"🎉 Congratulations! You are eligible for {selected_scheme_name}!")
            if st.button("📩 Apply Now"):
                supabase.table("citizen_applications").insert({
                    "name": citizen_name,
                    "age": int(age),
                    "income": int(income),
                    "employment_status": employment_status,
                    "crisis_type": crisis_type,
                    "scheme_id": scheme_options[selected_scheme_name]
                }).execute()
                st.success("✅ Application Submitted Successfully!")
        else:
            st.error(f"❌ Sorry, you are not eligible for {selected_scheme_name}.")
