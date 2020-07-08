# -*- coding: utf-8 -*-
"""
通用网页正文提取模块

特点：
1. 支持全网正文提取
2. 自动补全链接
3. 自动格式化内容，所有内容都将包含在p标签中
4. 可以获取内容的得分，字数以及图片数量，根据个人的需求进行筛选

结果内容判定:
1. 内容节点评分高: 根据算法计算出来的节点分数
2. 链接占比低: 内容节点中链接标签的比例
3. 链接文本数少: 内容节点中平均每个链接的文本数量
"""
import math
import re

from lxml import etree
from urllib.parse import urljoin


class CountInfo(object):
    def __init__(self):
        self.text_count = 0
        self.link_text_count = 0
        self.tag_count = 0
        self.link_tag_count = 0
        self.density = 0.0
        self.density_sum = 0.0
        self.score = 0.0
        self.pcount = 0
        self.leaflist = []


class Extractor(object):
    def __init__(self):
        self.__doc = None
        self.__infomap = {}
        self.__blockinfo = {}
        self.url = None  # 原始URL
        self.__newline = ["div", "li", "p", "h1", "h2",
                          "h3", "h4", "h5", "tr", "img"]
        self.top_node = None  # 最佳节点
        self.title = ""  # 网页标题
        self.__titlelen = 0
        self.clean_text = ""  # 纯文本
        self.format_text = ""  # 格式化文本
        self.score = 0.0  # 内容得分
        self.link_text_ratio = 0.0  # 链接文本比例
        self.text_count = 0  # 内容字数
        self.img_count = 0  # 图片数量
        self.__findtitle = True
        self.__title_tmp = ""

    def extract(self, url, html):
        """
        住提取函数
        :param url: 要提取的URL，主要用来做图片链接补全
        :param html: 网页源码
        :return:
        """
        try:
            clean_html = self.__clean_tag(html)
            self.__doc = etree.HTML(clean_html)
        except (TypeError, ValueError, etree.XMLSyntaxError):
            return
        if self.__doc is None:
            return
        self.url = url
        self.title = self.__get_title()
        if self.title is None:
            return
        self.__titlelen = len(self.title)
        self.score, self.link_text_ratio = self.__get_top_node()
        if self.top_node is None:
            return
        self.remove_link_block()
        try:
            if (len(self.__title_tmp) / float(self.__titlelen)) > 0.2:
                self.title = self.__title_tmp
        except ZeroDivisionError:
            return
        content = self.output_format(self.top_node)
        self.clean_text = "\n".join([t if "img" not in t else
                                     "" for t in content.split('\n')])
        for text in content.split("\n"):
            if "img" in text:
                self.img_count += 1
                self.format_text += '<p align="center">{}</p>'.format(text)
            else:
                text = text.strip()
                if not text:
                    continue
                self.text_count += len(text)
                self.format_text += '<p>{}</p>'.format(text)
        return True

    def __abstructurl(self, urlpath):
        """URL相对链接补全"""
        return urljoin(self.url, urlpath)

    def __get_title(self):
        """获取网页标题"""
        title = self.__doc.xpath('//title/text()')
        if title:
            return title[0].strip()

    @staticmethod
    def __clean_tag(doc):
        """去除掉script,noscript,style,iframe,br等标签"""
        doc = re.sub(r'<script.*?>.*?</script>', '', doc, flags=(re.I | re.S))
        doc = re.sub(r'<noscript.*?>.*?</noscript>', '', doc, flags=(re.I | re.S))
        doc = re.sub(r'<style.*?>.*?</style>', '', doc, flags=(re.I | re.S))
        doc = re.sub(r'<iframe.*?>.*?</iframe>', '', doc, flags=(re.I | re.S))
        doc = re.sub(r'[\r\t]+', '', doc)
        doc = re.sub(r'<br\s*/?>', '\n', doc, flags=re.I)
        doc = re.sub(r'<!--.*?-->', '', doc, flags=re.S)
        doc = re.sub(r'&nbsp;', ' ', doc, flags=re.S)
        return doc

    @staticmethod
    def __contents(node):
        """提取节点的所有文本以及子节点"""
        result = []
        result.extend(node.xpath("child::text()|child::*"))
        return result

    def __calcuate(self, node, record):
        """计算各个节点的信息"""
        if etree.iselement(node):
            info = CountInfo()
            for elem in self.__contents(node):
                childinfo = self.__calcuate(elem, record)
                info.text_count += childinfo.text_count
                info.link_text_count += childinfo.link_text_count
                info.tag_count += childinfo.tag_count
                info.link_tag_count += childinfo.link_tag_count
                info.leaflist.extend(childinfo.leaflist)
                info.density_sum += childinfo.density
                info.pcount += childinfo.pcount

            info.tag_count += 1
            tagname = node.tag
            if tagname == "a":
                info.link_text_count = info.text_count
                info.link_tag_count += 1
            elif tagname == "p":
                info.pcount += 1

            purelen = info.text_count - info.link_text_count
            not_link_tag_num = info.tag_count - info.link_tag_count

            if purelen == 0 or not_link_tag_num == 0:
                info.density = 0
            else:
                info.density = float(purelen) / not_link_tag_num
            record[node] = info
            return info
        elif hasattr(node, "is_text"):
            info = CountInfo()
            nodetext = node.strip()
            txtlen = len(nodetext)
            info.text_count = txtlen
            info.leaflist.append(txtlen)
            tmp_len = len(self.__title_tmp)
            if self.__findtitle and tmp_len < txtlen <= self.__titlelen \
                    and self.title.startswith(nodetext):
                self.__title_tmp = nodetext
            return info
        else:
            return CountInfo()

    def __calcuate_score(self, node):
        """计算节点得分"""
        info = self.__infomap.get(node)
        if info is None:
            return 0.0
        val = math.sqrt(self.__calcuate_var(info.leaflist) + 1)
        return math.log(val) * info.density_sum * \
               math.log(float(info.text_count - info.link_text_count) + 1.0) * \
               math.log10(float(info.pcount) + 2.0)

    @staticmethod
    def __calcuate_var(leafs):
        """计算平均分"""
        leaf_len = len(leafs)
        if leaf_len <= 0:
            return 0.0
        if leaf_len == 1:
            return leafs[0] / 2.0
        sums = 0.0
        for v in leafs:
            sums += float(v)
        ave = sums / leaf_len
        sums = 0.0
        for v in leafs:
            sums += (float(v) - ave) ** 2
        sums /= leaf_len
        return sums

    def __get_top_node(self):
        """获取内容主体节点"""
        self.__findtitle = True
        body = self.__doc.find("body")
        self.__calcuate(body, self.__infomap)
        max_score = 0.0
        link_text_ratio = 0.0
        for node, info in self.__infomap.items():
            tagname = node.tag
            if tagname in ["a", "body"]:
                continue
            score = self.__calcuate_score(node)
            if score > max_score:
                max_score = score
                self.top_node = node
                try:
                    link_text_ratio = info.link_text_count / \
                                      float(info.text_count)
                except ZeroDivisionError:
                    pass
        return max_score, link_text_ratio

    def output_format(self, cnode):
        """格式化内容输出"""
        content = ""
        for node in self.__contents(cnode):
            if hasattr(node, "is_text"):
                content += node
            elif etree.iselement(node):
                if node.tag in self.__newline:
                    content += "\n"
                if node.tag == "img":
                    src = node.attrib.get("data-src", "") \
                          or node.attrib.get("src", "")
                    src = self.__abstructurl(src)
                    content += '<img src="{}" />'.format(src)
                content += self.output_format(node)
        return content.strip()

    def remove_link_block(self):
        """删除链接块"""
        self.__findtitle = False
        self.__calcuate(self.top_node, self.__blockinfo)
        for node, info in self.__blockinfo.items():
            if node.tag == "a":
                continue
            try:
                link_text_ratio = info.link_text_count / info.text_count
            except ZeroDivisionError:
                continue
            if link_text_ratio > 0.5:
                parentnode = node.getparent()
                if etree.iselement(parentnode):
                    parentnode.remove(node)
