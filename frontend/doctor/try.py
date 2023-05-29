import streamlit as st
import requests
import threading
import time

from streamlit.runtime.scriptrunner import add_script_run_ctx


# Function to call the API and update the session variable
def update_session_variable():
    # API endpoint
    api_url = "https://jsonplaceholder.typicode.com/posts"
    print("ok")

    # Call the API
    response = requests.get(api_url)

    if response.status_code == 200:
        # Update the session variable with the API response
        st.session_state["data"] = response.json()
        st.write(st.session_state["data"])

    # Wait for 5 seconds before making the next API call
    time.sleep(5)


# Check if the session variable exists, if not, create it
if "data" not in st.session_state:
    st.session_state["data"] = None

# Start the background thread
background_thread = threading.Thread(target=update_session_variable)
add_script_run_ctx(background_thread)
background_thread.start()


# Streamlit app UI
def main():
    st.title("Background API Caller")

    if st.session_state["data"]:
        st.write("API Data:")
    else:
        st.write("Waiting for API data...")


if __name__ == "__main__":
    main()
