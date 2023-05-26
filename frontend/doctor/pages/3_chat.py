import streamlit as st

import requests
import pandas as pd
from utils.ui import header, remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="View Appointments",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.sidebar.success(body="View Users")
remove_header_footer()

from streamlit_custom_notification_box import custom_notification_box


def get_chat_requests():
    url = f"http://127.0.0.1:8000/chatrequest/today/{st.session_state.username}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    patient = []
    room = []
    for x in response.json()["req"]:
        patient.append(x["patient"])
        room.append(x["room_id"])
    return patient, room


import json
import datetime


def accept_request(
    chat_room_id: str,
    patient,
    doctor,
    date: str = datetime.datetime.now().strftime(r"%Y-%m-%d"),
    accepted=True,
):
    url = "http://127.0.0.1:8000/update_accepted_status"

    payload = json.dumps(
        {
            "patient": patient,
            "doctor": doctor,
            "date": date,
            "chat_room_id": chat_room_id,
            "accepted": accepted,
        }
    )
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("PUT", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True


styles = {
    "material-icons": {"color": "red"},
    "text-icon-link-close-container": {
        "box-shadow": "#3896de 0px 4px",
    },
    "notification-text": {"": ""},
    "close-button": {"": ""},
    "link": {"": ""},
}
try:
    if st.session_state.auth:
        st.title("Chat Requests")

        patient, room = get_chat_requests()
        try:
            index = st.selectbox(
                "Doctor", range(len(patient)), format_func=lambda x: patient[x]
            )

            if st.button("Accept"):
                patient_name = patient[index]
                room_id = room[index]
                accept_request(
                    room_id, patient=patient_name, doctor=st.session_state.username
                )

        except KeyError:
            st.info("No Appointments yet")
        for x in patient:
            custom_notification_box(
                icon="info",
                textDisplay=f"New chat request from {x}",
                url="#",
                externalLink="",
                styles=styles,
                key="foo",
            )

    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError as e:
    st.exception(e)
    st.warning("You must be logged in to see this page")
