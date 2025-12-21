from django.urls import path
from .views import RegisterView, UsernameCountView, LoginView, LogoutView, UserCenterInfoView, AddressCreateView
from apps.users.views import ImageCodeView
from .views import SmsCodeView
from .views import EmailView, EmailActiveView

from .views import (
    AddressView,
    AddressUpdateView,
    DefaultAddressView,
    AddressTitleView,
)

app_name = "users"

urlpatterns = [
    # 用户注册登录相关
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("center/", UserCenterInfoView.as_view(), name="center"),

    # 用户名重复检查（AJAX）
    path('usernames/<username>/count/', UsernameCountView.as_view(), name='username_count'),

    # ===== 图形验证码 =====
    path("image_codes/<uuid:uuid>/", ImageCodeView.as_view(), name="image_code"),

    # ===== 短信验证码 =====
    path('sms_codes/<mobile>/', SmsCodeView.as_view()),

    # 保存邮箱（PUT）
    path("emails/", EmailView.as_view(), name="emails"),

    # 邮箱激活
    path("emails/verify/", EmailActiveView.as_view(), name="email_verify"),

    # 收货地址
    path('addresses/', AddressView.as_view(), name='addresses'),        # 页面
    path('addresses/create/', AddressCreateView.as_view()),             # POST API
    path('addresses/<int:address_id>/', AddressUpdateView.as_view()),
    path('addresses/<int:address_id>/default/', DefaultAddressView.as_view()),
    path('addresses/<int:address_id>/title/', AddressTitleView.as_view()),

]

