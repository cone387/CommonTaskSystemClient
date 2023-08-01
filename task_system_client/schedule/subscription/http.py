try:
    import requests
except ImportError:
    raise ImportError('requests is required for http subscription, please install requests first')

import logging
import time
from sys import stdout
from typing import Union
from .base import Subscription
from task_system_client.schedule import Schedule

logger = logging.getLogger(__name__)


class HttpSubscription(Subscription):

    @classmethod
    def processable(cls, url) -> bool:
        return url.startswith('http')

    def request(self) -> Union[Schedule, None]:
        response = requests.get(self.url, timeout=5, **self.kwargs)
        if response.status_code == 200:
            return Schedule(response.json())
        elif response.status_code == 202:
            stdout.write('[%s]no more schedule now, wait 1 second...\r' % time.strftime('%Y-%m-%d %H:%M:%S'))
            stdout.flush()
        else:
            # 有可能存在500情况是被nginx代理的，所以输出response.text不会错
            stdout.write('[%s]get schedule error, status code: %s\n' % (
                time.strftime('%Y-%m-%d %H:%M:%S'), response.text))
            stdout.flush()
        return None
