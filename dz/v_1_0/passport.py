from dz.models import User
from . import api
from flask import request, jsonify, current_app, session, make_response
from dz.utils.response_code import RET
import re
from dz import redis_store, db
from dz import redis_store
from dz.utils.captcha.captcha import captcha
from config import settings
import random
from dz.utils.yuntongxun.send_sms import SendSMS


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    实现图片验证码， url：api/image_codes/xxx
    :param image_code_id: 由前端请求时自带id值，后端将此id值作为redis的键保存
    :return: resp
    """
    name, text, data = captcha.generate_captcha()

    try:
        redis_store.setex("image_code_%s" % image_code_id, settings.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="保存图片验证码失败")

    resp = make_response(data)
    resp.headers["Content-Type"] = "image/jpg"
    return resp


@api.route("/smscode/")
def send_sms():
    """
    发送短信验证码，并保存到redis，判断图片验证码的有效性,并删除原有图片验证码
    url： /api/smscode/?mobile=xx&code=xx&codeId=xx
    :param
    :return:
    """
    image_code = request.args.get("code")
    image_code_id = request.args.get("codeId")
    mobile = request.args.get("mobile")

    if not all([image_code_id, image_code, mobile]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # 判断图片验证码
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

    if real_image_code.lower() != real_image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="图片验证码错误")

    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")

    # 判断手机号
    if not re.match(r'1[3458]\d{9}', str(mobile)):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        if user is not None:
            return jsonify(error=RET.DATAEXIST, errmsg="手机号已存在")

    sms_code = "%06d" % random.randint(0, 99999)
    try:
        redis_store.setex("sms_code_%s" % mobile, settings.SMS_CODE_REDIS_EXPIRES, sms_code)
        redis_store.setex("send_sms_code_%s" % mobile, settings.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    try:
        sms = SendSMS()
        result = sms.send_template_sms(mobile, [sms_code, int(settings.SEND_SMS_CODE_INTERVAL/60)], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    if result == 0:
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")


@api.route("/users", methods=["POST"])
def register():
    """
    注册
    :param 手机号、短信验证码、密码、确认密码
    :return: json 提示前端是否注册成功
    """
    req_dict = request.get_json()

    mobile = req_dict.get("mobile")
    sms_code = req_dict.get("sms_code")
    password = req_dict.get("password")
    confirm_password = req_dict.get("password2")

    # 校验
    if not all([mobile, sms_code, password, confirm_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    if not re.match(r'1[3578]\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    if password != confirm_password:
        return jsonify(errno=RET.PARAMERR, errmsg="两次密码不一致")

    try:
        real_sms_code = redis_store.get("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="服务器错误")  # 读取短信验证码失败

    if real_sms_code is None:
        return jsonify(errno=RET.NODATA, errmsg="验证码失效")

    try:
        redis_store.delete("sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)

    if str(real_sms_code, encoding='utf-8') != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    user = User(name=mobile, mobile=mobile)
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="手机号已存在")
    session['name'] = mobile
    session['mobile'] = mobile
    session['user_id'] = user.id

    return jsonify(errno=RET.OK, errmsg="注册成功")






