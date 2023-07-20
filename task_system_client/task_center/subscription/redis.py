
try:
    import redis
except ImportError:
    raise ImportError('redis is required for redis subscription, please install redis first')
import json
from .base import Subscription
from ..task import TaskSchedule


class RedisSubscription(Subscription):

    def __init__(self, url):
        """
        :type url: str, https://github.com/lettuce-io/lettuce-core/wiki/Redis-URI-and-connection-details
        :param url: example: redis://user:pwd@1.2.3.4:6379/0
        """
        super(RedisSubscription, self).__init__(url)
        self.queue_name = self.kwargs.pop('queue', None)
        pool = redis.ConnectionPool.from_url(self.url)
        self.client = redis.Redis(connection_pool=pool, decode_responses=True)
        assert self.client.ping(), 'redis connection failed'

    @classmethod
    def validate_kwargs(cls, kwargs):
        assert 'queue' in kwargs, 'queue is required'

    @classmethod
    def processable(cls, url):
        return url.startswith('redis')

    def request(self):
        o = self.client.lpop(self.queue_name)
        if o:
            return TaskSchedule(json.loads(o))
        return o

    def stop(self):
        self.client.close()
