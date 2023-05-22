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


def get_history(username: str):
    url = f"http://127.0.0.1:8000/doctor/appointments?username={username}"

    payload = {}
    headers = {"accept": "application/json"}

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.json())

    return response.json()


try:
    if st.session_state.auth:
        st.title("Appointments")
        try:
            dataframe = pd.DataFrame(get_history(st.session_state.username)).drop(
                ["_id", "doctor"], axis=1
            )
            dataframe.columns = ["Patient Name", "Date of Appointment"]
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
