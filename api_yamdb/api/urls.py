from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet)

urlpatterns = [
    path(settings.VERSION, include(router_v1.urls)),
]
