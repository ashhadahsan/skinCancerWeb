import streamlit as st

import requests
import pandas as pd
from utils.ui import header, remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="Delete Users",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.sidebar.success(body="Delete Users")
remove_header_footer()

if "usernames" not in st.session_state:
    st.session_state.usernames = []


def get_usernames():
    url = "http://127.0.0.1:8000/doctor/getAll/usernames"

    headers = {}
    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["doctors"]
    else:
        return False


def update_doctor_password(username, password):
    url = f"http://127.0.0.1:8000/dotor/update/password/{username}/{password}"
    payload = {}
    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False


try:
    if st.session_state.auth:
        usernames = get_usernames()
        st.session_state.usernames = usernames
        user = st.selectbox(label="Doctors", options=st.session_state.usernames)
        password = st.text_input("Password", type="password")
        if st.button("Update Password"):
            if update_doctor_password(username=user, password=password):
                st.success(f"Doctor {user} password updated succesfully")
            else:
                st.error("Something went wrong")
    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError:
    st.warning("You must be logged in to see this page")
    switch_page("dashboard")
