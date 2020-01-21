from flask import Blueprint

api = Blueprint('api', __name__)

from . import passport, certification, profile, auth, my, index, myhouse,\
    new_house, detail, orders

"""
passport: 注册界面
Certification: 登录界面
profile: 用户头像设置和用户名设置
auth: 实名认证
my: 查询个人信息、退出登录
index: 检查登陆状态，获取城区信息，轮播图，搜索页面，主页轮播图展示
myhouse: 获取房东房源信息
new_house: 发布新房源
detail: 获取房屋详情
orders: 保存订单，房东接单，拒单， 获取用户订单，保存订单评论信息，支付宝支付，保存支付结果
"""
"""
问题：
2.不能再搜索页面点击后自动搜索
"""