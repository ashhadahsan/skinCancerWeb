import streamlit as st
import requests
import time


# Streamlit app
def main():
    # Set the page title
    st.set_page_config(page_title="Chat App")

    # Add a title and description
    st.title("Chat App")
    st.markdown("Chat with other users")

    # Display container for chat messages
    messages_container = st.empty()

    # Input field for new message
    new_message = st.text_input("Type your message")

    # Publish button
    if st.button("Publish"):
        if new_message:
            # Publish the new message
            response = requests.post(
                "http://localhost:8000/chat", params={"message": new_message}
            )
            if response.status_code == 200:
                st.success("Message published successfully")
            else:
                st.error("Failed to publish message")
        else:
            st.warning("Please enter a message")

    # Continuously check for new messages
    while True:
        # Retrieve chat messages
        response = requests.get("http://localhost:8000/chat")
        if response.status_code == 200:
            messages = response.text.split("<br>")
            messages_container.write(messages)
        else:
            st.error("Failed to retrieve chat messages")

        # Wait for a few seconds before checking again
        time.sleep(5)


if __name__ == "__main__":
    main()
