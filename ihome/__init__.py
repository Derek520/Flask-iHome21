# -*- coding:utf-8 -*-
#  导入Ｆlask包
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# 创建Flask应用程序实例对象
app = Flask(__name__)

db = SQLAlchemy()

# 定义路由以及视图
@app.route('/')
def hello_flask():
    return 'hello world'




