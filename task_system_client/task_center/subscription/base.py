from queue import Queue, Empty
from threading import Lock
from ..task import TaskSchedule
from typing import Union
from task_system_client.settings import logger, SEMAPHORE
from task_system_client.utils import url as url_utils


class SubscriptionError(Exception):
    pass


def load_subscriptions(module_path='task_system_client.task_center.subscription'):
    import importlib
    from pathlib import Path
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        return
    if not hasattr(module, '__loaded__'):
        module_file = Path(module.__file__)
        if module_file.name == "__init__.py":
            package = module_file.parent
            for p in package.glob('*'):
                if (p.is_dir() and (p / '__init__.py').exists()) or (p.suffix == '.py' and (not p.stem.startswith('_'))):
                    load_subscriptions(module_path + '.' + p.stem)
    module.__loaded__ = True


class Subscription(Queue):
    lock = Lock()

    def __new__(cls, url):
        if cls is Subscription:
            load_subscriptions()
            for x in Subscription.__subclasses__():
                if x.processable(url):
                    obj = super(Subscription, x).__new__(x)
                    break
            else:
                raise ValueError('No subscription can process url %s' % url)
            return obj
        return super(Subscription, cls).__new__(cls)

    def __init__(self, url):
        self.url, self.kwargs = url_utils.get_split_url_params(url)
        self.validate_kwargs(self.kwargs)
        super(Subscription, self).__init__()

    @classmethod
    def validate_kwargs(cls, kwargs):
        pass

    @classmethod
    def processable(cls, url) -> bool:
        raise NotImplementedError

    def request(self) -> Union[TaskSchedule, None]:
        raise NotImplementedError

    def try_get(self, block=False) -> Union[TaskSchedule, None]:
        try:
            return self.get(block=block)
        except Empty:
            return None

    def update(self, num=SEMAPHORE):
        with self.lock:
            n = 0
            while n < num:
                try:
                    o = self.request()
                except Exception as e:
                    logger.exception(e)
                    break
                if isinstance(o, (list, tuple)):
                    for i in o:
                        n += 1
                        self.put(i)
                elif o:
                    n += 1
                    self.put(o)
                else:
                    break

    def stop(self):
        pass
