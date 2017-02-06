import unittest
import mock

from fcm_sender.sender import Sender
import fcm_sender


class SenderTest(unittest.TestCase):
    def setUp(self):
        self.sender = Sender()

    def test_existing_sender(self):
        pass

    def test_sender_has_method_send_message_with_only_message(self):
        self.sender.send_message(message="some message")

    def test_send_message_accepts_also_a_topic(self):
        self.sender.send_message(message="some message", topic="some topic")


class TestSendMessage(unittest.TestCase):
    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_uses_requests_to_send_an_http_post_request(self, mock_requests):
        assert mock_requests is fcm_sender.sender.requests

        sender = Sender()
        sender.send_message(message="")
        assert mock_requests.post.called

    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_uses_the_fcm_url(self, mock_requests):
        assert mock_requests is fcm_sender.sender.requests
        expected_fcm_url = 'https://fcm.googleapis.com/fcm/send'

        sender = Sender()
        sender.send_message(message="")
        self.assertIsNotNone(mock_requests.post.call_args[1].get('url'))
        self.assertEqual(mock_requests.post.call_args[1].get('url'), fcm_sender.sender.fcm_url)

