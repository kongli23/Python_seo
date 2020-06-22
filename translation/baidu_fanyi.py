#百度通用翻译API,不包含词典、tts语音合成等资源，如有相关需求请联系translate_api@baidu.com
# coding=utf-8

import http.client
import hashlib
import urllib
import random
import json
import re

def fanyi(text):
    appid = '20200622000503976'  # 填写你的appid
    secretKey = 'w1Wmf2Z3WD18QFXRQ2Yi'  # 填写你的密钥

    result = None
    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'auto'  # 原文语种
    toLang = 'zh'  # 译文语种
    salt = random.randint(32768, 65536)
    # q = 'apple'
    sign = appid + text + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        text) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

    except Exception as e:
        result = None
        print(e)
    finally:
        if httpClient:
            httpClient.close()

    return result


def baidu_fanyi(text):
    new_text = ''
    result = fanyi(text)
    contents = re.compile(r"dst': '(.*?)'}").findall(str(result))
    for str_text in contents:
        new_text += str_text+'\n\n'
    return new_text

if __name__ == '__main__':
    text = '''
    Many novices are very troubled about the daily work of SEO. In addition to sending articles every day, only articles are left, and the articles are also pseudo-original. I feel that the work content is very monotonous and meaningless. In fact, doing SEO work is not just about publishing articles, but also about sending out links, new media operations, web page optimization, etc., the super ranking system is compiled and released.

1. Check whether the published article is included

Whether you are pseudo-original or original, you should check whether your published articles are included. What is the proportion of the entire website or section page included? Analyze the reason why the article is not included, and analyze which column page has a low percentage of inclusion Is there a problem with the structure of the article? Is this page not crawled? Looking for reasons?

If the page is included, analyze whether the page is effectively included, can it bring natural search traffic to the web page, does the included page have duplicate content? What pages will reduce the time to be crawled?

Second, insist on making high-quality original content

Webmasters may all understand that it is not easy to create original content, but it is really good to stick to one thing. For example, in our optimization industry, such as the well-known Moonlight blog, we insist on being original, although occasionally It is carried out in the mode of submission, but the actual benefits brought by original content are inestimable. Anyway, you also need to do pseudo-original, it is better to spend more time to do original creation. The benefits gained in this way will be higher.

3. The importance of uninterrupted keyword research

When we are doing original or pseudo-original, we don’t think of where we are, the premise is that we must meet the psychological needs of consumers in order to complete the user experience. In the optimization process, the most important thing for user needs is keyword analysis.

Everyday keywords need continuous research and analysis, focusing on user preferences? What are the needs? What kinds of breaking news can be used every day, after all, there are many domestic social hotspots, and any one can create a lot of gimmicks, attracting public attention and clicks, which involves industry hotspots. By the way, long tail keywords can be considered. What are the corresponding key Have word pages ranked? Can you find effective keywords from the traffic changes on the page?

3. Whether the website pages meet the real needs of users

Perhaps there are objections to search engines and user experience, but a good user experience is not a bad thing. After all, improving user volume is our ultimate goal.

Can the content of your website be liked by users? What data are there to prove? What software is used for testing? Which section pages have a high bounce rate? Which page users stay for a long time and visit a deep path? What methods can be used to change these status quo? Is the overall website conversion rate good? What multivariate tests have been done on the page?

4. Check whether the basic optimization of the website is perfect

In fact, the basic optimization of the website is divided into in-site optimization and off-site optimization. The optimization details mainly include: the internal link structure layout optimization of the website, the design of the URL mechanism, the basic label operation of the page, the perfect layout of the page, whether the layout is conducive to optimization ? Whether the keyword density of the page is properly arranged, and the speed of page opening, server settings, database, program, and picture optimization, as far as possible to reduce the number of data requests, cache time, CND use and other series of problems are resolved and perfected in time.

V. Reasonably optimize the mobile terminal

At present, the mobile terminal has occupied a favorable domestic market, although the computer terminal optimization will drive the mobile terminal optimization, if you can spend a little thought on the mobile terminal optimization, the mobile terminal mobile page is displayed normally on the phone without zooming in, and the screen is pulled horizontally That's it.

Sixth, do a good job in social media operations

Although the fans and likes on social media are not good for the ranking of the website, but as long as you manage the social media number and synchronize the content with the content of the website, more or less will have a certain influence on the website.

As an SEO person, as long as you insist on perfecting and implementing your work, you will find that there are actually a lot of work that you need to do to do SEO. There is no boring time, and there are surprises and fun brought by doing website optimization everywhere.
    '''
    content = baidu_fanyi(text)
    print(content)