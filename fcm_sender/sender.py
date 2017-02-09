import requests
import json

fcm_url = 'https://fcm.googleapis.com/fcm/send'


class AuthError(Exception):
    def __init__(self, message):
        super(AuthError, self).__init__(message)
        self.message = message


class UnavailableServiceError(Exception):
    def __init__(self):
        super(UnavailableServiceError, self).__init__()


class Sender():
    default_topic = ''
    api_key = ''

    def create_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'key={}'.format(self.api_key)
        }

    def create_data(self, message, topic):
        return json.dumps({
            'to': '/topics/{}'.format(topic),
            'data': {
                'message': message
            }
        })

    def send_message(self, message, topic=default_topic):
        response = requests.post(url=fcm_url, data=self.create_data(message, topic), headers=self.create_headers())
        if response.status_code == 400:
            raise ValueError
        elif response.status_code == 401:
            raise AuthError('Error on the authentication')
        elif 500 <= response.status_code <= 599:
            raise UnavailableServiceError
        else:
            json_content = response.json
            if 'error' in json_content:
                raise UnavailableServiceError
