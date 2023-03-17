from task_system_client.callback.base import BaseCallback, Callback
from task_system_client import settings
import requests


@Callback()
class HttpUploadLogCallback(BaseCallback):

    name = 'Http日志上报'

    def run(self):
        config = settings.HTTP_UPLOAD_LOG_CALLBACK
        url = config['url']
        requests.post(
            url=url,
            headers=config.get('headers', None),
            data=self.executor.generate_log(),
        )
