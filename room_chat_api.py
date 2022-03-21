from asyncio.windows_events import NULL
import socket
import logging
import json
from fastapi import FastAPI, Request, status, Form
from fastapi.responses import JSONResponse, ORJSONResponse, Response
from fastapi.templating import Jinja2Templates
from room import *
from constants import *
from users import *

MY_IPADDRESS = ""

# This is an extremely rare case where I have global variables. The first is the documented way to deal with running the app in uvicorn, the second is the 
# instance of the rmq class that is necessary across all handlers that behave essentially as callbacks. 

'''
Launch the uvicorn server with: python -m uvicorn room_chat_api:app --reload
Use postman to manually test the API at: 127.0.0.1:8000/
'''

app = FastAPI()
room_list = RoomList()
users = UserList()
templates = Jinja2Templates(directory="")
logging.basicConfig(filename='chat.log', level=logging.INFO)

@app.get("/")
async def index():
    return None

@app.get("/page/send", status_code=200)
async def send_form(request: Request):
    """ HTML GET page form sending a message
    """
    pass

@app.post("/page/send", status_code=201)
async def get_form(request: Request, room_choice: str = Form(...), message: str = Form(...), alias: str = Form(...)):
    """ HTML POST page for sending a message
    """
    pass

@app.get("/page/messages", status_code=200)
async def form_messages(request: Request, room_name: str = DEFAULT_PUBLIC_ROOM):
    """ HTML GET page for seeing messages
    """
    pass

@app.post("/page/messages", status_code=201)
async def form_messages(request: Request, room_name: str = Form(...)):
    """ HTML POST page for seeing messages in a different room or different quantities
    """
    pass


@app.get("/messages/", status_code=200)
async def get_messages(request: Request, alias: str, room_name: str, messages_to_get: int = GET_ALL_MESSAGES):
    """ API for getting messages (from a specific room AND person?)
    """
    room_to_get = ChatRoom(room_name, owner_alias=alias, room_type=ROOM_TYPE_PUBLIC)
    room_messages = room_to_get.get_messages(alias)

    return room_messages[0]

@app.get("/users/", status_code=200)
async def get_users():
    """ API for getting users
    """
    try:
        users = UserList()
    except:
        users = UserList('test_users')

    return users.get_all_users()

@app.post("/alias", status_code=201)
async def register_client(client_alias: str, group_alias: bool = False):
    """ API for adding a user alias
    """
    pass

@app.post("/room")
async def create_room(room_name: str, owner_alias: str, room_type: int = ROOM_TYPE_PRIVATE):
    """ API for creating a room
    """
    room_to_create = ChatRoom(room_name, owner_alias=owner_alias, room_type=ROOM_TYPE_PUBLIC, create_new=False)
    room_to_create.put('')
    return room_to_create
 
@app.post("/message", status_code=201)
async def send_message(room_name: str, message: str, from_alias: str, to_alias: str):
    """ API for sending a message
    """
    room_to_send = ChatRoom(room_name, owner_alias=to_alias, room_type=ROOM_TYPE_PUBLIC, create_new=False)
    return room_to_send.send_message(message, from_alias, MessageProperties(room_name, to_alias, from_alias, ROOM_TYPE_PUBLIC))

def main():
    logging.basicConfig(filename='chat.log', level=logging.INFO)
    MY_IPADDRESS = socket.gethostbyname(socket.gethostname())
    MY_NAME = input("Please enter your name: ")
