from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User
import os
import json


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными: пользователи, теги, ингредиенты, рецепты"

    def handle(self, *args, **options):
        admin, created_admin = User.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "username": "admin",
                "first_name": "Админ",
                "last_name": "Системы",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created_admin:
            admin.set_password("admin")
            admin.save()
            self.stdout.write(
                f"✅ Суперпользователь создан: ID={admin.pk}, email={admin.email}"
            )

        user1, created_user1 = User.objects.get_or_create(
            email="user1@example.com",
            defaults={
                "username": "user1",
                "first_name": "Иван",
                "last_name": "Петров",
                "password": "",
            },
        )
        if created_user1:
            user1.set_password("password")
            user1.save()
            self.stdout.write(
                f"✅ Пользователь создан: ID={user1.pk}, email={user1.email}"
            )

        user2, created_user2 = User.objects.get_or_create(
            email="user2@example.com",
            defaults={
                "username": "user2",
                "first_name": "Мария",
                "last_name": "Сидорова",
                "password": "",
            },
        )
        if created_user2:
            user2.set_password("password")
            user2.save()
            self.stdout.write(
                f"✅ Пользователь создан: ID={user2.pk}, email={user2.email}"
            )

        tags_data = [
            {"name": "Завтрак", "slug": "breakfast"},
            {"name": "Обед", "slug": "lunch"},
            {"name": "Ужин", "slug": "dinner"},
        ]
        tags = []
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_data)
            if created:
                self.stdout.write(f"✅ Тег создан: {tag.name}")
            tags.append(tag)

        file_path = "data/ingredients.json"
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Файл {file_path} не найден. Убедитесь, что папка data смонтирована."
                )
            )
            return

        with open(file_path, "r", encoding="utf-8") as f:
            ingredients_data = json.load(f)

        created_ingredients = 0
        for item in ingredients_data:
            _, created = Ingredient.objects.get_or_create(
                name=item["name"], measurement_unit=item["measurement_unit"]
            )
            if created:
                created_ingredients += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Успешно загружено {created_ingredients} ингредиентов."
            )
        )

        sugar = Ingredient.objects.filter(name__iexact="сахар").first()
        egg = (
            Ingredient.objects.filter(name__icontains="яйц").first()
            or Ingredient.objects.first()
        )
        milk = Ingredient.objects.filter(name__iexact="молоко").first()

        recipe1, created = Recipe.objects.get_or_create(
            author=admin,
            name="Омлет с сыром",
            defaults={
                "text": "Взбить яйца, добавить молоко и соль, вылить на сковороду, посыпать сыром.",
                "cooking_time": 10,
                "image": "recipes/omelette.jpg",
            },
        )
        if created:
            recipe1.tags.add(tags[0])
            if egg and milk:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe1, ingredient=egg, amount=2
                )
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe1, ingredient=milk, amount=100
                )
            self.stdout.write("✅ Рецепт 'Омлет' создан")

        recipe2, created = Recipe.objects.get_or_create(
            author=user1,
            name="Борщ",
            defaults={
                "text": "Сварить бульон, добавить свёклу, капусту, картофель, морковь.",
                "cooking_time": 90,
                "image": "recipes/borscht.jpg",
            },
        )
        if created:
            recipe2.tags.add(tags[1])
            if egg:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe2, ingredient=egg, amount=1
                )
            self.stdout.write("✅ Рецепт 'Борщ' создан")

        recipe3, created = Recipe.objects.get_or_create(
            author=user2,
            name="Чай с лимоном",
            defaults={
                "text": "Заварить чай, добавить ломтик лимона и сахар по вкусу.",
                "cooking_time": 5,
                "image": "recipes/tea.jpg",
            },
        )
        if created:
            recipe3.tags.add(tags[2])
            if sugar:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe3, ingredient=sugar, amount=2
                )
            self.stdout.write("✅ Рецепт 'Чай' создан")

        self.stdout.write("✅ База данных полностью заполнена тестовыми данными!")
        print("\n🔍 Проверка: все пользователи в БД после создания:")
        for u in User.objects.all():
            print(f" - {u.email} ({u.username}) | superuser={u.is_superuser}")
