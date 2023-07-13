try:
    import redis
except ImportError:
    raise ImportError('redis is required for redis subscription, please install redis first')


from .base import Subscription


class RedisSubscription(Subscription):

    def __init__(self, url, **kwargs):
        """
        :type url: str, https://github.com/lettuce-io/lettuce-core/wiki/Redis-URI-and-connection-details
        :param url: example: redis://user:pwd@1.2.3.4:6379/0
        :param kwargs:
        """
        self.client = redis.from_url(url)
        super(RedisSubscription, self).__init__(url, **kwargs)

    @classmethod
    def validate_kwargs(cls, kwargs):
        assert 'queue' in kwargs, 'queue is required'

    @classmethod
    def processable(cls, url):
        return url.startswith('redis')

    def request(self):
        return self.client.blpop(self.queue)

    def stop(self):
        self.client.close()
