import unittest
from fcm_sender.sender import Sender


class SenderTest(unittest.TestCase):
    def test_existing_sender(self):
        sender = Sender()

    def test_sender_has_method_send_message_with_only_message(self):
        sender = Sender()
        sender.send_message(message="some message")

    def test_send_message_accepts_also_a_topic(self):
        sender = Sender()
        sender.send_message(message="some message", topic="some topic")