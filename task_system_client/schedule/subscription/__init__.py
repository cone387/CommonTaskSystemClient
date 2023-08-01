from .base import SubscriptionError, Subscription
from task_system_client.utils.class_loader import load_class
from task_system_client import settings
from typing import Any


def get_subscription_cls(subscription: Any):
    return load_class(subscription, Subscription)


def create_subscription(subscription: Any) -> Subscription:
    cls = get_subscription_cls(subscription)
    return cls(settings.SUBSCRIPTION_URL)
