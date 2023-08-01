import logging
import traceback
from task_system_client import settings
from .log import create_log_engine

logger = logging.getLogger(__name__)


class ExceptionPrintter:
    name = 'exception_handler'

    def __init__(self, expected=None):
        self.expected = expected or [Exception]

    def process(self, e):
        logger.exception(e)

    def handle(self, e):
        for p in self.expected:
            if isinstance(e, p):
                self.process(e)
                break

    def __str__(self):
        return self.name


class ExceptionUploader(ExceptionPrintter):

    def __init__(self):
        self.log_engine = create_log_engine(settings.EXCEPTION_UPLOAD_URL)
        super(ExceptionUploader, self).__init__()

    def process(self, e):
        super(ExceptionUploader, self).process(e)
        self.log_engine.upload({
            'content': traceback.format_exc(),
        })
