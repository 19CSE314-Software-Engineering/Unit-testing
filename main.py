import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from streamlit_extras.switch_page_button import switch_page

# Load environment variables
load_dotenv()

# Supabase credentials (Replace with your Supabase project URL and API Key in .env file)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit UI
st.set_page_config(page_title="Citizen & Employee Portal", page_icon="🔐", layout="centered")

st.title("Citizen & Employee Portal")

# Session state initialization
if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "Home"

# # Centered layout with navigation box
# st.markdown("""
#     <style>
#         .navbox {
#             display: flex;
#             flex-direction: column;
#             align-items: center;
#             justify-content: center;
#             width: 350px;
#             padding: 20px;
#             border: 2px solid #ddd;
#             border-radius: 10px;
#             box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
#             background-color: white;
#             text-align: center;
#         }
#         .stTabs {
#             display: flex;
#             justify-content: center;
#         }
#     </style>
# """, unsafe_allow_html=True)

st.markdown('<div class="navbox">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Citizen", "Employee Login"])

with tab1:
    st.subheader("Citizen Login")
    st.write("Click below to continue as a citizen user.")
    st.page_link("pages/citizen_dashboard.py", label="Go to Citizen Dashboard", icon="🏛")


with tab2:
    st.subheader("Employee Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login as Employee")
    #logout_button = st.button("Logout")
    
    if login_button:
        if email and password:
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if response and response.user:
                    st.session_state["user"] = response.user
                    st.session_state["role"] = "Employee"
                    st.success("Login successful!")
                    switch_page("dashboard")

                else:
                    st.error("Invalid credentials, please try again.")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
        else:
            st.warning("Please enter email and password.")
    
    # if logout_button and st.session_state["user"]:
    #     supabase.auth.sign_out()
    #     st.session_state["user"] = None
    #     st.session_state["role"] = None
    #     st.success("Logged out successfully!")
    #     st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
