from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title, User

from .filtres import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (
    AdminModerAuthorOrReadOnly,
    AllReadOrAuthAdminOnly,
    AuthAdminOnly,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ObtainTokenSerializer,
    RegistrationSerializer,
    ReviewSerializer,
    TitleSerializer,
    UserSerializer,
)


class RegistrationView(APIView):
    """Регистрация пользователя."""

    def send_mail(self, user):
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Регистрация пользователя',
            message=f'Код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            user = User.objects.filter(
                email=serializer.initial_data.get('email')
            ).first()
            if user and user.username == serializer.initial_data.get(
                'username'
            ):
                user.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        user = serializer.save()
        self.send_mail(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuthTokenView(APIView):
    """Получение токена."""

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username']
        )
        if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
        ):
            token = AccessToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями."""

    permission_classes = (AuthAdminOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"
    http_method_names = settings.METHOD_ALLOW
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=["GET", "PATCH"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == "PATCH":
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['role'] = request.user.role
                serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CreateListDestroyViewSet):
    """ViewSet для управления категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllReadOrAuthAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(CreateListDestroyViewSet):
    """ViewSet для управления жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AllReadOrAuthAdminOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для управления произведениями."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score')).order_by(
        'name'
    )
    permission_classes = (AllReadOrAuthAdminOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = settings.METHOD_ALLOW

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для управления отзывами."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminModerAuthorOrReadOnly,
    )
    http_method_names = settings.METHOD_ALLOW

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления Комментариями."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminModerAuthorOrReadOnly,
    )
    http_method_names = settings.METHOD_ALLOW

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
