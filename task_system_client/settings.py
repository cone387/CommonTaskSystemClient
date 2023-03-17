import logging

SUBSCRIPTION_ENGINE = {
    "HttpSubscription": {
        # "subscription_url": "https://api.cone387.top/t/queue/next/",
        # "subscription_url": "http://127.0.0.1:8000/t/schedule/queue/get/",
        # "subscription_url": "http://cone387.top:9000/t/schedule/queue/get/",
    },

    "RedisSubscription": {
        "engine": {
            "host": "",
            "port": 6379,
            "db": 0,
            "password": "",
        },
        "queue": "task_queue",
    },

}

HTTP_UPLOAD_LOG_CALLBACK = {
    "url": None
}

DISPATCHER = "task_system_client.task_center.dispatch.Dispatcher"
SUBSCRIPTION = "task_system_client.task_center.subscription.HttpSubscription"
EXECUTOR = "task_system_client.executor.base.CategoryNameExecutor"

SUBSCRIBER = "task_system_client.subscriber.BaseSubscriber"

THREAD_SUBSCRIBER = {
    "THREAD_NUM": 2,
    "MAX_QUEUE_SIZE": 1000,
    "THREAD_CLASS": "task_system_client.subscriber.threaded.ThreadExecutor",
    "QUEUE": "task_system_client.subscriber.threaded.PriorityQueue",
}


logger = logging.getLogger(__name__)
BASIC_FORMAT = "[%(asctime)s][%(levelname)s]%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# override settings
import importlib
import os
env_settings = os.environ.get('TASK_CLIENT_SETTINGS_MODULE', None)
if env_settings:
    settings = importlib.import_module(env_settings)
    for key in dir(settings):
        if key.isupper():
            globals()[key] = getattr(settings, key)

