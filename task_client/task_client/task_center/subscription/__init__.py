from .http import HttpSubscription
from .base import SubscriptionError, BaseSubscription
from ...utils.class_loader import load_class
from ...settings import SUBSCRIPTION_ENGINE
from typing import Any


def get_subscription_cls(subscription: Any):
    return load_class(subscription, HttpSubscription)


def create_subscription(subscription: Any) -> BaseSubscription:
    cls = get_subscription_cls(subscription)
    return cls(**SUBSCRIPTION_ENGINE.get(cls.__name__, {}))
