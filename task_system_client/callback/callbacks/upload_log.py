from task_system_client.callback.base import BaseCallback, Callback
from task_system_client import settings
import requests
import json
from task_system_client.utils import url as url_utils


class LogEngine:

    def upload(self, log):
        raise NotImplementedError


class HttpLogEngine(LogEngine):
    name = 'Http日志上报'

    def upload(self, log):
        try:
            res = requests.post(
                url=settings.LOG_UPLOAD_URL,
                headers=None,
                json=log,
            )
            settings.logger.info('HttpUploadLogCallback: %s', res.text)
        except Exception as e:
            settings.logger.exception('HttpUploadLogCallback error: %s -> %s', log, e)


class RedisLogEngine(LogEngine):
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

    def upload(self, log):
        try:
            r = self.client.lpush(self.queue, json.dumps(log))
            settings.logger.info('RedisUploadLogCallback -> %s: %s', self.queue, r)
        except Exception as e:
            settings.logger.exception('RedisUploadLogCallback error: %s -> %s', log, e)


@Callback()
class LogUploadCallback(BaseCallback):
    name = '日志上报'

    _engine = None

    @property
    def engine(self):
        if not self._engine:
            if settings.LOG_UPLOAD_URL.startswith('http'):
                LogUploadCallback._engine = HttpLogEngine()
            elif settings.LOG_UPLOAD_URL.startswith('redis'):
                LogUploadCallback._engine = RedisLogEngine()
            else:
                raise ValueError('could not find log engine for %s' % settings.LOG_UPLOAD_URL)
        return self._engine

    def run(self):
        self.engine.upload(self.executor.generate_log())
