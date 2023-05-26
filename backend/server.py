from fastapi import FastAPI, HTTPException
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel
from load_model import model
from fastapi import FastAPI

app = FastAPI()

# MongoDB setup and functions
import pymongo
from passlib.hash import bcrypt

client = pymongo.MongoClient("mongodb://127.0.0.1:27017")

db = client["skin_clinic"]
admins_col = db["admins"]
users_col = db["users"]
doctors_col = db["doctors"]
appointment_col = db["appointments"]
admins_col.create_index("username", unique=True)
users_col.create_index("username", unique=True)
doctors_col.create_index("username", unique=True)
chat_req_col = db["chat_request"]
import numpy as np
from PIL import Image


class Admin(BaseModel):
    username: str
    password: str


class Patients(BaseModel):
    username: str
    password: str
    fullname: str
    date_of_birth: str
    gender: str
    needs_doctor: bool


class Appointment(BaseModel):
    patient: str
    doctor: str
    date: str


class Doctor(BaseModel):
    username: str
    password: str
    fullname: str


class UserLogin(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    patient: str
    doctor: str
    date: str
    chat_room_id: str
    accepted: bool = False


class ChatModel(BaseModel):
    from_text: str
    to_text: str
    text: str
    room_id: str


from bson.json_util import dumps, loads


@app.post("/create_chat")
def create_chat(chat: ChatModel):
    chat_col = db[chat.room_id]
    chat_dict = {
        "from_text": chat.from_text,
        "to_text": chat.to_text,
        "text": chat.text,
    }
    result = chat_col.insert_one(chat_dict)
    return {"message": "Chat created successfully", "chat_id": str(result.inserted_id)}


@app.get("/latest_message/{room_id}")
def get_latest_message(room_id: str):
    collection = db[room_id]
    message = collection.find_one({}, sort=[("_id", -1)])

    try:
        print(loads(dumps(message)))
        message = loads(dumps(message))["text"]
        from_text = loads(dumps(message))["from_text"]
        to_text = loads(dumps(message))["to_text"]
        print(message)
        return {"text": message, "from_text": from_text, "to_text": to_text}
    except Exception as e:
        raise HTTPException(404, detail=e)


@app.put("/update_accepted_status")
def update_accepted_status(chat_request: ChatRequest):
    query = {"patient": chat_request.patient}
    update = {"$set": {"accepted": True}}
    chat_req_col.update_one(query, update)
    return {"message": "Accepted status updated successfully"}


@app.post("/chatrequest")
def create_chat_request(chat_request: ChatRequest):
    today = datetime.now().strftime("%Y-%m-%d")

    if chat_request.date < today:
        raise HTTPException(
            status_code=400, detail="Cannot create a chat request for a past date."
        )

    existing_request = chat_req_col.find_one(
        {"date": chat_request.date, "patient": chat_request.patient}
    )
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="You have already made a chat request for this date.",
        )

    chat_request_dict = chat_request.dict()
    chat_req_col.insert_one(chat_request_dict)
    return {"status": "OK"}


@app.get("/chatrequest/today/{doctor}")
def get_chat_requests_today(doctor: str):
    today = datetime.now().strftime("%Y-%m-%d")
    chat_requests = chat_req_col.find({"doctor": doctor, "date": today})

    patient_names = [
        {"patient": request["patient"], "room_id": request["chat_room_id"]}
        for request in chat_requests
    ]
    print(patient_names)
    return {"req": patient_names}


@app.get("/chatrequest/status/{user_id}")
def get_chat_requests_today(user_id: str):
    today = datetime.now().strftime("%Y-%m-%d")
    chat_requests = chat_req_col.find({"patient": user_id, "date": today})

    patient_names = [{"accepted": request["accepted"]} for request in chat_requests]
    print(patient_names)
    return {"response": patient_names}


def create_admin(username: str, password: str):
    hashed_password = bcrypt.hash(password)
    admin = {"username": username, "password": hashed_password}
    admins_col.insert_one(admin)


