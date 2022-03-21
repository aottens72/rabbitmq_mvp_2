import unittest
from unittest import TestCase
from constants import *
from users import *

class UserTest(TestCase):
    """ Class for testing user functionality
    """
    def setUp(self) -> None:
#        super().__init__(methodName)
        self.__cur_users = UserList('test_users')

    @property
    def users(self):
        return self.__cur_users

    def test_adding(self):
        """ Test for register function that adds users
        """
        user1 = self.__cur_users.register(NAME1)
        self.assertEqual(user1.to_dict()['alias'], NAME1)
        
        user2 = self.__cur_users.register(NAME2)
        self.assertEqual(user2.to_dict()['alias'], NAME2)

        user3 = self.__cur_users.register(NAME3)
        self.assertEqual(user3.to_dict()['alias'], NAME3)

    def test_getting(self):
        """ Test to get the users added in previous test
        """
        self.test_adding()
        user1 = self.__cur_users.get(NAME1)
        self.assertEqual(user1.to_dict()['alias'], NAME1)
        
        user2 = self.__cur_users.get(NAME2)
        self.assertEqual(user2.to_dict()['alias'], NAME2)

        user3 = self.__cur_users.get(NAME3)
        self.assertEqual(user3.to_dict()['alias'], NAME3)
    
if __name__ == "__main__":
    unittest.main()
