import requests

fcm_url = "https://fcm.googleapis.com/fcm/send"


class Sender():
    default_topic = ""
    api_key = ""

    def send_message(self, message, topic=default_topic):
        try:
            requests.post(url=fcm_url, data={}, headers={'Content-Type': 'application/json', 'Authorization': 'key=' + self.api_key})
        except:
            pass