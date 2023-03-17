from threading import Thread
from ..executor import BaseExecutor
from task_system_client import settings
import time
from queue import Queue
from .base import BaseSubscriber
from ..utils.class_loader import load_class


logger = settings.logger


class ThreadExecutor(Thread):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, queue, on_succeed=None, on_failed=None, on_done=None, name='Subscribe'):
        self.queue = queue
        self.on_succeed = on_succeed
        self.on_failed = on_failed
        self.on_done = on_done
        super().__init__(name=name, daemon=True)

    @classmethod
    def run_executor(cls, executor: BaseExecutor):
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

    def run(self):
        while True:
            executor: BaseExecutor = self.queue.get()
            time.sleep(0.1)
            try:
                try:
                    self.run_executor(executor)
                except Exception as e:
                    self.on_failed(executor.schedule, executor, e)
                else:
                    self.on_succeed(executor.schedule, executor)
                self.on_done(executor.schedule, executor)
            except Exception as e:
                logger.exception("Run error: %s", e)


class ThreadSubscriber(BaseSubscriber):

    def __init__(self, name=None, queue=None, thread_num=None):
        super().__init__(name=name)
        thread_subscriber = settings.THREAD_SUBSCRIBER
        self.max_queue_size = thread_subscriber.get('MAX_QUEUE_SIZE', 100)
        self.queue = queue or Queue(maxsize=self.max_queue_size)
        self.thread_num = thread_num or thread_subscriber.get('THREAD_NUM', 2)
        thread_class = thread_subscriber.get('THREAD_CLASS', ThreadExecutor.__module__ + '.' + ThreadExecutor.__name__)
        self._threads = [self.create_thread(thread_class,
                                            name=f'{self.name}_{i}',
                                            queue=self.queue,
                                            on_succeed=self.on_succeed,
                                            on_failed=self.on_failed,
                                            on_done=self.on_done)
                         for i in range(self.thread_num)]

    @classmethod
    def create_thread(cls, thread_class, **kwargs):
        return load_class(thread_class)(**kwargs)

    def run(self):
        get_schedule = self.subscription.get_one
        dispatch = self.dispatcher.dispatch
        while self._state.is_set():
            time.sleep(0.1)
            try:
                if not self.is_runnable():
                    continue
                schedule = get_schedule()
                executor = dispatch(schedule)
                self.run_executor(executor)
            except Exception as e:
                logger.exception("Run error: %s", e)

    def run_executor(self, executor):
        self.queue.put(executor)

    def start(self):
        for t in self._threads:
            t.start()
        super(ThreadSubscriber, self).start()
