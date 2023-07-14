import requests
from .base import BaseHandler
from task_system_client import settings
import logging

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
        assert settings.EXCEPTION_REPORT_URL, "EXCEPTION_REPORT_URL is not set"

    def process(self, e):
        logger.exception(e)
        try:
            response = requests.post(settings.EXCEPTION_REPORT_URL, json={
                'content': str(e),
            })
            if response.status_code != 201:
                logger.error("Upload exception error: %s", response.text)
            else:
                logger.info("Upload exception succeed: %s", response.text)
        except Exception as e:
            logger.exception("Upload exception error: %s", e)
