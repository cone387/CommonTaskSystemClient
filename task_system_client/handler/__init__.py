from task_system_client.utils.class_loader import load_class
from .base import BaseHandler
from .exception import ExceptionUploader, ExceptionPrintter


def get_exception_handler(handler=None):
    return load_class(handler, ExceptionUploader)


def create_exception_handler(handler=None) -> ExceptionPrintter:
    return get_exception_handler(handler)()
