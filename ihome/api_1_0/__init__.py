# -*- coding:utf-8 -*-

from flask import Blueprint

# 1.创建蓝图,导入子模块
api = Blueprint('api',__name__)

import index

