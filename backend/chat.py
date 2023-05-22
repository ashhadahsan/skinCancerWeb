import requests
import streamlit as st
import time

# Define the FastAPI server URL
server_url = "http://localhost:8000"
# if "sender" not in st.session_state:
#     st.session_state["sender"] = None
# if "recipient" not in st.session_state:
#     st.session_state["recipient"] = None
# Streamlit app layout
st.title("Chat App")
sender = st.text_input("Your Name")
recipient = st.text_input("Recipient Name")
message = st.text_input("Message")
submit_button = st.button("Send")


# Send message when the submit button is clicked
if submit_button:
    if sender and recipient and message:
        try:
            response = requests.post(
                f"{server_url}/messages",
                params={
                    "sender": sender,
                    "recipient": recipient,
                    "message": message,
                },
            )
            if response.status_code == 200:
                st.success("Message sent successfully!")
        except requests.exceptions.RequestException:
            st.error("Failed to send the message. Please try again later.")

# Retrieve and display the latest message
previous_message = ""
if sender and recipient:
    while True:
        try:
            response = requests.get(f"{server_url}/messages/{recipient}/{sender}")
            if response.status_code == 200:
                latest_message = response.json().get("message")
                if latest_message and latest_message != previous_message:
                    st.subheader("Latest Message")
                    st.info(f"Sender {sender} -> {recipient}")
                    st.info(latest_message)
                    previous_message = latest_message
        except requests.exceptions.RequestException:
            st.error("Failed to retrieve the latest message. Please try again later.")
        time.sleep(1)
