# -*- coding:utf-8 -*-

from flask import Blueprint

# 创建蓝图,导入子模块
api = Blueprint('api',__name__,url_prefix='/api/1')


import index

