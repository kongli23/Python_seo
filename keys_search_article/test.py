import requests
from threading import Thread
from lxml import etree

def download(url):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }
    try:
        resp = requests.get(url,headers=headers)
        html = resp.content.decode('utf-8')
    except Exception as err:
        print('下载异常：',err)

    return html

def parse_html(html):
    element_text = etree.HTML(html)
    keyList = element_text.xpath('//table//tr//th/a/text()')
    print(keyList)
    print('-' * 50)

def task(url):
    html = download(url)
    parse_html(html)

def main():
    keyList = []
    with open('gif图片.txt', "r", encoding='utf-8') as file:
        for line in file:
            keyList.append(line.replace('\n',''))

    threads = []
    for key in keyList:
        url = 'https://www.baidu.com/s?wd={0}&pn=10'.format(key)
        th = Thread(target=task,args=(url,))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

if __name__ == '__main__':
    main()