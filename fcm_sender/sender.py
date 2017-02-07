import requests

fcm_url = "https://fcm.googleapis.com/fcm/send"


class Sender():
    default_topic = ""
    api_key = ""

    def create_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'key={}'.format(self.api_key)
        }

    def create_data(self, message, topic):
        return {
            'to': '/topic/{}'.format(topic),
            'data': {
                'message': message
            }
        }

    def send_message(self, message, topic=default_topic):
        try:
            requests.post(url=fcm_url, data=self.create_data(message, topic), headers=self.create_headers())
        except:
            pass