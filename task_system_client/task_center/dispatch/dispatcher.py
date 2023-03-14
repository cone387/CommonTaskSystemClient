from ...executor import BaseExecutor, Executor
from ..task import TaskSchedule


class DispatchError(KeyError):
    pass


class Dispatcher:

    def dispatch(self, schedule) -> 'BaseExecutor':
        schedule = TaskSchedule(schedule)
        params = self.get_dispatch_params(schedule)
        try:
            return Executor(schedule=schedule, **params)
        except KeyError:
            raise DispatchError('Dispatch error, no executor for task: %s' % params)

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        return {
            "name": schedule.task.unique_name,
            "category": schedule.task.unique_category,
        }
