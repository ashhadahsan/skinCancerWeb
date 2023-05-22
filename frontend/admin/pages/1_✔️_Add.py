import streamlit as st

import requests
import json
from utils.ui import header, remove_header_footer
import os
import boto3
from pathlib import Path

# from utils.firebase import bucket
from utils.helpers import get_url
from streamlit_extras.switch_page_button import switch_page
from typing import List

st.set_page_config(
    layout="wide",
    page_title="Add Doctors",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.sidebar.success(body="Add Users")
remove_header_footer()
if os.name == "nt":  # Windows
    from dotenv import load_dotenv

    load_dotenv()


def add_doctors(
    username: str,
    password: str,
    fullname: str,
):
    url = "http://127.0.0.1:8000/doctor/create"

    payload = json.dumps(
        {
            "username": username,
            "password": password,
            "fullname": fullname,
        }
    )
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.status_code)
    if response.status_code == 201:
        return True
    else:
        return False


try:
    if st.session_state.auth == True:
        login_form = st.form("Login")

        username = login_form.text_input("Username").lower()

        password = login_form.text_input("Password", type="password")
        fullname = login_form.text_input("Full Name")

        if login_form.form_submit_button("Add"):
            with st.spinner():
                add = add_doctors(
                    username=username, password=password, fullname=fullname.title()
                )
                if add:
                    st.success("User created")
                else:
                    st.error("User already exists")
        if st.sidebar.button("Logout"):
            st.session_state["loggedin"] = False
            st.session_state.auth = None
            switch_page("dashboard")


except AttributeError as error:
    st.warning("You must be logged in to see this page")
    switch_page("dashboard")
