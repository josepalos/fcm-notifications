import unittest
import mock
import inspect

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

    def test_sender_knows_the_api_secret_key(self):
        self.assertIsNotNone(self.sender.api_key)

    @staticmethod
    def get_dict_with_args_and_defaults(method):
        result = dict()

        inspected = inspect.getargspec(method)
        args_list = inspected.args
        default_values = inspected.defaults
        args_with_default_count = len(default_values)

        args_with_no_default = args_list[:-args_with_default_count]
        args_with_default = args_list[-args_with_default_count:]

        for arg in args_with_no_default:
            result[arg] = None

        for arg, default in zip(args_with_default, default_values):
            result[arg] = default

        return result

    @mock.patch('fcm_sender.sender.requests')  # patch used for avoid launching unnecessary requests.
    def test_call_send_message_without_topic_uses_the_default_one(self, _):
        send_message_params_with_defaults = self.get_dict_with_args_and_defaults(self.sender.send_message)
        self.assertIsNotNone(send_message_params_with_defaults.get('topic'))
        self.assertEqual(self.sender.default_topic, send_message_params_with_defaults.get('topic'))


class TestSendMessage(unittest.TestCase):
    @mock.patch('fcm_sender.sender.requests')
    def setUp(self, mock_requests):
        assert mock_requests is fcm_sender.sender.requests
        self.sender = Sender()
        self.sender.send_message(message="", topic="some topic")
        self.mock_requests = mock_requests

    def test_send_message_uses_requests_to_send_an_http_post_request(self):
        assert self.mock_requests.post.called

    def test_send_message_uses_the_fcm_url(self):
        self.assertIsNotNone(self.mock_requests.post.call_args[1].get('url'))
        self.assertEqual(self.mock_requests.post.call_args[1].get('url'), fcm_sender.sender.fcm_url)

    def test_send_message_puts_data_in_the_request(self):
        self.assertIsNotNone(self.mock_requests.post.call_args[1].get('data'))

    def test_request_data_contains_dict_data(self):
        self.assertIsInstance(self.mock_requests.post.call_args[1].get('data'), dict)

    def test_send_message_request_has_headers(self,):
        self.assertIsInstance(self.mock_requests.post.call_args[1].get('headers'), dict)

    def test_send_message_request_has_expected_headers(self):
        headers = self.mock_requests.post.call_args[1].get('headers')
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers.get('Content-Type'), 'application/json')
        self.assertIn('Authorization', headers)
        self.assertEqual(headers.get('Authorization'), 'key={}'.format(self.sender.api_key))
