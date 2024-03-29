import streamlit as st

import requests
from utils.ui import remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="Chat",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
# st.sidebar.success(body="View Users")
remove_header_footer()
from streamlit_chat import message


if "ready" not in st.session_state:
    st.session_state["ready"] = False
if "user_input" not in st.session_state:
    st.session_state.user_input = None
if "generated_dooc" not in st.session_state:
    st.session_state["generated_dooc"] = ["Hi Doctor"]
if "past_doc" not in st.session_state:
    st.session_state["past_doc"] = ["Hello Patient"]
if "chat_room_id" not in st.session_state:
    st.session_state["chat_room_id"] = ""
if "to" not in st.session_state:
    st.session_state.to = ""


import threading


# Create a flag to control the background thread
if "background_thread" not in st.session_state:
    st.session_state["background_thread"] = None


def start_background_thread(room_id, from_text):
    """
    Function to start the background thread that continuously checks for new messages.
    """
    if (
        st.session_state["background_thread"] is None
        or not st.session_state["background_thread"].is_alive()
    ):
        # Create a new thread and start it
        st.session_state["background_thread"] = threading.Thread(
            target=background_task(room_id=room_id, from_text=from_text)
        )
        st.session_state["background_thread"].start()


import time


def background_task(room_id, from_text):
    """
    Background task function that continuously calls the recieve_message() function.
    """
    while True:
        time.sleep(5)
        if st.session_state.auth and st.session_state.ready:
            recieve_message(room_id=room_id, from_text=from_text)


def get_chat_requests():
    url = f"http://127.0.0.1:8000/chatrequest/today/{st.session_state.username_doc}"

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


# def recieve_message(room_id: str):
#     url = f"http://127.0.0.1:8000/latest_message/{room_id}?from_text={st.session_state.to}"

#     payload = {}
#     headers = {"accept": "application/json"}

#     response = requests.request("GET", url, headers=headers, data=payload)
#     if response.status_code == 200:
#         data = response.json()
#         print(data)

#         print(data["text"])
#         if data["text"] not in st.session_state.generated_dooc:
#             st.session_state["generated_dooc"].append(data["text"])

from typing import Optional


def recieve_message(room_id: str, from_text: str):
    print(from_text, room_id)
    url = f"http://localhost:8000/messages/{room_id}/{from_text}"
    print(url)

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.json())
        messages = response.json()["messages"]
        result = [x for x in messages if x not in st.session_state.generated_dooc]
        for x in result:
            st.session_state.generated_dooc.append(x)


def send_message(from_text, to_text, text, room_id):
    url = "http://127.0.0.1:8000/create_chat"

    payload = json.dumps(
        {"from_text": from_text, "to_text": to_text, "text": text, "room_id": room_id}
    )
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        st.session_state["past_doc"].append(text)


from itertools import zip_longest


def chat():
    response_container = st.container()

    # with container:
    user_input = st.text_input(
        "You:",
        key="input",
    )
    if user_input:
        with st.spinner(text=""):
            send_message(
                from_text=st.session_state.username_doc,
                to_text=st.session_state.to,
                text=user_input,
                room_id=st.session_state["chat_room_id"],
            )
            # recieve_message(
            #     st.session_state.chat_room_id, from_text=st.session_state.to
            # )

    if st.session_state["generated_dooc"]:
        with response_container:
            for (
                i,
                (x, y),
            ) in enumerate(
                zip_longest(
                    st.session_state["past_doc"],
                    st.session_state.generated_dooc,
                    fillvalue=None,
                )
            ):
                if x is not None:
                    message(
                        x,
                        is_user=True,
                        key=str(i) + "_user",
                        avatar_style="thumbs",
                    )
                if y is not None:
                    message(
                        y,
                        key=str(i),
                        avatar_style="bottts",
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
        # global room_id
        # global patient_name

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
            # send_message(
            #     from_text=st.session_state.username,
            #     to_text=st.session_state.to,
            #     text="Hello Patient",
            #     room_id=st.session_state["chat_room_id"],
            # )

            chat()
            start_background_thread(
                room_id=st.session_state.chat_room_id, from_text=st.session_state.to
            )
            # if "generated_dooc" not in st.session_state:
            #     st.session_state["generated_dooc"] = ["Hello"]
            # if "past_doc" not in st.session_state:
            #     st.session_state["past_doc"] = ["Hi"]

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
    switch_page("dashboard")
