import unittest
from fcm_sender.sender import Sender

class SenderTest(unittest.TestCase):
    def test_existing_sender(self):
        sender = Sender()