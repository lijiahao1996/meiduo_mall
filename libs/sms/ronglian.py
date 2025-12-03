# libs/sms/ronglian.py

import json
from ronglian_sms_sdk import SmsSDK
from django.conf import settings
import logging

logger = logging.getLogger("meiduo")


class RongLianSMS:
    """容联云通讯短信发送封装"""

    def __init__(self):
        cfg = settings.RONG_LIAN
        self.sdk = SmsSDK(cfg["accId"], cfg["accToken"], cfg["appId"])

    def send(self, mobile, template_id, datas):
        """
        datas: ('验证码', '有效期')
        """
        try:
            resp_str = self.sdk.sendMessage(template_id, mobile, datas)

            # ⚠⚠ 关键修复：SDK 返回的是字符串，需要手动 loads
            resp = json.loads(resp_str)

            logger.info(f"短信发送 → 手机号={mobile}, 返回={resp}")

            # 判断发送是否成功
            if resp.get("statusCode") == "000000":
                return True
            else:
                logger.error(f"短信发送失败 → {resp}")
                return False

        except Exception as e:
            logger.error("短信 SDK 调用异常", exc_info=True)
            return False
