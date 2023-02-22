import json
from ... import Request
from ....spider import TopListSpider
from .....executor import Executor


@Executor()
class WeiboTopListSpider(TopListSpider):
    name = '微博爬虫-微博热搜'

    def get_start_requests(self):
        yield Request(
            method='post',
            url='https://passport.weibo.com/visitor/genvisitor',
            data={
                "cb": 'gen_callback',
                "fp": ""
            },
            callback=self.gen_callback
        )

    def gen_callback(self, response):
        json_text = json.loads(response.text.replace("window.gen_callback && gen_callback(", "").replace(');', ""))
        tid = json_text['data']['tid']
        print("tid is %s" % tid)
        params = {
            "a": "incarnate",
            "t": tid,
            "w": 0,
            "cb": "cross_domain",
            "from": "weibo",
        }
        yield Request(
            url='https://passport.weibo.com/visitor/visitor',
            params=params,
            cookies=response.cookies.get_dict(),
            callback=self.parse_visitor
        )

    def parse_visitor(self, response):
        for request in super(WeiboTopListSpider, self).get_start_requests():
            request.cookies = response.cookies.get_dict()
            yield request

    def parse(self, response):
        print(response.text)


