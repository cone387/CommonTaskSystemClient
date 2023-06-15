from task_system_client import settings
from .executor import BaseExecutor
from task_system_client.utils.module_loading import import_string
from cone.utils.classes import ClassManager


Executor: ClassManager = import_string(settings.EXECUTOR)
