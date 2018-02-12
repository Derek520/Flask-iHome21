# -*- coding:utf-8 -*-
from . import api
from flask import request,jsonify,session
from ihome.utils.response_code import RET
import re,logging
from ihome.models import User
from ihome import redis_store,db
from ihome.utils.commons import login_required


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
        user.password=password
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
    request_json = request.get_json()
    username = request_json.get('username')
    password = request_json.get('password')
    print username,password
    # 2.校验参数
    # 校验完整性
    if not all([username,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')
    # 3.逻辑处理
    # 进行登录次数限制
    # 查询redis数据库,登录了多少次
    # 用ip 进行统计
    ip = request.remote_addr
    try:
        count = redis_store.get('erro_count_'+ip)
    except Exception as e:
        logging.error(e)
        return jsonify(erron=RET.DBERR,errmsg='查询数据库失败')

    if count is not None and int(count)>=5:
        return jsonify(erron=RET.DATAERR,errmsg='已超出最大连续登录次数,请稍后登录')


    try:
        user = User.query.filter_by(mobile=username).first()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户信息失败')

    # 3. 如果登录不对, 应该设置redis的错误次数. 同时如果登录正确, 清除redis的错误次数

    # 账号或密码错误, 需要返回
    # 登录的逻辑, 一定是账号或密码错误

    # 判断用户名和密码是否正确
    pas = user.check_password(password)
    print user,pas
    if user is None or not user.check_password(password):
        # 设置错误次数
        try:
            redis_store.incr('erro_count_'+ ip)
            # 设置redsi限制时间
            redis_store.expire('erro_count_'+ ip)
        except Exception as e:
            logging.error(e)
        return jsonify(erron=RET.DATAERR,errmsg='用户名或密码错误')

    # 如果手机号和密码都成功,说明登录成功,需要清楚限制
    # 清楚redis数据的限制
    try:
        redis_store.delete('erro_count_'+ ip)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='清除redis数据库失败')

    # 记录用户登录状态
    session['user_id']=user.id
    session['mobile']=user.mobile
    session['user_name']=user.name

    # 4.返回数据
    return jsonify(errno=RET.OK,errmsg='OK')

'''
检验用户登录
URL:
api/v1_0/sessions
请求方式
GET
接收数据
session.get(user_id)
接收数据格式
JSON
返回数据格式
JSON

'''

@api.route('/sessions',methods=['GET'])
def check_login():
    # 1.获取session中的用户名
    user_name = session.get('user_name')
    # 2.判断是否存在
    # 如果session中数据name名字存在，则表示用户已登录，否则未登录
    if user_name is not None:
        return jsonify(errno=RET.OK,errmsg='用户已登录',data={'name':user_name})
    else:
        return jsonify(errno=RET.SESSIONERR,errmsg='用户未登录')


'''
用户退出

URL:
api/v1_0/sessions
请求方式
DELETE
接收数据

接收数据格式
JSON
返回数据格式
JSON
'''

# 用户在退出之前,必须是登录状态,所以要进行用户登录判断
@api.route('/sessions',methods=['DELETE'])
@login_required
def cler_login():
    # 用户退出登录,就是清除session
    # 在清除之前需要先保存csrf_token,因为redis和浏览器是互相同步的,删除任何一个,另一个也会同时删除
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='退出成功')