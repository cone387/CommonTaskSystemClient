from cone.utils.classes import ClassManager
from enum import Enum


CategoryNameExecutor = ClassManager(name='CategoryNameExecutor', unique_keys=['category', 'name'])

NameExecutor = ClassManager(name='NameExecutor', unique_keys=['name'])


class ExecuteStatus(str, Enum):
    INIT = 'I'
    RUNNING = 'R'
    SUCCEED = 'S'
    FAILED = 'F'
    DONE = 'D'
    TIMEOUT = 'T'
