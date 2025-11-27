"""
URL configuration for meiduo_mall project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render



import logging
logger = logging.getLogger("meiduo")
def index(request):

    return render(request, "index.html", {"name": "TestName"})


from django.core.cache import cache
from django.http import HttpResponse

def test_redis(request):
    cache.set("name", "zhangsan", 30)  # 设置 30 秒缓存
    value = cache.get("name")
    return HttpResponse(f"Redis OK: {value}")

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", index, name="index"),
    # path("test_redis/", test_redis),
    path("users/", include(("apps.users.urls", "users"), namespace="users")),
    path("", include(("apps.contents.urls", "contents"), namespace="contents")),
]


