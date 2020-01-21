from werkzeug.utils import secure_filename
from dz.utils.converter import login_require
from flask import g, request, jsonify, current_app, session, make_response
from . import api
from dz.utils.response_code import RET
from dz import db
from config import Config
import os
from dz.utils.toolbox import allowed_file
import uuid
from dz.models import User


@api.route("/user/name", methods=["PUT"])
@login_require
def change_user_name():
    """
    更改用户名
    """
    user_id = g.user_id

    req_data = request.get_json()
    name = req_data.get("name")
    if not all([name]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="用户名不能为空")

    try:
        user = User.query.filter_by(name=name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    if user:
        if user.name is not None:
            return jsonify(errno=RET.PARAMERR, errmsg="用户名已存在")

    try:
        User.query.filter_by(id=user_id).update({"name": name})
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollbcak()
        return jsonify(errno=RET.DBERR, errmsg="设置用户名失败")

    session['name'] = name

    return jsonify(errno=RET.OK, errmsg="OK", data={"name": name})


@api.route("/user/avatar", methods=["POST"], strict_slashes=False)
@login_require
def set_user_avatar():
    """
    保存头像
    :return:
    """
    user_id = g.user_id

    file_dir = Config.FILE_DIR
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files["avatar"]
    if f and allowed_file(f.filename):
        f_name = secure_filename(f.filename)
        ext = f_name.rsplit('.', 1)[1]
        new_filename = str(uuid.uuid4()) + '.' + ext  # 采用uuid保存文件名
        f.save(os.path.join(file_dir, new_filename))
        try:
            User.query.filter_by(id=user_id).update({"avatar_url": new_filename})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")

        return jsonify(errno=RET.OK, errmsg="ok")
    else:
        return jsonify(errno=RET.DATAERR, errmsg="上传失败")


@api.route("/user", methods=["GET"])
@login_require
def get_user_profile():
    """获取个人信息"""
    user_id = g.user_id

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户信息失败")

    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")

    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/user/show/<string:filename>", methods=["GET"])
def show_photo(filename):
    file_dir = os.path.join(Config.BASEDIR, Config.UPLOAD_FOLDER)

    if filename is None:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    else:
        image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
        response = make_response(image_data)
        response.headers["Content-Type"] = "image/jpg"
        return response
