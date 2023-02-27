from queue import PriorityQueue, Empty
from threading import Lock


class SubscriptionError(Exception):
    pass


class BaseSubscription:

    queue = PriorityQueue()
    lock = Lock()

    def get_one(self):
        try:
            return self.queue.get_nowait()
        except Empty:
            with self.lock:
                o = self.get()
                if isinstance(o, (list, tuple)):
                    for i in o:
                        self.queue.put(i)
                elif o is not None:
                    return o
        return self.get_one()

    def get(self):
        pass

    def stop(self):
        pass
