import re

# 过滤联系方式，手机号,微信号,邮箱号,网址
def content_filter(code):
    '''
    过滤联系方式，手机号,微信号,邮箱号,网址
    :param code:
    :return:
    '''
    phone_code = f_phone('<.*>[^<img.*?>].*(1[35678]\d{9}).*</.*>', code)
    wx_code = f_wx('<.*>.*(微信：[\w,-]{5,10}|vx：[\w,-]{5,10}|VX:[\w,-]{5,10}).*</.*>', phone_code)
    email_code = f_email('\w+@\w+\.[com,cn,net]{1,3}', wx_code)
    url_code = f_url('<.*>.*(https?://(?![^" ]*(?:jpg|png|gif))[^" ]+).*</.*>', email_code)

    f_020_code = f_020_phone('\d{3}-\d{8}',url_code)
    f_400_code = f_400('\d{3}-\d{4}-\d{3}',f_020_code)
    f_QQ_code = f_QQ('QQ：\d{5,11}',f_400_code)
    f_flts1_code = f_flts1('以上内容.*?查看更多',f_QQ_code)
    f_flts2_code = f_flts2('更多.*?查看更多',f_flts1_code)

    return f_flts2_code

# 手机号
def f_phone(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) >0:
        for pat in res:
            result = html.replace(pat, '13420877713')
    else:
        result = html
    return result

# 微信号
def f_wx(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '微信：sky7make')
    else:
        result = html
    return result

# 邮箱号
def f_email(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '50377564@qq.com')
    else:
        result = html
    return result

# url网址
def f_url(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, 'https://www.ncle.net')
    else:
        result = html
    return result

# 020电话
def f_020_phone(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '13420877713')
    else:
        result = html
    return result

# 400电话
def f_400(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '13420877713')
    else:
        result = html
    return result

# QQ号
def f_QQ(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '50377564')
    else:
        result = html
    return result

# 多内容替换1
def f_flts1(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '')
    else:
        result = html
    return result

# 多内容替换2
def f_flts2(re_pat,html):
    result = ''
    res = re.compile(r'{}'.format(re_pat), re.I).findall(html)
    if len(res) > 0:
        for pat in res:
            result = html.replace(pat, '')
    else:
        result = html
    return result

def title_filter(title):
    '行者娱乐网站如何进行收录写给至今仍在做SEO外链专员的你'
    '行者娱乐网站如何进行收录写给至今仍在做SEO外链专员的你'
    '行者娱乐平台注册为什么要考虑做一个web站点SEO站内优化方案整体操作步骤'
    'SEO大神进阶过程及搜索引擎优化与竞价排名的优缺点介绍'
    'www.tlkjt.com 网络推广外包公司_成都网站建设_成都网站优化推广-推来客'
    '鼎极SEO-关键词排名_网站SEO优化_整站快速推广_搜索引擎_网络推广公司'
    'SEM百度竞价培训之优化客服话术的3大技巧，第3个太实用了！'
    '网赚怎么推广呢_关键字百度快速排名方案技术分享找牛BSEOsz-seo.org'
    str_length = len('实验室建设规划方案')
    print(str_length)

