# -*- coding:utf-8 -*-


from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from ihome import app, db

manager = Manager(app)

Migrate(app, db)

manager.add_command('db',MigrateCommand)

# 运行
if __name__ == '__main__':
    manager.run()



