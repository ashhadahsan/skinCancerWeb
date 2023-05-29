import streamlit as st
from utils.ui import remove_header_footer, header
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="Patients",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
remove_header_footer()
header()
import requests
import json

BASE_URL = "http://127.0.0.1:8000/"


def authenticate(username, password):
    payload = json.dumps({"username": username, "password": password})
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    url = BASE_URL + "user" + "/" + "login"

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        return False


def signup(username_inp, password_inp, fullname_inp, date_of_birth_inp, gender_inp):
    url = "http://127.0.0.1:8000/user/create"

    payload = json.dumps(
        {
            "username": username_inp,
            "password": password_inp,
            "fullname": fullname_inp,
            "date_of_birth": date_of_birth_inp,
            "gender": gender_inp,
            "needs_doctor": False,
            "date_of_appointment": "",
        }
    )
    headers = {"accept": "application/json", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code == 201:
        return True
    else:
        return False


if "auth" not in st.session_state:
    st.session_state.auth = None
if "loggedin" not in st.session_state:
    st.session_state.loggedin = False

if "username_patient" not in st.session_state:
    st.session_state.username_patient = None

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
from datetime import datetime

if st.session_state["loggedin"] == False:
    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1:
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
                st.session_state.username_patient = username
                switch_page("book")
                if st.sidebar.button("Logout"):
                    st.session_state["loggedin"] = None
                    st.session_state.auth = False
                    st.session_state.username_patient = ""

            else:
                st.session_state.auth = False
                st.error("Username/password is incorrect")
                st.markdown(hide_bar, unsafe_allow_html=True)
    with tab2:
        signup_form = st.form("Signup")

        fullName = signup_form.text_input("Full Name")
        username_sng = signup_form.text_input("username")
        password_sng = signup_form.text_input("password", type="password")
        confirm_password = signup_form.text_input("Confirm Password", type="password")
        gender = signup_form.selectbox("Gender", ("Male", "Female"))
        dob = str(signup_form.date_input("Date of Birth", max_value=datetime.now()))

        if signup_form.form_submit_button(
            label="Login",
        ):
            if password_sng != confirm_password:
                st.error("Password does not match")
            else:
                if signup(
                    username_inp=username_sng,
                    password_inp=password_sng,
                    fullname_inp=fullName,
                    date_of_birth_inp=dob,
                    gender_inp=gender,
                ):
                    st.info("Your account is created, now you can login")
                else:
                    st.error("Your account already exists")


if st.session_state.auth == None:
    st.warning("Please enter your username and password")
    st.markdown(hide_bar, unsafe_allow_html=True)
if st.session_state.auth:
    switch_page("book")
