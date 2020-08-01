# -*- coding:utf-8 -*-
import pymysql
from spider_key_article.wordpress import wp_post
from spider_key_article.translate.google import google
from spider_key_article.tuisong import tuisong

# 创建链接字符串
conn = pymysql.connect(host='103.44.241.97',user='spider',password='spider',database='spider',port=3306)
# 创建游标，操作mysql必须得有这个
cursor = conn.cursor()

# 2.返回多条数据,0-10000条
sql = 'select id,keywords,title,content from baidu_search limit 0,10000'
cursor.execute(sql)
result = cursor.fetchall()

for resList in result[150:]:
    id,keywords,title,content = resList

    if len(content) > 300:
        post_id = wp_post(title, google(content), keywords, 'SEO优化')
        art_url = 'https://www.ncle.net/seo/{}'.format(post_id)
        print('发布成功,地址：{},等待推送...'.format(art_url))
        tuisong(art_url)

# 操作完毕必须关闭连接
conn.close()
print('执行发布完成!')