import execjs   #使用它，得安装另一个库 pip install PyExecJS
import requests
import re
import json

JS_CODE = """
function a(r, o) {
    for (var t = 0; t < o.length - 2; t += 3) {
        var a = o.charAt(t + 2);
        a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
        a = "+" === o.charAt(t + 1) ? r >>> a: r << a,
        r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
    }
    return r
}
var C = null;
var token = function(r, _gtk) {
    var o = r.length;
    o > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(o / 2) - 5, 10) + r.substring(r.length, r.length - 10));
    var t = void 0,
    t = null !== C ? C: (C = _gtk || "") || "";
    for (var e = t.split("."), h = Number(e[0]) || 0, i = Number(e[1]) || 0, d = [], f = 0, g = 0; g < r.length; g++) {
        var m = r.charCodeAt(g);
        128 > m ? d[f++] = m: (2048 > m ? d[f++] = m >> 6 | 192 : (55296 === (64512 & m) && g + 1 < r.length && 56320 === (64512 & r.charCodeAt(g + 1)) ? (m = 65536 + ((1023 & m) << 10) + (1023 & r.charCodeAt(++g)), d[f++] = m >> 18 | 240, d[f++] = m >> 12 & 63 | 128) : d[f++] = m >> 12 | 224, d[f++] = m >> 6 & 63 | 128), d[f++] = 63 & m | 128)
    }
    for (var S = h,
    u = "+-a^+6",
    l = "+-3^+b+-f",
    s = 0; s < d.length; s++) S += d[s],
    S = a(S, u);
    return S = a(S, l),
    S ^= i,
    0 > S && (S = (2147483647 & S) + 2147483648),
    S %= 1e6,
    S.toString() + "." + (S ^ h)
}
"""


class Dict:
    def __init__(self):
        self.sess = requests.Session()
        self.headers = {
            'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        self.token = None
        self.gtk = None

        # 获得token和gtk
        # 必须要加载两次保证token是最新的，否则会出现998的错误
        self.loadMainPage()
        self.loadMainPage()

    def loadMainPage(self):
        """
            load main page : https://fanyi.baidu.com/
            and get token, gtk
        """
        url = 'https://fanyi.baidu.com'

        try:
            r = self.sess.get(url, headers=self.headers)
            self.token = re.findall(r"token: '(.*?)',", r.text)[0]
            self.gtk = re.findall(r"window.gtk = '(.*?)';", r.text)[0]
        except Exception as e:
            raise e
            # print(e)

    def langdetect(self, query):
        """
            post query to https://fanyi.baidu.com/langdetect
            return json
            {"error":0,"msg":"success","lan":"en"}
        """
        url = 'https://fanyi.baidu.com/langdetect'
        data = {'query': query}
        try:
            r = self.sess.post(url=url, data=data)
        except Exception as e:
            raise e
            # print(e)

        json = r.json()
        if 'msg' in json and json['msg'] == 'success':
            return json['lan']
        return None

    def dictionary(self, query):
        """
            max query count = 2
            get translate result from https://fanyi.baidu.com/v2transapi
        """
        url = 'https://fanyi.baidu.com/v2transapi'

        sign = execjs.compile(JS_CODE).call('token', query, self.gtk)

        lang = self.langdetect(query)
        data = {
            'from': 'en' if lang == 'en' else 'zh',
            'to': 'zh' if lang == 'en' else 'en',
            'query': query,
            'simple_means_flag': 3,
            'sign': sign,
            'token': self.token,
        }
        try:
            r = self.sess.post(url=url, data=data)
        except Exception as e:
            raise e

        if r.status_code == 200:
            json = r.json()
            if 'error' in json:
                raise Exception('baidu sdk error: {}'.format(json['error']))
                # 998错误则意味需要重新加载主页获取新的token
            return json
        return None

    def dictionary_by_lang(self, query, fromlang, tolang):
        """
            max query count = 2
            get translate result from https://fanyi.baidu.com/v2transapi
        """
        url = 'https://fanyi.baidu.com/v2transapi'

        sign = execjs.compile(JS_CODE).call('token', query, self.gtk)

        lang = self.langdetect(query)
        data = {
            'from': fromlang,
            'to': tolang,
            'query': query,
            'simple_means_flag': 3,
            'sign': sign,
            'token': self.token,
        }
        try:
            r = self.sess.post(url=url, data=data)
        except Exception as e:
            raise e

        if r.status_code == 200:
            js = json.loads(r.text)

            text = ''
            for dst in js['trans_result']['data']:
                result = dst['result']
                for res in result:
                    # print(res)
                    text += str(res[1])+str(res[3])
            text = text.replace('[]','')
            text = text.replace(r"['1|\n']",'\n\n')
            return text
        return None

    def baidu_fanyi(self, text):
        ret1 = self.dictionary_by_lang(text, "en", "zh")
        return ret1

if __name__ == '__main__':
    text = '''
    Active push is to put a string of JS code on each page of the site. When the user visits, the code will be triggered, and SEO outsourcing will submit the page URL to Baidu. It is a very convenient and worry-free SEO optimized link push method.

 

New site SEO optimization pages that want to be ranked should have a lot of internal links connected to them. Intranet with strong correlation can not only improve the entry, but also increase the weight score of the page. External links, through a large number of external links to point to the pages you want to participate in ranking, to reach user referrals, is also a very good way.

 

With the active push code installed, the website only needs to have visitors to push the address to Baidu, and the spider will get the information at the first moment, thereby facilitating crawling and entry.

 

SEO optimized articles must be depicted around the long-tailed words of the title, showing the dry goods to the user. The longer the user stays, the better the ranking will be. Recommended reading: If you want to expand your website’s popularity, SEO optimization starts here

 

The structure of the website is simple and clear, and its ability is conducive to spider crawling. SEO outsourcing If the page calls a lot of JS, the Iframe framework tends to grow, because spiders can't fully read its content, the frame structure should use "DIV+CSS" for layout.

Set the link to actively push, let the spider find your website the first time
    '''
    dt = Dict()
    res = dt.baidu_fanyi(text)
    print(res)