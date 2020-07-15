import re
from translation.google_fanyi import google_fanyi
from translation.baidu_fanyi import Dict

def fanyi_content(text):
    '''
    传入中文，将中文翻译成英文，再将英文翻译成中文

    :param text: 要翻译的p标签
    :return: 返回翻译后的中文
    '''

    success_text = ''
    # 使用谷歌将中文翻译英文
    en_text = google_fanyi(text)

    # 使用百度将英文翻译中文
    dt = Dict()
    # print('谷歌内容：{}'.format(en_text))
    try:
        cn_text = dt.baidu_fanyi(en_text)
        if cn_text is None:
            return
        res = re.sub(r'“|”', '"', cn_text)
    except AttributeError as err:
        print('异常：{}，百度翻译：{}'.format(err,en_text))
    else:
        success_text = res
    return success_text

if __name__ == '__main__':

    text = '''
    主动推送是将一串JS代码放在站点的每一个页面中，当用户访问时就会触发代码，SEO外包从而把页面URL提交给百度。是一款很便捷无忧的SEO优化链接推送办法。

 

新站SEO优化想要做排名的页面，应该有大量内链与其相连接。相关性强的内链不仅能提高录入，还能提高页面的权重分值。外部链接，通过大量的外链来指向想要参加排名的页面，到达用户引荐，也是一个非常好的办法。

 

装了主动推送的代码，网站只需有访客，就为推送地址给百度，蜘蛛就会第一时刻获取到信息，从而促进抓取，录入。

 

SEO优化文章必须围绕标题的长尾词进行描绘，把干货展现给用户看，用户停留的时刻越长，排名会越好。推荐阅读:想扩大网站知名度，seo优化要从这里入手

 

网站结构简略明晰，才干利于蜘蛛爬行。SEO外包如果页面调用了大量的JS，Iframe框架往往会拔苗助长，因为蜘蛛还不能完全读取到其内容，框架结构应使用“DIV+CSS”进行布局。

设置链接主动推送，让蜘蛛第一时间发现你的网站
    '''
    result = fanyi_content(text)
    print(result)