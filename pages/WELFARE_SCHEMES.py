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

st.set_page_config(page_title="Welfare Schemes", page_icon="💰", layout="wide")
st.title("📜 Welfare Scheme Eligibility & Registration")

# Fetch available welfare schemes
def fetch_schemes():
    response = supabase.table("welfare_schemes").select("*").execute()
    return response.data if response.data else []

schemes = fetch_schemes()

# Display schemes and eligibility criteria
st.subheader("📋 Available Welfare Schemes")
for scheme in schemes:
    st.markdown(f"""
    <div style="border: 1px solid #ddd; padding: 10px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;">
        <h4 style="color: #2c3e50;">{scheme['scheme_name']}</h4>
        <p style="color: #2c3e50;"><strong>📖 Description:</strong> {scheme['description']}</p>
        <p style="color: #2c3e50;"><strong>✅ Eligibility:</strong> {scheme['eligibility_criteria']}</p>
        <p style="color: #2c3e50;"><strong>🎁 Benefits:</strong> {scheme['benefits']}</p>
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
