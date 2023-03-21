from task_system_client.callback.base import BaseCallback, Callback
from task_system_client import settings
import requests


@Callback()
class HttpUploadLogCallback(BaseCallback):

    name = 'Http日志上报'

    def run(self):
        config = settings.HTTP_UPLOAD_LOG_CALLBACK
        url = config['url']
        try:
            res = requests.post(
                url=url,
                headers=config.get('headers', None),
                data=self.executor.generate_log(),
            )
            settings.logger.info('HttpUploadLogCallback: %s', res.text)
        except Exception as e:
            settings.logger.exception('HttpUploadLogCallback error: %s', e)
