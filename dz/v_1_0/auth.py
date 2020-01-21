from flask import current_app, g, request, jsonify
from . import api
from dz.utils.converter import login_require
from dz.utils.response_code import RET
from dz.models import User
from dz import db


@api.route("/users/auth", methods=["POST"])
@login_require
def set_user_auth():
    """保存用户实名认证信息"""
    user_id = g.user_id
    req_data = request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    real_name = req_data.get("real_name")
    id_card = req_data.get("id_card")

    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if len(id_card) != 18:
        return jsonify(errno=RET.PARAMERR, errmsg="身份证号码格式不正确，请重新填写！")

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")
    if user.id_card or user.real_name:
        return jsonify(errno=RET.PARAMERR, errmsg="操作频繁，请稍后再试！")

    try:
        User.query.filter_by(id=user_id, real_name=None, id_card=None).update({"real_name": real_name, "id_card": id_card})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存用户实名信息失败")

    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/users/auth", methods=["GET"])
@login_require
def get_user_auth():
    """获取用户实名认证消息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取实名认证信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效信息")

    return jsonify(errno=RET.OK, errmsg="OK", data={"real_name": user.real_name, "id_card": user.id_card})
