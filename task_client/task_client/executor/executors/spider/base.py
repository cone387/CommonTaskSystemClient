from abc import ABCMeta
from ...executor import BaseExecutor
from types import GeneratorType
from .response import Response
from .request import Request
from requests import request as requests_request
from requests.exceptions import Timeout, ProxyError


class SpiderExecutor(BaseExecutor):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    }
    category = '爬虫'
    start_urls = []

    def __init__(self, task):
        super().__init__(task=task)
        self.config = self.task.config
        self.headers = self.config.get('headers', self.headers)

    def get_start_requests(self):
        start_urls = self.config.get('start-urls') or self.start_urls
        if isinstance(start_urls, str):
            start_urls = start_urls.split(',')
        elif isinstance(start_urls, (list, tuple)):
            pass
        else:
            raise ValueError('start-urls must be str or list')
        for url in start_urls:
            yield Request(url=url.strip(),
                          headers=self.headers,
                          callback=self.parse)

    def parse(self, response: Response):
        raise NotImplementedError

    # def get_title(self, item, selector=None, xpath=None):
    #     if selector:
    #         return item(selector).text()
    #     return item.text()
    #
    # def get_url(self, item, selector=None, xpath=None):
    #     if selector:
    #         return item(selector).attr('href')
    #     return item.attr('href')
    #
    # def get_tag(self, item, selector=None, xpath=None):
    #     if selector:
    #         return item(selector).text()
    #     return ''
    #
    # def get_image(self, item, selector=None, xpath=None):
    #     if selector:
    #         image = item(selector).attr('src')
    #         if image:
    #             if image.startswith('//'):
    #                 return self.subscribe_url.split('//')[0] + image
    #             elif not image.startswith('http'):
    #                 return urljoin(self.subscribe_url, image)
    #             return image
    #     return ''
    #
    # def parse_common(self, response):
    #     config = self.spider_module['config_columns']
    #     items = response.doc(config.get('selector-item', None))
    #     selector_url = config.get('selector-link', None)
    #     selector_title = config.get('selector-title', None)
    #     selector_tag = config.get('selector-tag', None)
    #     selector_img = config.get('selector-img', None)
    #
    #     for pos, item in enumerate(items.items(), 1):
    #         url = self.get_url(item, selector_url)
    #         title = self.get_title(item, selector_title)
    #         tag = self.get_tag(item, selector_tag)
    #         image = self.get_image(item, selector_img)
    #         if url and title:
    #             yield {
    #                 'url': url,
    #                 'title': title,
    #                 'tag': tag,
    #                 'image': image,
    #                 'crawl_pos': pos,
    #             }
    #     self.logger.info("get %s origin items", len(items))

    def download(self, request: Request):
        try:
            return requests_request(request.method, **request)
        except Timeout:
            if request.done_times < request.try_times:
                request.done_times += 1
                self.process_request(request)
            else:
                if request.err_call:
                    request.err_call(request)
        except ProxyError:
            if request.done_times < request.try_times:
                request.done_times += 1
                self.process_request(request)
            else:
                if request.err_call:
                    request.err_call(request)
        return None

    def process_request(self, request: Request):
        response = self.download(request)
        self.process_response(request, response)

    def process_response(self, request, response: Response):
        callback = request.callback
        result = callback(response)
        if isinstance(result, GeneratorType):
            for o in result:
                if isinstance(o, Request):
                    self.process_request(o)
                elif isinstance(o, dict):
                    self.process_item(o)

    def process_item(self, item):
        pass

    def process(self):
        start_requests = list(self.get_start_requests())
        assert start_requests, "start requests is empty"
        for request in start_requests:
            self.process_request(request)


class TopListSpider(SpiderExecutor, metaclass=ABCMeta):

    category = '爬虫-榜单'
