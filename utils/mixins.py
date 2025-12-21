from django.contrib.auth.mixins import LoginRequiredMixin
from django import http

from utils.response_code import RETCODE


class LoginRequiredJSONMixin(LoginRequiredMixin):
    """
    用于 AJAX / API 请求的登录校验：
    未登录时返回 JSON，而不是重定向
    """

    def handle_no_permission(self):
        """
        重写父类 LoginRequiredMixin 的未登录处理逻辑
        """
        return http.JsonResponse(
            {
                "code": RETCODE.SESSIONERR,
                "errmsg": "您未登录"
            },
            status=401   # 可选：HTTP 语义更标准
        )
