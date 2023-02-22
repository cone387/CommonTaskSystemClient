import json
from task_client.executor.executors.spider import TopListSpider
from task_client.executor import Executor


@Executor()
class ZhihuTopList(TopListSpider):
    name = '知乎爬虫-知乎热搜'

    def parse(self, response):
        data = json.loads(response.doc('#js-initialData').text())
        hot_list = data['initialState']['topstory']['hotList']
        for hot in hot_list:
            target = hot['target']
            yield {
                "image": target["imageArea"]['url'],
                "title": target['titleArea']['text'],
                "url": target["link"]['url'],
                "tag": target['metricsArea']['text']
            }
