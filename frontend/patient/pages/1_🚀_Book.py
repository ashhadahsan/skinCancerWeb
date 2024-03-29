import streamlit as st

import requests
from utils.ui import remove_header_footer
from streamlit_extras.switch_page_button import switch_page
from streamlit_chat import message
import threading

st.set_page_config(
    layout="wide",
    page_title="Book Appointments",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
# st.sidebar.success(body="View Users")
remove_header_footer()
from pathlib import Path

if "ready" not in st.session_state:
    st.session_state["ready"] = False
if "user_input" not in st.session_state:
    st.session_state.user_input = None


if "chat_room_id" not in st.session_state:
    st.session_state["chat_room_id"] = ""
if "doctorname" not in st.session_state:
    st.session_state["doctorname"] = ""


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


def check_cancer(img_path):
    url = f"http://127.0.0.1:8000/upload/image?file={img_path}"

    payload = {}

    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["needs_doctor"]


import json


def book_appointment(patient, doctorname, date):
    url = "http://127.0.0.1:8000/appointment"
    payload = json.dumps({"patient": patient, "doctor": doctorname, "date": date})
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True


def get_all_docs():
    url = "http://127.0.0.1:8000/doctor/getAll/fullnames"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["doctors"]


def get_all_docs_username():
    url = "http://127.0.0.1:8000/doctor/getAll/usernames"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["doctors"]


def check_acceptance(room_id: str):
    url = f"http://127.0.0.1:8000/get_accepted/{room_id}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False


import datetime
import uuid


def make_chat_request(
    patient: str,
    doc: str,
    chat_room_id: str,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
):
    url = "http://127.0.0.1:8000/chatrequest"

    payload = json.dumps(
        {
            "patient": patient,
            "doctor": doc,
            "date": date,
            "chat_room_id": chat_room_id,
            "accepted": False,
        }
    )
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        return True
    else:
        return False


# def recieve_message(room_id: str):
#     url = f"http://127.0.0.1:8000/latest_message/{room_id}?from_text={st.session_state.doctorname}"

#     payload = {}
#     headers = {"accept": "application/json"}

#     response = requests.request("GET", url, headers=headers, data=payload)
#     if response.status_code == 200:
#         data = response.json()
#         print(data)
#         if data["text"] not in st.session_state.generated:
#             st.session_state["generated"].append(data["text"])


def recieve_message(room_id: str, from_text: str):
    url = f"http://localhost:8000/messages/{room_id}/{from_text}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.json())
        messages = response.json()["messages"]
        result = [x for x in messages if x not in st.session_state.generated]
        for x in result:
            st.session_state.generated.append(x)


def send_message(from_text, to_text, text, room_id):
    url = "http://127.0.0.1:8000/create_chat"

    payload = json.dumps(
        {"from_text": from_text, "to_text": to_text, "text": text, "room_id": room_id}
    )
    print(payload)
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 200:
        st.session_state["past"].append(text)


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
                from_text=st.session_state.username_patient,
                to_text=st.session_state.doctorname,
                text=user_input,
                room_id=st.session_state["chat_room_id"],
            )
            # recieve_message(st.session_state.chat_room_id)

    if st.session_state["generated"]:
        with response_container:
            for (
                i,
                (x, y),
            ) in enumerate(
                zip_longest(
                    st.session_state["past"],
                    st.session_state.generated,
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


if "check" not in st.session_state:
    st.session_state.check = False

import datetime


try:
    if st.session_state.auth:
        if st.sidebar.button("Logout"):
            st.session_state["loggedin"] = False
            st.session_state.auth = None
            st.session_state.check = False

            switch_page("dashboard")

        if st.session_state.check == False:
            # st.success(f"Welcome {st.session_state.username}")
            st.title("Upload the picture")
            img = st.file_uploader(
                label="Your image",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=False,
            )
            if img is not None:
                bytes_data = img.read()
                save_folder = "content"
                save_path = Path(save_folder, img.name)
                with open(save_path, mode="wb") as w:
                    w.write(img.getvalue())

                if check_cancer(img_path=save_path.absolute()):
                    with st.spinner():
                        tab1, tab2 = st.tabs(
                            ["Book and appointment", "Chat with doctor"]
                        )
                        with tab1:
                            selected_Date = st.date_input(
                                label="Pick appointment date",
                                min_value=datetime.datetime.now().date(),
                                max_value=datetime.datetime.now().date()
                                + datetime.timedelta(days=7),
                            )
                            options = get_all_docs()
                            index = st.selectbox(
                                "Doctor",
                                range(len(options)),
                                format_func=lambda x: options[x],
                                key="tab1",
                            )

                            doctorusername = get_all_docs_username()
                            # st.session_state.doctorname = doctorusername
                            doctorname = doctorusername[index]
                            st.session_state.doctorname = doctorname
                            if st.button("Book Appointment"):
                                book_appointment(
                                    patient=st.session_state.username_patient,
                                    doctorname=doctorname,
                                    date=str(selected_Date),
                                )
                                st.success("Your appointment has been booked ")
                        with tab2:
                            options = get_all_docs()
                            index = st.selectbox(
                                "Doctor",
                                range(len(options)),
                                format_func=lambda x: options[x],
                                key="tab2",
                            )

                            doctorusername = get_all_docs_username()
                            doctorname = doctorusername[index]
                            if st.button("Send Chat request"):
                                st.session_state.chat_room_id = str(uuid.uuid1())

                                if make_chat_request(
                                    patient=st.session_state.username_patient,
                                    doc=doctorname,
                                    chat_room_id=st.session_state.chat_room_id,
                                ):
                                    while True:
                                        st.session_state.check = check_acceptance(
                                            st.session_state["chat_room_id"]
                                        )
                                        # time.sleep(10)
                                        if st.session_state.check:
                                            # st.write(st.session_state.check)
                                            break
                                        else:
                                            print("no")

                                else:
                                    st.error("You have already made a chat request")

                else:
                    st.info("You are healthy and do not need any appointments")
        if st.session_state.check == True:
            if "generated" not in st.session_state:
                st.session_state["generated"] = ["Hello Patient"]
                st.session_state["past"] = ["Hi Doctor"]
            # if "past" not in st.session_state:
            #     st.session_state["past"] = ["Hi"]

            # send_message(
            #     from_text=st.session_state.username,
            #     to_text=st.session_state.doctorname,
            #     text="Hi Doctor",
            #     room_id=st.session_state["chat_room_id"],
            # )

            chat()
            start_background_thread(
                st.session_state["chat_room_id"], st.session_state.doctorname
            )


except AttributeError as w:
    st.exception(w)
    # st.warning("You must be logged in to see this page")
    # switch_page("dashboard")
