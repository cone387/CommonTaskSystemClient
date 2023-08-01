from threading import Thread
from queue import Queue
from ..executor import BaseExecutor
from task_system_client import settings
from .base import BaseClient
from task_system_client.utils.class_loader import load_class


logger = settings.logger


class ThreadExecutor(Thread):
    SUBSCRIPTION = None
    DISPATCHER = None

    def __init__(self, queue, execute=None, on_exception=None, name='Subscribe'):
        self.queue = queue
        self.execute = execute
        self.on_exception = on_exception
        super().__init__(name=name, daemon=True)

    def run(self):
        execute = self.execute
        on_exception = self.on_exception
        while True:
            executor: BaseExecutor = self.queue.get()
            try:
                execute(executor)
            except Exception as e:
                if on_exception:
                    on_exception(e)


class FixedThreadClient(BaseClient):

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
                                            on_schedule_processed=self.on_schedule_processed)
                         for i in range(self.thread_num)]

    @classmethod
    def create_thread(cls, thread_class, **kwargs):
        return load_class(thread_class)(**kwargs)

    def run_executor(self, executor):
        self.queue.put(executor)

    def start(self):
        for t in self._threads:
            t.start()
        super(FixedThreadClient, self).start()


class ThreadPoolClient(BaseClient):

    def __init__(self, name=None):
        super(ThreadPoolClient, self).__init__(name=name)
        self._threads = []

    def is_schedulable(self):
        return self.subscription.qsize() < settings.SEMAPHORE

    def is_executable(self, executor):
        n = len(self._threads)
        if n < settings.SEMAPHORE:
            return True
        free = False
        for t in range(n)[::-1]:
            if not self._threads[t].is_alive():
                self._threads.pop(t)
                free = True
        return free

    def run_executor(self, executor):
        if self.is_executable(executor):
            thread = Thread(target=self.execute, args=(executor,), daemon=True)
            thread.start()
            self._threads.append(thread)
        else:
            self.subscription.put(executor)
