from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, CategoryViewSet, GenreViewSet, TitleViewSet

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('users', UserViewSet)

urlpatterns = [
    path(settings.VERSION, include(router_v1.urls)),
]
