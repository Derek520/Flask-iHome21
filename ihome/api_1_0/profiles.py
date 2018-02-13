# -*- coding:utf-8 -*-

# import logging
# from . import api
# from flask import g,request,jsonify,session
# from ihome.utils.response_code import RET
# from ihome.utils.image_storage import storage
# from ihome.models import User
# from ihome import db
# from ihome.utils import constants
# from ihome.utils.commons import login_required

import logging
from . import api
from ihome.utils.commons import login_required
from flask import request, jsonify, g, session, current_app
from ihome.utils.response_code import RET
from ihome.utils.image_storage import storage
from ihome.models import User
from ihome import db
from ihome.utils import constants


# 上传图片,修改头像
"""
URL:
api/v1_0/users/avatar
请求方式
post
接受数据
file
返回数据类型
JSON
"""
# @api.route('/users/avatar', methods=['POST'])
# @login_required
# def set_users_avatar():
#     print 123456
#     # 1.获取用户id
#     usre_id = g.user_id
#     # 2.获取用户上传的图片
#     image_flie = request.files.get('avatar')
#     # 参数校验
#     if image_flie is None:
#         return jsonify(errno=RET.PARAMERR,errmsg='图片未上传')
#     # 3.业务逻辑处理
#     # 将图片上传到七牛云,并且保存到mysql
#
#     # 读取文件
#     image_data = image_flie.read()
#
#     # 上传到七牛云服务器
#     try:
#         # 调用七牛云封装好函数上传图片,会返回一个结果值,是存储在七牛云的图片名称,需要保存在mysql中
#         file_name = storage(image_data)
#     except Exception as e:
#         logging.error(e)
#         return jsonify(errno=RET.THIRDERR,errmsg='图片上传失败')
#
#     # 将上传后返回的结果值,保存在mysql
#     try:
#         User.query.filter_by(id=usre_id).update({'avatar_url':file_name})
#         db.session.commit()
#     except Exception as e:
#         logging.error(e)
#         db.session.rollback()
#         return jsonify(errno=RET.DBERR,errmsg='数据库保存失败')
#
#
#     # 4.返回数据
#     # 此时的文件名, 没有域名. 因此如果直接返回给客户端, 客户端无法直接加载
#     # ozcxm6oo6.bkt.clouddn.com
#     # 为了避免在数据库存储过多重复的域名前缀, 因此保存的时候, 不加域名. 返回给前端数据时, 我们拼接域名即可
#
#     # 拼接完整的图像URL地址
#     avatar_url = constants.QINIU_URL_DOMAIN + file_name
#
#     # 将拼接好的图片路径一起返回给前端
#     # 如果还需要额外的返回数据, 可以再后方自行拼接数据, 一般会封装成一个字典返回额外数据
#     return jsonify(errno=RET.OK,errmsg='保存图像成功',data={'avatar_url':avatar_url})


# 该文件处理用户相关的信息

# 需要从form表单中上传图像
# 设置用户头像
@api.route('/users/avatar', methods=['POST'])
@login_required
def set_user_avatars():
    print 12456

    # 1. 获取图像
    user_id = g.user_id
    image_file = request.files.get('avatar')

    # 2. 判断是否为空
    if image_file is None:
        return jsonify(errno=RET.PARAMERR, errmsg='未上传图像')

    # 3. 调用工具类, 上传图像
    image_data = image_file.read()
    try:
        image_name = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传图像异常')

    # 4. 修改用户的数据
    try:
        # user = User.query.filter_by(id=user_id).first()
        # user.avatar_url = image_name
        # db.session.add(user)
        # db.session.commit()

        # update: 查询之后拼接update, 可以直接进行更新操作
        # update中需要传入字典
        User.query.filter_by(id=user_id).update({"avatar_url": image_name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库保存图像失败')

    # 此时的文件名, 没有域名. 因此如果直接返回给客户端, 客户端无法直接加载
    # ozcxm6oo6.bkt.clouddn.com
    # 为了避免在数据库存储过多重复的域名前缀, 因此保存的时候, 不加域名. 返回给前端数据时, 我们拼接域名即可

    # 拼接完整的图像URL地址
    avatar_url = constants.QINIU_URL_DOMAIN + image_name

    # 返回的时候, 记得添加图像url信息
    # 如果还需要额外的返回数据, 可以再后方自行拼接数据, 一般会封装成一个字典返回额外数据
    return jsonify(errno=RET.OK, errmsg='保存图像成功', data={"avatar_url": avatar_url})

@api.route('/users/name',methods=['PUT'])
@login_required
def update_name():
    '''修改用户名'''
    # 获取用户id,因为登录的时候将用户id保存在了g变量,为了减少查询redis数据库次数
    user_id = g.user_id

    # 获取用户要设置的用户名
    req_data =request.get_json()

    # 判断数据完整性
    if req_data is None:
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    # 查询提交的表单数据姓名:
    name = req_data.get('name')
    # 如果为none说明,姓名为空
    if name is None:
        return jsonify(errno=RET.NODATA,errmsg='用户名不能为空')

    # 将修改的姓名更新到mysql数据库中
    try:
        User.query.filter_by(id=user_id).update({'name':name})
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='用户名保存失败')

    session['user_name']=name

    return jsonify(errno=RET.OK,errmsg='用户名修改成功',data={'name':name})

# 个人信息获取
@api.route('/users',methods=['GET'])
@login_required
def get_user_profiles():
    '''个人信息获取'''


    return 'get_user_profiles'