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
supabase.postgrest.auth(SUPABASE_KEY)

# Streamlit UI
st.set_page_config(page_title="Citizen & Employee Portal", page_icon="🔐", layout="centered")

st.title("Citizen & Employee Portal")

# Session state initialization
if "user" not in st.session_state:
    st.session_state["user"] = None
    st.session_state["role"] = None
    st.session_state["page"] = "Home"

st.markdown('<div class="navbox">', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Citizen", "Employee Login", "Admin Login"])

with tab1:
    st.subheader("Citizen Login")
    st.write("Click below to continue as a citizen user.")
    st.page_link("pages/CITIZEN_DASHBOARD.py", label="Go to Citizen Dashboard", icon="🏛")

    


with tab2:
    st.subheader("Employee Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login as Employee")
    #logout_button = st.button("Logout")

    stt = st.button("Change Password 🔑")
    
    
    if stt:
        switch_page("change_password") 
    if login_button:
        if email and password:
            try:
                # Step 1: Authenticate user
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})

                if response and response.user:
                    st.session_state["user"] = response.user
                    st.session_state["role"] = "Employee"
                    

                    # Step 2: Fetch employee details (including department)
                    emp_response = (
                        supabase.table("employees")
                        .select("id, name, dept_id, department(dept_name), position_id, positions(position_name)")
                        .eq("email", email)
                        .execute()
                    )

                    if emp_response.data and len(emp_response.data) > 0:
                        employee = emp_response.data[0]
                        department_name = employee["department"]["dept_name"]
                        position_name = employee["positions"]["position_name"]  # Fetch position
                       
                        # Store in session state
                        st.session_state["dept"] = department_name
                        st.session_state["employee_id"] = employee["id"]
                        print(employee)

                        # Step 3: Redirect based on department
                        if department_name.lower() == "water":
                            if position_name.lower() == "admin":
                                st.session_state["role"] = "Water Admin"
                                st.success("Login successful! Redirecting to Water Admin Dashboard...")
                                switch_page("water admin")
                            else:
                                st.success("Login successful! Redirecting to Water Management...")
                                switch_page("water station updation")

                        if department_name.lower() == "electricity":
                            if position_name.lower() == "admin":
                                st.session_state["role"] = "Electricity Admin"
                                st.success("Login successful! Redirecting to Electricity Admin Dashboard...")
                                switch_page("electricity admin")
                            else:
                                st.session_state["employee_id"] = int(employee["id"])  # Ensure employee_id is an integer
                                st.success("Login successful! Redirecting to Electricity Management...")
                                switch_page("electricity substation updation")


                        else:
                            st.success("Login successful! Redirecting to Dashboard...")
                            switch_page("admin dashboard")

                    else:
                        st.error("Employee record not found.")

                else:
                    st.error("Invalid credentials, please try again.")

            except Exception as e:
                st.error(f"Login failed: {str(e)}")

        else:
            st.warning("Please enter email and password.")


with tab3:
    st.subheader("Admin Login")
    admin_email = st.text_input("Admin Email", key="admin_email")
    admin_password = st.text_input("Admin Password", type="password", key="admin_password")
    admin_login_button = st.button("Login as Admin")

    if admin_login_button:
        if admin_email == "admin@gmail.com" and admin_password:
            try:
                response = supabase.auth.sign_in_with_password({"email": admin_email, "password": admin_password})
                if response and response.user:
                    st.session_state["user"] = response.user
                    st.session_state["role"] = "Admin"
                    st.success("Admin login successful!")
                    switch_page("admin dashboard")  # Redirect to Admin Dashboard
                else:
                    st.error("Invalid credentials, please try again.")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
        else:
            st.warning("Please enter a valid Admin email and password.")


st.markdown('</div>', unsafe_allow_html=True)

