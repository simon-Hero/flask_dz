from flask import Flask
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask.ext.wtf import CSRFProtect
from config import envs
from flask_sqlalchemy import SQLAlchemy
from dz.utils.converter import ReConverter
import redis
import logging
from logging.handlers import RotatingFileHandler


db = SQLAlchemy()
redis_store = None

# 配置日志信息
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/logs", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级


def create_app(config_name):
    app = Flask(__name__)

    config_class = envs.get(config_name)
    app.config.from_object(config_class)

    # 初始化db
    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 将session保存在redis中
    Session(app)

    # 添加CSRF
    # CSRFProtect(app)

    # 添加自定义转换器
    app.url_map.converters['re'] = ReConverter

    from dz import web_html
    app.register_blueprint(web_html.html)

    from dz import v_1_0
    app.register_blueprint(v_1_0.api, url_prefix="/api")

    return app
