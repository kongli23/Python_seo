import hashlib
import requests
import time
import random
import re
from top_50_article.user_agents import RandomUserAgent

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
    content = ','.join(tgt)
    # print('有道结果：{}'.format(content))
    # .replace(',', '')
    return content

if __name__ == '__main__':
    text = """<p>It's hard to say, laboratory decoration is generally to follow up your budget and expectations to determine a reasonable plan, a penny and a penny. Need to know, you can find the staff of Guangzhou Jiadong.</p><p>Laboratory decoration design is a huge project, so all aspects need to be considered, whether it is the early design or the later decoration, there are still many precautions. The following Anhui Renhe Purification introduces you to the standard PCR laboratory decoration design...</p><p>Based on Xige's many years of experience, I would like to ask: Isn't there only four rooms for PCR genetic testing? Is there any other laboratory function requirements?</p><p>The key depends on how you want to get it. Only about 4000 walls are refurbished. The cost of renovating the kitchen and bathroom is 10,000 to tens of thousands. If the ground is to be refurbished, it will cost more than 10,000.</p><p>See your decoration requirements, install it for 40,000, the room is small, the material must use diatom mud floor, diatom mud paint and other environmentally friendly materials1</p><p>The flexibility of the decoration is relatively large, and your idea is to simply decorate; but there are also "key" requirements, I give you a comprehensive consideration: may need to invest 10,000 yuan, so as to meet your "key" requirements, and ...</p><p>As I have been engaged in the construction and decoration industry for many years, many decoration friends in my life often ask me the question is how many square meters of house decoration is about how much money I want to say is the decoration of 10,000 to 5,000 yuan per square meter. Some of the so-called packages of a certain decoration company of 688 per square meter are also some, depending on the decoration quality and what you want...</p><p>It depends on your decoration style. The relationship between this budget and your materials is too big, please consult a special decoration company.</p><p>This depends on which city you are in, whether you plan to lay wooden floors or ceramic tiles, or an apartment structure, etc. Basically, if the decoration of a house with a simple decoration of about 50 square meters does not include furniture, it is about 30,000. 600 level. Ceramic tiles are slightly more expensive than wooden floors. But if you can calculate it, you can save thousands of dollars without wasting materials. 1</p><p>Brother, please tell us how to install at least, so that we can give you a quotation, whether it is simple, hardcover, luxury, contractor materials, or not contractors, private contractors or companies, can’t open, where to decorate, companies, residential , Places, special places? If you don’t say anything, I can only tell you, about 10,000 to 100 million.</p><p>I'm in Shanghai, my home building materials decoration company over 20,000 decoration</p><p>Whether the new house is a second-hand house or not, whether it needs hydropower renovation or not, these will affect the decoration price. I used the decoration calculator to make a simple calculation for you. You can see the screenshot below, which is a rough quote for a conventional decoration project. The price of light industry auxiliary materials, the design cost can be ignored, the simple package can be directly planned by the construction party, and the construction party can give some suggestions.</p><p>Professional and regular decoration companies, generally 50 square meters of houses, if the contractor and package materials are simple decoration, the price will be at least 20,000-30,000 yuan. Including decoration design, diversion and replacement of coal, water, electricity, heating pipes, scraping white, tiling, installing sanitary ware, lamps...</p><p>It depends on how you decorate it. My public rental house bought furniture and appliances and cost nearly 20,000.</p><p>See how you want to install, basic decoration-simple decoration-fine decoration-300-500-700/㎡. And the total price difference of the after-sales service of different decoration companies will be around 10,000. You can go to Nanning's local decoration portal to see the outfit...</p><p>There are too many decoration companies in Ningbo now, and it is very troublesome to find one by one.Now many people are sending decoration bidding online, and many decoration companies come to bid, free budget quotation, design plan , Find multiple outfits...</p><p>It depends on whether you want to spend simple decoration or hardcover decoration on how much money you can spend. If you want simple decoration, first think about where you want to install it. If you want to find out the basic price, 500,000 square meters can basically be obtained. If you want high-end, at least It’s all 40,000 going up 6</p><p>It's hard to say, laboratory decoration is generally to follow up your budget and expectations to determine a reasonable plan, a penny and a penny. Need to know, you can find the staff of Guangzhou Jiadong.</p><p>It depends on whether you are an ordinary laboratory or a special laboratory. The ordinary cost is not expensive. The expensive is a special laboratory such as a biosafety laboratory or a clean laboratory.</p><p>How much is the decoration of 50 square meters; house decoration (all-inclusive) is required to have decoration standards, because the decoration price is more or less: If you want high-end point fine decoration, you need 1600-1700/ square to carry out decoration. If it is a mass decoration, it needs to be around 1100-1200 yuan/square, which is a general fine decoration. If you want to generalize the decoration, you can invest about 800-900 yuan / square, which is ordinary decoration. If the decoration is invested at 600-650 yuan/square, it is a simple and simple decoration. Therefore, house decoration depends on how much money is invested. If the investment is more, the decoration will be better. If the investment is less, the decoration will be general. If it is less, the decoration will be simple.</p><p>It depends on your requirements, style, brand, construction environment, etc. to determine the final offer. Hope it helps you</p><p>It depends on what kind of laboratory you are decorating. Generally, it needs tens of thousands of yuan! If it is just a simple whitewashed ceiling, it will be cheaper, or five or six thousand dollars!</p><p>office renovation? It depends on how you want to decorate. If it is a simple decoration for the general employee's collective office, it will not cost much. If it is the chairman's office or other high-level office, such a budget is not easy to estimate. After all, I don't know if you use What materials, design styles, and requirements, if you want to know the specific budget, I suggest you go to a regular decoration company to help you look, according to your design requirements, let them give you a corresponding budget plan.</p><p>How much is the wholesale manufacturer of Fuzhou color steel plate, supply Gansu Baiyin supply Fuzhou color steel plate Fuzhou special color steel plate? Fuzhou color... Drawing design, engineering installation, commissioning and after-sales service for clean engineering and supporting equipment of laboratories and so on.</p><p>How much does a 90 square meter house renovation cost? In fact, the simple decoration of a 90-square-meter house is about more than 30,000. If it is modern or European-style, with medium-grade equivalent materials, it will cost about 100,000. 200,000 for the Chinese style and 150,000 for the new pilot. There are also big differences according to the selection of materials. Here is to briefly talk to everyone. The decoration price of 90-square-meter house is simple, and the decoration is more than 30,000. The more common decoration method is half-package, 90 square meters is about 40,000 to 60,000; the all-inclusive can't quote you, because the main material is good or bad, the price is not capped. , Depending on your requirements; the general decoration main material costs are as follows: ceramic tile: about 6000 paint: about 1000 ceiling: about 2500 doors and windows: about 3000 cabinets: about 3000 bathroom: about 5000 water and electricity transformation: about 5000 labor Fee: About 9000 or so depends on the situation. When buying things, most people usually have already made a good price, but when they finally make a decision, they will think about their house. It doesn't matter if the budget is slightly exceeded. There are too many things that exceed the budget, and the final overrun amount ranges from 10,000 to 20,000, and more than 30,000 to 50,000. All must be controlled and cleared. The current labor cost is 200 to 400 a day, depending on your decoration project and construction period Length. Material cost pvp ceiling of 90 square house decoration price: 20-30 yuan/?. Paper gypsum board: 25-35/? (Standard specifications: 1200? × 2400? ×</p><p>How much is the general decoration of a house of 50 square meters in Chengdu; house decoration (all-inclusive) is required to have decoration standards, because the price of decoration is more or less: if you want high-end fine decoration, you need 1700-1800/square Decoration. If it is a general decoration, it needs to be about 1200-1300 yuan/square, which is a general fine decoration. If you want to generalize the decoration, you can invest about 800-900 yuan / square, which is ordinary decoration. If the decoration is invested at 600-650 yuan/square, it is a simple and simple decoration. Therefore, house decoration depends on how much money is invested. If the investment is more, the decoration will be better. If the investment is less, the decoration will be general. If it is less, the decoration will be simple.</p><p>Square, black series. Mainly depends on the brand, generally domestic 150-500 yuan & 47; square. Imported 300-1500 yuan & 47; square, beige series is very good. Natural ones are also available. The price is not equal. The price is 800-2000 yuan & 47, I mainly push the beige artificial best</p><p>It depends on whether you want to spend money in simple or hardcover decoration. If you want simple decoration, think about where you want to install first. If you want to find out the basic price according to your needs, 500,000 square meters can basically get it. Are all going up 40,000</p><p>How much is the general decoration of a house of 50 square meters in Jinan; house decoration (all-inclusive) is required to have decoration standards, because the price of decoration is more or less: if high-point fine decoration is required, it needs 1700-1800/square Decoration. If it is a general decoration, it needs to be about 1200-1300 yuan/square, which is a general fine decoration. If you want to generalize the decoration, you can invest about 800-900 yuan / square, which is ordinary decoration. If the decoration is invested at 600-650 yuan/square, it is a simple and simple decoration. Therefore, house decoration depends on how much money is invested. If the investment is more, the decoration will be better. If the investment is less, the decoration will be general. If it is less, the decoration will be simple. Last year, Jinsheju Decoration Company gave the decoration, I think the price is more appropriate! The quality of the decoration is no problem.</p><p>You don’t mean to invest in Shahe. Xisanqi, Beiyuan, or the place close to the 5th ring, it’s better to go to the 5th ring, go to the ground, and Qinghe to be honest</p><p>Apartment decoration depends on whether you live or rent. If you live by yourself, according to your own living requirements, material quality and brand requirements, there are pure differences in price. Generally speaking, the decoration price in the form of a half package is about 50,000 to 60,000. Depends on where your area is</p>"""
    res = youdao(text)
    print(res)