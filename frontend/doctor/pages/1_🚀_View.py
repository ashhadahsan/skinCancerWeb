import streamlit as st

import requests
import pandas as pd
from utils.ui import remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="View Appointments",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
# st.sidebar.success(body="View Users")
remove_header_footer()


def get_history(username: str):
    url = f"http://127.0.0.1:8000/doctor/appointments?username={username}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()


def get_patients():
    url = "http://127.0.0.1:8000/patient/getAll"

    headers = {}
    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return False


try:
    if st.session_state.auth:
        st.title("Appointments")
        patient = pd.DataFrame(get_patients()["patient"])
        try:
            dataframe = pd.DataFrame(get_history(st.session_state.username_doc)).drop(
                ["_id", "doctor"], axis=1
            )
            dataframe.columns = ["Patient Name", "Date of Appointment"]
            dataframe = pd.merge(
                left=dataframe,
                right=patient,
                left_on="Patient Name",
                right_on="username",
            ).drop(["username", "Patient Name"], axis=1)
            dataframe.columns = ["Date", "Patient Name"]
            dataframe = dataframe[["Patient Name", "Date"]]

            hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(dataframe)
        except KeyError:
            st.info("No Appointments yet")
    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError:
    st.warning("You must be logged in to see this page")
    switch_page("dashboard")
