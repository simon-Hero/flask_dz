from . import api
from flask import g, current_app, jsonify, request, session
from dz.utils.response_code import RET
from dz.models import Area, House, HouseImage, Facility, User, Order
from dz import db, redis_store
from config import settings
from dz.utils.converter import login_require
from datetime import datetime
import json


@api.route("/user/houses", methods=["GET"])
@login_require
def get_user_houses():
    """获取房东发布的房源信息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
        houses = user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    houses_list = []

    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_list})
