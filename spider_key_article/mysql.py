# -*- coding:utf-8 -*-
import pymysql
from spider_key_article.wordpress import wp_post
from spider_key_article.translate.google import google

# 创建链接字符串
conn = pymysql.connect(host='192.168.244.128',user='spider',password='spider',database='spider',port=3306)
# 创建游标，操作mysql必须得有这个
cursor = conn.cursor()

# insert 插入数据操作
# for i in range(10,20):
#     # 构建sql语句，此处的参数，不管是int 还是str 都得用 %s否则会报错
#     sql = "insert ignore into article(keywords,title,content) values('seo','seo是什么意思标题{}','seo是什么意思文章')".format(i)
#     # 执行sql语句
#     cursor.execute(sql)
#     # 提交要执行的sql命令
#     conn.commit()

# 2.返回多条数据
sql = 'select id,keywords,title,content from baidu_search'
cursor.execute(sql)
result = cursor.fetchall()
# print(result)
for resList in result[56:]:
    id,keywords,title,content = resList
    # print(keywords,title,google(content))
    res = wp_post(title,google(content),keywords,'SEO优化')
    print(res)

# 操作完毕必须关闭连接
conn.close()
print('执行插入完成!')