import os
from flask import request, g, current_app, jsonify
from dz.models import Order, House
from dz import db, redis_store
from dz.utils.converter import login_require
from dz.utils.response_code import RET
from . import api
import datetime
from alipay import AliPay
from config import settings


@api.route("/orders", methods=["POST"])
@login_require
def save_order():
    """
    保存订单
    :return:
    """
    user_id = g.user_id
    req_json = request.get_json()
    house_id = req_json.get("house_id")
    start_date = req_json.get("start_date")
    end_date = req_json.get("end_date")

    if not all([house_id, start_date, end_date]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        assert start_date <= end_date
        if (end_date - start_date).days == 0:
            days = 1
        else:
            days = (end_date - start_date).days
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="日期格式错误")

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取房屋信息失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不能预订自己的房源")

    try:
        count = Order.query.filter(Order.house_id == house_id, Order.begin_time <= end_date, Order.end_time
                                   >= start_date).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="检查出错")
    if count > 0:
        return jsonify(errno=RET.DATAERR, errmsg="房屋已被预订")

    amount = days * house.price

    order = Order(
        house_id=house_id,
        user_id=user_id,
        begin_time=start_date,
        end_time=end_date,
        days=days,
        house_price=house.price,
        amount=amount,
    )
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存订单失败")
    return jsonify(errno=RET.OK, errmsg="OK", data={"order_id": order.id})


@api.route("/orders", methods=["GET"])
@login_require
def get_user_order():
    """获取用户的订单"""
    user_id = g.user_id

    role = request.args.get("role", "")
    try:
        if role == "landlord":  # 房东
            houses = House.query.filter(House.user_id == user_id).all()
            houses_ids = [house.id for house in houses]
            orders = Order.query.filter(Order.house_id.in_(houses_ids)).order_by(Order.create_time.desc()).all()
        else:
            orders = Order.query.filter(Order.user_id == user_id).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询订单信息失败")

    order_to_dict = []
    if orders:
        for order in orders:
            order_to_dict.append(order.to_dict())

    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": order_to_dict})


@api.route("/orders/<int:order_id>/status", methods=["PUT"])
@login_require
def deal_with_order(order_id):
    """
    房东接单，拒单
    :return:
    """
    user_id = g.user_id

    req_json = request.get_json()

    action = req_json.get("action")
    if not all([action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        order = Order.query.filter(Order.id == order_id, Order.status == "WAIT_ACCEPT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作无效")

    if not order or house.user_id != user_id:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")

    if action == "accept":
        order.status = "WAIT_PAID"
    elif action == "reject":
        reason = req_json.get("reason")
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        order.status = "REJECT"
        order.comment = reason

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")
    return jsonify(errno=RET.OK, errmsg="OK")


@api.route("/orders/<int:order_id>/comment", methods=["PUT"])
@login_require
def save_order_comment(order_id):
    """保存订单评论信息"""
    user_id = g.user_id

    req_json = request.get_json()

    comment = req_json.get("comment")
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_COMMENT").first()
        house = order.house
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if not order:
        return jsonify(errno=RET.REQERR, errmsg="操作无效")

    try:
        order.status = "COMPLETE"
        order.comment = comment
        house.order_count += 1
        db.session.add(order)
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    try:
        redis_store.delete("house_info_%s" % order.house.id)
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(errno=RET.OK, errmsg="OK")


app_private_key_string = open(os.path.join(os.path.dirname(__file__), "keys/rsa_private_key.pem")).read()
alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem")).read()


@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_require
def order_pay(order_id):
    """支付宝支付"""
    user_id = g.user_id

    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id == user_id, Order.status == "WAIT_PAID").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单有误")

    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )
    order_string = alipay.api_alipay_trade_wap_pay(
        out_trade_no=order.id,
        total_amount=str(order.amount),
        subject=u"短租平台%s" % order.id,
        return_url="http://127.0.0.1:5000/payComplete.html",
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    pay_url = (settings.ALIPAY_URL + order_string).replace("+", "%20")
    print(pay_url)
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})


@api.route("/order/payment", methods=["PUT"])
@login_require
def save_order_result():
    """保存支付结果"""
    alipay_dict = request.form.to_dict()
    signature = alipay_dict.pop("sign")

    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False
    )

    result = alipay.verify(alipay_dict, signature)
    if result:
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no")

        try:
            Order.query.filter_by(id=order_id).update({"status": "WAIT_COMMENT", "trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    return jsonify(errno=RET.OK, errmsg="OK")
