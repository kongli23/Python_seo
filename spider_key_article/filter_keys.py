# -*- coding:utf-8 -*-
import re

# 加载特征词
badwords = r'|'.join(w.strip() for w in open('exclude.txt', encoding='utf-8'))
# 检测包含特征词的正则
rm_bad_sentence = re.compile(badwords, re.I | re.S)
# 检测内容网址的正则
rm_links = re.compile('((https?|ftp|file)://)?[-a-z0-9+&@#/%=~|?!:,\.。;]+\.[-a-z0-9+&@#/%=~|]+', re.I | re.S)
# 提取段落
exp = re.compile(r'<p>([^>]+)</p>', re.I | re.S)


# 采集内容的一般处理方法
# 1. 对内容去除噪音之后直接使用
# 2. 直接拼接
# 3. 在1的基础上，加上自己的一两段话，分别加在首末段，这种都是有模板的
def clean_content(content):
    """
    对内容进行清洗
    1. 去除内容噪音（特征词包含），只要包含特征词的句子全部干掉
    2. 去除网址
    """
    # 提取文章段落
    sentences = exp.findall(content)
    new_content = ""
    for p in sentences:
        if rm_bad_sentence.search(p):
            continue
        # 过滤完文本之后,立即进行文本翻译伪原创处理
        new_content += f'<p>{p}</p>'
    # 删除链接并返回
    return rm_links.sub('', new_content)

# 对于标题的建议
# 1. 直接有用关键词作为标题
# 2. 关键词+相关词作为标题
# 3. 对原标题进行处理

def test():
    str = '实验室布局是实验室规划的基础。只要按照功能分区和工作流程的要求进行相应的布置规划，就可以保证后续的水、电、风等技术专业设计方案。“因此”，平面布置设计阶段应尽可能详细地考虑工作和发展需要，合理分配空间，尽可能优化和整合。除了优化布局和实验室设备摆放设计外，“还应充分考虑人员流向和物品流向是否符合工作要求”。'
    str2 = '实验室布局是实验室规划的基础。只要按照功能分区和工作流程的要求进行相应的布置规划，就可以保证后续的水、电、风等技术专业设计方案。因此，平面布置设计阶段应尽可能详细地考虑工作和发展需要，合理分配空间，尽可能优化和整合。除了优化布局和实验室设备摆放设计外，还应充分考虑人员流向和物品流向是否符合工作要求。'
    res = re.sub(r'“|”', '"', str2)
    print(res)

if __name__ == '__main__':
    test()