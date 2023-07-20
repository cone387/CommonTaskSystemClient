import logging
import argparse
import re

parser = argparse.ArgumentParser("task_system_client")
parser.add_argument('-s', '--settings', type=str, help='settings module env(TASK_CLIENT_SETTINGS_MODULE)')
parser.add_argument('-p', '--path', type=str, help='executor path')
parser.add_argument('-i', '--subscription-url', type=str, help='订阅地址')
parser.add_argument('--semaphore', type=int, help='semaphore', default=10)
args = parser.parse_args()


SUBSCRIPTION_URL: str = args.subscription_url

# 日志上传地址，可以是http或者redis
LOG_UPLOAD_URL = None

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
EXCEPTION_HANDLER = None
EXCEPTION_UPLOAD_URL = None

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

for k, v in locals().copy().items():
    if k.isupper():
        logger.info("%s: %s" % (k, v))


if SUBSCRIPTION_URL.startswith('http'):
    if not LOG_UPLOAD_URL:
        LOG_UPLOAD_URL = re.sub(r'schedule/.*', 'schedule-log/', SUBSCRIPTION_URL)
        logger.info("LOG_UPLOAD_URL['url'] is not set, use default: %s" % LOG_UPLOAD_URL)
    if EXCEPTION_HANDLER is None:
        EXCEPTION_HANDLER = "task_system_client.handler.exception.HttpExceptionUpload"
    if EXCEPTION_UPLOAD_URL is None and EXCEPTION_HANDLER == "task_system_client.handler.exception.HttpExceptionUpload":
        EXCEPTION_UPLOAD_URL = re.sub(r'schedule/.*', 'exception/', SUBSCRIPTION_URL)
        logger.info("EXCEPTION_UPLOAD_URL is not set, use default: %s" % EXCEPTION_UPLOAD_URL)

elif SUBSCRIPTION_URL.startswith('redis'):
    base_queue = re.search(r'(queue=.*)&?', SUBSCRIPTION_URL).group(1)
    if LOG_UPLOAD_URL is None:
        LOG_UPLOAD_URL = SUBSCRIPTION_URL.replace(base_queue, "%s:LOG" % base_queue)
        logger.info("LOG_UPLOAD_URL not set, use default: %s" % LOG_UPLOAD_URL)
    if EXCEPTION_HANDLER is None:
        EXCEPTION_HANDLER = "task_system_client.handler.exception.RedisExceptionUpload"
    if EXCEPTION_UPLOAD_URL is None and EXCEPTION_HANDLER == "task_system_client.handler.exception.RedisExceptionUpload":
        EXCEPTION_UPLOAD_URL = SUBSCRIPTION_URL.replace(base_queue, "%s:EXCEPTION" % base_queue)
        logger.info("EXCEPTION_UPLOAD_URL is not set, use default: %s" % EXCEPTION_UPLOAD_URL)
