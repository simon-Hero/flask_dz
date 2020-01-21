from sqlalchemy.orm import backref
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import settings


class BaseModel(object):
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel, db.Model):
    """用户"""
    __tablename__ = "dz_user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)
    real_name = db.Column(db.String(32))  # 真实姓名
    id_card = db.Column(db.String(20))
    avatar_url = db.Column(db.String(128))  # 头像url
    houses = db.relationship("House", backref="user")
    order = db.relationship("Order", backref="user")

    @property
    def password(self):
        raise AttributeError("只能设置，不能读取")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(password=value)

    def check_password(self, password):
        return check_password_hash(pwhash=self.password_hash, password=password)

    def to_dict(self):
        """将对象数据转换为字典"""
        user_dict = {
            "user_id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "avatar": self.avatar_url,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict


class Area(BaseModel, db.Model):
    """城区"""

    __tablename__ = "dz_area"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    houses = db.relationship("House", backref="area")

    def to_dict(self):
        area_dict = {
            "aid": self.id,
            "a_name": self.name,
        }
        return area_dict


house_facility = db.Table(
    "dz_facility",
    db.Column("house_id", db.Integer, db.ForeignKey("dz_house.id"), primary_key=True),
    db.Column('facility_id', db.Integer, db.ForeignKey('dz_facilities.id'), primary_key=True)
)


class Facility(BaseModel, db.Model):
    """房屋设施"""

    __tablename__ = "dz_facilities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)


class House(BaseModel, db.Model):
    """房屋"""
    __tablename__ = "dz_house"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("dz_user.id"), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("dz_area.id"), nullable=False)
    title = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Integer, default=0)
    address = db.Column(db.String(512), default="")
    room_count = db.Column(db.Integer, default=1)  # 房间数目
    house_area = db.Column(db.Integer, default=0)  # 房屋面积
    house_pattren = db.Column(db.String(32), default="")  # 房屋格局
    capacity = db.Column(db.Integer, default=1)  # 容纳人数
    beds = db.Column(db.String(64), default="")
    deposit = db.Column(db.Integer, default=0)  # 押金
    min_days = db.Column(db.Integer, default=1)
    max_days = db.Column(db.Integer, default=0)  # 0表不限制
    order_count = db.Column(db.Integer, default=0)  # 该房屋预定成功的订单数
    index_image_url = db.Column(db.String(256), default="")
    facilities = db.relationship("Facility", secondary=house_facility)
    images = db.relationship("HouseImage", backref="house", uselist=False)
    orders = db.relationship("Order", backref="house")

    def to_basic_dict(self):
        """将基本信息转换为字典"""
        house_dict = {
            "house_id": self.id,
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "index_url": self.index_image_url,
            "user_url": self.user.avatar_url,
            "area_name": self.area.name,
            "order_count": self.order_count,
            "ctime": self.create_time.strftime("%Y-%m-%d")
        }
        return house_dict

    def to_full_dict(self):
        """将详细信息转换为字典"""
        house_dict = {
            "house_id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_avatar": self.user.avatar_url,
            "title": self.title,
            "price": self.price,
            "address": self.address,
            "room_count": self.room_count,
            "house_area": self.house_area,
            "house_pattren": self.house_pattren,
            "capacity": self.capacity,
            "beds": self.beds,
            "deposit": self.deposit,
            "min_days": self.min_days,
            "max_days": self.max_days
        }
        facilities = []
        if self.facilities:
            for facility in self.facilities:
                facilities.append(facility.id)
        house_dict["facilities"] = facilities

        img_urls = []
        house_img = HouseImage.query.filter_by(house_id=self.id)
        for img in house_img:
            img_urls.append(img.url)
        house_dict["img_urls"] = img_urls

        comments = []
        orders = Order.query.filter(Order.house_id == self.id, Order.status == "COMPLETE", Order.comment != None)\
            .order_by(Order.update_time.desc()).limit(settings.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        if orders:
            for order in orders:
                comment = {
                    "comment": order.comment,
                    "user_name": order.user.name if order.user.name != order.user.mobile else "匿名用户",
                    "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%s")
                }
                comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


class HouseImage(BaseModel, db.Model):
    """房屋图片"""

    __tablename__ = "dz_house_image"

    id = db.Column(db.Integer, primary_key=True)
    house_id = db.Column(db.Integer, db.ForeignKey("dz_house.id"), nullable=False)
    url = db.Column(db.String(256), nullable=False)


class Order(BaseModel, db.Model):
    """订单"""

    __tablename__ = "dz_order"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("dz_user.id"), nullable=False)
    house_id = db.Column(db.Integer, db.ForeignKey("dz_house.id"), nullable=False)
    begin_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.Integer, nullable=False)  # 预定总天数
    house_price = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # 订单总金额
    status = db.Column(
        db.Enum(
            "WAIT_ACCEPT",  # 待接单
            "ACCEPT",  # 已接单
            "REJECT",  # 已拒单
            "WAIT_PAID",  # 待支付
            "PAID",  # 已支付
            "CANCEL",  # 已取消
            "WAIT_COMMENT",  # 待评价
            "COMPLETE",  # 已评价
        ),
        default="WAIT_ACCEPT",
        index=True  # 建立索引，提高查询速度
    )
    comment = db.Column(db.Text)
    trade_no = db.Column(db.String(80))  # 支付宝流水号

    def to_dict(self):
        order_dict = {
            "order_id": self.id,
            "title": self.house.title,
            "img_url": self.house.index_image_url,
            "start_date": self.begin_time.strftime("%Y-%m-%d"),
            "end_date": self.end_time.strftime("%Y-%m-%d"),
            "ctime": self.create_time.strftime("%Y-%m-%d"),
            "days": self.days,
            "amount": self.amount,
            "status": self.status,
            "comment": self.comment if self.comment else ""
        }
        return order_dict


