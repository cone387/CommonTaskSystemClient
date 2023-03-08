import time
from .threaded import ThreadSubscriber
from ..utils.class_loader import load_class


def get_subscriber_cls(subscriber=None):
    if subscriber is None:
        from ..settings import SUBSCRIBER
        subscriber = SUBSCRIBER
    return load_class(subscriber, ThreadSubscriber)


def create_subscriber(subscriber=None):
    if subscriber is None:
        from ..settings import SUBSCRIBER
        subscriber = SUBSCRIBER
    return get_subscriber_cls(subscriber)()


class SubscriberPool:

    def __init__(self, num=2):
        self._subscribes = [create_subscriber() for _ in range(num)]

    def start_event_loop(self):
        while True:
            for o in self._subscribes:
                if not o.is_alive():
                    o.start()
            time.sleep(1)

    def start(self):
        for o in self._subscribes:
            o.start()
        self.start_event_loop()

    def stop(self):
        for o in self._subscribes:
            o.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
