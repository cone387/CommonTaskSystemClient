from task_system_client.utils.module_loading import import_string
from task_system_client import settings
from .base import BaseHandler


if settings.EXCEPTION_HANDLER:
    ExceptionHandler = import_string(settings.EXCEPTION_HANDLER)
else:
    ExceptionHandler = None
