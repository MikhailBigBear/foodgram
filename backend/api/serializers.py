"""
Сериализаторы API приложения foodgram.

Содержит сериализаторы для пользователей, рецептов,
ингредиентов, тегов и связанных моделей.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

from .fields import Base64ImageField

logger = logging.getLogger(__name__)


class UserShortSerializer(serializers.ModelSerializer):
    """
    Краткий сериализатор пользователя.

    Используется в связях (например, подписки, автор рецепта).
    Добавляет поле is_subscribed.
    """

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на данного автора."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        """Метаданные сериализатора."""

        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        """Метаданные сериализатора."""

        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField()

    class Meta:
        """Метаданные сериализатора."""

        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(
        many=True, source="recipeingredient_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_author(self, obj):
        """Возвращает автора в виде UserShortSerializer."""
        from .serializers import UserShortSerializer

        return UserShortSerializer(obj.author, context=self.context).data

    def get_is_favorited(self, obj):
        """Добавлен ли рецепт в избранное авторизованным пользователем."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Добавлен ли рецепт в список покупок авторизованным пользователем."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Определяет, подписан ли текущий пользователь на данного автора."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        request = self.context.get("request")
        if not request:
            return []

        recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()

        if not recipes.exists():
            return []

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[: int(recipes_limit)]

        from .serializers import RecipeSerializer

        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        return serializer.data

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "avatar",
        )


class RecipesIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания связи рецепт-ингредиент.

    Используется во вложенных данных при создании рецепта.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        """Метаданные сериализатора."""

        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.

    Поддерживает base64-изображения, валидацию ингредиентов и тегов.
    """

    ingredients = RecipesIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        """Метаданные сериализатора."""

        model = Recipe
        fields = (
            "id",
            "author",
            "name",
            "text",
            "ingredients",
            "tags",
            "image",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        """Проверяет, что ингредиенты указаны и не дублируются."""
        if not value:
            raise ValidationError("Нужно добавить хотя бы один ингредиент.")
        ingredient_ids = [item["ingredient"].id for item in value]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise ValidationError("Ингредиенты не должны повторяться.")
        return value

    def validate_tags(self, value):
        """Проверяет, что теги указаны."""
        if not value:
            raise ValidationError("Нужно выбрать хотя бы один тег.")
        return value

    def create(self, validated_data):
        """Создает новый рецепт с ингредиентами и тегами."""
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=item["ingredient"],
                    amount=item["amount"],
                )
                for item in ingredients_data
            ]
        )

        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт, заменяя теги и ингредиенты."""
        ingredients_data = validated_data.pop("ingredients", None)
        tags_data = validated_data.pop("tags", None)

        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        if "image" in validated_data:
            instance.image = validated_data["image"]
        instance.save()

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()

            new_ingredients = []
            for item in ingredients_data:
                try:
                    ingredient = item["ingredient"]
                    amount = item["amount"]
                    if not isinstance(amount, (int, float)) or amount <= 0:
                        raise ValidationError(f"Неверное количество: {amount}")
                    new_ingredients.append(
                        RecipeIngredient(
                            recipe=instance,
                            ingredient=ingredient,
                            amount=amount,
                        )
                    )
                except Exception as e:
                    raise ValidationError(f"Ошибка в ингредиенте: {e}")

            if new_ingredients:
                RecipeIngredient.objects.bulk_create(new_ingredients)

        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache = {}

        fresh_instance = Recipe.objects.get(id=instance.id)
        return fresh_instance

    def to_representation(self, instance):
        """Используем обычный RecipeSerializer для вывода."""
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Проверяет пароль, email и username на уникальность.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        """Метаданные сериализатора."""

        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
        )

    def validate(self, data):
        """Проверяет валидность пароля и уникальность email."""
        try:
            validate_password(data["password"])
        except DjangoValidationError as e:
            raise ValidationError({"password": e.messages})

        if User.objects.filter(email=data["email"]).exists():
            raise ValidationError(
                {"email": "Пользователь с таким email уже существует."}
            )

        return data

    def create(self, validated_data):
        """Создает нового пользователя с хешированным паролем."""
        password = validated_data.pop("password")
        username = validated_data["username"]

        if User.objects.filter(username=username).exists():
            raise ValidationError(
                {"username": "Пользователь с таким именем уже существует."}
            )

        user = User.objects.create_user(
            username=username,
            email=validated_data["email"],
            password=password,
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user
