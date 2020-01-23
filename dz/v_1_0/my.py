from dz.utils.converter import login_require
from flask import g, request, jsonify, current_app, session
from . import api
from dz.utils.response_code import RET
from dz.models import User


@api.route("/user/info", methods=["GET"])
@login_require
def get_user_name():
    user_id = g.user_id

    try:
        user = User.query.filter_by(id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")
    return jsonify(errno=RET.OK, errmsg="OK", data={"name": user.name, "mobile": user.mobile, "avatar_url": user.avatar_url})


@api.route("/session", methods=["DELETE"])
def logout():
    """退出登录"""
    session.clear()
    print("session clear")
    return jsonify(errno=RET.OK, errmsg="OK")