from rest_framework import viewsets, permissions, status, response, decorators
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from recipes.models import (
     Recipe, Tag, Ingredient, Favorite, ShoppingCart, Subscription
)
from users.models import User
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    UserSerializer,
    RecipeIngredientSerializer,
)
from .permissions import IsAuthorOrReadOnly, IsAuthenticated
from .pagination import StandardResultsSetPagination


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для работы с пользователями.
    Поддерживает:
    - Получение профиля текущего пользователя (/me/)
    - Загрузка и удаление аватара (/me/avatar/)
    - Смена пароля (/set_password/)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """Возвращает профиль текущего авторизованного пользователя."""
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=["put"], url_path="me/avatar")
    def set_avatar(self, request):
        """Загружает аватар пользователя в формате Base64."""
        user = request.user
        avatar = request.data.get("avatar")
        if not avatar:
            return response.Response(
                {"avatar": ["Обязательное поле."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.avatar = avatar
        user.save()
        serializer = self.get_serializer(user)
        return response.Response({"avatar": serializer.data["avatar"]})

    @decorators.action(detail=False, methods=["delete"], url_path="me/avatar")
    def delete_avatar(self, request):
        """Удаляет аватар пользователя."""
        user = request.user
        user.avatar.delete(save=True)
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

    def get_queryset(self):
        """Фильтрует ингредиенты по параметру 'name'."""
        name = self.request.query_params.get("name", "")
        if name:
            return self.queryset.filter(name__istartswith=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.

    Поддерживает:
    - CRUD рецептов (только автор может редактировать/удалять)
    - Фильтрацию: по автору, тегам, избранному, списку покупок
    - Добавление/удаление из избранного и списка покупок
    - Выгрузку списка покупок в TXT
    """

    queryset = Recipe.objects.prefetch_related(
        "tags", "ingredients", "recipeingredient_set"
    )
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Фильтрует рецепты по параметрам запроса."""
        queryset = self.queryset
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get("is_in_shopping_cart")
        author_id = self.request.query_params.get("author")
        tags = self.request.query_params.getlist("tags")

        if is_favorited == "1" and self.request.user.is_authenticated:
            queryset = queryset.filter(favorites__user=self.request.user)

        if is_in_shopping_cart == "1" and self.request.user.is_authenticated:
            queryset = queryset.filter(shopping_cart__user=self.request.user)

        if author_id:
            queryset = queryset.filter(author_id=author_id)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    def perform_create(self, serializer):
        """Сохраняет автора рецепта."""
        serializer.save(author=self.request.user)

    @decorators.action(detail=True, methods=["post"], url_path="favorite")
    def add_to_favorite(self, request, pk=None):
        """Добавляет рецепт в избранное текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["delete"], url_path="favorite")
    def remove_from_favorite(self, request, pk=None):
        """Удаляет рецепт из избранного текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=["post"], url_path="shopping_cart")
    def add_to_shopping_cart(self, request, pk=None):
        """Добавляет рецепт в список покупок текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe, context={"request": request})
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["delete"], url_path="shopping_cart")
    def remove_from_shopping_cart(self, request, pk=None):
        """Удаляет рецепт из списка покупок текущего пользователя."""
        recipe = get_object_or_404(Recipe, id=pk)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=["get"], url_path="download_shopping_cart")
    def download_shopping_cart(self, request):
        """Выгружает список покупок текущего пользователя в формате TXT."""
        recipes = Recipe.objects.filter(
            shopping_cart__user=request.user
        ).prefetch_related("recipeingredient_set__ingredient")

        ingredients = {}
        for recipe in recipes:
            for ri in recipe.recipeingredient_set.all():
                key = (ri.ingredient.name, ri.ingredient.measurement_unit)
                if key in ingredients:
                    ingredients[key] += ri.amount
                else:
                    ingredients[key] = ri.amount

        content = ""
        for (name, unit), amount in ingredients.items():
            content += f"{name} ({unit}) — {amount}\n"

        response = FileResponse(content, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="shopping_list.txt"'
        return response


class SubscriptionViewSet(viewsets.ViewSet):
    """
    ViewSet для работы с подписками.

    Поддерживает:
    - Получение списка подписок текущего пользователя (/subscriptions/)
    - Подписку/отписку от автора (/users/{id}/subscribe/)
    """

    permission_classes = [IsAuthenticated]

    @decorators.action(detail=False, methods=["get"], url_path="subscriptions")
    def subscriptions(self, request):
        """Возвращает список подписок текущего пользователя с пагинацией."""
        subscriptions = (
            Subscription.objects.filter(user=request.user)
            .select_related("author", "author__avatar")
            .prefetch_related("author__recipes")
        )

        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = UserSerializer(
                [sub.author for sub in page], many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        return response.Response([], status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], url_path="subscribe")
    def subscribe(self, request, pk=None):
        """Подписывает текущего пользователя на автора с ID=pk."""
        author = get_object_or_404(User, id=pk)
        Subscription.objects.get_or_create(user=request.user, author=author)
        return response.Response({"success": True}, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["delete"], url_path="subscribe")
    def unsubscribe(self, request, pk=None):
        """Отписывает текущего пользователя от автора с ID=pk."""
        author = get_object_or_404(User, id=pk)
        Subscription.objects.filter(user=request.user, author=author).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
