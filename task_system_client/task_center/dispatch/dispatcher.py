from ...executor import BaseExecutor, Executor
from ..task import TaskSchedule


class DispatchError(KeyError):
    pass


class Dispatcher:

    def dispatch(self, task) -> 'BaseExecutor':
        schedule = TaskSchedule(task)
        try:
            return Executor(category=schedule.task.unique_category,
                            name=schedule.task.unique_name,
                            schedule=schedule)
        except KeyError:
            raise DispatchError('Dispatch error, no executor for task: %s:%s' % (
                schedule.task.unique_category, schedule.task.unique_name
            ))
