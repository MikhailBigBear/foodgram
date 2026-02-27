from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    """
    Модель ингредиента для рецептовю.

    Содержит название ингредиента и единицу измерения.
    """

    name = models.CharField(
        max_length=128,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Модель тега для классификации рецептов.

    Каждый тег имеет уникальное название и
    slug (короткую текстовую метку).
    """

    name = models.CharField(max_length=32, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=32, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.

    Описывает рецепт, включая автора, название, изображение,
    описание, время приготовления, теги и ингредиенты.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=256,
        verbose_name="Название",
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Изображение",
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления",
    )
    tag = models.ManyToManyField(Tag, verbose_name="Теги")
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
    )
    created_at = models.DateTimsField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов.

    Определяет количество конкретного ингредиента в конкретном рецепте.
    """

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField(validators=[MinValueValidator(0.1)])

    class Meta:
        unique_together = ("recipe", "ingredient")
        verbose_name = "Связь рецепта и ингредиента"
        verbose_name_plural = "Связи рецептов и ингредиентов"

    def __str__(self):
        return f"{self.recipe.name} — {self.ingredient.name}"


class Favorite(models.Model):
    """
    Модель избранного рецепта.

    Позволяет пользователю сохранять рецепты в списке избранного.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        unique_together = ("user", "recipe")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"

    def __str__(self):
        return f"{self.user.username} — {self.recipe.name}"


class ShoppingCart(models.Model):
    """
    Модель корзины покупок.

    Позволяет пользователю добавлять рецепты в корзину
    для последующего использования.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shopping_cart"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="shopping_cart"
    )

    class Meta:
        unique_together = ("user", "recipe")
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f"{self.user.username} — {self.recipe.name}"


class Subscription(models.Model):
    """
    Модель подписки на автора рецептов.

    Позволяет пользователю подписываться на других пользователей.
    Гарантирует уникальность подписки: один пользователь может
    подписаться на одного автора только один раз.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following", verbose_name="Автор"
    )
    created_at = models.DateTimsField(auto_now_add=True)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "author")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.author.username}"

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValueError("Нельзя подписаться на самого себя.")
        super().save(*args, **kwargs)
