from . import api
from flask import current_app, jsonify, g, session
from dz.utils.response_code import RET
from dz.models import Area, House
from dz import redis_store
from config import settings
import json


@api.route("/detail/<int:house_id>", methods=["GET"])
def get_house_detail(house_id):
    """获取房屋的详细信息"""
    user_id  = session.get("user_id")

    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")

    try:
        ret = redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logget.error(e)
        ret = None
    if ret:
        data = {
            "user_id": user_id,
            "house_data": str(ret, encoding="utf8")
        }
        current_app.logger.info("redis have house_data")
        return jsonify(errno=RET.OK, errmsg="OK", data=data)

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="无有效数据")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")
    try:
        house_data = house.to_full_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")

    json_house = json.dumps(house_data)
    try:
        redis_store.setex("house_info_%s" % house_id, settings.HOUSE_DETAIL_REDIS_EXPIRE_SECOND, json_house)
    except Exception as e:
        current_app.logger.error(e)
    data = {
        "user_id": user_id,
        "house_data": json_house
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=data)
