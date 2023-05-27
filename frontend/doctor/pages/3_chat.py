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
from streamlit_chat_media import message

from streamlit_custom_notification_box import custom_notification_box


if "ready" not in st.session_state:
    st.session_state["ready"] = False
if "user_input" not in st.session_state:
    st.session_state.user_input = None
if "generated" not in st.session_state:
    st.session_state["generated"] = ["Hi"]
if "past" not in st.session_state:
    st.session_state["past"] = ["Hello"]
if "chat_room_id" not in st.session_state:
    st.session_state["chat_room_id"] = ""
if "to" not in st.session_state:
    st.session_state.to = ""


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
):
    url = f"http://127.0.0.1:8000/update_accepted/{chat_room_id}?accepted=true"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("PUT", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False


def recieve_message(room_id: str):
    url = f"http://127.0.0.1:8000/latest_message/{room_id}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        if data["to_text"] == st.session_state.username:
            st.session_state["generated"].append(data["text"])


def send_message(from_text, to_text, text, room_id):
    url = "http://127.0.0.1:8000/create_chat"

    payload = json.dumps(
        {"from_text": from_text, "to_text": to_text, "text": text, "room_id": room_id}
    )
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        st.session_state["past"].append(text)


def chat():
    response_container = st.container()
    recieve_message(st.session_state.chat_room_id)

    # container for text box
    empty = st.empty()

    # with container:
    user_input = st.text_input(
        "Query:",
        placeholder="e.g: How many rows?",
        key="input",
    )
    if user_input:
        with st.spinner(text=""):
            send_message(
                from_text=st.session_state.username,
                to_text=st.session_state.to,
                text=user_input,
                room_id=st.session_state["chat_room_id"],
            )
            recieve_message(st.session_state.chat_room_id)

    if st.session_state["generated"]:
        with response_container:
            for i in range(len(st.session_state["past"])):
                message(
                    st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs",
                    allow_html=True,
                )
            for i in range(len(st.session_state["generated"])):
                message(
                    st.session_state["generated"][i],
                    key=str(i),
                    avatar_style="bottts",
                    allow_html=True,
                )


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
        index = st.selectbox(
            "Doctor", range(len(patient)), format_func=lambda x: patient[x]
        )

        if st.button("Accept"):
            try:
                patient_name = patient[index]
                room_id = room[index]
                accept_request(room_id)
                st.session_state.chat_room_id = room_id
                st.session_state.to = patient_name
                st.session_state.ready = True
            except:
                pass
        if st.session_state.ready:
            chat()
            # if "generated" not in st.session_state:
            #     st.session_state["generated"] = ["Hello"]
            # if "past" not in st.session_state:
            #     st.session_state["past"] = ["Hi"]

        # for x in patient:
        #     custom_notification_box(
        #         icon="info",
        #         textDisplay=f"New chat request from {x}",
        #         url="#",
        #         externalLink="",
        #         styles=styles,
        #         key="foo",
        #     )

    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError as e:
    st.exception(e)
    st.warning("You must be logged in to see this page")
