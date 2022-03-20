from datetime import datetime
from sre_constants import ASSERT
from unittest import TestCase
import unittest
from constants import *
from room import ChatMessage, ChatRoom, MessageProperties, RoomList

PRIVATE_ROOM_NAME = 'EJEA'
PUBLIC_ROOM_NAME = 'general'
SENDER_ALIAS = 'testing_sender'
NON_MEMEBER_ALIAS = 'non-member'
DEFAULT_PRIVATE_TEST_MESS = 'Test private'
DEFAULT_PUBLIC_TEST_MESS = 'Test public'
EMPTY_STRING = ""
NUM_STRING = "12345"
NEW_LINE = "Yo\nWhat's up\n\n"
DIFFERENT_LANGUAGE_CHARACTERS = "త్వరిత గోధుమ నక్క సోమరి కుక్కపైకి దూకుతుంది"
RECEIVER_ALIAS = 'testing_reciever'
MEMBER_LIST = [SENDER_ALIAS, RECEIVER_ALIAS]
PRIVATE_PROPS = message_props_private = MessageProperties(PRIVATE_ROOM_NAME, RECEIVER_ALIAS, SENDER_ALIAS, MESS_TYPE_SENT)
PUBLIC_PROPS = message_props_public = MessageProperties(PUBLIC_ROOM_NAME, RECEIVER_ALIAS, SENDER_ALIAS, MESS_TYPE_SENT)


class RoomTest(TestCase):
    """ Docstring
    """
    def setUp(self) -> None:
        self.test_public_room = ChatRoom(PUBLIC_ROOM_NAME, owner_alias=RECEIVER_ALIAS, 
            room_type=ROOM_TYPE_PUBLIC, create_new=True)
        self.test_private_room = ChatRoom(room_name=PRIVATE_ROOM_NAME, owner_alias=RECEIVER_ALIAS, 
            room_type=ROOM_TYPE_PRIVATE, create_new=True)

    def test_send(self, private_message: str = DEFAULT_PRIVATE_TEST_MESS, public_message: str = DEFAULT_PUBLIC_TEST_MESS) -> bool:
        """ Testing the send message functionality
        Sends standard test messages, an empty string, a number string, a string with newline characters, 
        and a string with non-english characters
        """

        sent = self.test_public_room.send_message(public_message, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_public_room.send_message(EMPTY_STRING, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_public_room.send_message(NUM_STRING, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_public_room.send_message(NEW_LINE, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_public_room.send_message(DIFFERENT_LANGUAGE_CHARACTERS, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        
        sent = self.test_private_room.send_message(private_message, SENDER_ALIAS, message_props_private)
        self.assertTrue(sent)
        sent = self.test_private_room.send_message(EMPTY_STRING, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_private_room.send_message(NUM_STRING, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_private_room.send_message(NEW_LINE, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        sent = self.test_private_room.send_message(DIFFERENT_LANGUAGE_CHARACTERS, SENDER_ALIAS, message_props_public)
        self.assertTrue(sent)
        return sent
        

    def test_get(self) -> list:
        """ Testing the get messages functionality
        """
        self.test_send()
        message_objects, message_bodies, num_messages = self.test_public_room.get_messages(RECEIVER_ALIAS)
        self.assertEqual(len(message_objects), len(message_bodies))
        self.assertEqual(num_messages, len(message_bodies))
        self.assertGreater(num_messages, 0)

        self.test_send()
        message_bodies, num_messages = self.test_public_room.get_messages(RECEIVER_ALIAS, return_objects=False)
        self.assertEqual(num_messages, len(message_bodies))
        self.assertGreater(num_messages, 0)

        self.test_send()
        message_objects, message_bodies, num_messages = self.test_public_room.get_messages(RECEIVER_ALIAS, NUM_MESSAGES_TO_GET)
        self.assertLessEqual(num_messages, NUM_MESSAGES_TO_GET)

        self.test_send()
        message_objects, message_bodies, num_messages = self.test_private_room.get_messages(RECEIVER_ALIAS)
        self.assertEqual(len(message_objects), len(message_bodies))
        self.assertEqual(num_messages, len(message_bodies))
        self.assertGreater(num_messages, 0)

        self.test_send()
        message_bodies, num_messages = self.test_private_room.get_messages(RECEIVER_ALIAS, return_objects=False)
        self.assertEqual(num_messages, len(message_bodies))
        self.assertGreater(num_messages, 0)

        self.test_send()
        message_objects, message_bodies, num_messages = self.test_private_room.get_messages(RECEIVER_ALIAS, NUM_MESSAGES_TO_GET)
        self.assertLessEqual(num_messages, NUM_MESSAGES_TO_GET)
        return message_bodies

    def test_full(self):
        """ Doing both and make sure that what we sent is in what we get back
        """
        self.test_public_room.send_message(DEFAULT_PUBLIC_TEST_MESS, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_public_room.send_message(EMPTY_STRING, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_public_room.send_message(NUM_STRING, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_public_room.send_message(DIFFERENT_LANGUAGE_CHARACTERS, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_public_room.send_message(NEW_LINE, SENDER_ALIAS, PUBLIC_PROPS)
        message_objs, message_bodies, num_messages = self.test_public_room.get_messages(RECEIVER_ALIAS, 10)
        self.assertIn(DEFAULT_PUBLIC_TEST_MESS, message_bodies)
        self.assertIn(EMPTY_STRING, message_bodies)
        self.assertIn(NUM_STRING, message_bodies)
        self.assertIn(DIFFERENT_LANGUAGE_CHARACTERS, message_bodies)
        self.assertIn(NEW_LINE, message_bodies)

        self.test_private_room.send_message(DEFAULT_PUBLIC_TEST_MESS, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_private_room.send_message(EMPTY_STRING, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_private_room.send_message(NUM_STRING, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_private_room.send_message(DIFFERENT_LANGUAGE_CHARACTERS, SENDER_ALIAS, PUBLIC_PROPS)
        self.test_private_room.send_message(NEW_LINE, SENDER_ALIAS, PUBLIC_PROPS)
        message_objs, message_bodies, num_messages = self.test_public_room.get_messages(RECEIVER_ALIAS, 10)
        self.assertIn(DEFAULT_PUBLIC_TEST_MESS, message_bodies)
        self.assertIn(EMPTY_STRING, message_bodies)
        self.assertIn(NUM_STRING, message_bodies)
        self.assertIn(DIFFERENT_LANGUAGE_CHARACTERS, message_bodies)
        self.assertIn(NEW_LINE, message_bodies)


if __name__ == "__main__":
    unittest.main()