"""
Модели приложения recipes.

Содержит основные сущности:
- Ингредиенты
- Теги
- Рецепты
- Связи: рецепт-ингредиент, избранное, корзина, подписки
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .const import (
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH,
    RECIPE_NAME_MAX_LENGTH
)


class Ingredient(models.Model):
    """
    Модель ингредиента для рецептовю.

    Содержит название ингредиента и единицу измерения.
    """

    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Название ингредиента",
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name="Единица измерения",
        help_text="Единица измерения ингредиента",
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]

    def __str__(self):
        """Возвращает название ингредиента."""
        return self.name


class Tag(models.Model):
    """
    Модель тега для классификации рецептов.

    Каждый тег имеет уникальное название и
    slug (короткую текстовую метку).
    """

    name = models.CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True,
        verbose_name="Название",
        help_text="Название тега",
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name="Slug",
        help_text="Короткая метка для URL",
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        """Возвращает название тега."""
        return self.name


class Recipe(models.Model):
    """
    Модель рецепта.

    Описывает рецепт, включая автора, название, изображение,
    описание, время приготовления, теги и ингредиенты.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
        help_text="Пользователь, создавший рецепт",
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name="Название",
        help_text="Название рецепта"
    )
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        null=True,
        verbose_name="Изображение",
        help_text="Фото готового блюда",
    )
    text = models.TextField(
        verbose_name="Описание", help_text="Пошаговый рецепт приготовления"
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления",
        help_text="Время приготовления в минутах (не менее 1)",
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Теги",
        help_text="Категории, к которым относится рецепт.",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты",
        help_text="Список ингредиентов",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания"
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для связи рецептов и ингредиентов.

    Определяет количество конкретного ингредиента в конкретном рецепте.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text="Рецепт, к которому относится ингредиент",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text="Используемый ингредиент",
    )
    amount = models.FloatField(
        validators=[MinValueValidator(0.1)], help_text="Количество ингредиента"
    )

    class Meta:
        """Метаданные модели."""

        unique_together = ("recipe", "ingredient")
        verbose_name = "Связь рецепта и ингредиента"
        verbose_name_plural = "Связи рецептов и ингредиентов"
        ordering = ["recipe", "ingredient"]

    def __str__(self):
        """Возвращает название рецепта и ингредиента."""
        return f"{self.recipe.name} — {self.ingredient.name}"


class Favorite(models.Model):
    """
    Модель избранного рецепта.

    Позволяет пользователю сохранять рецепты в списке избранного.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
        help_text="Пользователь, который добавил рецепт в избранное",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
        help_text="Рецепт, который добавлен в избранное",
    )

    class Meta:
        """Метаданные модели."""

        unique_together = ("user", "recipe")
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["-recipe__created_at"]

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return f"{self.user.username} — {self.recipe.name}"


class ShoppingCart(models.Model):
    """
    Модель корзины покупок.

    Позволяет пользователю добавлять рецепты в корзину
    для последующего использования.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
        help_text="Рецепт, добавленный в корзину",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
        help_text="Рецепт, добавленный в корзину",
    )

    class Meta:
        """Метаданные модели."""

        unique_together = ("user", "recipe")
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        ordering = ["-recipe__created_at"]

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return f"{self.user.username} — {self.recipe.name}"


class Subscription(models.Model):
    """
    Модель подписки на автора рецептов.

    Позволяет пользователю подписываться на других пользователей.
    Гарантирует уникальность подписки: один пользователь может
    подписаться на одного автора только один раз.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
        help_text="Пользователь, оформивший подписку",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Автор",
        help_text="Пользователь, на которого оформлена подписка",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата подписки"
    )

    class Meta:
        """Метаданные модели."""

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "author")
        ordering = ["-created_at"]

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return f"{self.user.username} → {self.author.username}"

    def save(self, *args, **kwargs):
        """
        Переопределённый метод сохранения объекта.

        Проверяет, что пользователь не пытается подписаться на самого себя.
        """
        if self.user == self.author:
            raise ValueError("Нельзя подписаться на самого себя.")
        super().save(*args, **kwargs)
