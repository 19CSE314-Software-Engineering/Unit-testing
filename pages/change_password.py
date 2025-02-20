import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Change Password", page_icon="🔑")

st.title("🔑 Change Password")

# Password Change Form
email = st.text_input("📧 Email", key="email")
old_password = st.text_input("🔒 Old Password", type="password", key="old_password")
new_password = st.text_input("🆕 New Password", type="password", key="new_password")
confirm_password = st.text_input("🔄 Confirm New Password", type="password", key="confirm_password")

# Submit Button
if st.button("Update Password"):
    if not email or not old_password or not new_password or not confirm_password:
        st.warning("Please fill in all fields.")
    elif new_password != confirm_password:
        st.error("New Password and Confirm Password do not match.")
    else:
        try:
            # Authenticate User with Old Password
            response = supabase.auth.sign_in_with_password({"email": email, "password": old_password})

            if response and response.user:
                # Update Password
                supabase.auth.update_user({"password": new_password})
                st.success("✅ Password updated successfully! Please login again.")
            else:
                st.error("❌ Incorrect old password. Try again.")

        except Exception as e:
            st.error(f"⚠️ Error updating password: {str(e)}")
