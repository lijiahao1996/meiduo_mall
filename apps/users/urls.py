from django.urls import path
from .views import RegisterView, UsernameCountView, LoginView, LogoutView, UserCenterInfoView
from apps.users.views import ImageCodeView

app_name = "users"

urlpatterns = [
    # 用户注册登录相关
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('info/', UserCenterInfoView.as_view(), name='info'),

    # 用户名重复检查（AJAX）
    path('usernames/<username>/count/', UsernameCountView.as_view(), name='username_count'),

    # ===== 图形验证码 =====
    path("image_codes/<uuid:uuid>/", ImageCodeView.as_view(), name="image_code"),

]

