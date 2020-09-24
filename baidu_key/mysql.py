# -*- coding:utf-8 -*-
import pymysql


# 创建链接字符串
conn = pymysql.connect(host='127.0.0.1',user='spider',password='123456',database='spider',port=3306)
# 创建游标，操作mysql必须得有这个
cursor = conn.cursor()

# 2.返回多条数据,0-10000条
sql = 'select keywords from sys'
cursor.execute(sql)
result = cursor.fetchall()

for resList in result:
    print('{}'.format(resList[0]))

# 操作完毕必须关闭连接
conn.close()
print('执行发布完成!')