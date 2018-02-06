# -*- coding:utf-8 -*-

# 该文件处理图形和短信验证码

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome.utils import constants
from ihome.utils.response_code import RET
from flask import make_response,jsonify
import logging
'''
路由的定义,需要负责RESTFUL规范
主要符合第三,第四
路由:资源 /<id>


1.生成验证码
2.保存在redis
3.返回图片
'''

@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):

    # 1.生成验证码
    # name,text,image_data = captcha.generate_captcha()
    name, text, image_data = captcha.generate_captcha()
    # 2.存进redis
    # setex:可以设置redis的数据并且设置有效期
    # 需要传三个参数:key,time,val
    try:
        redis_store.setex('image_code_'+image_code_id,constants.IMAGE_CODE_REDIS_EXPIRE,text)
    except Exception as e:
        logging.error(e)

        res = {
            'errcode':RET.DBERR,
            'errmsg':'redis存储错误'
        }

        return jsonify(res)

    # 3.返回数据
    res = make_response(image_data)
    res.headers['Content-Type'] = 'image/jpg'
    return res


