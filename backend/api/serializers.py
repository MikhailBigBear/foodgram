from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredient,
    ShoppingCart,
    Favorite,
    Subscription,
)
from .fields import Base64ImageField
from users.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request:
            print("🔴 get_is_subscribed: context['request'] отсутствует")
            return False
        if not request.user.is_authenticated:
            print("🟠 get_is_subscribed: пользователь не авторизован")
            return False
        try:
            result = Subscription.objects.filter(user=request.user, author=obj).exists()
            print(f"🟢 get_is_subscribed: {request.user} подписан на {obj}? {result}")
            return result
        except Exception as e:
            print(f"🔴 Ошибка в get_is_subscribed: {e}")
            return False

    class Meta:
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
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели RecipeIngredient."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit")
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    tags = TagSerializer(many=True)
    author = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(many=True, source="recipeingredient_set")
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_author(self, obj):
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
        return ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()

    class Meta:
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
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        print(f"📄 get_recipes вызван для {obj}")
        request = self.context.get("request")
        if not request:
            print("🔴 get_recipes: context['request'] отсутствует")
            return []

        recipes_limit = request.query_params.get("recipes_limit")
        recipes = obj.recipes.all()

        print(f"📄 get_recipes: найдено рецептов у {obj}: {recipes.count()}")

        if not recipes.exists():
            return []

        if recipes_limit and recipes_limit.isdigit():
            recipes = recipes[: int(recipes_limit)]
            print(f"✂️  get_recipes: ограничено до {recipes_limit}")

        from .serializers import RecipeSerializer

        serializer = RecipeSerializer(recipes, many=True, context=self.context)
        print(f"✅ get_recipes: сериализовано {len(serializer.data)} рецептов")
        return serializer.data

    class Meta:
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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient"
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipesIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
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
        if not value:
            raise ValidationError("Нужно добавить хотя бы один ингредиент.")
        ingredient_ids = [item["ingredient"].id for item in value]
        if len(set(ingredient_ids)) != len(ingredient_ids):
            raise ValidationError("Ингредиенты не должны повторяться.")
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError("Нужно выбрать хотя бы один тег.")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe, ingredient=item["ingredient"], amount=item["amount"]
                )
                for item in ingredients_data
            ]
        )

        return recipe

    def update(self, instance, validated_data):
        print(f"🔧 Обновление рецепта: {instance.id}")
        print(f"📥 validated_data: {validated_data}")

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
            print(f"📌 Устанавливаем теги: {tags_data}")
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            print(f"🥬 Удаляем старые ингредиенты")
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
                            recipe=instance, ingredient=ingredient, amount=amount
                        )
                    )
                except Exception as e:
                    print(f"❌ Ошибка при создании ингредиента: {e} | item: {item}")
                    raise ValidationError(f"Ошибка в ингредиенте: {e}")

            if new_ingredients:
                print(f"➕ bulk_create: {len(new_ingredients)} ингредиентов")
                RecipeIngredient.objects.bulk_create(new_ingredients)
                print(
                    "🔍 Количество ингредиентов после bulk_create:",
                    instance.recipeingredient_set.count(),
                )
        if hasattr(instance, "_prefetched_objects_cache"):
            instance._prefetched_objects_cache = {}

        fresh_instance = Recipe.objects.get(id=instance.id)
        return fresh_instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор нового пользователя."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "username",
            "password",
        )

    def validate(self, data):
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
