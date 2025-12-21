from celery_tasks.main import app
from django.core.mail import send_mail
from django.conf import settings
from email.header import Header
from email.utils import formataddr
import logging

logger = logging.getLogger("celery")


@app.task(
    bind=True,
    default_retry_delay=10,   # 每次失败后 10 秒再试
    max_retries=5             # 最多重试 5 次
)
def send_active_email(self, email, verify_url):
    """
    发送邮箱激活邮件（支持中文发件人 + 自动重试）
    """
    try:
        logger.info(f"开始发送激活邮件: {email}")

        # ✅ 正确处理【中文发件人】
        from_email = formataddr((
            str(Header("美多商城", "utf-8")),
            settings.EMAIL_HOST_USER
        ))

        # ✅ 正确处理【中文主题】
        subject = str(Header("美多商城邮箱激活", "utf-8"))

        html_message = (
            "<p>尊敬的用户您好！</p>"
            "<p>感谢您使用 <strong>美多商城</strong>。</p>"
            f"<p>您的邮箱为：{email}</p>"
            f"<p>请点击以下链接激活邮箱：</p>"
            f'<p><a href="{verify_url}">{verify_url}</a></p>'
        )

        send_mail(
            subject=subject,
            message="",                     # 纯 HTML 邮件
            from_email=from_email,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"激活邮件发送成功: {email}")

    except Exception as e:
        logger.error(f"激活邮件发送失败: {email}, err={e}")

        # ✅ Celery 自动重试（不阻塞 worker）
        raise self.retry(exc=e)
