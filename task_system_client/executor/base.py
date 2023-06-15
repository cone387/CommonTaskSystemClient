from cone.utils.classes import ClassManager
from enum import Enum


CategoryNameExecutor = ClassManager(
    path='task_system_client.executor.system',
    name='CategoryNameExecutor',
    unique_keys=['category', 'name']
)

CategoryParentNameExecutor = ClassManager(
    path='task_system_client.executor.system',
    name='CategoryParentNameExecutor',
    unique_keys=['category', 'parent', 'name']
)

ParentNameExecutor = ClassManager(
    path='task_system_client.executor.system',
    name='ParentNameExecutor',
    unique_keys=['parent', 'name']
)

NameExecutor = ClassManager(
    path='task_system_client.executor.system',
    name='NameExecutor', unique_keys=['name']
)


# 执行成功了，但是没有结果
class EmptyResult(Exception):
    pass


# 无需重试的异常, 发生此异常时, 任务将不会重试, 此任务状态为N
class NoRetryException(Exception):
    pass


class TimeoutException(Exception):
    pass


class ExecuteStatus(str, Enum):
    INIT = 'I'
    RUNNING = 'R'
    SUCCEED = 'S'
    EMPTY = 'E'
    ERROR_BUT_NO_RETRY = 'N'
    FAILED = 'F'
    DONE = 'D'
    TIMEOUT = 'T'
