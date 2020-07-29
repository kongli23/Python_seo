# -*- coding:utf-8 -*-
import requests
import cchardet
from spider_key_article.filter_keys import clean_content
from spider_key_article.extractor import Extractor
from spider_key_article.translate.google import google

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
        text = resp.content  # 这里返回的是二进制的内容
        encoding = cchardet.detect(text)['encoding']
        if encoding is None:
            encoding = 'gbk'
        html = text.decode(encoding=encoding, errors='ignore')
    return html

def extract_content(url, source):
    ex = Extractor()
    ex.extract(url, source)
    if ex.text_count > 300:
        text = clean_content(ex.format_text)
        print('开始翻译内容...')
        # result = start_translate(text)
        # result = google(text)
        result = google(text)
        print('原始内容：{}'.format(text))
        print('翻译内容：{}'.format(result))

if __name__ == '__main__':
    # url = 'http://bs.17house.com/16832/'
    url = 'https://www.wobosi.com/1586.html'
    source = download(url)
    if source:
        extract_content(url,source)