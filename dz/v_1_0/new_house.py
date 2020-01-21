import os
import uuid

from werkzeug.utils import secure_filename

from dz.utils.toolbox import allowed_file
from . import api
from flask import g, current_app, jsonify, request
from dz.utils.response_code import RET
from dz.models import Area, House, HouseImage, Facility
from dz import db
from config import Config
from dz.utils.converter import login_require


@api.route("/houses/info", methods=["POST"])
@login_require
def save_house_info():
    """发布新房源"""
    user_id = g.user_id
    house_data = request.get_json()

    title = house_data.get("title")
    price = house_data.get("price")
    area_id = house_data.get("area_id")
    address = house_data.get("address")
    room_count = house_data.get("room_count")
    acreage = house_data.get("acreage")
    unit = house_data.get("unit")
    capacity = house_data.get("capacity")
    beds = house_data.get("beds")
    deposit = house_data.get("deposit")
    min_days = house_data.get("min_days")
    max_days = house_data.get("max_days")

    if not all([title, price, area_id, address, room_count, acreage, unit,\
                capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    try:
        area = Area.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

    house = House(
        user_id=user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        house_area=acreage,
        house_pattren=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )

    facility_ids = house_data.get("facility")

    if facility_ids:
        try:
            facilities = Facility.query.filter(Facility.id.in_(facility_ids)).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        if facilities:
            house.facilities = facilities

    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK, errmsg="OK", data={"house_id": house.id})


@api.route("/houses/image", methods=["POST"])
@login_require
def save_house_image():
    """
    保存房屋图片
    :return:
    """
    file_dir = Config.FILE_DIR
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files.get("house_image")
    house_id = request.form.get("house_id")
    if not all([f, house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    if f and allowed_file(f.filename):
        f_name = secure_filename(f.filename)
        ext = f_name.rsplit('.', 1)[1]
        new_filename = str(uuid.uuid4()) + '.' + ext  # 采用uuid保存文件名
        f.save(os.path.join(file_dir, new_filename))

        house_image = HouseImage(house_id=house_id, url=new_filename)
        db.session.add(house_image)

        if not house.index_image_url:
            house.index_image_url = new_filename
            db.session.add(house)

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存图片异常")

        return jsonify(errno=RET.OK, errmsg="ok", data={"image_name": new_filename})
    else:
        return jsonify(errno=RET.DATAERR, errmsg="上传失败")


