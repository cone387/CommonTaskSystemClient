from cone.utils.classes import ClassManager
from task_system_client.schedule import Schedule
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


class AttributeDict(dict):

    def __setattr__(self, key, value):
        self[key] = value
        super(AttributeDict, self).__setattr__(key, value)


class ScheduleLogResult(AttributeDict):
    def __init__(self):
        super().__init__()
        self.logs = None


class ScheduleLog(AttributeDict):

    def __init__(self, schedule: Schedule):
        super().__init__()
        self.schedule = schedule.id
        self.status = ExecuteStatus.INIT
        self.result = ScheduleLogResult()
        self.queue = schedule.queue
        self.schedule_time = schedule.schedule_time.strftime('%Y-%m-%d %H:%M:%S')
        self.generator = schedule.generator


class ExecuteStatus(str, Enum):
    INIT = 'I'
    RUNNING = 'R'
    SUCCEED = 'S'
    EMPTY = 'E'
    ERROR_BUT_NO_RETRY = 'N'
    PARTIAL_FAILED = 'P'
    FAILED = 'F'
    DONE = 'D'
    TIMEOUT = 'T'


# 执行成功了，但是没有结果
class EmptyResult(Exception):

    @property
    def status(self):
        return ExecuteStatus.EMPTY


# 部分失败，部分成功
class PartialFailed(Exception):

    @property
    def status(self):
        return ExecuteStatus.PARTIAL_FAILED.value


# 无需重试的异常, 发生此异常时, 任务将不会重试, 此任务状态为N
class NoRetryException(Exception):

    @property
    def status(self):
        return ExecuteStatus.ERROR_BUT_NO_RETRY


class TimeoutException(Exception):

    @property
    def status(self):
        return ExecuteStatus.TIMEOUT

