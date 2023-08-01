from task_system_client.schedule import Schedule
from task_system_client.executor import ExecuteStatus, ScheduleLog
from task_system_client.callback import Callback
import time


class BaseExecutor(object):
    category = None
    parent = None
    name = None

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.task = schedule.task
        self.log = ScheduleLog(schedule)
        self.create_time = time.time()
        self.ttl = self.task.config.get('ttl', 60 * 60)

    @property
    def status(self):
        return self.log.status

    @status.setter
    def status(self, value):
        self.log.status = value

    @property
    def timeout(self):
        return time.time() - self.create_time > self.ttl

    def run(self):
        raise NotImplementedError

    def on_done(self, exception=None):
        schedule = self.schedule
        if schedule.callback:
            trigger_event = schedule.callback['trigger_event']
            if trigger_event == ExecuteStatus.DONE or trigger_event == self.status:
                callback = Callback(
                    name=schedule.callback['name'],
                    config=schedule.callback['config'],
                    executor=self
                )
                callback.start()
        self.status = ExecuteStatus.DONE

    def start(self):
        self.status = ExecuteStatus.RUNNING
        self.run()

    def __hash__(self):
        return hash(self.schedule)
