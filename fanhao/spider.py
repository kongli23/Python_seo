import requests
from lxml import etree


#http://www.okfhok.com/nvyouku/index_2.html
#http://www.okfhok.com/nvyouku/index_36.html

def download(url,retry=3):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://www.okfhok.com/nvyouku/',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/85.0.4183.102'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
    except requests.HTTPError as err:
        html = None
        print('下载异常：{}'.format(err))
        if (retry > 3):
            return download(url, retry - 1)
    else:
        resp.encoding = 'utf-8'
        html = resp.text
    return html

# 按得到的初始女优列表提取所有番号列表
def parse_list_items(url):
    htmlcode = download(url)
    html = etree.HTML(htmlcode)
    # 演员：//div[@class="infosay fr pos-r"]/h1/text()
    # 介绍：//div[@class="infosay fr pos-r"]/p/text()
    # 详情：//div[@class="infosay fr pos-r"]/ul/li
    # 1：//div[@class="infosay fr pos-r"]/ul/li[1]
    # 2：//div[@class="infosay fr pos-r"]/ul/li[1]
    # 3：//div[@class="infosay fr pos-r"]/ul/li[1]
    # 4#//div[@class="infosay fr pos-r"]/ul/li[1]
    # 6：
    # 番号列表：//div[@class="wrap loadimg avlist-small"]/ul/li/a/div/h3/text()

    html_name = html.xpath('//div[@class="infosay fr pos-r"]/h1/text()')
    # fanhao = html.xpath('//div[@class="wrap loadimg avlist-small"]/ul/li/a/div/h3/text()')
    # with open(r'nvyou/{}.txt'.format(html_name[0]),mode='w',encoding='utf-8') as fw:
    #     for fh in fanhao:
    #         fw.write('{}\n'.format(fh))
    # print('{},番号获取完毕！'.format(html_name[0]))
    with open(r'nvyou/nvyoudaquan.txt', mode='a', encoding='utf-8') as fw:
        fw.write('{}\n'.format(html_name))

# 解析源码得到初始女优列表url
def parse_html(html,url):
    htmlcode = etree.HTML(html)
    url_list = htmlcode.xpath('//div[@class="wrap nylist loadimg"]/ul/li/a/@href')  #url提取xpath
    name_list = htmlcode.xpath('//div[@class="wrap nylist loadimg"]/ul/li/a/div/h3/text()') #名称提取xpath
    for name,href in zip(name_list,url_list):
        # print('{}:http://www.okfhok.com/nvyouku{}'.format(name,href))

        # 提取演员的所有番号
        parse_list_items('http://www.okfhok.com/{}'.format(href))
    print('正在获取 url:{} 中的女优'.format(url))

if __name__ == '__main__':
    for i in range(1, 37):
        url = None
        if i == 1:
            url = 'http://www.okfhok.com/nvyouku/'
        else:
            url = 'http://www.okfhok.com/nvyouku/index_{}.html'.format(i)

        html = download(url)
        if html is None:
            continue
        else:
            parse_html(html, url)
            # print(html)
            # break
    print('所有女优获取完毕！')
    # html = download('http://www.okfhok.com/nvyouku/qiaobenyoucai.html')
    # print(html)