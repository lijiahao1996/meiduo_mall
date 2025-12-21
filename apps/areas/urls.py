from django.urls import path
from .views import AreasView

app_name = "areas"

urlpatterns = [
    path('areas/', AreasView.as_view(), name='areas'),
]
