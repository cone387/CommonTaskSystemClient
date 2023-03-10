from threading import Thread, Event
from ..task_center.subscription import create_subscription
from ..task_center.dispatch import create_dispatcher, DispatchError
from ..executor import BaseExecutor
from ..settings import SUBSCRIPTION, DISPATCHER, logger
import time


class ThreadSubscriber(Thread):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, name='Subscribe'):
        super().__init__(name=name, daemon=True)
        self._state = Event()
        self.start_time = time.time()
        self.dispatcher = create_dispatcher(self.DISPATCHER or DISPATCHER)
        self.subscription = create_subscription(self.SUBSCRIPTION or SUBSCRIPTION)

    def run(self):
        get_schedule = self.subscription.get_one
        dispatch = self.dispatcher.dispatch
        self._state.set()
        while self._state.is_set():
            self._state.wait()
            try:
                schedule = get_schedule()
            except Exception as e:
                logger.exception("Get task error: %s", e)
                time.sleep(1)
                continue

            try:
                executor: BaseExecutor = dispatch(schedule)
            except DispatchError as e:
                logger.info(e)
            except Exception as e:
                logger.exception("Dispatch %s error: %s", schedule, e)
            else:
                try:
                    executor.run()
                except Exception as e:
                    logger.exception("%s run error: %s", schedule, e)
                    executor.on_error(e)
                else:
                    executor.on_success()
            time.sleep(1)

    def stop(self):
        self._state.clear()
        end_time = time.time()
        logger.info("Subscriber %s run %s seconds", self.name, end_time - self.start_time)
        self.subscription.stop()
