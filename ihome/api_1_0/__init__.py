# -*- coding:utf-8 -*-
from flask import Blueprint

# 1. 创建蓝图对象, 导入子模块
api = Blueprint('api',__name__)

import index,passport,profiles,verify_code

