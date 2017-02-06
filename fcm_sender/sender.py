import requests

fcm_url = "https://fcm.googleapis.com/fcm/send"


class Sender():
    def send_message(self, message, topic=""):
        try:
            requests.post(url=fcm_url, data={})
        except:
            pass