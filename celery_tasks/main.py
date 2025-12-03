# celery_tasks/main.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 创建 Celery 应用
app = Celery("meiduo")

# 直接加载独立 Celery 配置
app.config_from_object("celery_tasks.celeryconfig")

# 明确告诉 Celery 去扫描 celery_tasks/sms/tasks.py
app.autodiscover_tasks([
    "celery_tasks.sms",
])
