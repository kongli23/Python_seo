import requests
from lxml import etree
import threading

look = threading.Lock()

class aizhan(threading.Thread):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56'
    }
    def __init__(self,url):
        super(aizhan, self).__init__()
        self.url = url

    def run(self):
        html = self.download(self.url)
        if html:
            self.parse_html(html)
        else:
            print('下载源码异常！')

    def download(self,url):
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
        except requests.HTTPError as err:
            print('下载异常：',err)
            html = None
        else:
            html = resp.content.decode('utf-8')
        return html

    def parse_html(self,code):
        html = etree.HTML(code)
        tds = html.xpath('//table[@class="table table-border table-s1"]//tbody//tr//td[not(@class="path")][1]/a/text()')

        for td in tds:
            look.acquire()
            with open('keywords.txt','a',encoding='utf-8') as app:
                app.write(td.strip()+'\n')
            look.release()
        print(self.url,'获取完毕！')
if __name__ == '__main__':
    domain = 'seowhy.com'
    thread = []
    for i in range(1,51):
        url = 'https://baidurank.aizhan.com/baidu/{}/-1/0/{}/position/1/'.format(domain,i)
        # print(url)
        az = aizhan(url)
        az.setDaemon(True)
        az.start()
        thread.append(az)

    for t in thread:
        t.join()