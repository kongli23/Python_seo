# -*- coding:utf-8 -*-
from wp_post.wordpress import wp_post
from wp_post.translate.google import google
from wp_post.tuisong import tuisong

def auto_post(title,content,keywords):
    # post_id = wp_post(title, google(content), keywords, 'SEO优化')

    print('正在发布标题：{}'.format(title))
    post_id = wp_post(title, content, keywords, 'SEM推广')
    art_url = 'https://www.ncle.net/sem/{}'.format(post_id)
    print('发布成功,地址：{},等待推送...'.format(art_url))
    tuisong(art_url)

    print('执行发布完成!')