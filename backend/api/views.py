"""
Модуль содержит представления (views) для API Foodgram.

Содержит ViewSets и APIView для:
- Управления пользователями (профиль, аватар, регистрация)
- Работы с рецептами, тегами, ингредиентами
- Подписками и избранным
- Авторизацией (логин/выход)
"""

import base64

from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import (
    decorators,
    mixins,
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView
from django_filters import rest_framework as filters

from .pagination import StandardResultsSetPagination
from .permissions import IsAuthenticated
from .serializers import (
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import User


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    ViewSet для управления пользователями.

    Поддерживает:
    - Получение списка пользователей
    - Просмотр профиля пользователя
    - Получение профиля текущего пользователя (/me/)
    - Загрузку и удаление аватара
    - Смену пароля

    Доступ:
    - Все действия требуют аутентификации пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Возвращает соответствующий сериализатор."""
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        """Возвращает список разрешений."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Возвращает профиль текущего авторизованного пользователя."""
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    @decorators.action(
        detail=False,
        methods=["put"],
        url_path="me/avatar",
        parser_classes=[JSONParser, MultiPartParser, FormParser],
    )
    def set_avatar(self, request):
        """Устанавливает аватар пользователя."""
        user = request.user
        avatar_data = request.data.get("avatar")

        if not avatar_data:
            return response.Response(
                {"avatar": ["Обязательное поле."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(avatar_data, str):
            if not avatar_data.startswith("data:image"):
                return response.Response(
                    {"avatar": ["Некорректный формат изображения."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                format, imgstr = avatar_data.split(";base64,")
                ext = format.split("/")[-1]
                file_data = ContentFile(
                    base64.b64decode(imgstr), name=f"avatar_{user.id}.{ext}"
                )
            except Exception:
                return response.Response(
                    {"avatar": ["Ошибка декодирования изображения."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if hasattr(
                avatar_data, "content_type"
            ) and avatar_data.content_type.startswith("image/"):
                file_data = avatar_data
                ext = (
                    avatar_data.name.split(".")[-1]
                    if "." in avatar_data.name
                    else "jpg"
                )
                file_data.name = f"avatar_{user.id}.{ext}"
            else:
                return response.Response(
                    {"avatar": ["Файл должен быть изображением."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.avatar.save(file_data.name, file_data, save=True)

        serializer = self.get_serializer(user)
        return response.Response({"avatar": serializer.data["avatar"]})

    @decorators.action(detail=False, methods=["delete"], url_path="me/avatar")
    def delete_avatar(self, request):
        """Удаляет аватар пользователя."""
        user = request.user

        if user.avatar and user.avatar.name != "defaults/avatar.png":
            user.avatar.delete(save=False)

        user.avatar = None
        user.save()

        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=["post"], url_path="set_password")
    def change_password(self, request):
        """Меняет пароль текущего пользователя."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return response.Response(
                {"current_password": ["Неверный текущий пароль."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения тегов.

    Поддерживает:
    - GET /api/tags/ — список всех тегов.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для чтения ингредиентов.

    Поддерживает:
    - GET /api/ingredients/?name= — поиск по началу названия.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.

    Поддерживает CRUD операции, фильтрацию и действия:
    - Избранное
    - Корзина покупок
    - Выгрузка списка покупок в TXT

    Доступ:
    - Чтение: всем
    - Создание/обновление: только авторизованным
    - Редактирование: только автору
    """

    queryset = Recipe.objects.prefetch_related(
        "tags", "ingredients", "recipeingredient_set"
    )
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Использует разные сериализаторы для создания/чтения."""
        if self.action in ("create", "update", "partial_update"):
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Сохраняет автора рецепта."""
        serializer.save(author=self.request.user)

    def add_to_favorite(self, request, pk=None):
        """Добавляет рецепт в избранное текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe, context={"request": request})
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def remove_from_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def add_to_shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe, context={"request": request})
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED
        )

    def remove_from_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False, methods=["get"], url_path="download_shopping_cart"
    )
    def download_shopping_cart(self, request):
        """Выгружает список покупок текущего пользователя в формате TXT."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        lines = [
            f"{item['ingredient__name']} "
            "({item['ingredient__measurement_unit']}) - "
            "{int(item['total_amount'])}"
            for item in ingredients
        ]
        content = "\n".join(lines)

        response = HttpResponse(content, content_type="text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def update(self, request, *args, **kwargs):
        """Обновляет рецепт, проверяя права доступа."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance.refresh_from_db()

        response_serializer = RecipeSerializer(
            instance, context=self.get_serializer_context()
        )
        return response.Response(
            response_serializer.data, status=status.HTTP_200_OK
        )


class SubscriptionViewSet(viewsets.GenericViewSet):
    """
    ViewSet для управления подписками.

    Поддерживает:
    - Получение списка подписок (/subscriptions/)
    - Подписку и отписку от автора

    Доступ: только авторизованным.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @decorators.action(detail=False, methods=["get"], url_path="subscriptions")
    def subscriptions(self, request):
        """
        Возвращает список авторов, на которых подписан пользователь.

        Поддерживает пагинацию и включает краткие данные о рецептах.

        Returns:
            Response: Список авторов с пагинацией.
        """
        subscriptions = (
            Subscription.objects.filter(user=request.user)
            .select_related("author")
            .prefetch_related(
                "author__recipes",
                "author__recipes__tags",
                "author__recipes__recipeingredient_set__ingredient",
            )
        )

        try:
            page = self.paginate_queryset(subscriptions)
        except Exception:
            return response.Response(
                {"error": "Ошибка пагинации"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if page is None or not page:
            return self.get_paginated_response([])
        authors = [sub.author for sub in page]

        serializer = UserSerializer(
            authors, many=True, context={"request": request}
        )

        return self.get_paginated_response(serializer.data)

    @decorators.action(detail=True, methods=["post"], url_path="subscribe")
    def subscribe(self, request, pk=None):
        """Подписывает текущего пользователя на автора с ID=pk."""
        author = get_object_or_404(User, id=pk)
        Subscription.objects.get_or_create(user=request.user, author=author)
        return response.Response(
            {"success": True}, status=status.HTTP_201_CREATED
        )

    @decorators.action(detail=True, methods=["delete"], url_path="subscribe")
    def unsubscribe(self, request, pk=None):
        """Отписывает текущего пользователя от автора с ID=pk."""
        author = get_object_or_404(User, id=pk)
        Subscription.objects.filter(user=request.user, author=author).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class TokenLoginView(ObtainAuthToken):
    """
    Представление для получения аутентификационного токена.

    Ожидает email и пароль.
    Возвращает токен при успешной авторизации.
    """

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос и возвращает токен."""
        email = request.data.get("email")
        password = request.data.get("password")

        if not email:
            return response.Response(
                {"email": "Обязательное поле."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not password:
            return response.Response(
                {"password": "Обязательное поле."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if not user:
            return response.Response(
                {"non_field_errors": ["Неверные учётные данные."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, created = Token.objects.get_or_create(user=user)
        return response.Response({"auth_token": token.key})


class TokenLogoutView(APIView):
    """View для выхода из системы."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Удаляет токен текущего пользователя."""
        request.user.auth_token.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserRegistrationView(views.APIView):
    """
    View для регистрации нового пользователя.

    Доступно всем (AllowAny).
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Обрабатывает POST-запрос на регистрацию."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return response.Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_subscribed": False,
                    "avatar": None,
                },
                status=status.HTTP_201_CREATED,
            )
        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
