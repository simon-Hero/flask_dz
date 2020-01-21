import os
import redis


class settings:
    IMAGE_CODE_REDIS_EXPIRES = 180  # 图片验证码的redis有效期
    SMS_CODE_REDIS_EXPIRES = 300  # 短信验证码的redis有效期
    SEND_SMS_CODE_INTERVAL = 60  # 发送短信验证码在redis中的有效期
    LOGIN_ERROR_MAX_TIMES = 100  # 用户登录错误次数限制
    LOGIN_ERROR_FORBID_TIME = 600  # 登录错误限制时间
    AREA_INFO_REDIS_CACHE_EXPIRES = 7200  # 城区信息的redis有效期
    HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200  # 房屋详情页面的redis有效期
    HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 5  # 房屋详情页评论信息县显示数量限制
    HOUSE_LIST_PAGE_CAPACITY = 10  # 限制房源信息的每页数据量
    HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES = 5  # 限制房源信息的每页数据量的redis有效期
    HOME_PAGE_MAX_HOUSES = 5  # 首页展示最多的房屋数量
    HOME_PAGE_DATA_REDIS_EXPIRES = 3600  # 首页展示最多的房屋数量的redis有效期
    ALIPAY_URL = "https://openapi.alipaydev.com/gateway.do?"  # 支付宝网关
    ALIPAY_APPID = "2016101200665649"  # 支付宝APPID


class Config(object):
    """配置信息"""

    SECRET_KEY = "sdafafsaca*2ee3da"
    BASEDIR = os.path.abspath(os.path.dirname(__name__))

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:root@127.0.0.1:3306/flask_dz"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # flask-session
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True  # 签名对话cookies_id
    PERMANENT_SESSION_LIFETIME = 86400  # session过期时间

    # 上传文件
    UPLOAD_FOLDER = "upload"  # 设置上传文件的相对地址
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG'])
    FILE_DIR = os.path.join(BASEDIR, UPLOAD_FOLDER)  # 上传文件的绝对地址


class DevelopmentConfig(Config):
    """开发模式"""
    DEBUG = True


class ProductionConfig(Config):
    """生产模式"""
    pass


envs = {
    "product": ProductionConfig,
    "develop": DevelopmentConfig,
    "default": DevelopmentConfig
}
