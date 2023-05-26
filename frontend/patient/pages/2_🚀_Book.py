import streamlit as st

import requests
import pandas as pd
from utils.ui import header, remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="Book Appointments",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.sidebar.success(body="View Users")
remove_header_footer()
from pathlib import Path


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


def check_acceptance():
    url = f"http://127.0.0.1:8000/chatrequest/status/{st.session_state.username}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["response"][0]["accepted"]


import datetime
import uuid


def make_chat_request(
    patient: str,
    doc: str,
    date: str = datetime.datetime.now().strftime("%Y-%m-%d"),
    chat_room_id: str = str(uuid.uuid1()),
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


import datetime

try:
    if st.session_state.auth:
        # st.success(f"Welcome {st.session_state.username}")
        st.title("Uplod the picture")
        img = st.file_uploader(
            label="Your image", type=["png", "jpg", "jpeg"], accept_multiple_files=False
        )
        if img is not None:
            bytes_data = img.read()
            save_folder = "content"
            save_path = Path(save_folder, img.name)
            with open(save_path, mode="wb") as w:
                w.write(img.getvalue())

            if check_cancer(img_path=save_path.absolute()):
                with st.spinner():
                    tab1, tab2 = st.tabs(["Book and appointment", "Chat with doctor"])
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
                        doctorname = doctorusername[index]
                        if st.button("Book Appointment"):
                            book_appointment(
                                patient=st.session_state.username,
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
                            send_req = make_chat_request(
                                patient=st.session_state.username, doc=doctorname
                            )
                            if send_req:
                                st.success("Sent")
                                while True:
                                    check = check_acceptance()
                                    if check:
                                        print("accepted")
                                        break
                                    else:
                                        print("no")
                                if check:
                                    st.write("accepted")
                            else:
                                st.error("You have already made a chat request")

            else:
                st.info("You are healthy and do not need any appointments")

    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError as w:
    pass
    # st.warning("You must be logged in to see this page")
    # switch_page("d")
