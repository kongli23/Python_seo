# -*- coding:utf-8 -*-
import requests
import json


def tuisong(url):
    jk = 'http://data.zz.baidu.com/urls?site=https://www.ncle.net&token=hf9ar3F0Cqi7qNYN'
    try:
        html = requests.post(jk,url).text
        html = json.loads(html)
        if html['success'] > 0:
            print("推送成功-----{}".format(html))
        else:
            print("推送失败-----{}".format(html))
    except Exception as e:
        print(e)

if __name__ == '__main__':
    url = 'https://www.ncle.net/seo/4139'
    tuisong(url)