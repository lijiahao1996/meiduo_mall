import re
from django.contrib.auth.backends import ModelBackend
from apps.users.models import User


"""
抽取：根据用户名或手机号获取 User 对象
"""
def get_user_by_username(username):
    try:
        # 手机号
        if re.match(r'^1[3-9]\d{9}$', username):
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    return user



"""
自定义认证后端：支持 用户名/手机号 登录
继承 ModelBackend，否则 Django admin 无法使用多字段认证
"""
class UsernameMobileModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        username: 用户输入的用户名或手机号
        password: 密码
        """
        # 1. 获取用户对象（可能是用户名，也可能是手机号）
        user = get_user_by_username(username)

        # 2. 校验密码
        if user and user.check_password(password):
            return user
        return None
