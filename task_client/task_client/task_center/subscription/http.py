try:
    import requests
except ImportError:
    raise ImportError('requests is required for http subscription, please install requests first')

import logging
import time
from sys import stdout
from .base import BaseSubscription

logger = logging.getLogger(__name__)


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
                stdout.write('[%s]no more task now, wait 1 second...\r' % time.strftime('%Y-%m-%d %H:%M:%S'))
                stdout.flush()
            else:
                stdout.write('[%s]get task error, status code: %s\n' % (
                    time.strftime('%Y-%m-%d %H:%M:%S'), response.json()))
                stdout.flush()
        except Exception as e:
            logger.exception(e)
        time.sleep(1)
        return self.get()
