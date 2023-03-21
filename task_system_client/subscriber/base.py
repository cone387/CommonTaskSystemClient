from threading import Event
from ..task_center.subscription import create_subscription
from ..task_center.dispatch import create_dispatcher
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
            logger.exception("%s run error: %s", executor, e)
            on_error = getattr(executor, 'on_error', None)
            if on_error:
                on_error(e)
        else:
            on_success = getattr(executor, 'on_success', None)
            if on_success:
                on_success()
        on_done = getattr(executor, 'on_done', None)
        if on_done:
            on_done()

    def on_succeed(self, schedule, executor):
        logger.info("succeed: %s", executor)

    def on_failed(self, schedule, executor, e):
        logger.info("failed: %s, %s", executor, e)

    def on_done(self, schedule, executor):
        logger.info("done: %s", executor)

    def is_schedulable(self):
        return True

    def is_executable(self, schedule):
        return True

    def run(self):
        get_schedule = self.subscription.get_one
        dispatch = self.dispatcher.dispatch

        while self._state.is_set():
            time.sleep(0.1)
            try:
                if not self.is_schedulable():
                    time.sleep(1)
                    continue
                schedule = get_schedule()
                executor = dispatch(schedule)
                if not self.is_executable(executor):
                    continue
                try:
                    self.run_executor(executor)
                except Exception as e:
                    self.on_failed(schedule, executor, e)
                else:
                    self.on_succeed(schedule, executor)
                self.on_done(schedule, executor)
            except Exception as e:
                logger.exception("Run error: %s", e)

    def start(self):
        self._state.set()
        self.run()

    def stop(self):
        self._state.clear()
        end_time = time.time()
        logger.info("Subscriber %s run %s seconds", self.name, end_time - self.start_time)
        self.subscription.stop()
