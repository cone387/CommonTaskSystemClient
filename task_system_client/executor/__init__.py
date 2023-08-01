from task_system_client import settings
from task_system_client.utils.module_loading import import_string
from cone.utils.classes import ClassManager
from .base import ExecuteStatus, ScheduleLog
from .executor import BaseExecutor


Executor: ClassManager = import_string(settings.EXECUTOR)
