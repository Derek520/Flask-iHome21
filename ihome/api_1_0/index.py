# -*- coding:utf-8 -*-

from . import api


# 使用蓝图

@api.route('/')
def hello_flask():
    return 'hello world'


