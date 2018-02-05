# -*- coding:utf-8 -*-

from . import api
from ihome import db
from flask import session
# 2. 使用蓝图装饰路由


@api.route('/index', methods=['GET', 'POST'])
def index():
    session['name']='derek'
    return 'index'