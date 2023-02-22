from cone.utils.classes import ClassManager


Executor = ClassManager(path='task_client/executor/executors', unique_keys=['category', 'name'], )


class BaseExecutor(object):
    category = None
    name = None

    def __init__(self, task):
        self.task_schedule = task
        self.task = task.task

    def process(self):
        pass
