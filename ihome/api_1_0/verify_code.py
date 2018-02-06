# -*- coding:utf-8 -*-

# 该文件处理图形和短信验证码

from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome.utils import constants
from ihome.utils.response_code import RET
from flask import make_response,jsonify,request
import logging,random
from ihome.models import User
from ihome.libs.yuntongxin.sms import CCP

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

"""
这里使用手机号当做id, 可以通过正则来过滤一些垃圾请求
GET /api/v1_0/sms_codes/17612345678?image_code=werz&image_code_id=61242
用户填写的验证码
用户的手机号
图像验证码的编码
"""


@api.route('/sms_codes/<re(r"1[356789]\d{9}"):moble>')
def send_sms_code(moble):
    print 'send_code'
    # 1. 获取参数
    image_code = request.args.get('image_code')
    image_code_id =request.args.get('image_code_id')
    print image_code_id,image_code
    # 2. 校验
    # 验证参数完整性
    if not all([image_code_id,image_code]):
        res = {
            'errcode':RET.PARAMERR,
            'errmsg': '参数不完整'
        }
        return jsonify(res)

    # 3. 处理业务逻辑
    # 查询redis数据库,是否存在该数据
    try:
        data = redis_store.get('image_code_'+image_code_id)
        print 'data %s' % data
    except Exception as e:
        logging.error(e)
        res = {
            'errcode':RET.DBERR,
            'errmsg':'获取redis数据失败'
        }
        return jsonify(res)
    else:
        # 如果查到数据,判断是否None
        if data is None:
            res = {
                'errcode':RET.NODATA,
                'errmsg':'验证码过期或已删除'
            }
            return jsonify(res)


    try:
        redis_store.delete('image_code_'+image_code_id)
    except Exception as e:
        logging.error(e)
        # 删除失败不需要返回消息



    # 对比是否一致, 不一致就返回 --> 转换相同格式再对比
    if image_code.lower() != data.lower():
        res = {
            'errcode':RET.PARAMERR,
            'errmsg':'验证码过期或已删除,请刷新验证码'
        }
        return jsonify(res)

    # 查询mysql数据库,查看用户是否已注册
    try:
        user = User.query.filter_by(mobile=moble).first()
        print user
    except Exception as e:
        logging.error(e)
        '不需要返回'
    else:
        if user is not None:
            res = {
                'errcode':RET.DATAEXIST,
                'errmsg': '用户已存在'
            }
            return jsonify(res)

    # 生成短信验证码
    send_code = '%0d6' % random.randint(0,999999)

    # 将生成的验证码存入redis数据库
    try:
        redis_store.setex('send_code_'+moble,300,send_code)
    except Exception as e:
        logging.error(e)
        res = {
            'errcode':RET.DBERR,
            'errmsg': 'redis数据库存储失败'
        }
        return jsonify(res)

    # 调用云通信发送短信验证码
    ccp = CCP()
    try:
        status_code = ccp.send_template_sms(17710928803,[send_code,5],1)
    except Exception as e:
        logging.error(e)
        res = {
            'errcode':RET.THIRDERR,
            'errmsg':'短信验证码发送失败'
        }
        return jsonify(res)
    # 判断返回的数据是否为000000
    else:
        if status_code == '000000':
            res = {
                'errcode':RET.OK,
                'errmsg': '验证码发送成功'
            }
            return jsonify(res)




