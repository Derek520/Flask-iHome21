# -*- coding:utf-8 -*-

import logging
from . import api
from flask import request,jsonify,json,g
from ihome import redis_store,db
from ihome.utils.commons import RET
from ihome.models import Area,House,HouseImage,Facility
from ihome.utils.constants import AREA_INFO_REDIS_EXPIRES,QINIU_URL_DOMAIN
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
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
        area_json = {'areas':[area.area_dict() for area in area_info]}

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
    return '{"errno":0, "errmsg":"成功","data": %s}' % area_json


# 发布房屋信息
# houses/info
@api.route('/houses/info', methods=['POST'])
@login_required
def save_houses_info():
    '''保存发布的房屋信息'''
    """保存房屋的基本信息
        前端发送过来的json数据
        {
            "title":"",
            "price":"",
            "area_id":"1",
            "address":"",
            "room_count":"",
            "acreage":"",
            "unit":"",
            "capacity":"",
            "beds":"",
            "deposit":"",
            "min_days":"",
            "max_days":"",
            "facility":["7","8"]
        }
        """
    # 1.获取参数
    house_data = request.get_json()
    if house_data is None:
        return jsonify(errno=RET.PARAMERR,errmsg='参数不能为空')

    title = house_data.get("title")  # 房屋名称标题
    price = house_data.get("price")  # 房屋单价
    area_id = house_data.get("area_id")  # 房屋所属城区的编号
    address = house_data.get("address")  # 房屋地址
    room_count = house_data.get("room_count")  # 房屋包含的房间数目
    acreage = house_data.get("acreage")  # 房屋面积
    unit = house_data.get("unit")  # 房屋布局（几室几厅)
    capacity = house_data.get("capacity")  # 房屋容纳人数
    beds = house_data.get("beds")  # 房屋卧床数目
    deposit = house_data.get("deposit")  # 押金
    min_days = house_data.get("min_days")  # 最小入住天数
    max_days = house_data.get("max_days")  # 最大入住天数
    facility = house_data.get('facility')

    # 2.参数校验
    if not all([title,price,area_id,address,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不全')

    # 对金额进行转换
    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='金额格式错误')
    # 3.保存数据
    # 3.1获取用户id
    user_id = g.user_id
    # 3.2创建房屋对象
    house_info = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count= room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days

    )

    print facility
    # 3.3处理房屋信息
    if facility:
        # 如果不为空代表提交了数据,进行数据查询,是否存在
        try:
            facility_list = Facility.query.filter(Facility.id.in_(facility)).all()
        except Exception as e:
            logging.error(e)
            return jsonify(errno=RET.DBERR,errmsg='查询数据库错误')

        if facility_list is None:
            return jsonify(errno=RET.NODATA,errmsg='数据不存在')

        house_info.facilities=facility_list

    # 3.4.添加到数据库
    try:
        db.session.add(house_info)
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据存储失败')

    # 4.返回数据
    return jsonify(errno=RET.OK,errmsg='成功',data={"house_id": house_info.id})

# 上传房屋图片
# house/images
@api.route('/houses/image', methods=['POST'])
@login_required
def save_house_image():
    '''保存房屋图片'''

    # 1.获取参数 房屋的图片、房屋编号
    house_id = request.form.get('house_id')
    image = request.files.get('house_image')
    print house_id,image
    # 2.参数验证
    if not all([file,image]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数不完整')

    # 判断房屋信息是否存在
    try:
        house =House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,ermsg='查询数据库错误')

    if house is None:
        return jsonify(errno=RET.PARAMERR,errmsg='房屋不存在')

    # 3.逻辑处理
    # 读取图片信息,用七牛云存储
    image_data = image.read()
    # 调用七牛云
    try:
        result = storage(image_data)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.SERVERERR,errmsg='图片上传失败')

    # 将图片地址存储到数据库
    house_image = HouseImage(
        house_id=house_id,
        url=result
    )
    db.session.add(house_image)
    # 处理房屋主图信息
    # 判断房屋是否存在主图,没有主图再添加主图
    if not house.index_image_url:
        house.index_image_url=result
        db.session.add(house)
    # 存储到数据库
    try:
        db.session.commit()
    except Exception as e:
        logging.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='数据库存储失败')

    image_url = QINIU_URL_DOMAIN+result
    print image_url
    # 返回数据
    return jsonify(errno=RET.OK,errmsg='成功',data={'image_url':image_url})




