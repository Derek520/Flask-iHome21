# -*- coding:utf-8 -*-
from flask import Blueprint

# 1. 创建蓝图对象, 导入子模块
api = Blueprint('api',__name__)

import index,passport,profiles,verify_code,house,order

# 请求钩子
@api.after_request
def after_request(response):
    '''响应头设置'''
    # 判断响应头,如果是text/html就进行设置,其他的不需要设置
    if response.headers.get('Content-Type').startswith('text'):
        # 设置头信息
        response.headers["Content-Type"] = "application/json"

    return response