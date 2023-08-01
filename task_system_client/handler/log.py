import logging
import requests
import json
from task_system_client.utils import url as url_utils
from task_system_client.utils.class_loader import load_class
from task_system_client.settings import LOG_ENGINE


logger = logging.getLogger(__name__)


class BaseLogEngine:

    def __init__(self, log_upload_url):
        self.log_upload_url = log_upload_url
        assert self.log_upload_url, "log_upload_url is not set"

    def upload(self, log):
        raise NotImplementedError


class HttpLogEngine(BaseLogEngine):
    name = 'Http日志上报'

    def upload(self, log):
        try:
            res = requests.post(
                url=self.log_upload_url,
                headers=None,
                json=log,
            )
            logger.info('HttpUploadLogCallback: %s', res.text)
        except Exception as e:
            logger.exception('HttpUploadLogCallback error: %s -> %s', log, e)


class RedisLogEngine(BaseLogEngine):
    name = 'Redis日志上报'
    _client = None
    queue = None

    @property
    def client(self):
        if not self._client:
            url, params = url_utils.get_split_url_params(self.log_upload_url)
            self.queue = params['queue']
            assert self.queue, "queue is not set"

            import redis
            pool = redis.ConnectionPool.from_url(url)
            self._client = redis.Redis(connection_pool=pool, decode_responses=True)
        return self._client

    def upload(self, log):
        try:
            r = self.client.lpush(self.queue, json.dumps(log))
            logger.info('RedisUploadLogCallback -> %s: %s', self.queue, r)
        except Exception as e:
            logger.exception('RedisUploadLogCallback error: %s -> %s', log, e)


class LogEngine(BaseLogEngine):
    name = '日志上报'

    _engine = None

    @property
    def engine(self):
        if not self._engine:
            if self.log_upload_url.startswith('http'):
                LogEngine._engine = HttpLogEngine(self.log_upload_url)
            elif self.log_upload_url.startswith('redis'):
                LogEngine._engine = RedisLogEngine(self.log_upload_url)
            else:
                raise ValueError('could not find log engine for %s' % self.log_upload_url)
        return self._engine

    def upload(self, log: dict):
        self.engine.upload(log)


def create_log_engine(*args, **kwargs) -> BaseLogEngine:
    return load_class(LOG_ENGINE, LogEngine)(*args, **kwargs)
