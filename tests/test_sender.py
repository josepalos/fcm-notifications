import unittest
import mock
import inspect
import json

from fcm_sender.sender import Sender
import fcm_sender


class SenderTest(unittest.TestCase):
    def setUp(self):
        self.sender = Sender()

    @mock.patch('fcm_sender.sender.requests')  # patch used for avoid launching unnecessary requests.
    def test_sender_has_method_send_message_with_only_message(self, _):
        self.sender.send_message(message="some message")

    @mock.patch('fcm_sender.sender.requests')  # patch used for avoid launching unnecessary requests.
    def test_send_message_accepts_also_a_topic(self, _):
        self.sender.send_message(message="some message", topic="some topic")

    @mock.patch('fcm_sender.sender.requests')  # patch used for avoid launching unnecessary requests.
    def test_sender_knows_the_api_secret_key(self, _):
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

        self.topic = 'some_topic'
        self.message = 'some message'

        self.sender = Sender()
        self.sender.send_message(message=self.message, topic=self.topic)
        self.mock_requests = mock_requests

    def test_send_message_uses_requests_to_send_an_http_post_request(self):
        assert self.mock_requests.post.called

    def test_send_message_uses_the_fcm_url(self):
        self.assertIsNotNone(self.mock_requests.post.call_args[1].get('url'))
        self.assertEqual(self.mock_requests.post.call_args[1].get('url'), fcm_sender.sender.fcm_url)

    def test_send_message_puts_data_in_the_request(self):
        self.assertIsNotNone(self.mock_requests.post.call_args[1].get('data'))

    def test_send_message_request_has_headers(self,):
        self.assertIsInstance(self.mock_requests.post.call_args[1].get('headers'), dict)

    def test_send_message_request_has_expected_headers(self):
        headers = self.mock_requests.post.call_args[1].get('headers')
        self.assertIn('Content-Type', headers)
        self.assertEqual(headers.get('Content-Type'), 'application/json')
        self.assertIn('Authorization', headers)
        self.assertEqual(headers.get('Authorization'), 'key={}'.format(self.sender.api_key))

    def test_send_message_sends_correct_request_payload(self):
        payload_raw = self.mock_requests.post.call_args[1].get('data')
        payload = json.loads(payload_raw)
        self.assertIn('to', payload)
        self.assertEqual(payload.get('to'), '/topic/{}'.format(self.topic))
        self.assertIn('data', payload)
        data = payload.get('data')

        self.assertIn('message', data)
        self.assertEqual(data.get('message'), self.message)


class TestServerResponse(unittest.TestCase):
    success_message_response = fcm_sender.sender.requests.Response()
    success_message_response.__setstate__({
        'json': {'message_id': '1023456'},
        'status_code': 200
    })

    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_ok_when_success_response(self, mock_requests):
        mock_requests.post.return_value = self.success_message_response
        sender = Sender()
        sender.send_message('some message', 'some topic')

    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_error_400(self, mock_requests):
        # when an error 400 is received it means invalid fields or invalid json
        sender = Sender()

        error_message_response = fcm_sender.sender.requests.Response()
        error_message_response.status_code = 400
        mock_requests.post.return_value = error_message_response

        with self.assertRaises(ValueError):
            sender.send_message('message', 'topic')

    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_error_401(self, mock_requests):
        # when an error 401 is received, there is an error with the authentication.
        sender = Sender()

        error_message_response = fcm_sender.sender.requests.Response()
        error_message_response.status_code = 401
        mock_requests.post.return_value = error_message_response

        with self.assertRaises(fcm_sender.sender.AuthError):
            sender.send_message('message', 'topic')
