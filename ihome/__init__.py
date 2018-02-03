# -*- coding:utf-8 -*-
#  导入Ｆlask包
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config_dict  # 导入配置文件config.py中的字典

# 为了方便直接调用db
db = SQLAlchemy()

# 定义app创建函数,接受一个参数,返回app.db
def create_app(config_app):
    # 创建Flask应用程序实例对象
    app = Flask(__name__)

    # app配置文件导入方法
    app.config.from_object(config_dict[config_app])

    # init_app延迟导入app对象,为了防止循环导入
    db.init_app(app)
    # db = SQLAlchemy(app)
    from ihome.api_1_0 import api  # 为了解决循环导入,放入函数体内当用的时候在再导入
    # 3.注册蓝图
    app.register_blueprint(api,url_prefix='/api/v1_0')
    return app,db

