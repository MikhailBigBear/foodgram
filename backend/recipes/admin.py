from django.contrib import admin
from .models import (
    Ingredient,
    Favorite,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели Ingredient в админке."""

    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка отображения модели Favorite в админке."""

    list_display = ("user", "recipe")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения модели Recipe в админке."""

    list_display = ('name', 'author', 'favorites_count')
    list_filter = ('author', 'tags', 'name')
    search_fields = ('name', 'author__username', 'author__email')
    filter_horizontal = ('tags',)

    @property
    def favorites_count(self):
        def _favorites_count(obj):
            return obj.favorited_by.count()

        _favorites_count.short_description = "Добавлено в избранное (раз)"
        _favorites_count.admin_order_field = "favorited_by"
        return _favorites_count


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели RecipeIngredient в админке."""

    list_display = ("recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка отображения модели ShoppingCart в админке."""

    list_display = ("user", "recipe")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка отображения модели Subscription в админке."""

    list_display = ("user", "author", "created_at")
    list_filter = ("created_at",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка отображения модели Tag в админке."""

    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
