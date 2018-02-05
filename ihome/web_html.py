# -*- coding:utf-8 -*-

# web_html.py专门处理静态文件

from flask import Blueprint,current_app

# 创建蓝图
web_html = Blueprint('web_html',__name__)

'''
127.0.0.1/       ----->     index.html
127.0.0.1/index.html  ----->index.html

127.0.0.1/favicon.ico ---->浏览器会默认发送这个请求,只会第一次请求
'''


@web_html.route('/<re(".*"):file>')
def index(file):
    print file
    # 如果没有传文件 访问的是127.0.0.1 就给file赋值index.html
    if not file:
        file = 'index.html'
    # 再判断如果file不等于favicon.ico,进行路径拼接
    if file != 'favicon.ico':
        file = 'html/'+file
    print '-'*30
    print file
    return current_app.send_static_file(file)

# @web_html.route('/')
# def index():
#     return current_app.send_static_file('html/index.html')
#
# @web_html.route('/<html>')
# def index2(html):
#     print html
#     return current_app.send_static_file('html/index.html')