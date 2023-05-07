from queue import Queue, Empty
from threading import Lock
from ..task import TaskSchedule
from typing import Union
from task_system_client.settings import logger, SEMAPHORE


class SubscriptionError(Exception):
    pass


class BaseSubscription(Queue):
    lock = Lock()

    def request(self) -> Union[TaskSchedule, None]:
        pass

    def try_get(self, block=False) -> Union[TaskSchedule, None]:
        try:
            return self.get(block=block)
        except Empty:
            return None

    def update(self, num=SEMAPHORE):
        with self.lock:
            n = 0
            while n < num:
                try:
                    o = self.request()
                except Exception as e:
                    logger.exception(e)
                    break
                if isinstance(o, (list, tuple)):
                    for i in o:
                        n += 1
                        self.put(i)
                elif o:
                    n += 1
                    self.put(o)
                else:
                    break

    def stop(self):
        pass
