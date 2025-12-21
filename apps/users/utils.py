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



from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
from django.conf import settings
from apps.users.models import User


def active_email_url(email, user_id):
    """
    生成邮箱激活链接
    """
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    data = {
        "email": email,
        "id": user_id
    }

    token = s.dumps(data)

    # ⚠️ 注意：这里不要写死域名
    return f"{settings.EMAIL_VERIFY_URL}?token={token.decode()}"


def check_email_active_token(token):
    """
    校验邮箱激活 token
    """
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)

    try:
        result = s.loads(token)
    except BadSignature:
        return None

    email = result.get("email")
    user_id = result.get("id")

    try:
        return User.objects.get(id=user_id, email=email)
    except User.DoesNotExist:
        return None
