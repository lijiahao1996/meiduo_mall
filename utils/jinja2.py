from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.middleware.csrf import get_token

def environment(**options):
    env = Environment(**options)

    env.globals.update({
        # 静态文件：{{ static('css/main.css') }}
        "static": staticfiles_storage.url,

        # URL 反向解析：{{ url('users:info') }}
        "url": reverse,

        # CSRF 隐藏 input：{{ csrf_field(request) | safe }}
        "csrf_field": lambda request: (
            f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'
        ),
    })

    return env