code = '''
<section class="post-content">
                        <p>
<p><p>有很多的同学是非常的想知道，男女一问一答的套路情话有哪些的，小编整理了相关信息，希望会对大家有所帮助！
</p><p align="center"><img class="alignnone size-full wp-image-2323" src="http://www.duanzi.io/wp-content/uploads/2020/06/6365715905771690791089800.jpg" width="600" height="375" srcset="http://www.duanzi.io/wp-content/uploads/2020/06/6365715905771690791089800.jpg 600w, http://www.duanzi.io/wp-content/uploads/2020/06/6365715905771690791089800-300x188.jpg 300w" sizes="(max-width: 600px) 100vw, 600px" /></p>
<p>让人无法拒绝的套路表白情话</p><p>1、“你喜欢猫还是狗?”</p><p>“猫”</p><p>-“喵～”</p>
<p>2.“爱或者不爱，给我一个字的答复”</p><p>“不爱”</p><p>“一个字的答复好吗!重来”</p>
<p>3.“我们来交换礼物好不好”</p><p>“好啊”</p><p>“嗯好现在开始我是你的你是我的”</p>
<p>4.“同学打扰一下请问这道题怎么做”</p><p>“不好意思我不会”</p><p>“哦你不会啊那我给你讲讲吧”</p>
<p>5.“我背你吧”</p><p>“为什么呀”</p><p>“昨晚一整夜你都在我梦里钻来跑去肯定累坏了”</p>
<p>6.“我可以向你问路吗?”</p><p>“到那里?”</p><p>“到你心里!”</p><p>7.“你能模仿下啄木鸟吗”</p>
<p>“怎么模仿”</p><p>“就拿我的脸当树”</p><p>8.“你怎么跑来了?”</p><p>“我想看到你”</p>
<p>“我会打电话给你啊”</p><p>“打电话看不到你”</p><p>套路情话撩男朋友的</p><p>1.</p>
<p>&#8220;一天天的脑子里想些什么呢&#8221;</p><p>&#8220;想你&#8221;</p>
<p>2.</p><p>&#8220;你不做饭给我吃&#8221;</p><p>&#8220;我哪来力气和你撒娇&#8221;</p>
<p>3.</p><p>说起我男朋友的优点</p><p>总结起来就是五个字</p><p>&#8220;会挑女朋友&#8221;</p>
<p>4.</p><p>&#8220;如果你不怕麻烦的话&#8221;</p><p>&#8220;那就麻烦你跟我在一起吧&#8221;</p><p>5.</p>
<p>&#8220;我昨晚失眠了&#8221;</p><p>&#8220;意思就是想你想了一夜&#8221;</p><p>6.</p>
<p>&#8220;今年只有一个旅游计划&#8221;</p><p>&#8220;就是，见你&#8221;</p><p>7.</p>
<p>“能在愚人节骗我一次吗”</p><p>“好啊”</p><p>“你喜欢我吗?”</p><p>经典撩妹套路</p>
<p>1.“能在愚人节骗我一次吗”</p><p>“好啊”</p><p>“你喜欢我吗?”</p><p>2.“你想清楚再跟我说话”</p>
<p>“我没有在想清楚我在想你”</p><p>3.&#8221;问你个问题，老爸老妈老姐老哥老公哪个和你没有血缘关系?&#8221;</p>
<p>&#8220;老公啊&#8221;</p><p>&#8220;诶~老婆真聪明~&#8221;</p><p>4.你忙归忙</p>
<p>什么时候有空嫁给我?</p><p>5.我想www.666.com你一定很忙</p><p>所以你只看前三个字就好</p><p>6.如果哪一天我想环游世界了，</p>
<p>我可以围着你转一www.77777.cn圈吗?</p><p>7.“今天早上照了照镜子，http://www.sfasb.com 然后就想到了找你”</p><p>“为什么”</p>
<p>“这么多日子来，你知道的，电话：13520877716每次看到好的东西我都想给你”</p><p>8.我只是喜欢你，</p><p>我没有恶意。</p></p>
</p>
<p>联系VX：kwysdkf 邮箱：88888@qq.com</p>
<p></p>
                    </section>
'''
# result = filter(code)
# print(result)

#更多.*?查看更多 匹配多内容联系方式
#以上内容.*?查看更多 匹配多内容联系方式
#QQ：\d{5,11} 匹配QQ号
#\d{3}-\d{4}-\d{3} 匹配400-1234-123 电话
#\d{3}-\d{8} 匹配020-12345678 电话

#<.*>[^<img.*?>].*(1[35678]\d{9}).*</.*> 匹配 html标签内的手机号
#<.*>.*(https?://(?![^" ]*(?:jpg|png|gif))[^" ]+).*</.*> 匹配 html标签内的网址 http https .com/abc.html
#<.*>.*(微信：[\w,-]{5,10}|vx：[\w,-]{5,10}|VX:[\w,-]{5,10}).*</.*> 匹配 html标签内的微信号
#<.*>[^<img.*?>].*(\d{5,11}).*</.*> 匹配 html标签内的5-11位数字，一般为qq号
#\w+@\w+\.[com,cn,net]{1,3} 匹配 html源码中所有的邮箱
# links = re.compile(r'\w+@\w+\.[com,cn,net]{1,3}',re.I).findall(code)
# for pat in links:
#     # str = ''.join(pat)
#     print(pat)

if __name__ == '__main__':
    # title_filter('行者娱乐平台注册为什么要考虑做一个web站点SEO站内优化方案整体操作步骤')
    res = content_filter(code)
    print('结果：',res)