from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from load_model import model
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/text")
db = client["chatdbs"]

# Create the FastAPI app
app = FastAPI()


# API route to create a new message
@app.post("/messages")
async def create_message(sender: str, recipient: str, message: str):
    collection_name = f"{sender}_{recipient}"
    collection = db[collection_name]
    new_message = {"sender": sender, "recipient": recipient, "message": message}
    result = collection.insert_one(new_message)
    return {"id": str(result.inserted_id)}


# API route to retrieve all messages for a specific recipient and sender
@app.get("/messages/{recipient}/{sender}")
async def get_messages(recipient: str, sender: str):
    collection_name = f"{sender}_{recipient}"
    collection = db[collection_name]
    message = collection.find_one({}, sort=[("_id", -1)])

    try:
        print(loads(dumps(message)))
        message = loads(dumps(message))["message"]
        print(message)
        return {"message": message}
    except:
        raise HTTPException(404, detail="No message")
