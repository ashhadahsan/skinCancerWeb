import streamlit as st

import requests
import pandas as pd
from utils.ui import header, remove_header_footer
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(
    layout="wide",
    page_title="View Doctors",
    page_icon="🧊",
    initial_sidebar_state="expanded",
)
st.sidebar.success(body="View Users")
remove_header_footer()


def get_doctors():
    url = "http://127.0.0.1:8000/doctor/getAll"

    headers = {}
    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return False


def get_patients():
    url = "http://127.0.0.1:8000/patient/getAll"

    headers = {}
    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return False

def get_appointments():
    url = "http://127.0.0.1:8000/appointments"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()


try:
    if st.session_state.auth:
        st.title("Appointments")
        doctor = pd.DataFrame(get_doctors()["doctors"])
        appointments = pd.DataFrame(get_appointments())
        patients=pd.DataFrame(get_patients()['patient'])
        try:
            df = pd.merge(
                left=doctor,
                right=appointments,
                left_on="username",
                right_on="doctor",
                how="inner",
            ).drop(["username", "_id", "doctor"], axis=1)
            
            df.columns = ["Doctor Name", "Patients", "Date"]
            df=pd.merge(df,patients,left_on="Patients",right_on="username").drop(['username','Patients'],axis=1)
            df.columns=['Doctor Name','Date','Patient Name']
            df=df[['Doctor Name','Patient Name','Date']]
            
            
            hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

            # Inject CSS with Markdown
            st.markdown(hide_table_row_index, unsafe_allow_html=True)
            st.table(df)
        except KeyError as e:
            st.excepton(e)
            st.info("No appointments")

    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state.auth = None
        switch_page("dashboard")


except AttributeError:
    st.warning("You must be logged in to see this page")
    switch_page("dashboard")
