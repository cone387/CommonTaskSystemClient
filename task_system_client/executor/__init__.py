from task_system_client import settings
from .executor import BaseExecutor
from task_system_client.utils.module_loading import import_string


Executor = import_string(settings.EXECUTOR)
