from ...executor import BaseExecutor, Executor
from ..task import TaskSchedule


class DispatchError(KeyError):
    pass


class Dispatcher:

    def dispatch(self, schedule: TaskSchedule) -> 'BaseExecutor':
        params = self.get_dispatch_params(schedule)
        try:
            return Executor(schedule=schedule, **params)
        except KeyError as e:
            error = 'Dispatch error, no executor for task: %s' % schedule
        except Exception as e:
            error = 'Dispatch error, %s' % e
        executor = BaseExecutor(schedule=schedule)
        executor.result = {"error": error}
        return executor

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        return {
            "name": schedule.task.unique_name,
            "category": schedule.task.unique_category,
        }
