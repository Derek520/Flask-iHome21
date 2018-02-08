# -*- coding:utf-8 -*-
from . import api
from flask import request,jsonify,session
from ihome.utils.response_code import RET
import re,logging
from ihome.models import User
from ihome import redis_store,db

# POST /avi/v1_0/users/
# 手机号   mobile
# 短信验证码 sms_code
# 密码    password
'''
    URL:
    api/v1_0/users
    
    请求方式
    post
    
    接收参数
    手机号   mobile
    短信验证码 sms_code
    密码    password
    
    接受数据格式
    json
    
    返回数据格式
    json
'''

@api.route('/users', methods=['POST'])
def register():
    #
    print 456789
    # # 获取数据
    # mobile = request.args.get('mobile')
    # sms_code = request.args.get('phonecode')
    # password = request.args.get('password')
    # print mobile,sms_code,password
    # 1.获取数据
    # request_data = request.get_data()  # 获取的是个字符串不是json
    # request_json = request.get_json()
    # mobile = request_json.get('mobile')

    request_json = request.get_json()
    mobile = request_json.get('mobile')
    sms_code = request_json.get('sms_code')
    password = request_json.get('password')

    print mobile,sms_code,password

    # 2.校验
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='数据不全')
    # 验证手机号
    if not re.match(r'^1[34589]\d{9}',mobile):
        return jsonify(errno=RET.DATAERR,errmsg='手机格式错误')
    # 查询redis数据库
    try:
        send_code = redis_store.get('send_code_'+mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询redis数据库失败')


    # 如果查询为None
    if send_code is None:
        return jsonify(errno=RET.NODATA,errmsg='验证码已删除或者过期')
    # 在进行数据比较
    if send_code != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码填写错误, 请重新输入')

    # 如果输入正确后,删除redis中的短信验证码
    try:
        redis_store.delete('send_code_'+mobile)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='短信验证码删除失败')

    # 查询mysql数据库查看用户是否已注册
    try:
        # print User.query.all()[0].mobile
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据库失败')
    else:
        if user is not None:
            return jsonify(errno=RET.DATAEXIST,errmsg='用户已存在')

        user = User(name=mobile,mobile=mobile)
        user.password_hash=password
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            logging.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg='添加用户失败')

    # 设置session,实现用户登录
    try:
        session['user_id']=user.id
        session['mobile']=mobile
        session['password']=password
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.LOGINERR,errmsg='请重新登录')

    return jsonify(errno=RET.OK,errmsg='注册成功')


'''
登录页面

URL:
api/v1_0/sessions

请求方式:
POST

接受数据:


接受数据格式:
JSON

返回数据格式:
JSON

'''

@api.route('/sessions', methods=['POST'])
def sessions():
    # 1.获取参数
    username = request.get_json('username')
    password = request.get_json('password')
    # 2.校验参数
    # 校验完整性
    if not all([username,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 3.逻辑处理
    # 进行登录次数限制
    # 查询redis数据库,登录了多少次
    # 用ip 进行统计
    ip = request.remote_addr()
    try:
        count = redis_store.get('erro_count_'+ip)
    except Exception as e:
        logging.error(e)
        return jsonify(erron=RET.DBERR,errmsg='查询数据库失败')

    if count is not None and int(count)>=5:
        return jsonify(erron=RET.DATAERR,errmsg='已超出最大连续登录次数,请稍后登录')

    try:
        user = User.query.filter_by(name=username).first()
    except Exception as e:
        logging.error(e)
        return jsonify(erron=RET.DBERR,errmsg='查询数据库错误')


    # 判断用户名和密码是否正确
    if user != username or user.check_password(password):
        # 设置错误次数
        try:
            redis_store.incr('erro_count_'+ip)
        except Exception as e:
            logging.error(e)


        return jsonify(erron=RET.DATAERR,errmsg='用户名或密码错误')


    # 4.返回数据
    return 'sessions'