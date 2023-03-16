from task_system_client.task_center.task import TaskSchedule


class BaseExecutor(object):
    category = None
    name = None

    def __init__(self, schedule: TaskSchedule):
        self.schedule = schedule
        self.task = schedule.task

    def run(self):
        raise NotImplementedError

    def on_success(self):
        pass

    def on_error(self, error):
        pass

    def __hash__(self):
        return hash(self.schedule)
