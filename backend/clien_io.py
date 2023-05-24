import asyncio
import websockets
import streamlit as st
from streamlit_chat import message
import uuid


async def connect_to_private_chat(user_id, room_id):
    async with websockets.connect(
        f"ws://localhost:8000/private-chat/{room_id}"
    ) as websocket:
        print("Connected to private chat!")
        try:
            while True:
                message_input = st.text_input(
                    "Enter your message:", key=str(uuid.uuid1())
                )
                if st.button("Send"):
                    message_content = message_input.strip()
                    if message_content:
                        await websocket.send(f"{user_id}: {message_content}")

                response = await websocket.recv()
                if response.split(":")[0] != user_id:
                    text = response.split(":")[1]
                    message(text, is_user=False)
                # if response.split(":")[0] == user_id:
                #     text = response.split(":")[1]
                #     message(text)

        except KeyboardInterrupt:
            print("Chat ended.")
        except websockets.ConnectionClosed:
            print("Connection closed.")


def main():
    st.title("Private Chat")
    name = st.selectbox("Enter your name:", options=["hammad", "ashhad"])
    room_id = 6969
    if st.button("Connect"):
        asyncio.run(connect_to_private_chat(name, room_id))


if __name__ == "__main__":
    main()
