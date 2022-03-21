import json
import requests
import logging
import unittest
from fastapi.testclient import TestClient
from users import *
from constants import *
import room_chat_api

MESSAGES = ["first"]
NUM_MESSAGES = 4

class ChatTest(unittest.TestCase):

    def setUp(self) -> None:
        logging.basicConfig(filename='api_tests.log', encoding='utf-8', level=logging.DEBUG)
        self.client = TestClient(room_chat_api.app)

    def test_send(self):
        """ Testing the send api
        """
        logging.info(f"Inside test_send_public... Posting request... Current Message: {TEST_MESSAGE_1}")
        response = self.client.post(f'/message?room_name=general&message={TEST_MESSAGE_1}&from_alias={NAME1}&to_alias={NAME2}')
        response_json = response.json()
        self.assertEqual(response.status_code, 200)

        logging.info(f"Inside test_send_public... Posting request... Current Message: {TEST_MESSAGE_2}")
        response = self.client.post(f'/message?room_name=general&message={TEST_MESSAGE_2}&from_alias={NAME1}&to_alias={NAME2}')
        response_json = response.json()
        self.assertEqual(response.status_code, 200)

        logging.info(f"Inside test_send_public... Posting request... Current Message: {TEST_MESSAGE_2}")
        response = self.client.post(f'/message?room_name=general&message={TEST_MESSAGE_2}&from_alias={NAME1}&to_alias={NAME2}')
        response_json = response.json()
        self.assertEqual(response.status_code, 200)


        

