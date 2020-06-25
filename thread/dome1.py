import requests
import re
import time
from threading import Thread

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
}
def download(url):
    '''
    下载函数
    :param url:
    :return:
    '''
    try:
        resp = requests.get(url,headers=headers)
    except Exception as err:
        html = None
    else:
        html = resp.text
    return html

def parse_html(html,base_url):
    '''
    解析源码，拿到详情页url

    :param html: 源码
    :param base_url: 根域名
    :return: 返回详情列表
    '''
    urls = re.findall(r'<div class="j-r-list-c-desc">.*?<a href="(/detail-\d+\.html)">[^<]+</a>',html,re.S)
    return [(base_url+url) for url in urls]

def parse_detail(html):
    h1 = re.findall(r'<h1>([^<]+)</h1>',html)
    print(''.join(h1))

def get_detail(url):
    html = download(url)
    if not html:
        return
    parse_detail(html)

if __name__ == '__main__':
    url = 'http://www.budejie.com'
    html = download(url)
    detail_urls = parse_html(html,url)

    start_time = time.time()
    threads = []
    for link in detail_urls:
        th = Thread(target=get_detail,args=(link,))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    print('总耗时：{}'.format(time.time() - start_time))