from django.core.management.base import BaseCommand
from users.models import User
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient


class Command(BaseCommand):
    """Команда для наполнения базы тестовыми данными."""

    help = "Наполняет базу тестовыми данными"

    def handle(self, *args, **options):
        user1 = User.objects.create_user(
            email="user1@example.com",
            username="user1",
            password="12345",
            first_name="Иван",
            last_name="Иванов",
        )
        user2 = User.objects.create_user(
            email="user2@example.com",
            username="user2",
            password="12345",
            first_name="Петр",
            last_name="Петров",
        )

        tag1 = Tag.objects.create(name="Завтрак", slug="breakfast")
        tag2 = Tag.objects.create(name="Обед", slug="lunch")
        tag3 = Tag.objects.create(name="Ужин", slug="dinner")

        ing1 = Ingredient.objects.create(name="Яйца", measurement_unit="шт")
        ing2 = Ingredient.objects.create(name="Молоко", measurement_unit="мл")
        ing3 = Ingredient.objects.create(name="Соль", measurement_unit="г")
        ing4 = Ingredient.objects.create(name="Сахар", measurement_unit="г")
        ing5 = Ingredient.objects.create(name="Говядина", measurement_unit="г")
        ing6 = Ingredient.objects.create(name="Лук", measurement_unit="шт")

        recipe1 = Recipe.objects.create(
            author=user1, name="Омлет", text="Жарим яйца с молоком.", cooking_time=10
        )
        recipe1.tag.add(tag1)
        RecipeIngredient.objects.create(recipe=recipe1, ingredient=ing1, amount=2)
        RecipeIngredient.objects.create(recipe=recipe1, ingredient=ing2, amount=50)
        RecipeIngredient.objects.create(recipe=recipe1, ingredient=ing3, amount=1)

        recipe2 = Recipe.objects.create(
            author=user2,
            name="Блины",
            text="Тесто на молоке, жарим на сковороде.",
            cooking_time=20,
        )
        recipe2.tag.add(tag1)
        RecipeIngredient.objects.create(recipe=recipe2, ingredient=ing2, amount=200)
        RecipeIngredient.objects.create(recipe=recipe2, ingredient=ing3, amount=2)
        RecipeIngredient.objects.create(recipe=recipe2, ingredient=ing4, amount=10)

        recipe3 = Recipe.objects.create(
            author=user1,
            name="Гуляш",
            text="Тушим говядину с луком и специями.",
            cooking_time=60,
        )
        recipe3.tag.add(tag2, tag3)  # Обед и ужин
        RecipeIngredient.objects.create(recipe=recipe3, ingredient=ing5, amount=500)
        RecipeIngredient.objects.create(recipe=recipe3, ingredient=ing6, amount=2)
        RecipeIngredient.objects.create(recipe=recipe3, ingredient=ing3, amount=5)

        self.stdout.write(
            self.style.SUCCESS(
                "База успешно наполнена тестовыми данными с использованием всех тегов."
            )
        )
