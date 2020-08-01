#coding:utf-8
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts


wp = Client('https://www.ncle.net/xmlrpc.php', 'test', 'test')

# filename = r'C:\Users\Kongli\Pictures\QQ图片20200513164614.jpg' #上传的图片文件路径

# prepare metadata
# data = {
#         'name': '123321.jpg',
#         'type': 'image/jpeg',  # mimetype
# }
#
# with open(filename, 'rb') as img:
#         data['bits'] = xmlrpc_client.Binary(img.read())
#
# response = wp.call(media.UploadFile(data))
# attachment_id = response['id']

def wp_post(title,content,tags,category):
    post = WordPressPost()
    post.title = title
    post.content = content
    post.post_status = 'publish'  # 文章状态，不写默认是草稿，private表示私密的，draft表示草稿，publish表示发布
    post.terms_names = {
        'post_tag': [tags],  # 文章所属标签，没有则自动创建
        'category': [category]  # 文章所属分类，没有则自动创建
    }
    # post.thumbnail = attachment_id #缩略图的id
    post.id = wp.call(posts.NewPost(post))
    return post.id

if __name__ == '__main__':
    post_id = wp_post('测试标题','测试内容','我是标签','SEO优化')
    print(post_id)