"""
Jacob Ottens
Alex Hollier
Ethan Ching
Evan Henderson

Lab 4 -- Rabbit MVP 2
"""
import pika
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
        """ Getter method to return all of the properties as a dictionary for easy access in other methods
        """
        return {'room_name': self.__room_name, 
            'mess_type': self.__mess_type,
            'to_user': self.__to_user, 
            'from_user': self.__from_user,
            'sent_time': self.__sent_time,
            'rec_time': self.__rec_time, 
            'sequence_num': self.__sequence_num,
        } 

    def __str__(self):
        """ Method to return dictionary as a string
        """
        return str(self.to_dict())

    @property
    def sequence_num(self):
        """ Getter to return the sequence number, Sequence number is essentially the index of the message to judge order
        """
        return self.__sequence_num

class ChatMessage():
    """ Class for holding individual messages in a chat thread/queue. 
        Each message a message, Message properties, later a sequence number, timestamp
        Message properties is an instance of the MessageProperties class above
    """
    def __init__(self, message: str = "", mess_props: MessageProperties = None, rmq_props = None) -> None:
        """ message: the str message stored in the ChatMessage
            mess_props: the MessageProperties of the ChatMessage
            dirty: the persistance status, True means the message needs to be persisted, Not yet in the database
        """
        self.__message = message
        self.__mess_props = mess_props
        self.__rmq_props = rmq_props
        self.__dirty = True

    @property
    def dirty(self):
        """ Gettter for dirty
        """
        return self.__dirty

    @dirty.setter
    def dirty(self, new_value):
        """ Setter for dirty
        """
        if type(new_value) is bool:
            self.__dirty = new_value       

    @property
    def message(self):
        """ Getter for message
        """
        return self.__message

    @property
    def rmq_props(self):
        return self.__rmq_props

    @property
    def mess_props(self):
        """ Getter for Message Properties
        """
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
            
        Class for holding all the Chat messages for a specific chatroom
        Each chatroom has metadata as well as being a deque with Chatmessages pushed on it
        Class uses RMQ to publish the messages
    """
    def __init__(self, room_name: str, member_list: UserList = None, owner_alias: str = "", room_type: int = ROOM_TYPE_PRIVATE, create_new: bool = False) -> None:
        """ init from deque first
            room_name: string name of the 
            room_type: string identifier for either public or private room
            owner_alias: string identifier for room owner
            user_list: UserList containing list of members
            
            Connects to mongo and rabbitmq 
            Sets up exchange for both types of rooms -- fanout for public and direct for private
            Attempts to restore from Mongo, setting dirty flag if unable 
        """
            
            
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
    
        room_meta_data = self.to_dict()

        # Set up mongo - client, db, collection, sequence_collection
        self.__mongo_client = MongoClient(host='34.94.157.136', port=27017, username='class', password='CPSC313', authSource='detest', authMechanism='SCRAM-SHA-256')
        self.__mongo_db = self.__mongo_client.detest
        self.__mongo_collection = self.__mongo_db.get_collection(room_name) 
        self.__mongo_seq_collection = self.__mongo_db.get_collection("sequence")
        if self.__mongo_collection is None:
            self.__mongo_collection = self.__mongo_db.create_collection(room_name)

        self.__rmq_creds = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
        self.__rmq_connection_params = pika.ConnectionParameters(RMQ_HOST, RMQ_PORT, credentials=self.__rmq_creds)
        self.__rmq_connection = pika.BlockingConnection(self.__rmq_connection_params)
        self.__rmq_channel = self.__rmq_connection.channel()
        self.__rmq_exchange_name = room_name + '_exchange'
        self.__rmq_queue = self.__rmq_channel.queue_declare(queue=room_name)
        self.__rmq_queue_name = room_name
        if room_type is ROOM_TYPE_PUBLIC:
            self.__rmq_exchange = self.__rmq_channel.exchange_declare(exchange=self.__rmq_exchange_name, exchange_type='fanout') 
            self.__rmq_channel.queue_bind(exchange=self.__rmq_exchange_name, queue=room_name)
        else:
            self.__rmq_exchange = self.__rmq_channel.exchange_declare(exchange=self.__rmq_exchange_name)
            self.__rmq_channel.queue_bind(exchange=self.__rmq_exchange_name, queue=room_name)
        if self.restore() is True:
            self.__dirty = False
        else:
            self.__create_time = datetime.now()
            self.__last_modified_time = datetime.now()
            self.__dirty = True
        # Restore from mongo if possible, if not (or we're creating new) then setup properties

    def to_dict(self):
        """ Getter to return the chat room metadata as a dict
        """
        return {
            'room_name': self.__room_name,
            'room_type': self.__room_type,
            'owner_alias': self.__owner_alias,
            #TODO: Figure out how the fuck to add member list
            #'memeber_list': self.__user_list.get_all_users(),
            'create_time': self.__create_time,
            'modify_time': self.__last_modified_time
        }
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
        """ appends push a message onto the deque
        """
        self.appendleft(message)
        self.persist()

    # overriding parent and setting block to false so we don't wait for messages if there are none
    def get(self) -> ChatMessage:
        """ return message at the top of the deque
        """
        return self.pop()

    def find_message(self, message_text: str) -> ChatMessage:
        """ query the database to find message passed in and return as a ChatMessage
        """
        filter = {"message": message_text}
        return self.__mongo_collection.find_one(filter=filter)

    def restore(self) -> bool:
        """ check whether or not the room can be restored (AKA whether or not the ChatRoom already exists)
            if the chatroom exists, pull the chatroom metadata and all the messages in the chatroom into the deque
            if the chatroom does not exist return false to begin creating a new chatroom
        """
        room_metadata = self.__mongo_collection.find_one( { 'room_name': { '$exists': 'true'}})
        if room_metadata is None:
            return False
        self.__room_name = room_metadata["room_name"]
        self.__create_time = room_metadata["create_time"]
        self.__modify_time = room_metadata["modify_time"]
        for mess_dict in self.__mongo_collection.find({ 'message': { '$exists': 'true'}}):
            new_mess_props = MessageProperties(
                self.__room_name, 
                mess_dict['mess_props']['to_user'],
                mess_dict['mess_props']['from_user'],
                mess_dict['mess_props']['mess_type'],
                mess_dict['mess_props']['sequence_num'],
                mess_dict['mess_props']['sent_time'],
                mess_dict['mess_props']['rec_time']
            )
            new_message = ChatMessage(mess_dict['message'], new_mess_props, None)
            new_message.dirty = False
            self.put(new_message)
        return True
        
    def persist(self):
        """ if the chatroom is dirty, save the message metadata, and all the messages to the database
        """
        if self.__mongo_collection.find_one({ 'room_name': { '$exists': 'false'}}) is None:
            self.__mongo_collection.insert_one(self.to_dict())
        for message in list(self):
            if message.dirty is True:
                serialized = message.to_dict()
                self.__mongo_collection.insert_one(serialized)
                message.dirty = False

    def get_messages(self, user_alias: str, num_messages:int=GET_ALL_MESSAGES, return_objects: bool = True):
        """ 
        Consumes messages from RMQ equal to or less than num_messages, unless it is equal to the GET_ALL_MESSAGES constant, in which case
        it will consume until it reads a None message
        
        it then returns a list of ChatMessage objects (unless return_objects is set to False), a list of the message bodies and the number of messages returned
        """
        message_obj_list = []
        message_body_list = []
        # return message texts, full message objects, and total # of messages
        logging.info("Starting retreive_messages")
        if self.__rmq_channel.is_closed:
            logging.warning(f'Inside __retrieve messages, the channel is CLOSED!!')
        logging.info(f'Inside retreive_messages, queue is {self.__rmq_queue_name}, exchange: {self.__rmq_exchange_name}, cache: {self}, channel: {self.__rmq_channel}')
        num_mess_received = 0
        for m_f, props, body in self.__rmq_channel.consume(self.__rmq_queue_name, auto_ack=True, inactivity_timeout=2):
            logging.info(f"inside retreive messages, processing a messsage. body = {body}")
            if body != None:
                num_mess_received += 1
                message_body_list.append(body.decode('utf-8'))
                new_mess_props = MessageProperties(
                    self.__room_name, # this is now received, the original will be sent
                    props.headers['_MessageProperties__to_user'],
                    props.headers['_MessageProperties__from_user'],
                    MESS_TYPE_RECEIVED,
                    props.headers['_MessageProperties__sequence_num'],
                    props.headers['_MessageProperties__sent_time'],
                    props.headers['_MessageProperties__rec_time']
                )
                new_message = ChatMessage(body.decode('utf-8'), new_mess_props)
                message_obj_list.append(new_message)
                logging.info(f'Inside retrieve, here is the new chatmessage: {new_message}')
                logging.info(f'Inside retrieve, chatmessage body: {body}\n mess_props: {new_mess_props}\n')
                self.put(new_message)
                if num_mess_received >= num_messages and num_messages is not GET_ALL_MESSAGES:
                    break
            else:
                break
        requeued_messages = self.__rmq_channel.cancel()
        logging.info(f'Called cancel after retreive messages, result of that call is {requeued_messages}')
        if return_objects:
            return message_obj_list, message_body_list, num_mess_received
        else:
            return message_body_list, num_mess_received
        
    def send_message(self, message: str, from_alias: str, mess_props: MessageProperties) -> bool:
        """ push the message onto the queue using the put method after publishing the message using rmq
        """
        try:
            self.__rmq_channel.basic_publish(self.__rmq_exchange_name, 
                                        routing_key=self.__rmq_queue_name, 
                                        properties=pika.BasicProperties(headers=mess_props.__dict__),
                                        body=message, mandatory=True)
            logging.info(f'Publish to messaging server succeeded. Message: {message}')
            self.put(ChatMessage(message=message, mess_props=mess_props))
            return(True)
        except pika.exceptions.UnroutableError:
            logging.debug(f'Message was returned undeliverable. Message: {message} and target queue: {self.rmq_queue}')
            return(False) 

class RoomList():
    """ 
        Class holds a list of chat rooms in a dictionary
        Class is also used to create chatrooms and tye them to specific users roomlist
    """
    def __init__(self, name: str = DEFAULT_ROOM_LIST_NAME) -> None:
        """ 
            name: name of the roomlist
            room_list: dictionary that holds the room name as a string for the key and the Chatroom object as the value
            create_time: datetike for when the roomlist was created, created if restore returns false
        """
        self.__name = name
        self.__mongo_client = MongoClient(host='34.94.157.136', port=27017, username='class', password='CPSC313', authSource='detest', authMechanism='SCRAM-SHA-256')
        self.__mongo_db = self.__mongo_client.detest
        self.__room_list = {}
        self.__mongo_collection = self.__mongo_db["roomlist"]
        if not self.__restore():
            self.__create_time = datetime.now()

    def create(self, room_name: str, owner_alias: str, member_list: list = None, room_type: int = ROOM_TYPE_PRIVATE) -> ChatRoom:
        """ class creates a new chatroom with given metadata and adds the new chatroom to the dictionary using the add method
        """
        new_chatroom = ChatRoom(room_name=room_name, owner_alias=owner_alias, member_list=member_list, room_type=room_type, create_new=True)
        self.add(new_chatroom)

    def add(self, new_room: ChatRoom, new_room_name):
        """ adds given chatroom the chatroom dictionary
        """
        self.__room_list[new_room_name] = new_room
        self.__persist()

    def find_room_in_metadata(self, room_name: str) -> dict:
        """ get the metadata for a chatroom as a dictionary
        """
        return self.__room_list[room_name].to_dict()

    def get_rooms(self):
        """ returns the list of chatrooms
        """
        return self.__room_list.values()

    def get(self, room_name: str) -> ChatRoom:
        """ return given room_name from the chatroom dictionary
        """
        return self.__room_list[room_name]
    
    def find_by_member(self, member_alias: str) -> list:
        # TODO after member list works in jsons
        #for chatroom in self.__room_list.keys():
        #    metadata = self.find_room_in_metadata(chatroom)
        pass

    def find_by_owner(self, owner_alias: str) -> list:
        """ return chatroom by given owner alias
        """
        return_list = []
        for chatroom in self.__room_list.keys():
            metadata = self.find_room_in_metadata(chatroom)
            if metadata['owner_alias'] == owner_alias:
                return_list.append(chatroom)
        return return_list


    def remove(self, room_name: str):
        """ remove chatroom from chatroom dictionary and persists it
        """
        del self.__room_list[room_name]
        self.__persist()

    def __persist(self):
        """
            Uploads the metadata to the room_list collection in the database
            list_name is the specific name of the list
            room_names is the list of chatroom names in the dictionary
            create_time is the tiem created
            modify_time is the time the list was last persisted
        """
        metadata = {
            'list_name': self.__name,
            'room_names': self.__room_list.keys,
            'create_time': self.__create_time,
            'modify_time': datetime.now()
        }
        self.__mongo_collection.insert_one(metadata)


    def __restore(self) -> bool:
        """ loads the metadata for the room_list name from the database into the RoomList object,
            if list_name does not exist return false meaning no RoomList exists
        """
        room_metadata = self.__mongo_collection.find_one( { 'list_name': self.__name})
        if room_metadata:
            restore_room_names = room_metadata['room_names']
            for room_name in restore_room_names:
                self.__room_list[room_name] = ChatRoom(room_name=room_name)
            return True
        return False
