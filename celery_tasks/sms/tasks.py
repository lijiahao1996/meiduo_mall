# celery_tasks/sms/tasks.py
from celery_tasks.main import app
from libs.sms.ronglian import RongLianSMS

import logging

# 使用 Celery 的 logger（而不是 print）
# 好处：日志等级可控、可写入日志文件、不会和多进程输出乱序
logger = logging.getLogger("celery")


@app.task(
    bind=True,              # bind=True：使第一个参数是 task 对象本身（self），好用于 retry()
    default_retry_delay=5   # 任务失败后默认等待 5 秒再重试
)
def send_sms_code(self, mobile, sms_code):
    """
    异步发送短信验证码任务（Celery Worker 执行）
    :param mobile: 手机号
    :param sms_code: 验证码内容
    """

    # 记录任务开始日志（方便排查）
    logger.info(f"开始向 {mobile} 发送短信验证码 {sms_code}")

    try:
        # 调用容联云短信 SDK 发送短信
        # template_id = "1" 表示你在容联云平台配置的模板编号
        # datas = (短信验证码, 有效期)
        ok = RongLianSMS().send(
            mobile,
            "1",
            (sms_code, "5")
        )

        # 打印容联云返回结果 True / False
        logger.info(f"容联云返回: ok={ok}")

        # 如果 SDK 返回失败，主动抛异常触发 retry()
        if not ok:
            raise Exception("短信发送失败")

    except Exception as e:
        # 记录错误日志（包括容联云 API 错误、网络异常等）
        logger.error(f"短信发送失败: {e}")

        # Celery 自动重试（最多重试 10 次）
        # retry() 会再次把任务丢回队列，不会阻塞当前 worker
        raise self.retry(exc=e, max_retries=10)
