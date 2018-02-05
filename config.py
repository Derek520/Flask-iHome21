# -*- coding:utf-8 -*-


# config配置信息



class Config(object):
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:yuan121423@127.0.0.1/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Development(Config):

    DEBUG = True

class Production(Config):
    pass

config_dict = {
    'develop':Development,
    'production':Production
}