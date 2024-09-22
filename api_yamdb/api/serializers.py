from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title, User


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

# ЭТО АНДРЕЙ МОЖЕТ ЗАСТРАТЬ ТЕМ, ЧТО ДВАЖДЫ ПОВТОРЯЕТСЯ ТАКЖЕ В СЛЕДУЮЩЕМ КЛАССЕ, НАДО ПОДУМАТЬ КАК ИСПРАВИТЬ!!!!
    def validate(self, data):
        """Проверка на использование имени 'me' в качестве username."""
        if data.get('username') != 'me':
            return data
        raise serializers.ValidationError(
            'Имя пользователя не должно совпадать с эндпоинтом!'
        )


class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        """Проверка на использование имени 'me' в качестве username."""
        if data.get('username') != 'me':
            return data
        raise serializers.ValidationError(
            'Имя пользователя не должно совпадать с эндпоинтом!'
        )


class ObtainTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для токена."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


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

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = '__all__'

    def get_rating(self, obj):
        """
        Рассчитывает средний рейтинг произведения на основе отзывов.
        """
        average_rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if average_rating is not None:
            return round(average_rating)
        return None


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для созадния произведений."""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


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
