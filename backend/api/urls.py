"""Модуль настраивает URL-маршруты API проекта Foodgram."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("tags", views.TagViewSet, basename="tags")
router.register(
    "ingredients", views.IngredientViewSet, basename="ingredients"
)
router.register("recipes", views.RecipeViewSet, basename="recipes")
urlpatterns = [
    path("", include(router.urls)),
    path(
        "users/",
        views.UserViewSet.as_view({
            "get": "list",
            "post": "create"
        }),
        name="user-list"
    ),
    path(
        "users/<int:pk>/",
        views.UserViewSet.as_view({"get": "retrieve"}),
        name="user-detail"
    ),
    path(
        "users/me/",
        views.UserViewSet.as_view({"get": "me"}),
        name="user-me"
    ),
    path(
        "users/me/avatar/",
        views.UserViewSet.as_view({
            "put": "set_avatar",
            "patch": "set_avatar",
            "delete": "delete_avatar"
        }),
        name="user-avatar"
    ),
    path(
        "users/subscriptions/",
        views.SubscriptionViewSet.as_view({"get": "subscriptions"}),
        name="subscriptions",
    ),
    path(
        "users/<int:pk>/subscribe/",
        views.SubscriptionViewSet.as_view(
            {"post": "subscribe", "delete": "unsubscribe"}
        ),
        name="subscribe",
    ),

    path(
        "auth/token/login/", views.TokenLoginView.as_view(), name="token_login"
    ),
    path(
        "auth/token/logout/",
        views.TokenLogoutView.as_view(),
        name="token_logout",
    ),
    path(
        "recipes/<int:pk>/shopping_cart/",
        views.RecipeViewSet.as_view({
            "post": "add_to_shopping_cart",
            "delete": "remove_from_shopping_cart",
        }),
        name="recipe-shopping-cart",
    ),
    path(
        "recipes/<int:pk>/favorite/",
        views.RecipeViewSet.as_view({
            "post": "add_to_favorite",
            "delete": "remove_from_favorite",
        }),
        name="recipe-favorite",
    ),
]
