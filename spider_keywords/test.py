import requests
from lxml import etree
import threading
import time

initial = ['seo优化','seo推广']
contain = ['seo','网站优化']
existed = []

# 下载提取源码
def getHtml(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }
    resp = requests.get(url,headers=headers)
    text = resp.text
    return parse_html(text)

# 解析源码得到相关词
def parse_html(html):
    element_text = etree.HTML(html)
    keyList = element_text.xpath('//table//tr//th/a/text()')
    for key in keyList:
        # 过滤，必须包含
        for con in contain:
            if con in key:
                # 过滤已采集过的词
                if key not in existed:
                    initial.append(key) #此处可以保存
                    print('新词：{}'.format(key))
    return initial
if __name__ == '__main__':
    # url = 'https://www.baidu.com/s?wd=seo&pn=10'
    # keyList = getHtml(url)
    # print(keyList)
    for index,key in enumerate(initial):
        print('正在采集：{}'.format(key))
        print('当前词数：{}'.format(len(initial)))
        url = 'https://www.baidu.com/s?wd={0}&pn=10'.format(key)
        keyList = getHtml(url)
        # threading.Thread(target=getHtml,args=(url,)).start()
        # print('{0}：采集完成，现总数：{1}'.format(key,len(initial)))
        #采集过的都存储起来
        existed.append(key)

        # 采过的删除
        initial.pop(index)
        time.sleep(0.3)