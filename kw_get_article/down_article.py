from bluextracter import Extractor
import requests
import re
from kw_get_article.article_filter import content_filter
from translation.content_fanyi import fanyi_content

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)'
}

def download(url):
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as err:
        print('{}:下载异常：{}'.format(url, err))
        html = None
    else:
        resp.encoding = get_encoding(resp.text)
        html = resp.text
    return html

def get_encoding(html):
    encoding = re.findall('<meta.*?charset="?([\w-]*)".*>',html,re.I)
    if encoding:
        return encoding[0]
    return 'utf-8'

def extract_content(url, source):
    ex = Extractor()
    ex.extract(url, source)
    # if ex.score > 10000 and len(ex.title) > 10:
    title = ex.title
    content = ex.clean_text
    print(title)
    print(content)
    print('-' * 50)
    new_content = fanyi_content(content)
    new_content = content_filter(new_content)
    print(new_content)
    # print(ex.clean_text)

if __name__ == '__main__':
    url = 'http://seo-ntuiw.com/content/?1718.html'
    source = download(url)
    if source:
        extract_content(url,source)