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
from django.contrib.auth.models import User


admin.site.register(Ingredient)
admin.site.register(Favorite)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели Ingredient в админке."""

    list_display = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)
    search_fields = ("name",)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройка отображения модели Favorite в админке."""

    list_display = ("user", "recipe", "created_at")
    list_filter = ("user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__name")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка отображения модели Recipe в админке."""

    list_display = ("name", "author", "cooking_time", "created_at")
    list_filter = ("author", "tag", "created_at")
    search_fields = ("name", "author__username")
    filter_horizontal = ("tag", "ingredient")
    readonly_fields = "created_at"
    fields = (
        ("Основное", {"fields": (
            "name", "author", "image", "text", "cooking_time"
            )}),
        (
            "Дополнительно",
            {
                "classes": ("collapse",),
                "fields": ("tag", "ingredients", "created_at"),
            },
        ),
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Настройка отображения модели RecipeIngredient в админке."""

    list_display = ("recipe", "ingredient", "amount")
    list_filter = ("recipe", "ingredient")
    search_fields = ("recipe__name", "ingredient__name")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройка отображения модели ShoppingCart в админке."""

    list_display = ("user", "recipe", "created_at")
    list_filter = ("user", "recipe", "created_at")
    search_fields = ("user__username", "recipe__name")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Настройка отображения модели Subscription в админке."""

    list_display = ("user", "author", "created_at")
    list_filter = ("user", "author", "created_at")
    search_fields = ("user__username", "author__username")
    date_hierarchy = "created_at"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка отображения модели Tag в админке."""

    list_display = ("name", "slug")
    list_filter = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройка отображения модели User в админке."""

    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email", "first_name", "last_name")
