from . import api
from flask import request, jsonify, current_app, session
from dz.utils.response_code import RET
import re
from dz.models import User
from dz import redis_store
from config import settings


@api.route("/session/", methods=["POST"])
def login():
    """
    用户登录
    :return:
    """
    req_dict = request.get_json()
    mobile = req_dict.get("mobile")
    password = req_dict.get("passwd")

    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if not re.match(r'1[3578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式不正确")

    # 判断是否超出错误次数限制
    user_ip = request.remote_addr
    try:
        access_num = redis_store.get("access_num_%s" % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_num is not None and int(access_num) > settings.LOGIN_ERROR_MAX_TIMES:
            return jsonify(errno=RET.REQERR, errmsg="操作频繁，请稍后再试")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None or not user.check_password(password):
        try:
            if user_ip != "127.0.0.1":
                redis_store.incr("access_num_%s" % user_ip)
                redis_store.expire("access_num_%s" % user_ip, settings.LOGIN_ERROR_FORBID_TIME)
        except Exception as e:
            current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="账号或密码错误")
    session["mobile"] = user.mobile
    session["name"] = user.name
    session["user_id"] = user.id
    return jsonify(errno=RET.OK, errmsg="登录成功")






