from translation.google_fanyi import google_fanyi
from translation.baidu_fanyi import Dict

def fanyi_content(text):
    '''
    传入中文，将中文翻译成英文，再将英文翻译成中文

    :param text: 要翻译的p标签
    :return: 返回翻译后的中文
    '''
    # 使用谷歌将中文翻译英文
    en_text = google_fanyi(text)

    # 使用百度将英文翻译中文
    dt = Dict()
    cn_text = dt.baidu_fanyi(en_text)
    return cn_text

if __name__ == '__main__':

    text = '''
    <p>从未知的领域来到seo，感到搜索引擎无比神奇，接触seo久了，有每天必做的工作内容，大量的seo从业者，每天的工作内容大同小异，主要做的工作有通过相应工具查看网站关键词排名情况，网站收录情况，组织内容，发外链，分析竞争对手数据以及seo做法等。</p>
    '''
    result = fanyi_content(text)
    print(result)