import logging
import re

from django import http
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from apps.users.models import User

logger = logging.getLogger("django")



# ============================================================
# 用户注册
# ============================================================
class RegisterView(View):
    """
    用户注册视图（前端表单提交到这里）
    前端 POST 提交：username、password、password2、mobile、allow、sms_code
    这里的版本暂不做短信验证码校验，可后续补充。
    """

    def get(self, request):
        """渲染注册页面"""
        return render(request, "users/register.html")

    def post(self, request):
        """
        注册流程：
        1. 接收表单参数
        2. 校验格式
        3. 校验是否重复（用户名 + 手机号）
        4. 创建用户（自动加密密码）
        5. 自动登录
        6. 跳转首页
        """

        # 1. 接收参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        mobile = request.POST.get("mobile")
        allow = request.POST.get("allow")

        # 2. 必填检查
        if not all([username, password, password2, mobile]):
            return http.HttpResponseBadRequest("缺少必要参数")

        # 校验协议
        if allow != "on":
            return http.HttpResponseBadRequest("请勾选同意协议")

        # 3. 用户名格式 5-20 位
        if not re.match(r"^[0-9a-zA-Z_]{5,20}$", username):
            return http.HttpResponseBadRequest("用户名格式不正确")

        # 4. 密码格式 8-20 位
        if not re.match(r"^[0-9A-Za-z_]{8,20}$", password):
            return http.HttpResponseBadRequest("密码格式不正确")

        # 两次密码一致
        if password != password2:
            return http.HttpResponseBadRequest("两次密码不一致")

        # 5. 手机号格式
        if not re.match(r"^1[3-9]\d{9}$", mobile):
            return http.HttpResponseBadRequest("手机号格式不正确")

        # 6. 用户名是否重复
        if User.objects.filter(username=username).exists():
            return http.HttpResponseBadRequest("用户名已存在")

        # 7. 手机号是否重复
        if User.objects.filter(mobile=mobile).exists():
            return http.HttpResponseBadRequest("手机号已被注册")


        # # 图形验证码校验
        # image_code = request.POST.get("pic_code")
        # image_code_id = request.POST.get("image_code_id")  # 你需要在前端传入此字段
        #
        # redis_conn = get_redis_connection("verify_codes")
        # real_image_code = redis_conn.get(f"img_{image_code_id}")
        #
        # if real_image_code is None:
        #     return http.HttpResponseBadRequest("验证码已过期")
        #
        # if real_image_code.decode().lower() != image_code.lower():
        #     return http.HttpResponseBadRequest("验证码错误")


        # 获取用户填写的短信验证码
        sms_code_client = request.POST.get("sms_code")

        # 判断是否填写
        if not sms_code_client:
            return http.HttpResponseBadRequest("请填写短信验证码")

        # 从 redis 读取
        redis_conn = get_redis_connection("verify_codes")
        sms_code_server = redis_conn.get(f"sms_{mobile}")

        if sms_code_server is None:
            return http.HttpResponseBadRequest("短信验证码已过期")

        # 对比
        if sms_code_client != sms_code_server.decode():
            return http.HttpResponseBadRequest("短信验证码错误")

        # 校验成功 → 删除 redis 验证码（防止重复使用）
        redis_conn.delete(f"sms_{mobile}")


        # 8. 入库：create_user 会自动把密码加密
        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                mobile=mobile
            )
        except Exception as e:
            logger.error("数据库异常：%s", e)
            return http.HttpResponseBadRequest("数据库写入异常")

        # 9. 自动登录
        login(request, user)

        # 10. 跳首页
        return redirect(reverse('contents:index'))


# ============================================================
# 用户名重复检查（AJAX）
# /usernames/<username>/count/
# ============================================================
class UsernameCountView(View):
    """判断用户名是否重复（前端失去焦点 AJAX 调用）"""

    def get(self, request, username):

        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger.error("数据库查询异常：%s", e)
            return http.JsonResponse({"code": 400, "errmsg": "数据库异常"})

        return http.JsonResponse({"code": 0, "count": count})


# ============================================================
# 图片验证码
# ============================================================

from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha


# 过期时间
IMAGE_CODE_EXPIRE_TIME = 120   # 图形验证码 120 秒

class ImageCodeView(View):
    """
    获取图形验证码
    URL: /users/image_codes/<uuid>/
    """

    def get(self, request, uuid):
        # 生成验证码 (name, text, image)
        text, image_data = captcha.generate_captcha()

        # 存 Redis
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex(f"img_{uuid}", IMAGE_CODE_EXPIRE_TIME, text)

        # 返回图片
        return HttpResponse(image_data, content_type="image/jpeg")


# ============================================================
# 短信验证码
# ============================================================
from django.views import View
from django import http
from random import randint


SMS_CODE_EXPIRE_TIME = 300     # 短信验证码 300 秒
SMS_FLAG_EXPIRE_TIME = 60      # 发送频率标记 60 秒


