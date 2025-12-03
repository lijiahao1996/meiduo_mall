##  在生产环境，celeryconfig 通常不是 python 文件，而是环境变量控制：

# broker_url = os.getenv("CELERY_BROKER_URL")
# result_backend = os.getenv("CELERY_RESULT_BACKEND")
# timezone = "Asia/Shanghai"

# 环境变量控制
# export CELERY_BROKER_URL=redis://10.0.0.1:6379/5
# export CELERY_RESULT_BACKEND=redis://10.0.0.1:6379/6


# =========== Celery 配置 ===========

# 使用 Redis 作为 Celery broker（任务调度队列）
broker_url = "redis://127.0.0.1:6379/5"

# Celery worker 执行结果存储（可不需要，但建议加上）
result_backend = "redis://127.0.0.1:6379/6"

# 时区与 Django 保持一致
timezone = "Asia/Shanghai"

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
