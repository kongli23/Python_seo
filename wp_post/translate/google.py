# -*- coding:utf-8 -*-
import urllib
import urllib.request
import urllib.parse
import requests
import execjs
import re
from spider_key_article.translate.youdao import youdao

class translate_google():
    def __init__(self,word_limit=1000, dl_words=300):
        self.spilt = re.compile(r'</?p.*?>|\n', re.I | re.S)
        self.sent_end = re.compile(r'([。.?？!！;；])', re.I)
        self.word_limit = word_limit
        self.dl_words = dl_words

        self.lan_dict = {
            '中文': 'zh-CN',
            '英文': 'en',
            '俄文': 'ru',
            '法文': 'fr',
            '日文': 'ja',
            '韩文': 'ko'
        }

        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
        self.url = 'http://translate.google.cn/translate_a/single'
        self.session = requests.Session()
        self.session.keep_alive = False

    def getTk(self, text):
        return self.get_ctx().call("TL", text)

    def get_ctx(self):
        ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 
        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 
        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 
    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)
        return ctx

    def buildUrl(self,text ,tk, sl,tl):
        baseUrl = 'http://translate.google.cn/translate_a/single'
        baseUrl += '?client=webapp&'  #这里client改成webapp后翻译的效果好一些 t翻译的比较差 ..
        baseUrl += 'sl=auto&'
        baseUrl += 'tl=' + str(tl) + '&'
        baseUrl += 'hl=zh-CN&'
        baseUrl += 'dt=at&'
        baseUrl += 'dt=bd&'
        baseUrl += 'dt=ex&'
        baseUrl += 'dt=ld&'
        baseUrl += 'dt=md&'
        baseUrl += 'dt=qca&'
        baseUrl += 'dt=rw&'
        baseUrl += 'dt=rm&'
        baseUrl += 'dt=ss&'
        baseUrl += 'dt=t&'
        baseUrl += 'ie=UTF-8&'
        baseUrl += 'oe=UTF-8&'
        baseUrl += 'clearbtn=1&'
        baseUrl += 'otf=1&'
        baseUrl += 'pc=1&'
        baseUrl += 'srcrom=0&'
        baseUrl += 'ssel=0&'
        baseUrl += 'tsel=0&'
        baseUrl += 'kc=2&'
        baseUrl += 'tk=' + str(tk) + '&'
        content=urllib.parse.quote(text)
        baseUrl += 'q=' + content
        return baseUrl

    def getHtml(self, session, url, headers):
        try:
            html = session.get(url, headers=headers)
            return html.json()
        except Exception as e:
            return None

    def translate(self, from_lan, to_lan, text):
        tk = self.getTk(text)
        url = self.buildUrl(text, tk, from_lan, to_lan)
        result = self.getHtml(self.session, url, self.headers)
        if result != None:
            ans = ""
            s=''
            try:
                for i in result[0]:
                    if i[0] != None:
                        s += i[0]
                for i in s.split('\n'):
                    ans += i
            except TypeError as err:
                pass
            return ans
        else:
            try:
                self.logger.info('谷歌翻译失败 ')
            except AttributeError as err:
                pass
            return None

    def split_article(self,article):
        sentences = self.spilt.split(article)
        text = ""
        ai_text = ""
        while sentences:
            text_len = len(text)
            if text_len < self.word_limit:
                t = sentences.pop(0)
                text += t.strip()
            if text_len >= self.word_limit or not sentences:
                ai_text += self.ai_article(text)
                text = ""
        return self.make_dl(ai_text)

    def ai_article(self, text):
        if not isinstance(text, str):
            return
        zh_en = self.translate('zh-CN', 'en', text)
        if not zh_en:
            return text
        en_zh = youdao(zh_en)
        # en_zh = self.translate(zh_en, "en", "zh-CN")
        return en_zh if en_zh else text

    def make_dl(self, text):
        new_text = self.sent_end.sub('\g<1>\n', text)
        sentences = re.split(r'\n', new_text)
        new_article = ""
        p_text = ""
        for t in sentences:
            if len(p_text) > self.dl_words:
                new_article += f'<p>{p_text}</p>'
                p_text = ""
                continue
            p_text += t
        else:
            new_article += f'<p>{p_text}</p>'
        return new_article

def google(text):
    '''
    谷歌翻译
    :param text:
    :return:
    '''
    g = translate_google()
    res = g.split_article(text)
    return res

if __name__ == '__main__':
    text = ""
    with open('demo.txt','r',encoding='utf-8') as f:
        text = f.read()
    # print(text)
    res = google(text)
    print('结果：{}'.format(res))