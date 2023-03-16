from threading import Event
from ..task_center.subscription import create_subscription
from ..task_center.dispatch import create_dispatcher, DispatchError
from ..executor import BaseExecutor
from ..settings import SUBSCRIPTION, DISPATCHER, logger
import time


class BaseSubscriber(object):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, name='BaseSubscribe'):
        self.name = name
        self._state = Event()
        self.start_time = time.time()
        self.dispatcher = create_dispatcher(self.DISPATCHER or DISPATCHER)
        self.subscription = create_subscription(self.SUBSCRIPTION or SUBSCRIPTION)

    def run_executor(self, executor):
        try:
            executor.run()
        except Exception as e:
            logger.exception("%s run error: %s", executor.schedule, e)
            executor.on_error(e)
        else:
            executor.on_success()

    def on_dispatch_error(self, schedule, e):
        logger.exception("Dispatch %s error: %s", schedule, e)

    def on_execute_error(self, executor, e):
        logger.exception("%s got an unexpected error: %s", executor, e)

    def run(self):
        get_schedule = self.subscription.get_one
        dispatch = self.dispatcher.dispatch
        while self._state.is_set():
            try:
                schedule = get_schedule()
            except Exception as e:
                logger.exception("Get task error: %s", e)
                time.sleep(1)
                continue
            try:
                executor: BaseExecutor = dispatch(schedule)
            except Exception as e:
                self.on_dispatch_error(schedule, e)
            else:
                try:
                    self.run_executor(executor)
                except Exception as e:
                    self.on_execute_error(executor, e)
            time.sleep(0.1)

    def start(self):
        self._state.set()
        self.run()

    def stop(self):
        self._state.clear()
        end_time = time.time()
        logger.info("Subscriber %s run %s seconds", self.name, end_time - self.start_time)
        self.subscription.stop()
