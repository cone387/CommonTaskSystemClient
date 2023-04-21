from queue import Queue, Empty
from threading import Lock
from ..task import TaskSchedule
from typing import Union, List, Tuple
from task_system_client.settings import SEMAPHORE


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
                objects = self.get_many(block=block)
                o = None
                if objects:
                    o = objects.pop(0)
                for i in objects:
                    self.queue.put(i)
                if o:
                    return o
                elif not block:
                    return None
        return self.get_one(block=block)

    def get(self, block=True) -> Union[TaskSchedule, List, Tuple, None]:
        pass

    def get_many(self, block=True) -> List:
        objects = []
        while len(objects) < SEMAPHORE:
            o = self.get(block=False)
            if isinstance(o, (list, tuple)):
                for i in o:
                    objects.append(i)
            elif o:
                objects.append(o)
            else:
                break
        return objects

    def stop(self):
        pass
