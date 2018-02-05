# -*- coding:utf-8 -*-
#  导入Ｆlask包
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config_dict,Config  # 导入配置文件config.py中的字典
from flask_wtf import CSRFProtect
from flask_session import Session
import logging

"""
CSRF保护
POST DELETE PUT都需要保护
"""

"""
日至等级
ERROR   错误级别
WARN    警告级别
INFO    信息级别
DEBUG   调试级别
"""

# 为了方便直接调用db
# print '-'*30
db = SQLAlchemy()

# 为了方便外界直接调用redis_store,操作redis数据库
redis_store =None
# print db.init_app,1
# 定义app创建函数,接受一个参数,返回app.db


# # 设置日志的记录等级
# logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
# file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
# formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# # 为刚创建的日志记录器设置日志记录格式
# file_log_handler.setFormatter(formatter)
# # 为全局的日志工具对象（flask app使用的）添加日志记录器
# logging.getLogger().addHandler(file_log_handler)


def create_app(config_app):
    # 创建Flask应用程序实例对象
    app = Flask(__name__)

    # app配置文件导入方法
    app.config.from_object(config_dict[config_app])

    # init_app延迟导入app对象,为了防止循环导入
    db.init_app(app)

    # CSRF保护 传入app
    CSRFProtect(app)
    # db = SQLAlchemy(app)

    # 创建redis
    # 声明全局使用
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

    # Flask-Session扩展包,可以讲cookie中的session信息同步到redis数据库中
    Session(app)

    from ihome.api_1_0 import api  # 为了解决循环导入,放入函数体内当用的时候在再导入
    # 3.注册蓝图
    app.register_blueprint(api,url_prefix='/api/v1_0')
    # print db,2
    return app,db

