import asyncio
import websockets


async def connect_to_private_chat(user_id, room_id):
    async with websockets.connect(
        f"ws://localhost:8000/private-chat/{room_id}"
    ) as websocket:
        print("Connected to private chat!")
        try:
            while True:
                message = input("Enter your message: ")
                await websocket.send(f"{user_id}: {message}")
                response = await websocket.recv()
                if response.split(":")[0] != user_id:
                    text = response.split(":")[1]
                    print(f"Received message {text}")
        except KeyboardInterrupt:
            print("Chat ended.")
        except websockets.ConnectionClosed:
            print("Connection closed.")


name = input("Enter name ")
asyncio.run(connect_to_private_chat(name, "6969"))
