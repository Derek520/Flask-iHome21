# -*- coding:utf-8 -*-

import logging
from . import api
from flask import request,jsonify,json
from ihome import redis_store
from ihome.utils.commons import RET
from ihome.models import Area
from ihome.utils.constants import AREA_INFO_REDIS_EXPIRES


'''
城区信息数据查询

URL:
api/v1_0/areas
请求方式
GET
返回数据类型
JSON

'''

@api.route('/areas',methods=['GET'])
def get_areas():
    '''城区信息数据查询'''
    '''
       1. 读取redis中的缓存数据
       2. 没有缓存, 去查询数据库
       3. 为了将来读取方便, 在存入redis的时候, 将数据转为JSON字典
       4. 将查询的数据, 存储到redis中
       '''

    # 一.读取redis中的缓存
    try:
        # 查询redis数据库,是否存在缓存数据
        area_json = redis_store.get('area_info')
    except Exception as e:
        logging.error(e)
        area_json = None


    # 二.读取数据库信息
    # 如果为None说明没有缓存数据,需要查询数据库
    print '缓存数据'

    if area_json is None:
        print '数据库数据'
        try:
            # 查询全部数据
            area_info = Area.query.all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR,errmsg='查询数据库失败')
        # 查询的数据是模型对象,需要转换,在模型中定义一个方法
        # 使用列表推导式
        area_json = {'area':[area.area_dict() for area in area_info]}

        # 在存入redsi数据库前需要进行转换
        # 为了将来读取方便, 在存入redis的时候, 将数据转为JSON字符串
        area_json =json.dumps(area_json)

        # 三.查询到的数据存储到redis中
        try:
            # 存储到redis数据中
            redis_store.setex('area_info',AREA_INFO_REDIS_EXPIRES,area_json)
        except Exception as e:
            logging.error(e)
            return jsonify(erron=RET.DBERR,errmsg='redis设置失败')



    # 四.返回结果
    # return jsonify(erron=RET.OK,errmsg='成功',data={'area':area_json})
    # 不能再次进行转换,需要拼接原始
    # return '{"erron":0, "errmsg":"成功","data": %s}' % area_json,200, {"Content-type":"application/json"}
    # 响应头交给请求钩子处理
    return '{"erron":0, "errmsg":"成功","data": %s}' % area_json


