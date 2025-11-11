import streamlit as st
import requests

# --- CONFIG ---
BASE_URL = "https://helpdesk.qiscus.com"
TOKEN = "Bearer KVlBEPYRBj5mTQsIWQZQhw829AETUT"
OMNI_BASE_URL = "https://multichannel-api.qiscus.com"
OMNI_APP_CODE = "lclmq-sngxucojgvuq98p"
OMNI_SECRET_KEY = "904eb6f8687c2aadc8c2864c01a0e2bf"

# --- FUNCTIONS ---
def upload_image(uploaded_image):
    st.image(uploaded_image, use_container_width=True)
    url = f"{BASE_URL}/api/v1/ticket/attachments"
    headers = {
        "Authorization": TOKEN
    }
    files = {
        "file": (uploaded_image.name, uploaded_image, uploaded_image.type)
    }

    return requests.post(url, headers=headers, files=files)

def omni_headers():
    return {
        "Content-Type": "application/json",
        "QISCUS-APP-ID": OMNI_APP_CODE,
        "QISCUS-SECRET-KEY": OMNI_SECRET_KEY
    }

def send_ticket_notification(phone_number, ticket):
    url = f"{OMNI_BASE_URL}/api/v3/admin/broadcast/client"
    headers = omni_headers()
    body = {
        "channel_id": 7733,
        "template_name": "japfa_ticket_created",
        "namespace": "27f5f7a6_c452_4f71_aeff_14fb50b67db8",
        "language": "id",
        "phone_number": str(phone_number),
        "variables": [
            ticket.get('requester').get('name'),
            ticket.get('sequential_id'),
            ticket.get('title'),
            ticket.get('summary')
        ]
    }

    print('body: ', body)

    return requests.post(url, headers=headers, json=body)

def get_latest_room(phone_number):
    url = f"{OMNI_BASE_URL}/api/v2/rooms/latest?channel_id=7733&source=wa&user_id={phone_number}"
    headers = omni_headers()

    return requests.get(url, headers=headers)

def send_message_as_bot(phone_number, ticket):
    print("phone_number:", phone_number)
    latest_room = get_latest_room(phone_number).json()
    print("lastest_room:", latest_room)

    url = f"{OMNI_BASE_URL}/{OMNI_APP_CODE}/bot"
    headers = {"QISCUS_SDK_SECRET": OMNI_SECRET_KEY}
    body = {
        "room_id": latest_room.get("data").get("room_id"),
        "sender_email": f"{OMNI_APP_CODE}_admin@qismo.com",
        "type": "text",
        "message": f"""Halo {ticket.get("requester").get("name")},

Terima kasih banyak sudah menghubungi kami. Kami sudah membuat tiket untuk permintaan Anda dengan detail berikut:

🆔 ID Tiket: {ticket.get("sequential_id")}
📌 Judul: {ticket.get("title")}
📝 Ringkasan: {ticket.get("summary")}

Tim kami akan segera menindaklanjuti dan membantu Anda sebaik mungkin.

Semoga harimu menyenangkan!
Salam hangat,
Tim Layanan Pelanggan"""
    }

    return requests.post(url, headers=headers, json=body)

# --- STREAMLIT ---
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
        # You can add logic to store or send the data here

        # Upload image
        attachment = ''
        if uploaded_image is not None:
            uploadResponse = upload_image(uploaded_image)
            if uploadResponse.status_code == 200:
                attachment = uploadResponse.json().get('data').get('data').get('signed_id')

        # Create ticket
        url = f"{BASE_URL}/api/v2/tickets"
        headers = {
            "Content-Type": "application/json",
            "Authorization": TOKEN
        }
        response = requests.post(url, json={
            "division_id": "37",
            "customer_email": f"user-{phone_number}@lclmq-sngxucojgvuq98p.com",
            "customer_name": case_owner_name,
            "title": f"Poultry Case - {case_owner_name}",
            "priority": "medium",
            "summary": problem_description,
            "channel_id": "431",
            "assignee_email": "eka@qiscus.com",
            "form_id": "145",
            "attachments": [
                attachment
            ],
            "custom_fields": [
                {
                    "id": 871, # type of chicken
                    "value": type_of_chicken
                },
                {
                    "id": 872, # body weight
                    "value": f"{body_weight}"
                },
                {
                    "id": 873, # Body Temperature (°C)
                    "value": f"{body_temperature}"
                },
                {
                    "id": 874, # Daily Production Performance
                    "value": daily_production
                },
                {
                    "id": 875, # Age (weeks)
                    "value": f"{age_weeks}"
                },
                {
                    "id": 876, # Symptoms
                    "value": symptoms
                },
                {
                    "id": 877, # Pattern of Spread / Drop
                    "value": pattern_of_spread
                }
            ]
        }, headers=headers)

        if response.status_code == 200:
            st.success("✅ Case submitted successfully!")

            ticket = response.json().get('data')
            # notifResponse = send_ticket_notification(phone_number, ticket)
            notifResponse = send_message_as_bot(phone_number, ticket)
            if notifResponse.status_code != 200:
                print("failed send notif to customer: ", notifResponse.json())
                st.error("❌ failed send notif to customer")
        else:
            print("failed to create ticket: ", response.json())
            st.error("❌ failed to create ticket.")
    else:
        st.error("❌ Please fill in all required fields marked with *.")
