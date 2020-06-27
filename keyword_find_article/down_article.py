


def get_redirect(self, url):
    '''
    解析搜索结果中的加密链接
    :param url:
    :return:
    '''
    try:
        requests.packages.urllib3.disable_warnings()  # 忽略urllib3 https警告
        resp = requests.get(url, headers=self.headers, timeout=10, verify=False)
    except requests.HTTPError as Err:
        print('解析加密链接异常：', Err)
        redirect_url = None
    else:
        redirect_url = resp.url
    return redirect_url


def parse_html(self, html, encoding='utf-8'):
    '''
    解析文章源码，得到无html标签的文章
    :param html:
    :return:
    '''

    extacter = Extractor()
    # 自能提取文章标题跟正文
    extacter.extract(self.url, html)
    # 过滤字数少于300的文章
    if extacter.text_count > 350 and extacter.score > 10000:
        # 过滤联系方式，手机,QQ,微信,邮箱,网址
        # html_code = html_filter.filter(extacter.format_text)
        article = html_filter.filter(extacter.clean_text)

        print(fanyi_content(article))  # 翻译并输出