from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.oauth.utils import generate_access_token, check_access_token
from apps.users.models import User
from meiduo_mall import settings


class OauthQQURLView(View):
    """
    拼接 QQ 登录 URL，前端点击 QQ 按钮时调用这个接口
    """
    def get(self, request):
        # state 一般用 next 参数或随机字符串，这里先用简单写法
        state = request.GET.get('next', '/')  # 支持传 next
        qqoauth = OAuthQQ(
            client_secret=settings.QQ_CLIENT_SECRET,
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=state
        )

        login_url = qqoauth.get_qq_url()
        return http.JsonResponse({'login_url': login_url})


class OauthQQUserView(View):
    """
    处理 QQ 回调 + 绑定逻辑
    """

    def get(self, request):
        """
        GET /oauth/qq/callback/?code=xxx
        1. 获取 code
        2. 用 code 换 access_token
        3. 用 access_token 换 openid
        4. 查询是否已绑定
        """
        code = request.GET.get('code')
        if code is None:
            return render(request, 'oauth_callback.html', context={'errmsg': '缺少 code 参数'})

        # 2. 换取 access_token
        qqoauth = OAuthQQ(
            client_secret=settings.QQ_CLIENT_SECRET,
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URI
        )

        try:
            token = qqoauth.get_access_token(code)
            openid = qqoauth.get_open_id(token)
        except Exception as e:
            # 调试时可以打印一下
            return render(request, 'oauth_callback.html', context={'errmsg': 'QQ 认证失败'})

        # 4. 根据 openid 查询绑定记录
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 没绑定：对 openid 加密，传给前端绑定页
            openid_access_token = generate_access_token(openid)
            return render(request, 'oauth_callback.html', context={'openid_access_token': openid_access_token})
        else:
            # 已绑定：直接登录
            user = qquser.user
            response = redirect(reverse('contents:index'))
            login(request, user)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
            return response

    def post(self, request):
        """
        绑定用户：
        1. 手机号 + 密码 + 短信验证码 + access_token(openid)
        2. 检查短信 / 手机格式 / 密码格式（可以简化）
        3. 解密 access_token 得到 openid
        4. 根据手机号查用户：
           - 没有：创建用户
           - 有：校验密码
        5. 创建 OAuthQQUser 绑定记录
        6. 登录 + 写 cookie
        """
        data = request.POST
        mobile = data.get('mobile')
        password = data.get('pwd')
        sms_code = data.get('sms_code')
        access_token = data.get('access_token')

        # 简单校验（你可按课程完善）
        if not all([mobile, password, sms_code, access_token]):
            return http.HttpResponseBadRequest('缺少必要参数')

        # TODO: 短信验证码校验（可以直接复用你注册时的逻辑，这里先略）

        # 4.解密 openid
        openid = check_access_token(access_token)
        if openid is None:
            return http.HttpResponseBadRequest('access_token 无效或已过期')

        # 5. 根据手机号查用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 没注册过，创建新用户
            user = User.objects.create_user(
                username=mobile,
                password=password,
                mobile=mobile
            )
        else:
            # 已存在用户，校验密码
            if not user.check_password(password):
                return http.HttpResponseBadRequest('密码错误')

        # 绑定 openid
        OAuthQQUser.objects.create(
            user=user,
            openid=openid
        )

        # 登录 + cookie
        login(request, user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=14 * 24 * 3600)
        return response
