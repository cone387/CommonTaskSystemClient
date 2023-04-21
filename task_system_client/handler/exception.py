import requests
from .base import BaseHandler
from task_system_client import settings


class ExceptionHandler(BaseHandler):
    name = 'exception_handler'

    def __init__(self, expected=None):
        self.expected = expected or [Exception]

    def process(self, e):
        pass

    def handle(self, e):
        for p in self.expected:
            if isinstance(e, p):
                self.process(e)
                break

    def __str__(self):
        return self.name


class HttpExceptionUpload(ExceptionHandler):

    def process(self, e):
        return requests.post(settings.EXCEPTION_REPORT_URL, json={
            'error': str(e),
        }).text
