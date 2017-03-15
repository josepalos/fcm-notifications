import requests
import json
import os
import configure

fcm_url = 'https://fcm.googleapis.com/fcm/send'
DEFAULT_TOPIC = 'global'

class AuthError(Exception):
    def __init__(self, message):
        super(AuthError, self).__init__(message)
        self.message = message


class UnavailableServiceError(Exception):
    def __init__(self):
        super(UnavailableServiceError, self).__init__()


def get_configuration():
    if not os.path.isfile(configure.CONFIG_FILENAME):
        print 'The sender is not configured. Please enter the information below:'
        configure.main()

    with open(configure.CONFIG_FILENAME, 'r') as config_file:
        content = config_file.read()
        marker_pos = content.find('\0')
        api_key = content[:marker_pos]
        sender_id = content[marker_pos+1:]

    return api_key, sender_id


class Sender():
    def __init__(self):
        (self.api_key, self.sender_id) = get_configuration()
    
    def create_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'key={}'.format(self.api_key)
        }

    def create_data(self, message, topic):
        return json.dumps({
            'to': '/topics/{}'.format(topic),
            'data': {
                'message': message,
                'sender_id': self.sender_id
            }
        })

    def send_message(self, message, topic=DEFAULT_TOPIC):
        response = requests.post(url=fcm_url, data=self.create_data(message, topic), headers=self.create_headers())
        if response.status_code == 400:
            raise ValueError
        elif response.status_code == 401:
            raise AuthError('Error on the authentication')
        elif 500 <= response.status_code <= 599:
            raise UnavailableServiceError
        else:
            json_content = response.json()
            if 'error' in json_content:
                raise UnavailableServiceError
            else:
                print 'Message sent with id %s to topic %s' % (json_content.get('message_id'), topic)
