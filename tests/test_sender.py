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
        self.assertEqual(fcm_sender.sender.DEFAULT_TOPIC, send_message_params_with_defaults.get('topic'))


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
        self.assertEqual(payload.get('to'), '/topics/{}'.format(self.topic))
        self.assertIn('data', payload)
        data = payload.get('data')

        self.assertIn('message', data)
        self.assertEqual(data.get('message'), self.message)


class TestServerResponse(unittest.TestCase):
    @staticmethod
    def create_response(status_code, json_content=None):
        response = fcm_sender.sender.requests.Response()
        response.status_code = status_code
        if json_content is not None:
            response.json = lambda: json_content  # correct this

        print "Mocked content: %s" % response.content
        return response

    def check_response_raises_exception(self, response, exception):
        with mock.patch('fcm_sender.sender.requests') as mock_requests:
            mock_requests.post.return_value = response

            sender = Sender()

            with self.assertRaises(exception):
                sender.send_message('message', 'topic')

    @classmethod
    def setUpClass(cls):
        cls.success_message_response = cls.create_response(200, {'message_id': '1023456'})

    @mock.patch('fcm_sender.sender.requests')
    def test_send_message_ok_when_success_response(self, mock_requests):
        mock_requests.post.return_value = self.success_message_response
        sender = Sender()
        sender.send_message('some message', 'some topic')

    def test_send_message_error_400_raises_ValueError(self):
        error_message_response = self.create_response(400)
        self.check_response_raises_exception(error_message_response, ValueError)

    def test_send_message_error_401_raises_AuthError(self):
        error_message_response = self.create_response(401)
        self.check_response_raises_exception(error_message_response, fcm_sender.sender.AuthError)

    def test_response_with_5XX_raises_an_UnavailableServiceError(self):
        for code in range(500, 599):
            error_message_response = self.create_response(code)
            self.check_response_raises_exception(error_message_response, fcm_sender.sender.UnavailableServiceError)

    def response_200_with_unavailable_service_errors_raises_UnavailableServiceError(self, error_message):
        error_message_response = self.create_response(200, {'error': error_message})
        self.check_response_raises_exception(error_message_response, fcm_sender.sender.UnavailableServiceError)

    def test_response_200_but_data_contains_error_Unavailable_raises_an_UnavailableServiceError(self):
        self.response_200_with_unavailable_service_errors_raises_UnavailableServiceError('Unavailable')

    def test_response_200_but_data_contains_error_InternalServerError_raises_an_UnavailableServiceError(self):
        self.response_200_with_unavailable_service_errors_raises_UnavailableServiceError('InternalServerError')

    def test_response_200_but_data_contains_error_TopicMessageRateExceeded_raises_an_UnavailableServiceError(self):
        self.response_200_with_unavailable_service_errors_raises_UnavailableServiceError('TopicMessageRateExceeded')
