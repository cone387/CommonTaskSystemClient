from queue import Queue, Empty
from threading import Lock
from ..task import TaskSchedule
from typing import Union


class SubscriptionError(Exception):
    pass


class BaseSubscription:

    queue = Queue()
    lock = Lock()

    def get_one(self, block=True) -> Union[TaskSchedule, None]:
        try:
            return self.queue.get_nowait()
        except Empty:
            with self.lock:
                o = self.get(block=block)
                if isinstance(o, (list, tuple)):
                    for i in o:
                        self.queue.put(i)
                    if o:
                        return o[0]
                    elif not block:
                        return None
                else:
                    return o
        return self.get_one(block=block)

    def get(self, block=True) -> Union[TaskSchedule, None]:
        pass

    def stop(self):
        pass
