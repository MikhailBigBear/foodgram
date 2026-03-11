from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r"ingredients", views.IngredientViewSet, basename="ingredients")
router.register(r"recipes", views.RecipeViewSet, basename="recipes")
router.register(r"tags", views.TagViewSet, basename="tags")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", views.TokenLoginView.as_view(), name="token_login"),
    path("auth/token/logout/", views.TokenLogoutView.as_view(), name="token_logout"),
    path("users/", views.UserRegistrationView.as_view(), name="user-registration"),
    path(
        "users/me/",
        views.UserViewSet.as_view(
            {"get": "me", "put": "set_avatar", "delete": "delete_avatar"}
        ),
        name="user-me",
    ),
    path(
        "users/set_password/",
        views.UserViewSet.as_view({"post": "change_password"}),
        name="user-set-password",
    ),
]