class SmsCodeView(View):
    """
    发送短信验证码
    URL: /sms_codes/<mobile>/?image_code=xxx&image_code_id=uuid
    """

    def get(self, request, mobile):
        # 1. 接收参数
        image_code = request.GET.get("image_code")
        image_code_id = request.GET.get("image_code_id")

        if not all([mobile, image_code, image_code_id]):
            return http.JsonResponse({"code": "4003", "errmsg": "缺少参数"})

        # 2. 取 Redis 图片验证码
        redis_conn = get_redis_connection("verify_codes")
        redis_key = f"img_{image_code_id}"
        real_image_code = redis_conn.get(redis_key)

        if real_image_code is None:
            return http.JsonResponse({"code": "4001", "errmsg": "验证码已过期"})

        # 用完删除
        redis_conn.delete(redis_key)

        # 校验（忽略大小写）
        if real_image_code.decode().lower() != image_code.lower():
            return http.JsonResponse({"code": "4001", "errmsg": "验证码错误"})

        # 3. 发送频率控制：60秒
        send_flag = redis_conn.get(f"send_flag_{mobile}")
        if send_flag:
            return http.JsonResponse({"code": "4002", "errmsg": "请勿频繁发送短信"})

        # 4. 生成短信验证码
        sms_code = "%04d" % randint(0, 9999)
        logger.info(f"{mobile} 的短信验证码是：{sms_code}")

        # 5. Redis 管道一次性写入
        pl = redis_conn.pipeline()
        pl.setex(f"sms_{mobile}", SMS_CODE_EXPIRE_TIME, sms_code)
        pl.setex(f"send_flag_{mobile}", SMS_FLAG_EXPIRE_TIME, 1)
        pl.execute()

        # 6. Celery 异步发送短信
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile, sms_code)

        # 7. 返回成功
        return http.JsonResponse({"code": "0", "errmsg": "短信发送成功"})




# ============================================================
# 用户登录
# ============================================================
class LoginView(View):
    """登录视图"""

    def get(self, request):
        return render(request, "users/login.html")

    def post(self, request):
        # 1. 获取参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")  # 是否记住登录

        # 2. 必填检查
        if not all([username, password]):
            return http.HttpResponseBadRequest("缺少必要参数")

        # 用户名 或 手机号 格式校验
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username) and \
                not re.match(r'^1[3-9]\d{9}$', username):
            return http.HttpResponseBadRequest("请输入正确的用户名或手机号")

        # 4. 使用 Django 内置认证
        user = authenticate(username=username, password=password)

        if user is None:
            # 认证失败，返回登录页并带错误信息
            return render(request, "users/login.html", {"account_errmsg": "用户名或密码错误"})

        # 5. 登录成功：写 session
        login(request, user)

        # 6. 设置 session 过期时间
        if remembered == "on":
            request.session.set_expiry(30 * 24 * 3600)   # 30 天
        else:
            request.session.set_expiry(0)                # 关闭浏览器失效

        # 7. 处理 next 参数（从登录拦截回来时会带上）
        next_url = request.GET.get("next")
        if next_url:
            resp = redirect(next_url)
        else:
            resp = redirect(reverse("contents:index"))

        # 8. 设置 cookie，用于首页展示用户名
        resp.set_cookie("username", user.username, max_age=14 * 24 * 3600)

        # print("username=", username, "password=", password, "remembered=", remembered)

        return resp



# ============================================================
# 用户退出登录
# ============================================================
from django.views import View
from django.contrib.auth import logout
from django.http import JsonResponse

class LogoutView(View):
    """退出登录"""

    def get(self, request):
        # 清除 session
        logout(request)

        # 删除 cookie
        resp = redirect(reverse("contents:index"))
        resp.delete_cookie("username")

        return resp


# ============================================================
# 用户中心（登录后可访问）
# ============================================================
from django.contrib.auth.mixins import LoginRequiredMixin


class UserCenterInfoView(LoginRequiredMixin, View):
    """
    用户中心（必须登录才能访问）
    LoginRequiredMixin 默认检查：
        - user.is_authenticated
        - 未登录自动跳转到 settings.LOGIN_URL
    """

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        return render(request, "users/user_center_info.html", context)



# ============================================================
# 邮箱模块
# ============================================================

import json
import re

from django.views import View
from django import http
from django.contrib.auth.mixins import LoginRequiredMixin

from utils.response_code import RETCODE
from apps.users.utils import active_email_url
from celery_tasks.email.tasks import send_active_email
from utils.mixins import LoginRequiredJSONMixin


