from werkzeug.routing import BaseConverter
from flask import g, session, jsonify
from functools import wraps
from dz.utils.response_code import RET


# 正则转换器
class ReConverter(BaseConverter):
    def __init__(self, url_map, regx):
        super(ReConverter, self).__init__(url_map)
        self.regex = regx


# 登录验证
def login_require(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if user_id is not None:
            g.user_id = user_id
            return func(*args, **kwargs)
        else:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    return wrapper
