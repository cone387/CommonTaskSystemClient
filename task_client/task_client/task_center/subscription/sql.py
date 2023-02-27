try:
    import pymysql
except ImportError:
    raise ImportError('pymysql is required for sql subscription, please install pymysql first')

from .base import BaseSubscription


class SqlSubscription(BaseSubscription):

    def __init__(self, engine, schedule):
        self.engine = engine
        self.schedule = schedule
        self.connection = pymysql.connect(**self.engine)
        self.cursor = self.connection.cursor()
        super(SqlSubscription, self).__init__()

    def get(self):
        self.cursor.execute(self.schedule)
        return self.cursor.fetchall()

    def stop(self):
        self.connection.close()

