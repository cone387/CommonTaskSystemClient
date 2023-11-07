import logging
import argparse
import time
import re
import os

parser = argparse.ArgumentParser("task_system_client")
parser.add_argument('-s', '--settings', type=str, help='settings module env(TASK_CLIENT_SETTINGS_MODULE)')
parser.add_argument('-p', '--path', type=str, help='executor path')
parser.add_argument('-i', '--subscription-url', type=str, help='订阅地址')
parser.add_argument('--semaphore', type=int, help='semaphore', default=10)
args = parser.parse_args()


SUBSCRIPTION_URL: str = args.subscription_url

# 日志上传地址，可以是http或者redis
LOG_UPLOAD_URL = None

# 客户端注册地址
CLIENT_REGISTER_URL = None

# 自定义程序下载地址
PROGRAM_DOWNLOAD_URL = None

# 客户端信号接收地址
CLIENT_SIGNAL_URL = None

# 客户端信号响应地址
CLIENT_ACTION_URL = None


CONSUME_QUEUE_NAME = None


CLIENT_ID = os.environ.get('TASK_CLIENT_ID', hex(int(time.time() * 1000))[2:])

GROUP = 'default'

DISPATCHER = "task_system_client.dispatch.ParentAndOptionalNameDispatcher"
SUBSCRIPTION = "task_system_client.schedule.subscription.Subscription"
EXECUTOR = "task_system_client.executor.base.ParentNameExecutor"
CLIENT = "task_system_client.client.BaseClient"
LOG_ENGINE = "task_system_client.handler.log.LogEngine"


THREAD_SUBSCRIBER = {
    "THREAD_NUM": 2,
    "MAX_QUEUE_SIZE": 1000,
    "THREAD_CLASS": "task_system_client.subscriber.threaded.ThreadExecutor",
    "QUEUE": "task_system_client.subscriber.threaded.PriorityQueue",
}

# 异常处理
EXCEPTION_HANDLER = "task_system_client.handler.exception.ExceptionUploader"
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


if args.settings:
    assert os.path.exists(args.settings), f'{args.settings} not exists'
    os.environ['TASK_CLIENT_SETTINGS_MODULE'] = args.settings


# override settings
import importlib
import os
env_settings = os.environ.get('TASK_CLIENT_SETTINGS_MODULE', None)
if env_settings:
    if os.path.exists(env_settings):
        # 此时认为是绝对路径, 需要将配置文件复制到tmp目录下
        tmp_path = os.path.join(os.path.dirname(__file__), "tmp")
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        tmp_settings = 'client_%s' % CLIENT_ID[:8]
        with open(env_settings, 'r', encoding='utf-8') as f:
            with open(os.path.join(tmp_path, f'{tmp_settings}.py'), 'w', encoding='utf-8') as f2:
                f2.write(f.read())
        env_settings = f'task_system_client.tmp.{tmp_settings}'
    settings = importlib.import_module(env_settings)
    for key in dir(settings):
        if key.isupper():
            old = globals().get(key, None)
            new = getattr(settings, key)
            globals()[key] = new
            logger.info("override settings: %s: %s -> %s" % (key, old, new))
    logger.info("load settings from %s" % env_settings)


# check params
assert SUBSCRIPTION_URL, "subscription_url is required, use --subscription-url to set it or specify it in settings.py"

for k, v in locals().copy().items():
    if k.isupper():
        logger.info("%s: %s" % (k, v))


if SUBSCRIPTION_URL.startswith('http'):
    if not LOG_UPLOAD_URL:
        LOG_UPLOAD_URL = re.sub(r'schedule/.*', 'schedule/log/', SUBSCRIPTION_URL)
        logger.info("LOG_UPLOAD_URL['url'] is not set, use default: %s" % LOG_UPLOAD_URL)
    if EXCEPTION_UPLOAD_URL is None and EXCEPTION_HANDLER == "task_system_client.handler.exception.ExceptionUploader":
        EXCEPTION_UPLOAD_URL = re.sub(r'schedule/.*', 'exception/', SUBSCRIPTION_URL)
        logger.info("EXCEPTION_UPLOAD_URL is not set, use default: %s" % EXCEPTION_UPLOAD_URL)
    if CLIENT_REGISTER_URL is None:
        CLIENT_REGISTER_URL = re.sub(r'schedule/.*', 'consumer/register/', SUBSCRIPTION_URL)
        logger.info("CLIENT_REPORT_URL is not set, use default: %s" % CLIENT_REGISTER_URL)
    SUBSCRIPTION_URL += '&id=%s' % CLIENT_ID if '?' in SUBSCRIPTION_URL else '?id=%s' % CLIENT_ID
    PROGRAM_DOWNLOAD_URL = re.sub(r'schedule/.*', 'program/download/', SUBSCRIPTION_URL)
    CLIENT_SIGNAL_URL = re.sub(r'schedule/.*', 'consumer/user/signal/', SUBSCRIPTION_URL)
    CLIENT_ACTION_URL = re.sub(r'schedule/.*', 'consumer/user/action/', SUBSCRIPTION_URL)
    try:
        CONSUME_QUEUE_NAME = re.search(r'schedule/queue/get/(\w+)/', SUBSCRIPTION_URL).group(1)
    except AttributeError:
        pass

elif SUBSCRIPTION_URL.startswith('redis'):
    base_queue = re.search(r'(queue=.*)&?', SUBSCRIPTION_URL).group(1)
    if LOG_UPLOAD_URL is None:
        LOG_UPLOAD_URL = SUBSCRIPTION_URL.replace(base_queue, "%s:LOG" % base_queue)
        logger.info("LOG_UPLOAD_URL not set, use default: %s" % LOG_UPLOAD_URL)

    if EXCEPTION_UPLOAD_URL is None and EXCEPTION_HANDLER == "task_system_client.handler.exception.ExceptionUploader":
        EXCEPTION_UPLOAD_URL = SUBSCRIPTION_URL.replace(base_queue, "%s:EXCEPTION" % base_queue)
        logger.info("EXCEPTION_UPLOAD_URL is not set, use default: %s" % EXCEPTION_UPLOAD_URL)
