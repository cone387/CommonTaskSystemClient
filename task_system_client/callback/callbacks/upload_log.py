from task_system_client.callback.base import BaseCallback, Callback
from task_system_client import settings
import requests
import json
from task_system_client.utils import url as url_utils


@Callback()
class HttpUploadLogCallback(BaseCallback):

    name = 'Http日志上报'

    def run(self):
        log = self.executor.generate_log()
        try:
            res = requests.post(
                url=settings.LOG_UPLOAD_URL,
                headers=None,
                json=self.executor.generate_log(),
            )
            settings.logger.info('HttpUploadLogCallback: %s', res.text)
        except Exception as e:
            settings.logger.exception('HttpUploadLogCallback error: %s -> %s', log, e)


@Callback()
class RedisUploadLogCallback(BaseCallback):
    name = 'Redis日志上报'
    _client = None
    queue = None

    @property
    def client(self):
        if not self._client:
            url, params = url_utils.get_split_url_params(settings.LOG_UPLOAD_URL)
            self.queue = params['queue']
            assert self.queue, "queue is not set"

            import redis
            pool = redis.ConnectionPool.from_url(url)
            self._client = redis.Redis(connection_pool=pool, decode_responses=True)
        return self._client

    def run(self):
        log = self.executor.generate_log()
        try:
            r = self.client.lpush(self.queue, json.dumps(log))
            settings.logger.info('RedisUploadLogCallback -> %s: %s', self.queue, r)
        except Exception as e:
            settings.logger.exception('RedisUploadLogCallback error: %s -> %s', log, e)
