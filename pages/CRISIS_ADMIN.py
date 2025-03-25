# CRISIS_ADMIN.py
import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from utils import fetch_crisis_reports, update_crisis_report, delete_crisis_report, post_news_update, fetch_recent_news_updates

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
supabase.postgrest.auth(SUPABASE_KEY)

st.set_page_config(page_title="Crisis Management Admin", page_icon="🚨", layout="wide")
st.title("Crisis Management - Admin Panel")

# Debugging - Print session state
st.write("🔍 **DEBUG INFO:**")
try: 
    st.write("👤 User:", st.session_state.get("user").email)
except:
    st.write("👤 User: None")
    
st.write("🛂 Role:", st.session_state.get("role"))

# Ensure user is logged in as an Employee in the Crisis Management department
if "user" not in st.session_state or st.session_state.get("role") != "Employee":
    st.error("🚫 Unauthorized access! Only Crisis Management employees can access this page.")
    st.stop()

st.success("✅ Access Granted! Modify or resolve crisis reports below.")

# Fetch Crisis Reports Assigned to the Logged-in Employee
employee_id = st.session_state.get("employee_id")
crises = fetch_crisis_reports(supabase, employee_id)

if crises:
    for crisis in crises:
        with st.expander(f"🚨 {crisis['name']} ({crisis['crisis_type']}) - Severity: {crisis['severity']}"):
            st.write(f"**Location:** {crisis['state_name']}")
            st.write(f"**Description:** {crisis['description']}")
            st.write(f"**Contact Info:** {crisis['contact_info']}")

            # Update Crisis Details
            new_severity = st.slider("Update Severity (1-5)", 1, 5, crisis['severity'], key=f"sev_{crisis['crisis_id']}")
            new_description = st.text_area("Update Description", crisis['description'], key=f"desc_{crisis['crisis_id']}")

            if st.button("Update Crisis", key=f"update_{crisis['crisis_id']}"):
                success, message = update_crisis_report(
                    supabase=supabase,
                    crisis_id=crisis['crisis_id'],
                    severity=new_severity,
                    description=new_description
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

            # Delete Crisis
            if st.button("Resolve & Remove Crisis", key=f"delete_{crisis['crisis_id']}"):
                success, message = delete_crisis_report(supabase, crisis['crisis_id'])
                if success:
                    st.warning(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
else:
    st.info("No crisis reports assigned to you.")

# ------------------ ADD NEWSBOARD FEATURE ------------------ #

st.header("📰 Crisis Newsboard - Post an Update")

news_title = st.text_input("News Title", placeholder="Enter a brief title for the update")
news_content = st.text_area("News Content", placeholder="Describe the update in detail")

# Fetch crises for dropdown selection (optional)
crisis_options_response = supabase.table("crisis_reports").select("crisis_id, name").execute()
crisis_options = crisis_options_response.data if crisis_options_response.data else []
crisis_dict = {crisis["name"]: crisis["crisis_id"] for crisis in crisis_options}

selected_crisis_name = st.selectbox("Related Crisis (Optional)", ["None"] + list(crisis_dict.keys()))

if st.button("Post News Update"):
    success, message = post_news_update(
        supabase=supabase,
        title=news_title,
        content=news_content,
        crisis_id=crisis_dict.get(selected_crisis_name, None),
        posted_by=st.session_state.get("user").email if st.session_state.get("user") else None
    )
    if success:
        st.success(message)
        st.rerun()
    else:
        st.warning(message)

# ------------------ DISPLAY EXISTING NEWS UPDATES ------------------ #

st.header("📢 Recent News Updates")

news_data = fetch_recent_news_updates(supabase, limit=10)

if news_data:
    for news in news_data:
        st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 10px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 10px;">
                <h4 style="color: #2c3e50;">📰 {news['title']}</h4>
                <p style=" color: #000;">{news['content']}</p>
                <p style="font-size: 12px; color: #888;"><strong>Posted by:</strong> {news['posted_by']}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("No news updates available.")