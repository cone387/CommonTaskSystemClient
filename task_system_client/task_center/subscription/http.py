try:
    import requests
except ImportError:
    raise ImportError('requests is required for http subscription, please install requests first')

import logging
import time
from sys import stdout
from .base import BaseSubscription
from ..task import TaskSchedule

logger = logging.getLogger(__name__)


class HttpSubscription(BaseSubscription):

    def __init__(self, subscription_url):
        self.subscription_url = subscription_url
        super(HttpSubscription, self).__init__()

    def get(self, block=True):
        try:
            response = requests.get(self.subscription_url)
            if response.status_code == 200:
                return TaskSchedule(response.json())
            elif response.status_code == 202:
                stdout.write('[%s]no more schedule now, wait 1 second...\r' % time.strftime('%Y-%m-%d %H:%M:%S'))
                stdout.flush()
            else:
                # 有可能存在500情况是被nginx代理的，所以输出response.text不会错
                stdout.write('[%s]get schedule error, status code: %s\n' % (
                    time.strftime('%Y-%m-%d %H:%M:%S'), response.text))
                stdout.flush()
        except Exception as e:
            logger.exception(e)
        if block:
            time.sleep(1)
            return self.get(block=block)
        return None
