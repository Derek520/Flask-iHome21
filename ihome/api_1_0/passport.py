# -*- coding:utf-8 -*-
from . import api
from flask import request


# POST /avi/v1_0/users/
# 手机号   mobile
# 短信验证码 sms_code
# 密码    password

@api.route('/users', methods=['GET','POST'])
def register():

    print 456789
    # 获取数据
    mobile = request.args.get('mobile')
    sms_code = request.args.get('phonecode')
    password = request.args.get('password')
    print mobile,sms_code,password
    return 'user'

    # 2.校验


    # 验证手机号

    # 是否已注册

    # 查询redis数据库

    # 如果存在进行数据比较

    # 若相等返回成功