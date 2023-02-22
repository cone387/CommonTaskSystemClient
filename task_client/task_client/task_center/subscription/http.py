import time
from sys import stdout
from .base import BaseSubscription
import requests


class HttpSubscription(BaseSubscription):

    def __init__(self, subscription_url):
        self.subscription_url = subscription_url
        super(HttpSubscription, self).__init__()

    def get(self):
        try:
            response = requests.get(self.subscription_url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                stdout.write('no more task now, wait 1 second...\r')
                stdout.flush()
            else:
                stdout.write('get task error, status code: %s\n' % response.status_code)
                stdout.flush()
        except Exception as e:
            stdout.write('get task error, %s\n' % e)
            stdout.flush()
        time.sleep(1)
        return self.get()
