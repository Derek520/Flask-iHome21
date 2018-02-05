# -*- coding:utf-8 -*-
import logging
from . import api
from flask import session
from ihome import models
# 2. 使用蓝图装饰路由


@api.route('/index', methods=['GET', 'POST'])
def index():
    # session['name']='derek'

    logging.error('error')
    logging.error('warn')
    logging.error('info')
    logging.error('debug')
    return 'index'