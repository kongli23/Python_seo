import requests
import threading
import re

class Find_article(threading.Thread):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56'
    }
    def __init__(self,url):
        super(Find_article, self).__init__()
        self.url = url

    def run(self):
        html = self.download(self.url)
        if not html:
            print('下载源码异常！')
            return
        else:
            links = self.parse_url_list(html)
            print(links)

    def download(self,url,encoding='utf-8'):
        '''
        通用下载源码函数
        :param url:
        :return:
        '''
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
        except requests.HTTPError as err:
            print('下载源码异常：',err)
            html = None
        else:
            html = resp.content.decode(encoding)
        return html

    def parse_url_list(self, html):
        '''
        得到百度搜索结果中的加密链接

        :param html:
        :return:
        '''

        pat = r'<h3 class="t" ><a[^<]+href = "(.*?)"'

        # 得到百度结果加密链接
        links = re.compile(pat).findall(html)
        return links

if __name__ == '__main__':
    'https://www.baidu.com/s?wd={0}&pn=10'
    keyList = []
    with open('keywords.txt','r',encoding='utf-8') as file:
        for key in file:
            keyList.append(key.strip())

    threads = []
    for s in keyList:
        url = 'https://www.baidu.com/s?wd={0}&pn=10'.format(s)
        search = Find_article(url)
        search.setDaemon(True)
        search.start()
        search.join()
        break