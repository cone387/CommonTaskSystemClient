from typing import Union
from urllib.parse import urlparse
import re


def query_to_dict(query: Union[str, bytes]):
    if not query:
        return {}
    return dict([(i.split('=')[0], i.split('=')[1]) for i in str(query).split('&')])


def get_url_params(url: str):
    p = urlparse(url)
    return query_to_dict(p.query)


def get_split_url_params(url: str):
    base_url = re.sub(r'\?.*', '', url)
    return base_url,  get_url_params(url)
