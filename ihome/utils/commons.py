# -*- coding:utf-8 -*-

# 正则文件

from werkzeug.routing import BaseConverter
from flask import session,jsonify,g
from ihome.utils.response_code import RET
from functools import wraps

class RegexConverter(BaseConverter):
    """自定义正则转换器"""

    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]

# 很多接口的调用都应该先判断是否登录, 所以在utils/common.py文件中, 新增一个公用的函数
# 定义一个新的装饰器,进行用户登录判断

# def login_required(views_func):
#     def warpper(*args,**kwargs):
#         # 1.获取session中的用户id
#         user_id = session.get('user_id')
#         # 2.判断用户id是否存在
#         if user_id is not None:
#             # 如果存在说明用户已登录,使用g变量存储用户id,用户各个函数之间传递
#             # 比如后面设置头像的时候, 仍然需要获取session的数据.为了避免多次访问redis服务器.可以使用g变量,提升网络性能
#             g.user_id = user_id
#             return views_func(*args,**kwargs)
#         else:
#             resp = {
#                 'errno': RET.SESSIONERR,
#                 'errmsg': '用户未登录'
#             }
#             # 3.返回数据
#             return jsonify(resp)
#     return warpper

# login_required装饰器
# 去session中获取数据 id
def login_required(view_func):
    """检验用户的登录状态"""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            # 表示用户已经登录
            # 使用g对象保存user_id，在视图函数中可以直接使用
            # 比如后面设置头像的时候, 仍然需要获取session的数据. 为了避免多次访问redis服务器. 可以使用g变量
            g.user_id = user_id
            return view_func(*args, **kwargs)
        else:
            # 用户未登录
            resp = {
                "errno": RET.SESSIONERR,
                "errmsg": "用户未登录"
            }
            return jsonify(resp)
    return wrapper

