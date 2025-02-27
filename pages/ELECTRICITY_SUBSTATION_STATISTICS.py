
import streamlit as st
import pandas as pd  # For data tables (optional but often useful)

st.title("Electricity Board Management (This is a Static Page)")

# Navigation Buttons
st.divider()
st.write("🔗 **Navigation**")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    if st.button("📊 View Substation Statistics"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_STATISTICS.py")

with col_nav2:
    if st.button("🗺 View Substation Mapping"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_MAPPING.py")

with col_nav3:
    if st.button("🗺 View Substation Updation"):
        st.switch_page("pages/ELECTRICITY_SUBSTATION_UPDATION.py")

st.divider()




st.header("Current Power Status")

# Example data (REPLACE with your actual data source)
power_status = {
    "Grid Status": "Normal",  # Or "Outage," "Warning," etc.
    "Current Load": "75 MW",
    "Frequency": "50.1 Hz",
}

for key, value in power_status.items():
    st.write(f"{key}: {value}")

# Example of conditional display based on grid status
if power_status["Grid Status"] == "Outage":
    st.error("Power outage detected!")
elif power_status["Grid Status"] == "Warning":
    st.warning("Potential power issues.")


st.header("Energy Consumption")

# Example data (REPLACE with your data - could be from a CSV, database, etc.)
consumption_data = {
    "Residential": 150000,  # kWh
    "Commercial": 80000,
    "Industrial": 220000,
    "Agricultural": 50000,
}


# Display as a bar chart
st.bar_chart(consumption_data)


# Display as a table (using pandas - install it: pip install pandas)
consumption_df = pd.DataFrame(list(consumption_data.items()), columns=['Sector', 'Consumption (kWh)'])
st.dataframe(consumption_df) # or st.table(consumption_df) for a static table


st.header("Tariff Information")

# Example tariff data (REPLACE with your actual data)
tariff_data = {
    "Residential": "₹7.50 per kWh",
    "Commercial": "₹9.00 per kWh",
    "Industrial": "₹6.00 per kWh",
}

st.write("Current Tariff Rates:")
for sector, rate in tariff_data.items():
    st.write(f"- {sector}: {rate}")


st.header("Outage Reporting")

with st.form("outage_report"):  # Using a form for better organization
    customer_id = st.text_input("Customer ID")
    location = st.text_area("Location of Outage")
    description = st.text_area("Description of Issue (Optional)")
    submit_button = st.form_submit_button("Report Outage")

    if submit_button:
        # Here you would add the logic to handle the outage report (e.g., store in database, send email)
        st.success("Outage report submitted successfully!")
        # In a real application, you'd want to validate the customer ID, etc.


st.header("Energy Saving Tips")

st.write("- Switch off lights when not in use.")
st.write("- Use energy-efficient appliances.")
st.write("- Unplug devices when not in use.")
st.write("- Optimize heating and cooling systems.")

# Example of a slider for setting a target consumption (replace with your logic)
target_consumption = st.slider("Set Target Monthly Consumption (kWh)", 0, 5000, 2500)
st.write(f"Target consumption: {target_consumption} kWh")


# Example of displaying an image (replace with your image path)
# st.image("path/to/your/electricity_image.jpg", caption="Powering the Future", use_column_width=True)


# Add more sections as per your electricity board application's requirements.