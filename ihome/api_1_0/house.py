# -*- coding:utf-8 -*-

import logging
from . import api
from flask import request,jsonify,json,g,session
from ihome import redis_store,db
from ihome.utils.commons import RET
from ihome.models import Area,House,HouseImage,Facility,Order
from ihome.utils.constants import AREA_INFO_REDIS_EXPIRES, QINIU_URL_DOMAIN, HOME_PAGE_MAX_HOUSES, \
    HOUSE_LIST_PAGE_CAPACITY, HOUSE_LIST_PAGE_REDIS_EXPIRES
from ihome.utils.commons import login_required
from ihome.utils.image_storage import storage
from datetime import datetime
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


# 获取首页轮播图
@api.route('/houses/index')
# @login_required
def get_houses_index():
    '''获取首页轮播'''
    print 456
    # 1.先从缓存中获取
    try:
        house_index = redis_store.get('home_page_data')
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.OK,errmsg='查询redis失败')

    print house_index
    if house_index:
        return '{"errno":0,"errmsg":"成功","data":%s}' % house_index

    # 2.若没有从数据库查询,只要前排序前5条数据
    try:
        houses = House.query.order_by(House.order_count.desc()).limit(HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据库失败')

    if houses is None:
        return jsonify(errno=RET.PARAMERR,errmsg='没有数据')

    house_list = []
    for house in houses:
        if not house.index_image_url:
            continue
        house_list.append(house.to_base_dict())
    # 转换为json数据,保存到redis
    house_json = json.dumps(house_list)
    # 存入redis数据库
    try:
        redis_store.setex('home_page_data',AREA_INFO_REDIS_EXPIRES,house_json)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.OK,errmsg='redis数据库失败')

    print house_json
    # 3.返回数据
    return '{"errno":0,"errmsg":"成功","data":%s}' % house_json

# 获取房屋详情页
@api.route('/houses/<int:house_id>')
# @login_required
def get_houses_info(house_id):
    '''获取房屋详情'''
    # 前端在房屋详情页面展示时，如果浏览页面的用户不是该房屋的房东，则展示预定按钮，否则不展示，
    # 所以需要后端返回登录用户的user_id
    # 尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id，否则返回user_id=-1
    # 1.获取参数
    # user_id=g.user_id

    user_id =session.get('user_id','-1')

    print user_id
    # print user_id,user_id2
    # 2.参数校验
    if not house_id:
        return jsonify(errno=RET.USERERR,errmsg='参数缺失')

    # 3.逻辑处理
    # 先查询redis缓存
    try:
        house_info = redis_store.get('house_info_%s' % house_id)
    except Exception as e:
        logging.error(e)
        # return jsonify(errno=RET.DBERR,errmsg='查询redis失败')
        house_info=None

    # 判断缓存数据是否为空
    if house_info:
        return '{"errno":0,"errmsg":"成功","data":{"user_id":%s,"house":%s}}' % (user_id,house_info)

    # 查询数据库
    try:
        # house_data = House.query.filter(House.id==house_id).frist()
        house = House.query.get(house_id)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')

    if not house:
        return jsonify(errno=RET.NODATA,errmsg='房屋不存在')

    print house.to_full_dict
    # 将房屋对象数据转换为字典
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='数据转换失败')

    # 将字典数据转换成json数据
    house_json =json.dumps(house_data)

    # 存入redis数据库
    try:
        redis_store.setex('house_info_%s' % house_id,AREA_INFO_REDIS_EXPIRES,house_json)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='设置redis失败')
    print 456
    return '{"errno":0,"errmsg":"成功","data":{"user_id":%s,"house":%s}}' % (user_id, house_json)


