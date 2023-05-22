import streamlit as st
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration

publish_key = "pub-c-064a1b8f-bdf0-4048-b0dd-656658ed1af3"
subscribe_key = "sub-c-8a3fdde4-de98-41bf-ac76-56e160f571b6"

pnconfig = PNConfiguration()

pnconfig.subscribe_key = "sub-c-8a3fdde4-de98-41bf-ac76-56e160f571b6"
pnconfig.publish_key = "pub-c-064a1b8f-bdf0-4048-b0dd-656658ed1af3"
pnconfig.user_id = "user2"
pubnub = PubNub(pnconfig)

from pubnub.callbacks import SubscribeCallback


class SubscribeHandler(SubscribeCallback):
    def message(self, pubnub, message):
        print("Message payload: %s" % message.message)
        print("Message publisher: %s" % message.publisher)
        sender = message.sender
        received_message = message.message
        self.messages.append(f"{sender}: {received_message}")
        st.session_state.messages = message.message
        st.experimental_rerun()


def publish_callback(result, status):
    if status.is_error():
        print(status.status_code, status.error_data.__dict__)
    else:
        print(result.timetoken)


def create_private_channel(username):
    return f"private_{username}"


def subscribe_to_private_channel(username):
    private_channel = create_private_channel(username)
    pubnub.subscribe().channels(private_channel).execute()
    st.write("Subscribed to", private_channel)


def send_message(sender, recipient, message):
    private_channel = create_private_channel(recipient)
    pubnub.publish().channel(private_channel).message(
        {"sender": sender, "message": message}
    ).sync()


def main():
    global messages

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    st.title("Personal Chatroom")

    users = ["user1", "user2", "user3"]
    sender = "user2"
    recipient = "user1"
    message = st.text_input("Type your message")

    if st.button("Send Message"):
        send_message(sender, recipient, message)
        pubnub.add_listener(SubscribeHandler())

    st.markdown("## Received Messages")
    st.text_area(
        "Messages",
        value="\n".join(st.session_state.callback.messages),
        height=200,
        key="messages",
    )


if __name__ == "__main__":
    # Subscribe to the private channels of all users
    for user in ["user1", "user2", "user3"]:
        subscribe_to_private_channel(user)

    main()