class EmailView(LoginRequiredJSONMixin, View):
    """
    用户设置邮箱 + 发送激活邮件
    PUT /users/emails/
    """

    def put(self, request):
        # 1. 解析 JSON 数据
        try:
            data = json.loads(request.body.decode())
        except Exception:
            return http.JsonResponse({
                "code": RETCODE.PARAMERR,
                "errmsg": "参数格式错误"
            })

        email = data.get("email")

        # 2. 校验 email
        if not email:
            return http.JsonResponse({
                "code": RETCODE.PARAMERR,
                "errmsg": "缺少 email"
            })

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.JsonResponse({
                "code": RETCODE.PARAMERR,
                "errmsg": "邮箱格式错误"
            })

        # 3. 保存 email（未激活）
        user = request.user
        user.email = email
        user.email_active = False
        user.save()

        # 4. 生成激活链接
        verify_url = active_email_url(email, user.id)

        # 5. Celery 异步发送邮件
        send_active_email.delay(email, verify_url)

        # 6. 返回成功
        return http.JsonResponse({
            "code": RETCODE.OK,
            "errmsg": "OK"
        })




from django.shortcuts import redirect
from django.urls import reverse
from apps.users.utils import check_email_active_token

class EmailActiveView(View):
    """
    邮箱激活回调
    """

    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return http.HttpResponseBadRequest("缺少 token")

        # 校验 token
        user = check_email_active_token(token)
        if not user:
            return http.HttpResponseBadRequest("无效或过期的激活链接")

        # 激活邮箱
        user.email_active = True
        user.save()

        # 跳转用户中心
        return redirect(reverse("users:center"))

# ============================================================
# Address 视图
# ============================================================
import json
import re
import logging

from django import http
from django.views import View

from utils.response_code import RETCODE
from utils.mixins import LoginRequiredJSONMixin
from apps.users.models import Address

logger = logging.getLogger('django')


# apps/users/views.py
import json
from django.shortcuts import render
from django import http
from django.views import View

from utils.mixins import LoginRequiredJSONMixin
from utils.response_code import RETCODE
from .models import Address


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        addresses = Address.objects.filter(
            user=request.user,
            is_deleted=False
        )

        address_list = []
        for addr in addresses:
            address_list.append({
                'id': addr.id,
                'title': addr.title,
                'receiver': addr.receiver,
                'province': addr.province.name,
                'province_id': addr.province_id,
                'city': addr.city.name,
                'city_id': addr.city_id,
                'district': addr.district.name,
                'district_id': addr.district_id,
                'place': addr.place,
                'mobile': addr.mobile,
                'tel': addr.tel,
                'email': addr.email,
            })

        context = {
            'addresses': address_list,
            'default_address_id': request.user.default_address_id
        }
        return render(request, 'users/user_center_site.html', context)


class AddressCreateView(LoginRequiredJSONMixin, View):
    def post(self, request):
        data = json.loads(request.body.decode())

        try:
            address = Address.objects.create(
                user=request.user,
                title=data.get('title'),
                receiver=data.get('receiver'),
                province_id=data.get('province_id'),
                city_id=data.get('city_id'),
                district_id=data.get('district_id'),
                place=data.get('place'),
                mobile=data.get('mobile'),
                tel=data.get('tel'),
                email=data.get('email'),
            )
        except Exception as e:
            return http.JsonResponse({
                'code': RETCODE.DBERR,
                'errmsg': '保存失败'
            })

        if not request.user.default_address:
            request.user.default_address = address
            request.user.save()

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'address': {
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email,
            }
        })

# 更新/删除 地址
class AddressUpdateView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        data = json.loads(request.body.decode())

        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user,
                is_deleted=False
            )
        except Address.DoesNotExist:
            return http.JsonResponse({
                'code': RETCODE.NODATAERR,
                'errmsg': '地址不存在'
            })

        # ===== 手动字段映射（关键）=====
        address.title = data.get('title', address.title)
        address.receiver = data.get('receiver', address.receiver)
        address.place = data.get('place', address.place)
        address.mobile = data.get('mobile', address.mobile)
        address.tel = data.get('tel', address.tel)
        address.email = data.get('email', address.email)

        # 外键要用 _id 赋值
        address.province_id = data.get('province_id', address.province_id)
        address.city_id = data.get('city_id', address.city_id)
        address.district_id = data.get('district_id', address.district_id)

        address.save()

        # 返回给前端的数据（和新增保持一致）
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'address': {
                'id': address.id,
                'title': address.title,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'province_id': address.province_id,
                'city_id': address.city_id,
                'district_id': address.district_id,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email,
            }

        })

    def delete(self, request, address_id):
        """
        删除地址（逻辑删除）
        """
        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user,
                is_deleted=False
            )
        except Address.DoesNotExist:
            return http.JsonResponse({
                'code': RETCODE.NODATAERR,
                'errmsg': '地址不存在'
            })

        address.is_deleted = True
        address.save()

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'ok'
        })

# 设为默认地址
class DefaultAddressView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user
            )
        except Address.DoesNotExist:
            return http.JsonResponse({
                'code': RETCODE.NODATAERR,
                'errmsg': '地址不存在'
            })

        request.user.default_address = address
        request.user.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

class AddressTitleView(LoginRequiredJSONMixin, View):

    def put(self, request, address_id):
        data = json.loads(request.body.decode())
        title = data.get('title')

        if not title:
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '缺少 title'
            })

        Address.objects.filter(
            id=address_id,
            user=request.user
        ).update(title=title)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
