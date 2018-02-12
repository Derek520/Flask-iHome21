# -*- coding:utf-8 -*-

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
# from ihome import app, db    # 导入的是ihome.__init__文件

from ihome import create_app

# 调用app创建函数 create_app()
app, db = create_app('develop')

# 创建命令行Manager对象
manager = Manager(app)

# 创建迁移对象
Migrate(app, db)

# 创建命令行数据库迁移指令
manager.add_command('db',MigrateCommand)

# 运行
if __name__ == '__main__':
    # manager启动
    # print app.url_map
    manager.run()



