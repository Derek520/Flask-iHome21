# -*- coding:utf-8 -*-


# config配置信息
import redis


class Config(object):
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'mysql://root:yuan121423@127.0.0.1/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SECRET_KEY = 'JJJ'
    # 配置redis的数据
    REDIS_HOST = '47.94.238.54'
    REDIS_PORT = 6379

    # 配置SECREK_KEY
    # import os, base64 ipython中导入
    # base64.b64encode(os.urandom(32)) 在ipython执行这行得到SECRET_KEY

    SECRET_KEY = 'it9XWlBwtIbmFhmZHqoS4X7PV+B0veFQpcVBZL79mNI='

    # 配置session存储到redis中
    PERMANENT_SESSION_LIFETIME = 86400  # 单位是秒, 设置session过期的时间
    SESSION_TYPE = 'redis'  # 指定存储session的位置为redis
    SESSION_USE_SIGNER = True  # 对数据进行签名加密, 提高安全性
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 设置redis的ip和端口


class Development(Config):

    DEBUG = True

class Production(Config):
    pass

config_dict = {
    'develop':Development,
    'production':Production
}
