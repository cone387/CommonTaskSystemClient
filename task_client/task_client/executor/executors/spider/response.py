import requests
from cone.utils.functional import cached_property
from pyquery import PyQuery


class Response(requests.Response):

    @cached_property
    def doc(self):
        return PyQuery(self.text)
