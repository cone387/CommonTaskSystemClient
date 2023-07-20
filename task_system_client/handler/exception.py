import requests
from .base import BaseHandler
from task_system_client import settings
import logging
import traceback
import json
from datetime import datetime
from task_system_client.utils import url as url_utils

logger = logging.getLogger(__name__)


class ExceptionHandler(BaseHandler):
    name = 'exception_handler'

    def __init__(self, expected=None):
        self.expected = expected or [Exception]
        self.validate()

    def validate(self):
        pass

    def process(self, e):
        logger.exception(e)

    def handle(self, e):
        for p in self.expected:
            if isinstance(e, p):
                self.process(e)
                break

    def __str__(self):
        return self.name


class HttpExceptionUpload(ExceptionHandler):
    name = 'http_exception_upload'

    def validate(self):
        assert settings.EXCEPTION_UPLOAD_URL, "EXCEPTION_REPORT_URL is not set"

    def process(self, e):
        logger.exception(e)
        try:
            response = requests.post(settings.EXCEPTION_UPLOAD_URL, json={
                'content': traceback.format_exc(),
            })
            if response.status_code >= 300:
                logger.error("Upload exception error: %s", response.text)
            else:
                logger.info("Upload exception succeed: %s", response.text)
        except Exception as e:
            logger.exception("Upload exception error: %s", e)


class RedisExceptionUpload(HttpExceptionUpload):
    _client = None
    queue = None

    @property
    def client(self):
        if not self._client:
            url, params = url_utils.get_split_url_params(settings.EXCEPTION_UPLOAD_URL)
            self.queue = params['queue']
            assert self.queue, "queue is not set"

            import redis
            pool = redis.ConnectionPool.from_url(url)
            self._client = redis.Redis(connection_pool=pool, decode_responses=True)
        return self._client

    def process(self, e):
        logger.exception(e)
        try:
            item = {
                'content': traceback.format_exc(),
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            r = self.client.lpush(self.queue, json.dumps(item))
            settings.logger.info('RedisExceptionUpload -> %s: %s', self.queue, r)
        except Exception as e:
            settings.logger.exception('RedisExceptionUpload error: %s', e)

