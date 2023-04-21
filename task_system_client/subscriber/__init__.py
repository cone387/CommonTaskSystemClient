from .base import BaseSubscriber
from .threaded import ThreadPoolSubscriber, FixedThreadSubscriber
from ..utils.class_loader import load_class


def get_subscriber_cls(subscriber=None):
    if subscriber is None:
        from ..settings import SUBSCRIBER
        subscriber = SUBSCRIBER
    return load_class(subscriber, BaseSubscriber)


def create_subscriber(subscriber=None):
    if subscriber is None:
        from ..settings import SUBSCRIBER
        subscriber = SUBSCRIBER
    return get_subscriber_cls(subscriber)()
