import unittest
from unittest import TestCase
from constants import *
from users import *

class UserTest(TestCase):
    """ Docstring
    """
    def setUp(self) -> None:
#        super().__init__(methodName)
        self.__cur_users = UserList('test_users')

    @property
    def users(self):
        return self.__cur_users

    def test_adding(self):
        pass

    def test_getting(self):
        pass
    
if __name__ == "__main__":
    unittest.main()