from fastapi import FastAPI
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pubnub.enums import PNOperationType, PNStatusCategory


pnconfig = PNConfiguration()

pnconfig.subscribe_key = "sub-c-8a3fdde4-de98-41bf-ac76-56e160f571b6"
pnconfig.publish_key = "pub-c-064a1b8f-bdf0-4048-b0dd-656658ed1af3"
pnconfig.user_id = "user1"
pubnub = PubNub(pnconfig)


app = FastAPI()


# Define PubNub callback class
class MySubscribeCallback(SubscribeCallback):
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            print("Connected to PubNub")
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            print("Reconnected to PubNub")
        elif status.category == PNStatusCategory.PNDisconnectedCategory:
            print("Disconnected from PubNub")

    def message(self, pubnub, message):
        # Broadcast the received message to all connected clients
        app.pubnub_messages.append(message.message)


# Initialize PubNub callback
pubnub_callback = MySubscribeCallback()
pubnub.add_listener(pubnub_callback)
pubnub.subscribe().channels(f"chat").execute()

# Store messages in memory for simplicity
app.pubnub_messages = []


# API endpoint to retrieve chat messages
@app.get("/chat", response_class=HTMLResponse)
async def get_chat_messages():
    # messages = "<br>".join(app.pubnub_messages)
    print(app.pubnub_messages[-1])
    return JSONResponse({"messages": app.pubnub_messages[-1]})
    # return f"<h1>Chat Messages:</h1><p>{messages}</p>"


# API endpoint to publish a chat message
@app.post("/chat")
async def publish_chat_message(message: str, sender: str):
    forms = {"username": sender, "message": message}
    pubnub.publish().channel("chat").message(forms).sync()
    return {"message": "Published successfully"}


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
