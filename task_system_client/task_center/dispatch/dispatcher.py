from task_system_client.executor import BaseExecutor, Executor
from task_system_client.task_center.task import TaskSchedule


class ExecutorNotFound(KeyError):
    pass


class DispatchError(Exception):
    pass


class BaseDispatcher:
    unique_keys = []

    def __init__(self):
        if sorted(self.unique_keys) != sorted(Executor.unique_keys):
            raise ValueError(f'Dispatcher unique_keys({self.unique_keys}) must be equal '
                             f'to Executor.unique_keys({Executor.unique_keys})')

    def dispatch(self, schedule: TaskSchedule) -> 'BaseExecutor':
        raise NotImplementedError


class Dispatcher(BaseDispatcher):

    def dispatch(self, schedule: TaskSchedule) -> 'BaseExecutor':
        params = self.get_dispatch_params(schedule)
        try:
            return Executor(schedule=schedule, **params)
        except KeyError:
            error = 'Dispatch error, no executor for task: %s' % schedule
        except Exception as e:
            error = 'Dispatch error, %s' % e
        executor = BaseExecutor(schedule=schedule)
        executor.result = {"error": error}
        return executor

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        raise NotImplementedError


class FullCategoryAndNameDispatcher(Dispatcher):
    unique_keys = ['category', 'name']

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        parent = task.parent
        names = [task.name]
        while parent:
            names.insert(0, parent.name)
            parent = parent.parent
        unique_name = '-'.join(names)

        if task.category:
            names = [task.category.name]
            parent = task.category.parent
            while parent:
                names.insert(0, parent.name)
                parent = parent.parent
            unique_category = '-'.join(names)
        else:
            unique_category = None

        return {
            "name": unique_name,
            "category": unique_category,
        }


class CategoryAndNameDispatcher(Dispatcher):
    unique_keys = ['category', 'name']

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        return {
            "name": task.name,
            "category": task.category.name if task.category else None,
        }


class NameDispatcher(Dispatcher):
    unique_keys = ['name']

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        return {
            "name": task.name,
        }


class CategoryParentNameDispatcher(Dispatcher):
    unique_keys = ['category', 'parent', 'name']

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        return {
            "name": task.name,
            "parent": task.parent.name if task.parent else None,
            "category": task.category.name if task.category else None,
        }


class CategoryParentAndOptionalNameDispatcher(BaseDispatcher):
    unique_keys = ['category', 'parent', 'name']

    def dispatch(self, schedule: TaskSchedule) -> 'BaseExecutor':
        params = self.get_dispatch_params(schedule)
        try:
            return Executor(schedule=schedule, **params)
        except KeyError:
            try:
                params.pop('name')
                return Executor(schedule=schedule, **params)
            except KeyError:
                error = 'Dispatch error, no executor for task: %s' % schedule
            except Exception as e:
                error = 'Dispatch error, %s' % e
        except Exception as e:
            error = 'Dispatch error, %s' % e
        executor = BaseExecutor(schedule=schedule)
        executor.result = {"error": error}
        return executor

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        return {
            "name": task.name,
            "parent": task.parent.name if task.parent else None,
            "category": task.category.name if task.category else None,
        }


class ParentAndOptionalNameDispatcher(CategoryParentAndOptionalNameDispatcher):
    unique_keys = ['parent', 'name']

    @staticmethod
    def get_dispatch_params(schedule: TaskSchedule):
        task = schedule.task
        return {
            "name": task.name,
            "parent": task.parent.name if task.parent else None,
        }
