import logging
import argparse

parser = argparse.ArgumentParser("task_system_client")
parser.add_argument('-s', '--settings', type=str, help='settings module env(TASK_CLIENT_SETTINGS_MODULE)')
parser.add_argument('-p', '--path', type=str, help='executor path')
parser.add_argument('--http-queue-url', type=str, help='http queue url')
parser.add_argument('--semaphore', type=int, help='semaphore', default=10)
args = parser.parse_args()


SUBSCRIPTION_ENGINE = {
    "HttpSubscription": {
        "subscription_url": args.http_queue_url,
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

DISPATCHER = "task_system_client.task_center.dispatch.ParentAndOptionalNameDispatcher"
SUBSCRIPTION = "task_system_client.task_center.subscription.HttpSubscription"
EXECUTOR = "task_system_client.executor.base.ParentNameExecutor"

SUBSCRIBER = "task_system_client.subscriber.BaseSubscriber"

THREAD_SUBSCRIBER = {
    "THREAD_NUM": 2,
    "MAX_QUEUE_SIZE": 1000,
    "THREAD_CLASS": "task_system_client.subscriber.threaded.ThreadExecutor",
    "QUEUE": "task_system_client.subscriber.threaded.PriorityQueue",
}

# 异常处理
EXCEPTION_HANDLER = "task_system_client.handler.exception.ExceptionHandler"
EXCEPTION_REPORT_URL = None

# 并发控制， 为None则不限制
SEMAPHORE = args.semaphore

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


# check params
if SUBSCRIPTION == "task_system_client.task_center.subscription.HttpSubscription":
    assert SUBSCRIPTION_ENGINE['HttpSubscription']['subscription_url'], \
        "subscription_url is required when using HttpSubscription, " \
        "use --http-queue-url to set it or specify it in settings.py"
    if not HTTP_UPLOAD_LOG_CALLBACK['url']:
        import re
        HTTP_UPLOAD_LOG_CALLBACK['url'] = re.sub(r'schedule/.*', 'schedule-log/',
                                                 SUBSCRIPTION_ENGINE['HttpSubscription']['subscription_url'])
        logger.info("HTTP_UPLOAD_LOG_CALLBACK['url'] is not set, use default: %s" % HTTP_UPLOAD_LOG_CALLBACK['url'])

elif SUBSCRIPTION == "task_system_client.task_center.subscription.RedisSubscription":
    assert SUBSCRIPTION_ENGINE['RedisSubscription']['engine']['host'], \
        "redis host is required when using RedisSubscription"
    assert SUBSCRIPTION_ENGINE['RedisSubscription']['engine']['port'], \
        "redis port is required when using RedisSubscription"
    assert SUBSCRIPTION_ENGINE['RedisSubscription']['engine']['db'], \
        "redis db is required when using RedisSubscription"
    assert SUBSCRIPTION_ENGINE['RedisSubscription']['queue'], \
        "redis queue is required when using RedisSubscription"
