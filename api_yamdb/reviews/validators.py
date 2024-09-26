from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(value):
    """Проверяет, что год выпуска произведения не превышает текущий год."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше текущего года ({current_year}).'
        )


def validate_username(value):
    """Проверка на использование имени 'me' в качестве username."""

    if value == 'me':
        raise ValidationError(
            'Имя пользователя не должно совпадать с эндпоинтом!'
        )
