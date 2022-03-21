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
    
    @property
    def alias(self):
        return self.__alias
        
class UserList():
    """ List of users, inheriting list class
    """
    def __init__(self, list_name: str = DEFAULT_USER_LIST_NAME) -> None:
        self.__user_list = {}
        self.__mongo_client = MongoClient('mongodb://34.94.157.136:27017/')
        self.__mongo_db = self.__mongo_client.detest
        self.__mongo_collection = self.__mongo_db.users    
        self.__name = list_name
        if not self.__restore():
            self.__create_time = datetime.now()
    
    def to_dict(self):
        return {'list_name': self.__name, 'user_list': self.__user_list, 'create_time': self.__create_time, 'modify_time': self.__modify_time}

    def register(self, new_alias: str) -> ChatUser:
        """
        """
        new_user = ChatUser(alias=new_alias)
        self.append(new_user)
        return new_user

    def get(self, target_alias: str) -> ChatUser:
        return self.__user_list.get(target_alias, None)

    def get_all_users(self) -> list:
        return self.__user_list.values()

    def append(self, new_user: ChatUser) -> None:
        new_alias = new_user.to_dict()['alias']
        self.__user_list[new_alias] = new_user
        self.__persist()

    def __restore(self) -> bool:
        """ First get the document for the queue itself, then get all documents that are not the queue metadata
        """
        user_list_metadata = self.__mongo_collection.find_one( { 'list_name': self.__name})
        if user_list_metadata:
            restore_user_names = user_list_metadata['user_names']
            self.__name = user_list_metadata['list_name']
            self.__create_time = user_list_metadata['create_time']
            for user_name in restore_user_names:
                user_data = self.__mongo_collection.find_one({ 'alias': user_name})
                self.__user_list[user_name] = ChatUser(alias=user_data['alias'], create_time=user_data['create_time'], modify_time=user_data['modify_time'])
            return True
        return False

    def __persist(self):
        """ First save a document that describes the user list (name of list, create and modify times)
            Second, for each user in the list create and save a document for that user
        """
        metadata = {
            'list_name': self.__name,
            'user_names': list(self.__user_list.keys()),
            'create_time': self.__create_time,
            'modify_time': datetime.now()
        }
        self.__mongo_collection.insert_one(metadata)
        for user in self.__user_list.values():
            self.__mongo_collection.insert_one(user.to_dict())