def create_cr(patient: str, doctor: str, date: str):
    req = {"patient": patient, "doctor": doctor, "date": date}
    chat_req_col.insert_one(req)


def login_admin(username: str, password: str) -> bool:
    admin = admins_col.find_one({"username": username})
    if admin and bcrypt.verify(password, admin["password"]):
        return True
    return False


def create_user(
    username: str,
    password: str,
    fullname: str,
    gender: str,
    dob: str,
):
    hashed_password = bcrypt.hash(password)
    user = {
        "username": username,
        "password": hashed_password,
        "fullname": fullname,
        "gender": gender,
        "date_of_birth": dob,
    }
    users_col.insert_one(user)


@app.post("/upload/image")
def create_upload_file(file: str):
    read = np.asarray(Image.open(file).convert("RGB"))
    read = read / 255
    read = np.reshape(read, (1, 224, 224, 3))
    print("output", np.argmax(model.predict(read), axis=1)[0])
    print("file", file)
    if np.argmax(model.predict(read), axis=1)[0] == 1:
        return {"needs_doctor": True}  # cancer
    else:
        return {"needs_doctor": False}


def create_doctor(
    username: str,
    password: str,
    fullname: str,
):
    hashed_password = bcrypt.hash(password)
    doctor = {
        "username": username,
        "password": hashed_password,
        "fullname": fullname,
    }
    doctors_col.insert_one(doctor)


def delete_doctor(username: str):
    doctors_col.delete_one({"username": username})


def get_count_doctors():
    count = doctors_col.count_documents({})
    return count


def get_all_doctorRecords() -> List[Dict]:
    users = doctors_col.find(
        {},
        {
            "username": 1,
            "fullname": 1,
            "_id": 0,
        },
    )
    user_list = [
        {
            "username": user["username"],
            "fullname": user["fullname"],
        }
        for user in users
    ]
    return user_list


def get_all_patientRecords() -> List[Dict]:
    users = users_col.find(
        {},
        {
            "username": 1,
            "fullname": 1,
            "_id": 0,
        },
    )
    user_list = [
        {
            "username": user["username"],
            "fullname": user["fullname"],
        }
        for user in users
    ]
    return user_list


def get_all_patientsRecords() -> List[Dict]:
    users = users_col.find(
        {},
        {
            "fullname": 1,
            "_id": 0,
            "gender": 1,
            "age": 1,
            "date_of_appointment": 1,
            "date_of_birth": 1,
        },
    )
    user_list = [
        {
            "fullname": user["fullname"],
            "gender": user["gender"],
            "age": user["age"],
            "date_of_appointment": user["date_of_appointment"],
            "date_of_birth": user["date_of_birth"],
        }
        for user in users
    ]
    return user_list


def update_password_doc(username: str, new_password: str):
    hashed_password = bcrypt.hash(new_password)

    doctors_col.update_one(
        {"username": username},
        {"$set": {"password": hashed_password}},
    )
    return True


def update_appointments(username: str, new_date: str):
    users_col.update_one(
        {"username": username}, {"$push": {"date_of_appointments": new_date}}
    )


def login_user(username: str, password: str) -> bool:
    user = users_col.find_one({"username": username})
    if user and bcrypt.verify(password, user["password"]):
        return True
    return False


def login_doctor(username: str, password: str) -> bool:
    user = doctors_col.find_one({"username": username})
    if user and bcrypt.verify(password, user["password"]):
        return True
    return False


def get_pat_countr():
    count = users_col.count_documents({})
    return count


def get_all_usernames() -> List[str]:
    users = doctors_col.find({}, {"username": 1, "_id": 0})
    user_list = [user["username"] for user in users]
    return user_list


def get_all_doctorNames() -> List[str]:
    users = doctors_col.find({}, {"fullname": 1, "_id": 0})
    user_list = [user["fullname"] for user in users]
    return user_list


