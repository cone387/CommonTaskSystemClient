from abc import ABC
from task_system_client.executor.executor import BaseExecutor


class SystemExecutor(BaseExecutor, ABC):
    category = '系统任务'
