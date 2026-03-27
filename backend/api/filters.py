"""
Модуль фильтров для Django REST Framework.

Содержит кастомные фильтры для моделей Ingredient и Recipe,
позволяющие фильтровать данные через API с поддержкой поиска,
тегов, избранного и списка покупок.
"""

from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(filters.FilterSet):
    """Фильтр для модели Ingredient."""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        """Метаданные фильтра."""

        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    """Фильтр для модели Recipe."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        """Добавляет фильтрацию по избранным рецептам текущего пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Добавляет фильтрацию по рецептам в списке покупок пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        """Метаданные фильтра."""

        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
