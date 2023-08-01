from .base import BaseClient
from .threaded import ThreadPoolClient, FixedThreadClient
from ..utils.class_loader import load_class


def get_client_class(client=None):
    if client is None:
        from task_system_client import settings
        client = settings.CLIENT
    return load_class(client, BaseClient)


def create_client(client=None):
    return get_client_class(client)()