# 搜索房屋
# http://127.0.0.1:5000/search.html?aid=&aname=&sd=&ed=
@api.route('/houses',methods=['GET'])
def get_houses():
    '''搜索房屋'''
    area_id = request.args.get('aid','')  # 区域id
    start_date_str = request.args.get('sd','') # 开始时间
    end_date_str = request.args.get('ed','')    # 结束时间
    sort_key = request.args.get('sk','new')  # 排序
    page = request.args.get('p','') # 页码

    # 判断时间
    try:
        start_date = None
        if start_date_str:
            start_date = datetime.strftime(start_date_str,"%Y-%m-%d")

        end_date = None
        if end_date_str:
            end_date = datetime.strftime(end_date_str,"%Y-%m-%d")

        # 判断时间不为空的前提下,开始时间不能大于结束时间
        if start_date and end_date:
            assert start_date>end_date
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DATAEXIST,errmsg='时间格式错误')

    # 判断页码
    try:
        page = int(page)
    except Exception as e:
        logging.error(e)
        page = 1

    try:
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        logging.error(e)
        resp_json = None

    if resp_json:
        return '{"errno":0,"errmsg":"ok", "data":%s}' % resp_json


    # 查询城区信息
    filter_params = []

    if area_id:
        # SQLAllchemy对'=='重写了__eq__函数, 不会返回True或False的信息
        filter_params.append(House.area_id==area_id)

    # 4. 处理时间, 需要获取不冲突的房屋信息 参数可能全填, 也可能不全
    # 4.1 找到冲突的订单(order_list = [XXX, XXX, XXX])
    try:
        conflict_orders_li = []
        if start_date and end_date:
            # 都有入住时间和离开时间情况
            conflict_orders_li = Order.query.filter(Order.begin_date>=end_date,Order.end_date<=start_date).all()
        elif start_date:
            # 查询只有入住时间的情况
            conflict_orders_li = Order.query.filter(Order.end_date<=start_date).all()
        elif end_date:
            # 查询只有离开时间的情况
            conflict_orders_li = Order.query.filter(Order.begin_date>=end_date).all()
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据错误')

    if conflict_orders_li:
        # 当不冲突的房屋信息不为空
        # 添加不冲突的房屋查询条件
        filter_params.append(House.id.in_(conflict_orders_li))

    # 下一步处理排序
    # 5.处理排序filter().order_by(new / price desc)
    # "new">最新上线 / "booking">入住最多 / "price-inc">价格 低-高 / "price-des">价格 高-低
    if sort_key == 'booking':
        # 安入住最多查询
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == 'price-inc':
        # 按照价格从低到高,生序
        house_query = House.query.filter(*filter_params).order_by(House.price)
    elif sort_key == 'price-des':
        # 按照价格从高到低,降序
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        # 剩下最后的就是最新上线的
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    # 6.分页处理
    try:
        # paginate: 是查询执行器 和all(), first(), count)
        #                                   页数     每页数量                        错误输出
        house_data = house_query.paginate(page, HOUSE_LIST_PAGE_CAPACITY, False)
    except Exception as e:
        logging.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")


    if not house_data:
        return jsonify
    # 获取分页后的数据
    # 7. 将数据转换JSON格式的字符串
    house_li = house_data.items  # 获取当前页对应的数据
    total_page = house_data.pages  # 获取总页码

    houses = []
    for house in house_li:
        houses.append(house.to_base_dict())

    resp = dict(errno=RET.OK, errmsg="查询成功", data={"houses": houses, "total_page": total_page, "current_page": page})
    resp_json = json.dumps(resp)

    # 8.缓存房屋信息
    if page <= total_page:
        # 页码不能超出分页后的总页码数

        # 用redis的哈希类型保存分页数据
        redis_key = "houses_%s_%s_%s_%s" % (start_date_str, end_date_str, area_id, sort_key)
        try:
            # 使用redis的事务保存数据
            pipeline = redis_store.pipeline()

            # 开启事务
            pipeline.multi()

            # 保存哈希数据, 并设置有效期
            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, HOUSE_LIST_PAGE_REDIS_EXPIRES)

            # 执行事务
            pipeline.execute()

        except Exception as e:
            logging.error(e)
            # redis的缓存如果没有设置成功, 也可以不用返回错误信息. 下一次的请求再去设置也行
            # pipeline: 失败会自动回滚

        # 四. 数据返回
        return resp_json