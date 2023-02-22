from .http import HttpSubscription
from ...utils.class_loader import load_class
from ...settings import SUBSCRIPTION_ENGINE
from typing import Any


def get_subscription_cls(subscription: Any):
    return load_class(subscription, HttpSubscription)


def create_subscription(subscription: Any):
    cls = get_subscription_cls(subscription)
    return cls(**SUBSCRIPTION_ENGINE.get(cls.__name__, {}))
