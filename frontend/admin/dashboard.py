import streamlit as st
from utils.ui import remove_header_footer, header
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="Admin",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
remove_header_footer()
header()
import requests
import json

BASE_URL = "http://127.0.0.1:8000/"


def get_doctors() -> int:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {}
    url = BASE_URL + "doctor" + "/" + "count"

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["n"]
    else:
        return 0


def get_patients() -> int:
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {}
    url = BASE_URL + "user" + "/" + "count"

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()["n"]
    else:
        return 0


def authenticate(username, password):
    payload = json.dumps({"username": username, "password": password})
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    url = BASE_URL + "admin" + "/" + "login"

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False


if "auth" not in st.session_state:
    st.session_state.auth = None
if "loggedin" not in st.session_state:
    st.session_state.loggedin = False


hide_bar = """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""


if st.session_state["loggedin"] == False:
    login_form = st.form("Login")

    username = login_form.text_input("Username").lower()
    password = login_form.text_input("Password", type="password")
    if login_form.form_submit_button(
        label="Login",
    ):
        if authenticate(username=username, password=password):
            st.session_state["loggedin"] = True
            st.session_state.auth = True
            st.success("Welcome")
            hide_st_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        header {visibility: hidden;}
                        </style>
                        """
            st.markdown(hide_st_style, unsafe_allow_html=True)
            switch_page("add")
            # if st.sidebar.button("Logout"):
            #     st.session_state["loggedin"] = None
            #     st.session_state.auth = False

        else:
            st.session_state.auth = False
            st.error("Username/password is incorrect")
            st.markdown(hide_bar, unsafe_allow_html=True)
if st.session_state.auth == None:
    st.warning("Please enter your username and password")
    st.markdown(hide_bar, unsafe_allow_html=True)
if st.session_state.auth:
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Doctors", value=get_doctors())
    with col2:
        st.metric(label="Total Patients", value=get_patients())
    # switch_page("add")
