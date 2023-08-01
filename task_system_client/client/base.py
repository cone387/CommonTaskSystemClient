from threading import Event
from task_system_client.schedule.subscription import create_subscription
from task_system_client.dispatch import create_dispatcher, DispatchError
from task_system_client import settings
from task_system_client.handler import create_exception_handler
from task_system_client.handler.log import create_log_engine
from task_system_client.schedule import Schedule
from task_system_client.executor.base import ExecuteStatus, ScheduleLog
from task_system_client.executor import BaseExecutor
from typing import Union
import time
import logging


logger = logging.getLogger(__name__)


class BaseClient(object):
    block_on_subscription = False

    def __init__(self, name='BaseClient'):
        self.name = name
        self._state = Event()
        self.start_time = time.time()
        self.dispatcher = create_dispatcher(settings.DISPATCHER)
        self.subscription = create_subscription(settings.SUBSCRIPTION)
        self.exception_handler = create_exception_handler(settings.EXCEPTION_HANDLER)
        self.log_engine = create_log_engine(settings.LOG_UPLOAD_URL)

    def run_synchronous(self, executor: BaseExecutor):
        exception = None
        try:
            executor.log.result.logs = executor.run()
            executor.status = ExecuteStatus.SUCCEED
        except Exception as e:
            exception = e
            executor.status = getattr(e, 'status', ExecuteStatus.FAILED)
            executor.log.result.logs = str(e)
            logger.exception("%s run error: %s", executor, e)
        executor.on_done(exception=exception)

    def execute(self, executor: BaseExecutor):
        exception = None
        try:
            self.run_synchronous(executor)
        except Exception as e:
            exception = e
        self.on_schedule_processed(executor.schedule, executor, exception)

    def run_executor(self, executor: BaseExecutor):
        """
        :param executor:
        :return:
        """
        self.execute(executor)

    def on_schedule_processed(self, schedule: Schedule, executor: Union[BaseExecutor, None] = None, exception=None):
        """
            Every schedule obtained will go through this method
        """
        if schedule.preserve_log:
            if executor is None:
                # executor is None means the schedule is not dispatched
                log = ScheduleLog(schedule)
                log.status = ExecuteStatus.FAILED
                log.result.logs = str(exception)
                self.log_engine.upload(log)
            else:
                self.log_engine.upload(executor.log)

    def on_exception(self, e):
        """
            any uncaught exception will go through this method
        """
        try:
            self.exception_handler.handle(e)
        except Exception as e:
            logger.exception("exception_handler.handle error: %s", e)

    def is_schedulable(self):
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
                if schedule is None:
                    time.sleep(1)
                    continue
                try:
                    executor = dispatch(schedule)
                except DispatchError as e:
                    logger.error(e)
                    self.on_schedule_processed(schedule, exception=e)
                else:
                    self.run_executor(executor)
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
