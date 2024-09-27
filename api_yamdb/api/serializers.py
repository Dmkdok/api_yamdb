from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User
from reviews.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'bio',
        )
        model = User


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(
        max_length=settings.USERNAME_LENGTH,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z'), validate_username],
    )
    email = serializers.EmailField(max_length=settings.MAX_EMAIL_LENGTH)

    def create(self, validated_data):
        """Создание/получение user."""
        try:
            user, _ = User.objects.get_or_create(**validated_data)
        except IntegrityError:
            raise ValidationError('Имя пользователя и/или email не валидно')
        return user


class ObtainTokenSerializer(serializers.Serializer):
    """Сериализатор для токена."""

    username = serializers.CharField(max_length=settings.USERNAME_LENGTH)
    confirmation_code = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['genre'] = GenreSerializer(
            instance.genre.all(), many=True
        ).data
        representation['category'] = CategorySerializer(instance.category).data
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        read_only_fields = ('title',)

    def validate(self, data):
        """
        Проверяем, что отзыв для данного автора и произведения уже существует.
        """
        request = self.context.get('request')
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST':
            if Review.objects.filter(
                author=request.user, title_id=title_id
            ).exists():
                raise ValidationError(
                    {
                        'detail': (
                            'Вы уже оставляли отзыв на данное произведение.'
                        )
                    }
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
        read_only_fields = ('review',)
