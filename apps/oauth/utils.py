from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from meiduo_mall import settings


def generate_access_token(openid, expires=600):
    """
    对 openid 进行加密，生成 access_token（10 分钟有效）
    """
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=expires)
    data = {"openid": openid}
    token_bytes = s.dumps(data)
    return token_bytes.decode()  # 返回 str


def check_access_token(access_token):
    """
    对 access_token 进行解密，获取 openid
    """
    s = Serializer(secret_key=settings.SECRET_KEY)
    try:
        data = s.loads(access_token)
    except BadData:
        return None
    else:
        return data.get("openid")
