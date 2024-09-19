from rest_framework import viewsets
from reviews.models import Category, Genre, Title, User


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""
    queryset = User.objects.all()


class CategoryViewSet(viewsets.GenericViewSet):
    """ViewSet для управления категориями."""

    queryset = Category.objects.all()


class GenreViewSet(viewsets.GenericViewSet):
    """ViewSet для управления жанрами."""

    queryset = Genre.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.all()
