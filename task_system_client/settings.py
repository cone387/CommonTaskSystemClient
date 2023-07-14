import logging
import argparse

parser = argparse.ArgumentParser("task_system_client")
parser.add_argument('-s', '--settings', type=str, help='settings module env(TASK_CLIENT_SETTINGS_MODULE)')
parser.add_argument('-p', '--path', type=str, help='executor path')
parser.add_argument('-i', '--subscription-url', type=str, help='订阅地址')
parser.add_argument('--semaphore', type=int, help='semaphore', default=10)
args = parser.parse_args()


SUBSCRIPTION_URL = args.subscription_url
SUBSCRIPTION_KWARGS = {}

HTTP_UPLOAD_LOG_CALLBACK = {
    "url": None
}

DISPATCHER = "task_system_client.task_center.dispatch.ParentAndOptionalNameDispatcher"
SUBSCRIPTION = "task_system_client.task_center.subscription.Subscription"
EXECUTOR = "task_system_client.executor.base.ParentNameExecutor"

SUBSCRIBER = "task_system_client.subscriber.BaseSubscriber"

THREAD_SUBSCRIBER = {
    "THREAD_NUM": 2,
    "MAX_QUEUE_SIZE": 1000,
    "THREAD_CLASS": "task_system_client.subscriber.threaded.ThreadExecutor",
    "QUEUE": "task_system_client.subscriber.threaded.PriorityQueue",
}

# 异常处理
EXCEPTION_HANDLER = "task_system_client.handler.exception.HttpExceptionUpload"
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
assert SUBSCRIPTION_URL, "subscription_url is required, use --subscription-url to set it or specify it in settings.py"
if SUBSCRIPTION_URL.startswith('http'):
    import re
    if not HTTP_UPLOAD_LOG_CALLBACK['url']:
        HTTP_UPLOAD_LOG_CALLBACK['url'] = re.sub(r'schedule/.*', 'schedule-log/', SUBSCRIPTION_URL)
        logger.info("HTTP_UPLOAD_LOG_CALLBACK['url'] is not set, use default: %s" % HTTP_UPLOAD_LOG_CALLBACK['url'])
    if EXCEPTION_REPORT_URL is None and EXCEPTION_HANDLER == "task_system_client.handler.exception.HttpExceptionUpload":
        EXCEPTION_REPORT_URL = re.sub(r'schedule/.*', 'exception/', SUBSCRIPTION_URL)
        logger.info("EXCEPTION_REPORT_URL is not set, use default: %s" % EXCEPTION_REPORT_URL)

