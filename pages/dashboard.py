import streamlit as st
import os
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Admin Privileges

# Supabase admin client
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠", layout="wide")
st.title("🛠 Admin Dashboard")
st.write("Invite users to the platform.")

# User Input Fields
name=st.text_input("Enter User Name")
email = st.text_input("Enter User Email")
role = st.selectbox("Select Role", ["Normal User", "Admin", "Convenor", "SysAdmin"])

if st.button("Send Invite"):
    if email.strip():  # Validate email
        # try:
            # Send invite email
            response = supabase_admin.auth.admin.invite_user_by_email(email)
            st.success(f"Invitation sent to {email}!")

            # Store user role in the Roles table
            role_data = {"name": name, "role": role, "email": email}  # Name will be set later
            supabase_admin.table("Roles").insert(role_data).execute()

        # except Exception as e:
        #     st.error(f"Error: {str(e)}")
    else:
        st.error("Email cannot be empty.")
