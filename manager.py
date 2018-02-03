# -*- coding:utf-8 -*-

#  导入Ｆlask包
from flask import Flask

# 创建Flask应用程序实例对象
app = Flask(__name__)
app.debug = True

# 定义路由以及视图
@app.route('/index')
def hello_flask():
    return 'hello world'


# 运行
if __name__ == '__main__':
    app.run(host='0.0.0.0')



