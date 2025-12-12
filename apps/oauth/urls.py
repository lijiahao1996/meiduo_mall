# apps/oauth/urls.py
from django.urls import path
from . import views

app_name = "oauth"

urlpatterns = [
    # 获取 QQ 登录 URL
    path('qq/login/', views.OauthQQURLView.as_view(), name='qq_login'),

    # QQ 回调
    path('qq/callback/', views.OauthQQUserView.as_view(), name='qq_callback'),
]