def get_all_usersRecords() -> List[Dict]:
    users = users_col.find({}, {"username": 1, "urls": 1, "_id": 0})
    user_list = [{"username": user["username"], "urls": user["urls"]} for user in users]
    return user_list


# API endpoints
@app.post("/admin/create", status_code=201)
def create_admin_pls(admin: Admin):
    if admins_col.find_one({"username": admin.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    create_admin(admin.username, admin.password)
    return {"message": "Admin created successfully"}


@app.post("chatRequest/{username}/{doctor}")
def mke_cr(cr: ChatRequest):
    pass


@app.post("/appointment")
async def create_appointment(appointment: Appointment):
    appointment_data = appointment.dict()
    appointment_col.insert_one(appointment_data)
    return {"message": "Appointment created successfully"}


@app.get("/appointments")
async def get_appointments(username: str = None):
    if username:
        appointments = appointment_col.find(
            {"$or": [{"patient": username}, {"doctor": username}]}
        )
    else:
        appointments = appointment_col.find()
    # Convert ObjectId to string for JSON serialization
    appointments = [
        {**appointment, "_id": str(appointment["_id"])} for appointment in appointments
    ]

    return appointments


@app.get("/user/appointments")
async def get_appointments(username: str):
    if username:
        appointments = appointment_col.find({"patient": username})
    else:
        appointments = appointment_col.find()

    # Convert ObjectId to string for JSON serialization
    appointments = [
        {**appointment, "_id": str(appointment["_id"])} for appointment in appointments
    ]

    return appointments


@app.get("/doctor/appointments")
async def get_appointments(username: str):
    if username:
        appointments = appointment_col.find({"doctor": username})
    else:
        appointments = appointment_col.find()

    # Convert ObjectId to string for JSON serialization
    appointments = [
        {**appointment, "_id": str(appointment["_id"])} for appointment in appointments
    ]

    return appointments


@app.get("/doctor/count")
def get_doc_counts():
    return {"n": get_count_doctors()}


@app.get("/user/count")
def get_doc_counts():
    return {"n": get_pat_countr()}


@app.get("/doctor/getAll/usernames", status_code=200)
def getAll():
    users = get_all_usernames()
    return {"doctors": users}


@app.get("/doctor/getAll/fullnames", status_code=200)
def getAll():
    users = get_all_doctorNames()
    return {"doctors": users}


@app.get("/doctor/getAll", status_code=200)
def getAll():
    users = get_all_doctorRecords()
    return {"doctors": users}


@app.get("/patient/getAll", status_code=200)
def getAll():
    users = get_all_patientRecords()
    return {"patient": users}


@app.get("/user/getAll", status_code=200)
def getAll():
    users = get_all_patientsRecords()
    return {"patients": users}


@app.delete("/doctor/{username}")
def delete_a_doctor(username: str):
    delete_doctor(username=username)

    return {"success": True}


@app.post("/admin/login")
def login_admin_endpoint(admin: Admin):
    if login_admin(admin.username, admin.password):
        return {"message": "Logged in successfully"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/user/create", status_code=201)
def create_user_endpoint(user: Patients):
    if users_col.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    create_user(
        user.username,
        user.password,
        user.fullname,
        user.gender,
        dob=user.date_of_birth,
    )
    return {"message": "User created successfully"}


@app.post("/doctor/create", status_code=201)
def create_user_endpoint(user: Doctor):
    if doctors_col.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    create_doctor(user.username, user.password, user.fullname)
    return {"message": "User created successfully"}


@app.post("/doctor/login")
def login_admin_endpoint(doctor: UserLogin):
    if login_doctor(doctor.username, doctor.password):
        return {"message": "Logged in successfully"}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/user/login")
def login_user_endpoint(patient: UserLogin):
    if login_user(patient.username, patient.password):
        return {"message": "Logged in successfully"}

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/dotor/update/password/{username}/{new_password}")
def update_the_pass_doctor(username, new_password):
    if update_password_doc(username=username, new_password=new_password):
        return {"message": "updated"}
