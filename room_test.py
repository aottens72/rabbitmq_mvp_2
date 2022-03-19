from datetime import datetime
from sre_constants import ASSERT
from unittest import TestCase
import unittest
from constants import *
from room import ChatMessage, ChatRoom, MessageProperties, RoomList

PRIVATE_ROOM_NAME = 'eshner'
PUBLIC_ROOM_NAME = 'general'
SENDER_ALIAS = 'testing_sender'
NON_MEMEBER_ALIAS = 'non-member'
DEFAULT_PRIVATE_TEST_MESS = 'DE: Test Private Queue at '
DEFAULT_PUBLIC_TEST_MESS = 'DE: Test Public Queue at '
RECEIVER_ALIAS = 'testing_reciever'
MEMBER_LIST = [SENDER_ALIAS, RECEIVER_ALIAS]

class RoomTest(TestCase):
    """ Docstring
    """
    def setUp(self) -> None:
        self.test_public_room = ChatRoom(PUBLIC_ROOM_NAME, owner_alias=RECEIVER_ALIAS, room_type=ROOM_TYPE_PUBLIC, create_new=True)
        self.test_private_room = ChatRoom(PUBLIC_ROOM_NAME, RECEIVER_ALIAS, ROOM_TYPE_PRIVATE, True)

    def test_send(self, private_message: str = DEFAULT_PRIVATE_TEST_MESS, public_message: str = DEFAULT_PUBLIC_TEST_MESS) -> bool:
        """ Testing the send message functionality
        """
        message_props_public = MessageProperties(PUBLIC_ROOM_NAME, RECEIVER_ALIAS, SENDER_ALIAS, ROOM_TYPE_PUBLIC)
        sent = self.test_public_room.send_message(public_message, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        
        

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