import streamlit as st
import os
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service key for admin operations

# Initialize Supabase client with service role key
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

st.set_page_config(page_title="Set Password", page_icon="🔑")
st.title("🔑 Set Your Password")

# User input fields
email = st.text_input("Enter your registered email")
password = st.text_input("Enter a new password", type="password")

if st.button("Set Password"):
    if email.strip() and password.strip():
        try:
            # **Step 1: Fetch the user ID by email**
            user_query = supabase.auth.admin.list_users()
            user_id = None
            for user in user_query.users:
                if user.email == email:
                    user_id = user.id
                    break
            
            if user_id is None:
                st.error("User not found! Please check the email.")
            else:
                # **Step 2: Update the password using user ID**
                supabase.auth.admin.update_user_by_id(user_id, {"password": password})
                st.success("Password set successfully! You can now log in.")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Both email and password are required!")
