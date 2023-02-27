from cone.utils.classes import ClassManager


Executor = ClassManager(name='Executor', unique_keys=['category', 'name'])


class BaseExecutor(object):
    category = None
    name = None

    def __init__(self, task):
        self.task_schedule = task
        self.task = task.task

    def run(self):
        raise NotImplementedError

    def on_success(self):
        pass

    def on_error(self, error):
        pass
