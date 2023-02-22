from cone.crypto import get_md5
from cone.utils.functional import cached_property


class Request(dict):
    def __init__(self, url=None, callback=None, method='GET', headers=None, cookies=None, meta=None, priority=0,
                 encoding=None, timeout=30, do_filter=False, try_times=3, err_call=None, **kwargs):
        super().__init__(**kwargs)
        self.priority = priority
        self.do_filter = do_filter
        self.err_call = err_call
        self.meta = meta
        self.method = method
        self.encoding = encoding
        self.callback = callback
        self.try_times = try_times
        self.done_times = 1
        self['timeout'] = timeout
        self['url'] = url
        self['cookies'] = cookies
        self['headers'] = headers

    @property
    def url(self):
        return self['url']

    @property
    def cookies(self):
        return self['cookies']

    @cookies.setter
    def cookies(self, value):
        self['cookies'] = value

    @property
    def headers(self):
        return self['headers']

    @headers.setter
    def headers(self, value):
        self['headers'] = value

    @cached_property
    def fingerprint(self):
        return get_md5(self['url'])

    def __lt__(self, other):
        # priority越小，处理优先级越高
        return self.priority < other.priority

    def __str__(self):
        return f'Request(method={self.method}, url={self["url"]})'
