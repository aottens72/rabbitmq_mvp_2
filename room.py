import pika
import json
import pika.exceptions
import logging
from users import *
from datetime import date, datetime
from pymongo import MongoClient, ReturnDocument
from collections import deque
from constants import *

MONGO_DB = 'detest'

#MONGO_DB = 'chatroom'
logging.basicConfig(filename='chatroom.log', level=logging.DEBUG, filemode='w')

class MessageProperties():
    """ Class for holding the properties of a message: type, sent_to, sent_from, rec_time, send_time
    """
    def __init__(self, room_name: str, to_user: str, from_user: str, mess_type: int, sequence_num: int = -1, sent_time: datetime = datetime.now(), rec_time: datetime = datetime.now()) -> None:
        self.__mess_type = mess_type
        self.__room_name = room_name
        self.__to_user = to_user
        self.__from_user = from_user
        self.__sent_time = sent_time
        self.__rec_time = rec_time     
        self.__sequence_num = sequence_num

    def to_dict(self):
        return {'room_name': self.__room_name, 
            'mess_type': self.__mess_type,
            'to_user': self.__to_user, 
            'from_user': self.__from_user,
            'sent_time': self.__sent_time,
            'rec_time': self.__rec_time, 
            'sequence_num': self.__sequence_num,
        } 

    def __str__(self):
        return str(self.to_dict())

    @property
    def sequence_num(self):
        return self.__sequence_num

class ChatMessage():
    """ Class for holding individual messages in a chat thread/queue. 
        Each message a message, Message properties, later a sequence number, timestamp
    """
    def __init__(self, message: str = "", mess_props: MessageProperties = None, rmq_props = None) -> None:
        self.__message = message
        self.__mess_props = mess_props
        self.__rmq_props = rmq_props
        self.__dirty = True

    @property
    def dirty(self):
        return self.__dirty

    @dirty.setter
    def dirty(self, new_value):
        if type(new_value) is bool:
            self.__dirty = new_value       

    @property
    def message(self):
        return self.__message

    @property
    def rmq_props(self):
        return self.__rmq_props

    @property
    def mess_props(self):
        return self.__mess_props

    def to_dict(self):
        """ Controlling getting data from the class in a dictionary. Yes, I know there is a built in __dict__ but I wanted to retain control
        """
        mess_props_dict = self.mess_props.to_dict()
        return {'message': self.message, 'mess_props': mess_props_dict, 'rmq_props': {}}

    def __str__(self):
        return f'Chat Message: {self.message} - message props: {self.mess_props}'

