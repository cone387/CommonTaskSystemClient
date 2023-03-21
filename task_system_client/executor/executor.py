from task_system_client.task_center.task import TaskSchedule
from .base import ExecuteStatus
from task_system_client.callback import Callback
import time


class BaseExecutor(object):
    category = None
    name = None

    def __init__(self, schedule: TaskSchedule):
        self.schedule = schedule
        self.task = schedule.task
        self.result = {}
        self.execute_status = ExecuteStatus.INIT
        self.create_time = time.time()
        self.ttl = self.task.config.get('ttl', 60 * 60)

    @property
    def timeout(self):
        return time.time() - self.create_time > self.ttl

    def generate_log(self):
        return {
            "schedule": self.schedule.schedule_id,
            "status": self.execute_status.value,
            "result": self.result,
            "schedule_time": self.schedule.schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
        }

    def run(self):
        raise NotImplementedError

    def on_success(self):
        self.execute_status = ExecuteStatus.SUCCEED

    def on_error(self, error):
        self.execute_status = ExecuteStatus.FAILED

    def on_done(self):
        schedule = self.schedule
        if schedule.callback:
            trigger_event = schedule.callback['trigger_event']
            if trigger_event == ExecuteStatus.DONE or trigger_event == self.execute_status:
                callback = Callback(
                    name=schedule.callback['name'],
                    config=schedule.callback['config'],
                    executor=self
                )
                callback.start()
        self.execute_status = ExecuteStatus.DONE

    def start(self):
        self.execute_status = ExecuteStatus.RUNNING
        self.run()

    def __hash__(self):
        return hash(self.schedule)
