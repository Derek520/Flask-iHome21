# -*- coding:utf-8 -*-
#  导入Ｆlask包
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ihome.api_1_0 import api
# 创建Flask应用程序实例对象
app = Flask(__name__)

db = SQLAlchemy()


# 注册蓝图

app.register_blueprint(api)


