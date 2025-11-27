from django.shortcuts import render
from django.views import View
import logging

logger = logging.getLogger("meiduo")


class IndexView(View):
    """
    网站首页视图
    后续可以扩展：轮播图、分类菜单、广告位等
    """

    def get(self, request):
        logger.info("访问首页")

        # 如果你未来要传数据给首页，可以在 context 里加
        context = {
            "title": "美多商城 - 首页",
        }

        # 模板路径：templates/index.html（你已有）
        return render(request, "index.html", context)