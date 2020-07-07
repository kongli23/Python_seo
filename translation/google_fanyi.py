from googletrans import Translator

# 英文翻译成中文
# #实例化
# translator = Translator(service_urls=['translate.google.cn'])
#
# content = 'Today is a gooday'
#
# transed_content = translator.translate(content, dest='zh-CN').text
#
# print(transed_content)

def google_fanyi(text):
    try:
        translator = Translator(service_urls=['translate.google.cn'])
        transed_content = translator.translate(text, dest='EN').text    #en
    except Exception as err:
        transed_content = None
        print('谷歌翻译异常：{}'.format(err))
    return transed_content

if __name__ == '__main__':
    text = '''
        1、熟悉SEO规则、搜索引擎的算法机制。主要是白帽手法的熟悉。

        2、懂得分析数据、分析百度统计、百度指数数据。如果可以的话也可以通过百度推广其他的统计渠道获取数据。

        3、懂得一些用户体验、用户心理学的研究。知道怎么去布局网站。因为数据并非真正用户，只有懂得用户了。你可以进一步和业务部门协商做好公司的业绩。
        '''
    content = google_fanyi(text)
    print(content)