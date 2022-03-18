from datetime import datetime
from unittest import TestCase
import unittest
from constants import *
from room import ChatRoom, MessageProperties, RoomList

PRIVATE_ROOM_NAME = 'eshner'
PUBLIC_ROOM_NAME = 'general'
SENDER_NAME = 'testing'
DEFAULT_PRIVATE_TEST_MESS = 'DE: Test Private Queue at '
DEFAULT_PUBLIC_TEST_MESS = 'DE: Test Public Queue at '
USER_ALIAS = 'testing'

class RoomTest(TestCase):
    """ Docstring
    """
    def setUp(self) -> None:
        pass

    def test_send(self, private_message: str = DEFAULT_PRIVATE_TEST_MESS, public_message: str = DEFAULT_PUBLIC_TEST_MESS) -> bool:
        """ Testing the send message functionality
        """
        pass

    def test_get(self) -> list:
        """ Testing the get messages functionality
        """
        pass

    def test_full(self):
        """ Doing both and make sure that what we sent is in what we get back
        """
        pass

if __name__ == "__main__":
    unittest.main()