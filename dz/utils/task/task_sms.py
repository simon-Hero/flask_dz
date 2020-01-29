from dz.utils.yuntongxun.send_sms import SendSMS
from dz.utils.task.main import celery_app


@celery_app.task
def task_send(to, datas, tempId):
    s = SendSMS()
    try:
        result = s.send_template_sms(to, datas, tempId)
    except Exception as e:
        result = -2
    return result
