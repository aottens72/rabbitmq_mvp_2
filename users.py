import queue
from datetime import date, datetime
from pymongo import MongoClient
from constants import *
        
class ChatUser():
    """ class for users of the chat system. Users must be registered 
    """
    def __init__(self, alias: str, user_id = None, create_time: datetime = datetime.now(), modify_time: datetime = datetime.now()) -> None:
        self.__alias = alias
        self.__user_id = user_id 
        self.__create_time = create_time
        self.__modify_time = modify_time
        if self.__user_id is not None:
            self.__dirty = False
        else:
            self.__dirty = True

    def to_dict(self):
        return {
                'alias': self.__alias,
                'create_time': self.__create_time,
                'modify_time': self.__modify_time
        }
        
class UserList():
    """ List of users, inheriting list class
    """
    def __init__(self, list_name: str = DEFAULT_USER_LIST_NAME) -> None:
        self.__user_list = list()
        self.__mongo_client = MongoClient('mongodb://34.94.157.136:27017/')
        self.__mongo_db = self.__mongo_client.detest
        self.__mongo_collection = self.__mongo_db.users    
        if self.__restore() is True:
#            raise Exception('No name and no document to restore')
            self.__dirty = False
        else:
            self.__name = list_name
            self.__create_time = datetime.now()
            self.__modify_time = datetime.now()
            self.__dirty = True
    
    def register(self, new_alias: str) -> ChatUser:
        """
        """
        pass

    def get(self, target_alias: str) -> ChatUser:
        pass

    def get_all_users(self) -> list:
        pass

    def append(self, new_user: ChatUser) -> None:
        pass

    def __restore(self) -> bool:
        """ First get the document for the queue itself, then get all documents that are not the queue metadata
        """
        pass

    def __persist(self):
        """ First save a document that describes the user list (name of list, create and modify times)
            Second, for each user in the list create and save a document for that user
        """
        pass