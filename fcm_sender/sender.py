import requests

fcm_url = "https://fcm.googleapis.com/fcm/send"


class Sender():
    default_topic = ""

    def send_message(self, message, topic=default_topic):
        try:
            requests.post(url=fcm_url, data={}, headers={})
        except:
            pass