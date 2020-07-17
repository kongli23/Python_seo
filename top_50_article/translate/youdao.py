import hashlib
import requests
import time
import random
import re
from top_50_article.translate.user_agent import RandomUserAgent

class translate_youdao():
    def __init__(self, msg):
        self.msg = msg
        self.url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
        self.get_ts = self.get_ts()
        self.user_agent = RandomUserAgent

    def get_ts(self):
        # 获取当前时间戳
        s = int(time.time() * 1000)
        return str(s)

    def get_salt(self):
        # salt参数 由时间戳 + 一位随机数组成
        s = str(int(time.time() * 1000)) + str(random.randint(0, 9))
        return s

    def get_sign(self):
        e = self.msg
        i = self.get_salt()
        words = "fanyideskweb" + e + i + "mmbP%A-r6U3Nw(n]BjuEU"
        # MD5加密
        m = hashlib.md5()
        m.update(words.encode("utf-8"))
        return m.hexdigest()

    def get_bv(self):
        n = hashlib.md5()
        n.update(self.user_agent.encode("utf-8"))
        return n.hexdigest()

    def fanyi(self):
        form_data = {
            "i": self.msg,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": self.get_salt(),
            "sign": self.get_sign(),
            "ts": self.get_ts,
            "bv": self.get_bv(),
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTlME"
        }
        headers = {
            "Referer": "http://fanyi.youdao.com/",
            "User-Agent": self.user_agent
        }
        res = requests.get("http://fanyi.youdao.com/", headers=headers)
        cookies = res.cookies
        dict = requests.utils.dict_from_cookiejar(cookies)
        if "OUTFOX_SEARCH_USER_ID" in dict:
            headers = {
                # "OUTFOX_SEARCH_USER_ID": dict["OUTFOX_SEARCH_USER_ID"],
                "OUTFOX_SEARCH_USER_ID": dict["OUTFOX_SEARCH_USER_ID"],
                "Referer": "http://fanyi.youdao.com/",
                "User-Agent": self.user_agent
            }
            res = requests.post(self.url, headers=headers, data=form_data)
            return res.content.decode().strip()
        else:
            return "返回出错"

def youdao(words):
    '''
    有道翻译
    :param words:
    :return:
    '''
    youdao = translate_youdao(words)
    result = youdao.fanyi()
    tgt = re.compile(r'"tgt":"(.*?)"').findall(str(result).replace('< p >', '<p>').replace('< \/ p >', '</p>'))
    content = ''.join(tgt)
    # print('有道结果：{}'.format(content))
    # .replace(',', '')
    return content

if __name__ == '__main__':
    text = """Sometimes it’s easier to act earlier than later, rationality is not so indecisive when it is determined, and you want to change when you act.
After a long time of work, I suddenly let go and changed my way to another road. This is a common occurrence on the road, because a person redefines himself, and this action must be a decision of no less than ten times. Too.
Some actions just change your own path, not the reality of prosperity and adversity, some actions really change your life, some actions just re-encounter a charm of life, some actions really surround a meaning value around life, some actions just Change to another field to create another possibility, some actions are really just to enrich the self to master the real world.
Every kind of action hopes to have a wonderful life down to earth, every kind of action realizes the potential of self-flying to form an influence, every kind of action is to convey the realm to itself, and every kind of action is to convey the ideological soul to the self.
Action is to re-select the direction, action is to change the present, action is to go to the ideal in your heart, action is to move forward to reality, action is your spirit to fight back.000"""
    res = youdao(text)
    print(res)