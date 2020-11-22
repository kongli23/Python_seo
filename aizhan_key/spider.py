import requests
from lxml import etree
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58'
}
def download(url):
    print('正在获取：{}'.format(url))

    try:
        resp = requests.get(url,headers=headers,timeout=10)
    except requests.RequestException as err:
        print('{}:下载异常：{}'.format(url,err))
        html = None
    else:
        resp.encoding = 'utf-8'
        html = resp.text
    return html

def parse_html(html):
    doc = etree.HTML(html)
    tds = doc.xpath('//table[@class="table table-border table-s1"]//tbody//tr//td[@class="title"]/a/text()')
    with open('keys.txt','a',encoding='utf-8') as f:
        for td in tds:
            keys = td.strip()
            if len(keys) > 5:
                f.write(td.strip()+'\n')

if __name__ == '__main__':
    for i in range(1,51):
        # query = 'https://baidurank.aizhan.com/baidu/ishuo.cn/-1/0/{}/position/1/'.format(i) #PC
        query = 'https://baidurank.aizhan.com/mobile/www.nnbbb.com/-1/0/{}/position/1/'.format(i) #移动
        source = download(query)
        if source is None:
            continue
        parse_html(source)
        time.sleep(2.5)

    print('获取完毕!')