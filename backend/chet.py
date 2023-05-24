from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.exceptions import WebSocketException
from typing import List

app = FastAPI()

# Store active connections
active_connections = {}


class ConnectionManager:
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id in active_connections:
            active_connections[user_id].append(websocket)
        else:
            active_connections[user_id] = [websocket]

    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in active_connections:
            active_connections[user_id].remove(websocket)

    async def send_message(self, user_id: str, message: str):
        if user_id in active_connections:
            for connection in active_connections[user_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/private-chat/{user_id}")
async def private_chat_endpoint(user_id: str, websocket: WebSocket):
    await manager.connect(user_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.send_message(user_id, message)
    except Exception as e:
        print(e)
        manager.disconnect(user_id, websocket)


# Endpoint to send a message to a specific user
@app.post("/private-chat/{user_id}/send-message")
async def send_private_message(user_id: str, message: str):
    await manager.send_message(user_id, message)
    return {"message": "Message sent."}


# Get active connections for a user
@app.get("/private-chat/{user_id}/active-connections")
async def get_active_connections(user_id: str):
    if user_id in active_connections:
        return {"active_connections": len(active_connections[user_id])}
    else:
        return {"active_connections": 0}
