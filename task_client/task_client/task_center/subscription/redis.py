try:
    import redis
except ImportError:
    raise ImportError('redis is required for redis subscription, please install redis first')


from .base import BaseSubscription


class RedisSubscription(BaseSubscription):

    def __init__(self, engine, queue):
        self.engine = engine
        self.queue = queue
        self.client = redis.Redis(**self.engine)
        super(RedisSubscription, self).__init__()

    def get(self):
        return self.client.get(self.queue)

    def stop(self):
        self.client.close()
