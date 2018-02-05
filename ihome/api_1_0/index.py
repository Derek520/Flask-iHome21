# -*- coding:utf-8 -*-

from . import api
from ihome import db

# 2. 使用蓝图装饰路由

@api.route('/')
def hello_flask():
    print db,3
    return 'hello world'


