import streamlit as st

st.title("🐔 Poultry Case Submission Form")

# Section: Case Owner Details
st.header("📋 Case Owner Details")

case_owner_name = st.text_input("Case Owner Name*", "")
farm_location = st.selectbox("Farm Location*", ["North", "South", "East", "West", "Central"])
country_code = st.selectbox("Country Code*", ["+62", "+60", "+65"])
phone_number = st.number_input("Phone Number*", min_value=0, format="%d")

# Section: Poultry Case Information
st.header("🐓 Poultry Case Information")

problem_description = st.text_area("Problem Description*", "")
type_of_chicken = st.selectbox("Type of Chicken*", ["Broiler", "Layer", "Free-range", "Other"])
body_weight = st.number_input("Body Weight (kg)", min_value=0.0, format="%.2f")
body_temperature = st.number_input("Body Temperature (°C)", min_value=0.0, format="%.1f")
daily_production = st.text_area("Daily Production Performance", "")
age_weeks = st.number_input("Age (Weeks)", min_value=0, format="%d")
symptoms = st.text_area("Symptoms*", "")
pattern_of_spread = st.text_area("Pattern of Spread / Drop", "")
uploaded_image = st.file_uploader("Upload Image")

# Submit button
if st.button("Submit Case"):
    required_fields = [case_owner_name, farm_location, country_code, phone_number,
                       problem_description, type_of_chicken, symptoms]
    if all(required_fields):
        st.success("✅ Case submitted successfully!")
        # You can add logic to store or send the data here
    else:
        st.error("❌ Please fill in all required fields marked with *.")