class ChatRoom(deque):
    """ Docstring
        We reuse the constructor for creating new or grabbing an existing instance. If owner_alias is empty and user_alias is not, 
            this is assuming an existing instance. The opposite (owner_alias set and user_alias empty) means we're creating new
            members is always optional, and room_type is only relevant if we're creating new.
    """
    def __init__(self, room_name: str, member_list: UserList = None, owner_alias: str = "", room_type: int = ROOM_TYPE_PRIVATE, create_new: bool = False) -> None:
        super(ChatRoom, self).__init__()
        self.__room_name = room_name
        self.__room_type = room_type
        self.__owner_alias = owner_alias
        if member_list is None:
            self.__user_list = UserList()
        else:
            self.__user_list = member_list
        self.__create_time = datetime.now()
        self.__last_modified_time = self.__create_time
    
        room_meta_data = {
            'room_name': self.__room_name,
            'room_type': self.__room_type,
            'owner_alias': self.__owner_alias,
            #TODO: Figure out how the fuck to add member list
            #'memeber_list': self.__user_list.get_all_users(),
            'create_time': self.__create_time,
            'modify_time': self.__last_modified_time
        }

        # Set up mongo - client, db, collection, sequence_collection
        self.__mongo_client = MongoClient(host='34.94.157.136', port=27017, username='class', password='CPSC313', authSource='detest', authMechanism='SCRAM-SHA-256')
        self.__mongo_db = self.__mongo_client.detest
        self.__mongo_collection = self.__mongo_db.get_collection(room_name) 
        self.__mongo_seq_collection = self.__mongo_db.get_collection("sequence")

        #self.__mongo_room_metadata_collection = self.__mongo_db.get_collection(METADATA_COLLECTION) #Save all room metadata into seperate collection, makes querying for messages in room collections easier

        if self.__mongo_collection is None:
            self.__mongo_collection = self.__mongo_db.create_collection(room_name)
        # Restore from mongo if possible, if not (or we're creating new) then setup properties
        if create_new or self.restore() is False:
            self.__mongo_collection.insert_one(room_meta_data)

    def __get_next_sequence_num(self):
        """ This is the method that you need for managing the sequence. Note that there is a separate collection for just this one document
        """
        sequence_num = self.__mongo_seq_collection.find_one_and_update(
                                                        {'_id': 'userid'},
                                                        {'$inc': {'seq': 1}},
                                                        projection={'seq': True, '_id': False},
                                                        upsert=True,
                                                        return_document=ReturnDocument.AFTER)
        return sequence_num

    #Overriding the queue type put and get operations to add type hints for the ChatMessage type
    def put(self, message: ChatMessage = None) -> None:
        self.appendleft(message)

    # overriding parent and setting block to false so we don't wait for messages if there are none
    def get(self) -> ChatMessage:
        return self.pop()

    def find_message(self, message_text: str) -> ChatMessage:
        pass

    def restore(self) -> bool:
        filter = { "message": { "$regex": ".*?" } }
        if self.__mongo_collection.count_documents == 0:
            return False
        else:
            for document in self.__mongo_collection.find(filter=filter):
                self.put(document['message'])
        
    def persist(self):
        dirty_message_list = []
        for message in self:
            if message.dirty:
                dirty_message_list.append(message.to_dict())
                message.dirty = False
        self.__mongo_collection.insert_many(dirty_message_list)

    def get_messages(self, user_alias: str, num_messages:int=GET_ALL_MESSAGES, return_objects: bool = True):
        # return message texts, full message objects, and total # of messages
        message_text_list = []
        message_object_list = []
        total_num_messages = 0
        filter = { "message": { "$regex": ".*?" } }
        if num_messages != GET_ALL_MESSAGES:
            for document in self.__mongo_collection.find(limit=num_messages, filter=filter).sort("sent_time"):
                total_num_messages += 1
                message_props_dict = document["mess_props"]
                message_props = MessageProperties(room_name=message_props_dict['room_name'], 
                    to_user=message_props_dict['to_user'], 
                    from_user=message_props_dict['from_user'], 
                    mess_type=message_props_dict['mess_type'], 
                    sequence_num=message_props_dict['sequence_num'], 
                    sent_time=message_props_dict['sent_time'], 
                    rec_time=message_props_dict['rec_time'])
                message_obj = ChatMessage(message=document["message"], mess_props=message_props)
                message_text_list.append(document["message"])
                message_object_list.append(message_obj)
        for document in self.__mongo_collection.find(filter).sort("sent_time"):
            total_num_messages += 1
            message_props_dict = document["mess_props"]
            message_props = MessageProperties(room_name=message_props_dict['room_name'], 
                to_user=message_props_dict['to_user'], 
                from_user=message_props_dict['from_user'], 
                mess_type=message_props_dict['mess_type'], 
                sequence_num=message_props_dict['sequence_num'], 
                sent_time=message_props_dict['sent_time'], 
                rec_time=message_props_dict['rec_time'])
            message_obj = ChatMessage(message=document["message"], mess_props=message_props)
            message_text_list.append(document["message"])
            message_object_list.append(message_obj)
        if return_objects:
            return message_text_list, message_object_list, total_num_messages
        else:
            return message_text_list, total_num_messages
        
    def send_message(self, message: str, from_alias: str, mess_props: MessageProperties) -> bool:
        message_obj = ChatMessage(message, mess_props)
        self.put(message_obj)
        self.persist()
        return True

class RoomList():
    """ Note, I chose to use an explicit private list instead of inheriting the list class
    """
    def __init__(self, name: str = DEFAULT_ROOM_LIST_NAME) -> None:
        """ Try to restore from mongo 
        """
        pass

    def create(self, room_name: str, owner_alias: str, member_list: list = None, room_type: int = ROOM_TYPE_PRIVATE) -> ChatRoom:
        pass

    def add(self, new_room: ChatRoom):
        pass

    def find_room_in_metadata(self, room_name: str) -> dict:
        pass

    def get_rooms(self):
        pass

    def get(self, room_name: str) -> ChatRoom:
        pass

    def __find_pos(self, room_name: str) -> int:
        pass
    
    def find_by_member(self, member_alias: str) -> list:
        pass

    def find_by_owner(self, owner_alias: str) -> list:
        pass

    def remove(self, room_name: str):
        pass

    def __persist(self):
        pass

    def __restore(self) -> bool:
        pass