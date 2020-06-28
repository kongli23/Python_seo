# -*- coding: utf-8 -*-
import threading
import re
from socket import timeout
import requests
import chardet
from bluextracter import Extractor
from translation.content_fanyi import fanyi_content

look = threading.Lock()
class Article(threading.Thread):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }

    def __init__(self, url, pase_func):
        self.url = url
        self.parse_fun = pase_func
        self.result = None
        super().__init__()

    def run(self):  # 这个是必须要的，这个方法就是线程调用start方法的时候运行的方法
        html = self.download(self.url)
        if not html:
            return
        self.result = self.parse_fun(html,self.url)

    def download(self, url, encoding='utf-8'):
        """
        下载函数
        :param url:
        :param encoding:
        :return:
        """
        try:
            resp = requests.get(url,headers=self.headers,timeout=5)
        except Exception as err:
            print('下载异常：', err)
            html = None
        else:
            try:
                coding = chardet.detect(resp.content)
                if (coding['encoding'] != ''):
                    html = resp.content.decode(coding['encoding'])  # 自动设置网页源码
            except Exception as coding_err:
                print('设置编码异常：',coding_err)
        return html

def extract(html,base_url):
    """
    解析函数
    :param html:
    :return:
    """
    urls = re.findall(r'<h3 class="t" ><a[^<]+href = "(.*?)"',
                      html, re.S)
    return [(encry_url) for encry_url in urls]


def parse_detail(html,base_url):
    """
    提取详情
    :param html:
    :return:
    """
    try:
        extacter = Extractor()
        extacter.extract(base_url, html)
        # 过滤字数少于300的文章
        if extacter.text_count > 350 and extacter.score > 10000:
            # 过滤联系方式，手机,QQ,微信,邮箱,网址
            text = extacter.clean_text
            new_text = fanyi_content(text)

            look.acquire()
            with open('article/{}.html'.format(extacter.title),'w',encoding='utf-8') as file:
                file.write(new_text)
                print('提取完毕!')
                print('-' * 50)
            look.release()

    except Exception as err:
        print('提取文章异常：',err)

if __name__ == '__main__':
    keylist = []
    with open('keywords.txt','r',encoding='utf-8') as file:
        for key in file:
            keylist.append(key.strip())

    for keys in keylist:
        query = 'https://www.baidu.com/s?wd={}&pn=10'.format(keys)
        art = Article(query, extract)
        art.start()
        art.join()
        details = art.result    #得到关键词的10条加密快照链接

        # 批量解析加密链接
        for link in details:
            b = Article(link, parse_detail)
            b.start()
            break
