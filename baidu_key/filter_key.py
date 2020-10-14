# -*- coding:utf-8 -*-
import re

# 加载特征词
badwords = r'|'.join(w.strip() for w in open('exclude.txt', encoding='utf-8'))
# 检测包含特征词的正则
rm_bad_sentence = re.compile(badwords, re.I | re.S)


# 过滤关键词
def clean_key(content):
    """
    对关键词过滤，存在文件的则排除，否则保持不变
    """
    if rm_bad_sentence.search(content):
        return None
    else:
        return content