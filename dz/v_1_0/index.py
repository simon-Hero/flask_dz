from . import api
from flask import current_app, jsonify, session, request
from dz.utils.response_code import RET
from dz.models import Area, Order, House
from dz import redis_store
from config import settings
import json
from datetime import datetime


@api.route("/areas")
def get_area_info():
    """获取城区信息"""
    # 查缓存
    try:
        resp_json = redis_store.get("area_info")
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            current_app.logger.info("redis have area info")
            return resp_json, 200, {"Content-Type": "application/json"}
    # 查数据库,转换为json，并保存入redis
    try:
        area_li = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    area_dict_li = []
    for area in area_li:
        area_dict_li.append(area.to_dict())

    res_dict = dict(errno=RET.OK, errmsg="OK", data=area_dict_li)
    resp_json = json.dumps(res_dict)

    try:
        redis_store.setex("area_info", settings.AREA_INFO_REDIS_CACHE_EXPIRES, resp_json)
    except Exception as e:
        current_app.logger.error(e)

    return resp_json, 200, {'Content-Type': "application/json"}


@api.route("/check", methods=["GET"])
def check_login():
    """检查登陆状态"""
    name = session.get("name")
    if name is not None:
        return jsonify(errno=RET.OK, errmsg="true", data={"name": name})
    else:
        return jsonify(errno=RET.SESSIONERR, errmsg="false")


@api.route("/houses", methods=["GET"])
def get_house_list():
    """
    搜索页面中根据条件查找相应房屋返回前端
    :return:
    """
    start_date = request.args.get("sd", "")
    end_date = request.args.get("ed", "")
    area_id = request.args.get("aid", "")
    page = request.args.get("p")
    sort_key = request.args.get("sk", "new")  # 排序关键字

    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date and end_date:
            assert start_date <= end_date
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期参数有误")

    if area_id:
        try:
            Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")

    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    # 获取缓存数据
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json = redis_store.hget(redis_key, page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}

    filter_params = []

    # 填充过滤参数，时间条件
    conflict_orders = None  # 有冲突的订单

    try:
        if start_date and end_date:
            conflict_orders = Order.query.filter(Order.begin_time <= end_date, Order.end_time >= start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_time >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_time <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if conflict_orders:
        # 从订单中获取冲突的房屋id
        conflict_house_ids = [order.house_id for order in conflict_orders]

        # 若房屋id不在冲突的房屋id中，向查询参数中添加条件
        if conflict_house_ids:
            filter_params.append(House.id.notin_(conflict_house_ids))

    if area_id:
        filter_params.append(House.area_id == area_id)

    if sort_key == "booking":
        house_query = House.query.filter(*filter_params).order_by(House.order_count.desc())
    elif sort_key == "price-inc":
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des":
        house_query = House.query.filter(*filter_params).order_by(House.price.desc())
    else:
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())

    try:
        page_obj = house_query.paginate(page=page, per_page=settings.HOUSE_LIST_PAGE_CAPACITY, error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    house_li = page_obj.items

    houses = []
    for house in house_li:
        houses.append(house.to_basic_dict())

    total_page = page_obj.pages

    data = {
        "total_page": total_page,
        "houses": houses,
        "current_page": page
    }
    resp_dict = dict(errno=RET.OK, errmsg="OK", data=data)

    resp_json = json.dumps(resp_dict)

    if page <= total_page:
        redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)

        try:
            pipeline = redis_store.pipeline()
            pipeline.multi()

            pipeline.hset(redis_key, page, resp_json)
            pipeline.expire(redis_key, settings.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES)

            pipeline.execute()
        except Exception as e:
            current_app.logger.error(e)
    return resp_json, 200, {"Content-Type": "application/json"}


@api.route("/house/index", methods=["GET"])
def get_house_index():
    """主页轮播图图片展示"""
    try:
        ret = redis_store.get("home_page_data")
    except Exception as e:
        current_app.logger.error(e)
        ret = None

    if ret:
        current_app.logger.info("redis have house_index data")
        return '{"errno":0, "errmsg":"OK", "data":%s}' % str(ret, encoding="utf8"), 200, {"Content-Type": "application/json"}

    try:
        houses = House.query.order_by(House.order_count.desc()).limit(settings.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not houses:
        return jsonify(errno=RET.NODATA, errmsg="无数据")

    houses_list = []
    for house in houses:
        if not house.index_image_url:
            continue
        houses_list.append(house.to_basic_dict())

    json_house = json.dumps(houses_list)
    try:
        redis_store.setex("home_page_data", settings.HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES, json_house)
    except Exception as e:
        current_app.logger.error(e)
    return '{"errno":0, "errmsg":"OK", "data":%s}' % json_house, 200, {"Content-Type": "application/json"}



