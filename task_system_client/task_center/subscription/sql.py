try:
    import pymysql
except ImportError:
    raise ImportError('pymysql is required for sql subscription, please install pymysql first')

from .base import Subscription
from urllib.parse import urlparse


class SqlSubscription(Subscription):

    def __init__(self, url, command=None, **kwargs):
        """
        :param url: example mysql+pymysql://root:wxnacy@127.0.0.1:3306/study?charset=utf8mb4
        :param kwargs:
        """
        assert command, 'command is required'
        conf = urlparse(url)
        query = {x.split('=')[0]: x.split('=')[1] for x in str(conf.query).split('&')}
        self.connection = pymysql.connect(
            host=conf.hostname,
            port=conf.port,
            user=conf.username,
            passwd=conf.password,
            db=conf.path[1:],
            **query
            # cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()
        self.command = command
        super(SqlSubscription, self).__init__(url, **kwargs)

    @classmethod
    def validate_kwargs(cls, kwargs):
        assert 'command' in kwargs, 'command is required'

    @classmethod
    def processable(cls, url):
        return url.startswith('mysql')

    def request(self):
        self.cursor.execute(self.command)
        return self.cursor.fetchall()

    def stop(self):
        self.connection.close()
