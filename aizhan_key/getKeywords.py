import requests
from lxml import etree
import time
import xlwt

# # 将获取到的数据写入excel中
work = xlwt.Workbook(encoding='GBK')
workSheet = work.add_sheet('Sheet')
# 设置表格的标头
workSheet.write(0, 0, '关键词')
workSheet.write(0, 1, '排名')
workSheet.write(0, 2, 'PC搜索量')
excel_line = 1  # 定义excel 的行号

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

def sava_excel(name,rank,search_num):
    global excel_line
    # 开始定入 excel
    workSheet.write(excel_line, 0, name)  # 第一列
    workSheet.write(excel_line, 1, rank)  # 第二列
    workSheet.write(excel_line, 2, search_num)  # 第三列
    excel_line = excel_line + 1

    work.save(r'网站关键词排名.xls')

# 解析页面得到关键词、排名、搜索量
def parse_html(html):
    doc = etree.HTML(html)
    key_name = doc.xpath('//div[@class="baidurank-list"]/table/tbody/tr/td[not(contains(@class,"path"))][1]/a/text()')    #key
    key_rank = doc.xpath('//div[@class="baidurank-list"]/table/tbody/tr/td[not(contains(@class,"path"))][2]/span/text()')   #排名
    key_search_num = doc.xpath('//div[@class="baidurank-list"]/table/tbody/tr/td[not(contains(@class,"path"))][3]/a/text()')    #搜索量

    for name,rank,search_num in zip(key_name,key_rank,key_search_num):
        # print('关键词{},排名{},搜索量{}'.format(name.strip(),rank.strip(),search_num.strip()))
        sava_excel(name,rank,search_num)

if __name__ == '__main__':
    for i in range(1,51):
        query = 'https://baidurank.aizhan.com/baidu/www.nnbbb.com/-1/0/{}/position/1/'.format(i) #PC
        # query = 'https://baidurank.aizhan.com/mobile/www.nnbbb.com/-1/0/{}/position/1/'.format(i) #移动
        source = download(query)
        if source is None:
            continue
        parse_html(source)
        time.sleep(2.5)
    print('获取完毕!')