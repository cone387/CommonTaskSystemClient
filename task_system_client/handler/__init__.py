from task_system_client import settings
from task_system_client.utils.class_loader import load_class
from .base import BaseHandler
from .exception import ExceptionHandler


def get_exception_handler(handler=None):
    return load_class(handler, ExceptionHandler)


def create_exception_handler(handler=None) -> ExceptionHandler:
    return get_exception_handler(handler or settings.EXCEPTION_HANDLER)()
