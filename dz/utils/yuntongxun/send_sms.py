from dz.utils.yuntongxun.CCPRestSDK import REST

accountSid = '8a216da86c8a1a54016c95919b0d08a3'
# 说明：主账号，登陆云通讯网站后，可在控制台首页中看到开发者主账号ACCOUNT SID。

accountToken = 'f1ae7d40b8e346ea974fbca34c297c13'
# 说明：主账号Token，登陆云通讯网站后，可在控制台首页中看到开发者主账号AUTH TOKEN。

appId = '8a216da86c8a1a54016c95919b5b08a9'
# 请使用管理控制台中已创建应用的APPID。

serverIP = 'app.cloopen.com'
# 说明：请求地址，生产环境配置成app.cloopen.com。

serverPort = '8883'
# 说明：请求端口 ，生产环境为8883.

softVersion = '2013-12-26'  # 说明：REST API版本号保持不变。 


# 创建一个单例模式
class SendSMS(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            obj = super(SendSMS, cls).__new__(cls, *args, **kwargs)
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls._instance = obj
        return cls._instance

    def send_template_sms(self, to, datas, tempId):
        """
        初始化REST SDK， 调用此方法发送短信。
        status_code的判断只写了一个，其他的都在容联云的短信错误码中。
        被注释的是Demo中提供的方法。
        :param to: string 短信接收端手机号码集合，用英文逗号分开，每批发送的手机号数量不得超过200个
        :param datas: string 内容数据外层节点，模板如果没有变量，此参数可不传
        :param tempId: string 模板ID，测试时id为1
        :return: int 0 成功 -1 失败
        """
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.iteritems():
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print('%s:%s' % (k, s))
        #     else:
        #             print('%s:%s' % (k, v))
        status_code = result.get("statusCode")
        if status_code == "000000":
            return 0
        else:
            return -1


if __name__ == "__main__":
    send = SendSMS()
    send_res = send.send_template_sms("18336023577", ["1234", "5"], 1)
    print(send_res)