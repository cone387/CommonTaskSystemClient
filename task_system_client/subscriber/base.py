from threading import Event
from ..task_center.subscription import create_subscription
from ..task_center.dispatch import create_dispatcher
from ..settings import SUBSCRIPTION, DISPATCHER, logger
from ..handler import ExceptionHandler, BaseHandler
from ..executor.base import EmptyResult, NoRetryException, ExecuteStatus, TimeoutException
import time


class BaseSubscriber(object):
    SUBSCRIPTION = None
    DISPATCHER = None
    block_on_subscription = False

    def __init__(self, name='BaseSubscribe'):
        self.name = name
        self._state = Event()
        self.start_time = time.time()
        self.dispatcher = create_dispatcher(self.DISPATCHER or DISPATCHER)
        self.subscription = create_subscription(self.SUBSCRIPTION or SUBSCRIPTION)
        self.exception_handler = None
        if ExceptionHandler is not None:
            self.exception_handler: BaseHandler = ExceptionHandler()

    def run_synchronous(self, executor):
        try:
            executor.run()
        except EmptyResult:
            executor.execute_status = ExecuteStatus.EMPTY
        except NoRetryException as e:
            executor.execute_status = ExecuteStatus.ERROR_BUT_NO_RETRY
            executor.result['error'] = str(e)
        except TimeoutException as e:
            executor.execute_status = ExecuteStatus.TIMEOUT
            executor.result['error'] = str(e)
        except Exception as e:
            executor.execute_status = ExecuteStatus.FAILED
            executor.result['error'] = str(e)
            logger.exception("%s run error: %s", executor, e)
            on_error = getattr(executor, 'on_error', None)
            if on_error:
                on_error(e)
        else:
            executor.execute_status = ExecuteStatus.SUCCEED
            on_success = getattr(executor, 'on_success', None)
            if on_success:
                on_success()
        on_done = getattr(executor, 'on_done', None)
        if on_done:
            on_done()

    def execute(self, executor):
        try:
            self.run_synchronous(executor)
        except Exception as e:
            self.on_execute_failed(executor.schedule, executor, e)
        else:
            self.on_execute_succeed(executor.schedule, executor)
        self.on_execute_done(executor.schedule, executor)

    def run_executor(self, executor):
        self.execute(executor)

    def on_execute_succeed(self, schedule, executor):
        pass

    def on_execute_failed(self, schedule, executor, e):
        pass

    def on_execute_done(self, schedule, executor):
        pass

    def on_exception(self, e):
        logger.exception("Subscriber %s error: %s", self.name, e)
        if self.exception_handler:
            self.exception_handler.handle(e)

    def is_schedulable(self):
        return True

    def is_executable(self, executor):
        return True

    def run(self):
        subscription = self.subscription
        dispatch = self.dispatcher.dispatch
        block = self.block_on_subscription

        while self._state.is_set():
            time.sleep(0.1)
            try:
                if self.is_schedulable():
                    subscription.update()
                schedule = subscription.try_get(block)
                if not schedule:
                    time.sleep(1)
                    continue
                executor = dispatch(schedule)
                if self.is_executable(executor):
                    self.run_executor(executor)
                else:
                    self.subscription.put(executor.schedule)
            except Exception as e:
                self.on_exception(e)

    def start(self):
        self._state.set()
        self.run()

    def stop(self):
        self._state.clear()
        end_time = time.time()
        logger.info("Subscriber %s run %s seconds", self.name, end_time - self.start_time)
        self.subscription.stop()
