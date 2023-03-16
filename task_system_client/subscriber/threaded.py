from threading import Thread
from ..executor import BaseExecutor
from task_system_client import settings
import time
from queue import PriorityQueue
from .base import BaseSubscriber
from ..utils.class_loader import load_class


logger = settings.logger


class ThreadExecutor(Thread):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, queue, name='Subscribe'):
        self.queue = queue
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
        on_complete = getattr(executor, 'on_complete', None)
        if on_complete:
            on_complete()

    def run(self):
        while True:
            executor: BaseExecutor = self.queue.get()
            self.run_executor(executor)
            time.sleep(0.1)


class ThreadSubscriber(BaseSubscriber):

    def __init__(self, name=None, queue=None, thread_num=None):
        super().__init__(name=name)
        thread_subscriber = settings.THREAD_SUBSCRIBER
        self.max_queue_size = thread_subscriber.get('MAX_QUEUE_SIZE', 100)
        self.queue = queue or PriorityQueue(maxsize=self.max_queue_size)
        self.thread_num = thread_num or thread_subscriber.get('THREAD_NUM', 2)
        thread_class = thread_subscriber.get('THREAD_CLASS', ThreadExecutor.__module__ + '.' + ThreadExecutor.__name__)
        self._threads = [self.create_thread(thread_class,
                                            name=f'{self.name}_{i}',
                                            queue=self.queue
                                            ) for i in range(self.thread_num)]

    @classmethod
    def create_thread(cls, thread_class, **kwargs):
        return load_class(thread_class)(**kwargs)

    def run_executor(self, executor):
        self.queue.put(executor)

    def is_fully_loaded(self):
        return self.queue.qsize() >= self.max_queue_size

    def on_fully_loaded(self):
        pass

    def on_not_idle(self):
        pass

    def is_not_idle(self):
        pass

    def run(self):
        get_schedule = self.subscription.get_one
        dispatch = self.dispatcher.dispatch
        is_fully_loaded = self.is_fully_loaded
        self._state.set()
        while self._state.is_set():
            time.sleep(0.1)
            if is_fully_loaded():
                self.on_fully_loaded()
                continue
            if self.is_not_idle():
                self.on_not_idle()
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

    def start(self):
        for t in self._threads:
            t.start()
        self.run()
