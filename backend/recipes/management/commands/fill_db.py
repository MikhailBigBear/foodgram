"""
Команда Django для заполнения базы данных тестовыми данными.

Создаёт:
- Администратора и пользователей
- Теги
- Ингредиенты (из CSV-файла и вручную)
- Рецепты (13 шт.) с ингредиентами и тегами

Использование:
    python manage.py fill_db

Переменные окружения:
    ADMIN_PASSWORD — пароль для администратора.
"""

import csv
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class Command(BaseCommand):
    """Команда Django для заполнения базы данных тестовыми данными."""

    help = "Заполняет базу: пользователи, теги, ингредиенты, рецепты"

    def handle(self, *args, **options):
        """Обработчик команды."""
        admin_password = os.getenv("ADMIN_PASSWORD", "admin")

        admin, created_admin = User.objects.get_or_create(
            email="miholxovikov92@mail.ru",
            defaults={
                "username": "admin_mihail",
                "first_name": "Михаил",
                "last_name": "Ольховиков",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.set_password(admin_password)
        admin.save()
        if created_admin:
            self.stdout.write(f"✅ Админ создан: {admin.email}")
        else:
            self.stdout.write(
                f"✅ Админ обновлён: {admin.email} (пароль сброшен)"
            )

        user1, created_user1 = User.objects.get_or_create(
            email="user1@example.com",
            defaults={
                "username": "user1",
                "first_name": "Иван",
                "last_name": "Петров",
            },
        )
        if created_user1:
            user1.set_password("password")
            user1.save()
            self.stdout.write(f"✅ Пользователь: {user1.username}")

        user2, created_user2 = User.objects.get_or_create(
            email="user2@example.com",
            defaults={
                "username": "user2",
                "first_name": "Мария",
                "last_name": "Сидорова",
            },
        )
        if created_user2:
            user2.set_password("password")
            user2.save()
            self.stdout.write(f"✅ Пользователь: {user2.username}")

        tags_data = [
            {"name": "Завтрак", "slug": "breakfast"},
            {"name": "Обед", "slug": "lunch"},
            {"name": "Ужин", "slug": "dinner"},
            {"name": "Выпечка", "slug": "baking"},
            {"name": "Напитки", "slug": "drinks"},
            {"name": "Горячее", "slug": "hot"},
        ]
        tags = []
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(**tag_data)
            if created:
                self.stdout.write(f"✅ Тег: {tag.name}")
            tags.append(tag)

        file_path = "/app/data/ingredients.csv"
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f"❌ Файл {file_path} не найден")
            )
            return

        created_ingredients = 0
        with open(file_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                name = row[0].strip()
                unit = row[1].strip()
                _, created = Ingredient.objects.get_or_create(
                    name=name, measurement_unit=unit
                )
                if created:
                    created_ingredients += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Загружено {created_ingredients} ингредиентов"
            )
        )

        def get_ingredient(name):
            try:
                return Ingredient.objects.get(name__iexact=name)
            except Ingredient.DoesNotExist:
                return None

        ingredients_map = {
            "сахар": get_ingredient("сахар"),
            "яйца куриные": get_ingredient("яйца куриные"),
            "молоко": get_ingredient("молоко"),
            "мука": get_ingredient("мука"),
            "масло сливочное": get_ingredient("масло сливочное"),
            "картофель": get_ingredient("картофель"),
            "лук репчатый": get_ingredient("лук репчатый"),
            "соль": get_ingredient("соль"),
            "перец чёрный": get_ingredient("перец чёрный"),
            "сыр плавленый": get_ingredient("сыр плавленый"),
            "растительное масло рафинированное": get_ingredient(
                "растительное масло рафинированное"
            ),
            "фарш (баранина и говядина)": get_ingredient(
                "фарш (баранина и говядина)"
            ),
            "соевый соус": get_ingredient("соевый соус"),
            "свёкла": get_ingredient("свёкла"),
            "капуста белокочанная": get_ingredient("капуста белокочанная"),
            "морковь": get_ingredient("морковь"),
            "лимон": get_ingredient("лимон"),
            "творог": get_ingredient("творог"),
            "огурцы маринованные": get_ingredient("огурцы маринованные"),
            "колбаса вареная": get_ingredient("колбаса вареная"),
            "майонез": get_ingredient("майонез"),
            "рис": get_ingredient("рис"),
            "перец болгарский": get_ingredient("перец болгарский"),
            "помидоры": get_ingredient("помидоры"),
            "сливки": get_ingredient("сливки"),
            "лапша для лагмана": get_ingredient("лапша для лагмана"),
            "зелень": get_ingredient("зелень"),
            "чеснок": get_ingredient("чеснок"),
            "рыба белая": get_ingredient("рыба белая"),
            "булочки для гамбургеров": get_ingredient(
                "булочки для гамбургеров"
            ),
            "томаты консервированные": get_ingredient(
                "помидоры консервированные"
            ),
            "лавровый лист": get_ingredient("лавровый лист"),
            "майонез «Слобода» На перепелиных яйцах": get_ingredient(
                "майонез «Слобода» На перепелиных яйцах"
            ),
        }

        for name, ing in ingredients_map.items():
            if not ing:
                ing, _ = Ingredient.objects.get_or_create(
                    name=name, defaults={"measurement_unit": "г"}
                )
                ingredients_map[name] = ing
                self.stdout.write(f"✅ Добавлен: {name}")

        recipe, created = Recipe.objects.get_or_create(
            author=admin,
            name="Омлет с сыром",
            defaults={
                "text": "Взбейте яйца с молоком, добавьте соль и перец. "
                "Вылейте на сковороду с маслом, "
                "обжаривайте до полуготовности. "
                "Посыпьте тертым сыром, накройте "
                "крышкой и дождитесь расплавления.",
                "cooking_time": 10,
                "image": "recipes/omelette.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[0], tags[5])
            for name, amount in [
                ("яйца куриные", 3),
                ("молоко", 150),
                ("сыр плавленый", 50),
                ("соль", 1),
                ("перец чёрный", 1),
                ("масло сливочное", 15),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Омлет' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user1,
            name="Борщ",
            defaults={
                "text": "Сварите мясной бульон. "
                "Отдельно потушите свёклу с луком и морковью. "
                "Добавьте капусту, картофель, специи. "
                "Заправьте томатом и уксусом. "
                "Подавайте со сметаной и зеленью.",
                "cooking_time": 90,
                "image": "recipes/borscht.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[1], tags[5])
            for name, amount in [
                ("свёкла", 300),
                ("капуста белокочанная", 400),
                ("картофель", 300),
                ("морковь", 100),
                ("лук репчатый", 50),
                ("томаты консервированные", 100),
                ("растительное масло рафинированное", 2),
                ("соль", 1),
                ("перец чёрный", 1),
                ("лавровый лист", 1),
                ("чеснок", 2),
                ("зелень", 30),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Борщ' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user2,
            name="Чай с лимоном",
            defaults={
                "text": "Заварите черный чай. Добавьте дольку "
                "свежего лимона и сахар по вкусу. "
                "Подавайте горячим или охлаждённым.",
                "cooking_time": 5,
                "image": "recipes/tea.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[2], tags[4])
            for name, amount in [
                ("сахар", 2),
                ("лимон", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Чай' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=admin,
            name="Картофель по-деревенски",
            defaults={
                "text": "Картофель нарежьте крупными кусками, "
                "посолите, сбрызните маслом. "
                "Выпекайте в духовке при 200°C до хрустящей корочки.",
                "cooking_time": 30,
                "image": "recipes/potatoes.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[0], tags[5])
            for name, amount in [
                ("картофель", 500),
                ("растительное масло рафинированное", 3),
                ("соль", 1),
                ("перец чёрный", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Картофель' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=admin,
            name="Сырники",
            defaults={
                "text": "Смешайте творог с яйцом, сахаром, мукой. "
                "Сформируйте лепёшки, "
                "обваляйте в муке и жарьте на масле до золотистой корочки.",
                "cooking_time": 25,
                "image": "recipes/syrniki.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[0])
            for name, amount in [
                ("творог", 400),
                ("яйца куриные", 1),
                ("сахар", 20),
                ("мука", 50),
                ("масло сливочное", 30),
                ("соль", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Сырники' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=admin,
            name="Гамбургер",
            defaults={
                "text": "Обжарьте котлету из фарша. "
                "Подготовьте булочку: подсушите в тостере. "
                "Смажьте майонезом. "
                "Соберите: котлета, сыр, лук, огурцы, соус.",
                "cooking_time": 20,
                "image": "recipes/burger.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[2])
            for name, amount in [
                ("фарш (баранина и говядина)", 150),
                ("сыр плавленый", 30),
                ("лук репчатый", 20),
                ("огурцы маринованные", 20),
                ("булочки для гамбургеров", 1),
                ("майонез", 15),
            ]:
                ing = ingredients_map[name]
                if not ing:
                    ing, _ = Ingredient.objects.get_or_create(
                        name=name, defaults={"measurement_unit": "г"}
                    )
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe, ingredient=ing, amount=amount
                )
            self.stdout.write("✅ Рецепт 'Гамбургер' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user1,
            name="Пельмени",
            defaults={
                "text": "Сварите пельмени в подсоленной воде. "
                "Подавайте со сметаной и зеленью. "
                "По желанию добавьте сливочное масло.",
                "cooking_time": 15,
                "image": "recipes/pelmeni.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[1])
            for name, amount in [
                ("фарш (баранина и говядина)", 400),
                ("мука", 300),
                ("яйца куриные", 1),
                ("лук репчатый", 50),
                ("соль", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Пельмени' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user1,
            name="Жареная рыба",
            defaults={
                "text": "Обваляйте куски рыбы в муке. "
                "Жарьте на разогретом масле до золотистой корочки. "
                "Подавайте с лимоном и зеленью.",
                "cooking_time": 25,
                "image": "recipes/fish.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[1], tags[5])
            for name, amount in [
                ("рыба белая", 500),
                ("мука", 50),
                ("растительное масло рафинированное", 3),
                ("соль", 1),
                ("перец чёрный", 1),
                ("лимон", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Жареная рыба' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user1,
            name="Оладьи",
            defaults={
                "text": "Смешайте молоко, яйца, муку, сахар и щепотку соли. "
                "Жарьте на масле до золотистого цвета. "
                "Подавайте со сметаной или вареньем.",
                "cooking_time": 30,
                "image": "recipes/oladi.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[0])
            for name, amount in [
                ("молоко", 200),
                ("яйца куриные", 2),
                ("мука", 150),
                ("сахар", 20),
                ("масло сливочное", 30),
                ("соль", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Оладьи' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user2,
            name="Салат Оливье",
            defaults={
                "text": "Отварите картофель, морковь, яйца, колбасу. "
                "Нарежьте кубиками. "
                "Смешайте с майонезом, посолите, поперчите. Украсьте зеленью.",
                "cooking_time": 20,
                "image": "recipes/olivier.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[2])
            for name, amount in [
                ("картофель", 300),
                ("морковь", 100),
                ("колбаса вареная", 200),
                ("яйца куриные", 3),
                ("перец чёрный", 1),
                ("майонез", 50),
                ("зелень", 20),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Оливье' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user2,
            name="Рис с овощами",
            defaults={
                "text": "Обжарьте лук и морковь. "
                "Добавьте болгарский перец, тушите 5 минут. "
                "Добавьте промытый рис, залейте водой и варите до готовности.",
                "cooking_time": 40,
                "image": "recipes/rice.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[1])
            for name, amount in [
                ("рис", 200),
                ("лук репчатый", 50),
                ("морковь", 100),
                ("перец болгарский", 100),
                ("растительное масло рафинированное", 2),
                ("соль", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Рис с овощами' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user2,
            name="Томатный суп",
            defaults={
                "text": "Потушите лук и морковь. "
                "Добавьте помидоры, влейте бульон, "
                "протрите блендером. Добавьте сливки, посолите. "
                "Прогрейте — не доводя до кипения.",
                "cooking_time": 35,
                "image": "recipes/soup.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[1])
            for name, amount in [
                ("помидоры", 500),
                ("лук репчатый", 50),
                ("морковь", 50),
                ("растительное масло рафинированное", 2),
                ("сливки", 100),
                ("соль", 1),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Томатный суп' создан")

        recipe, created = Recipe.objects.get_or_create(
            author=user1,
            name="Лапша удон с овощами",
            defaults={
                "text": "Обжарьте лук, морковь и болгарский перец. "
                "Добавьте отваренную лапшу удон. "
                "Полейте соевым соусом, посолите, "
                "перемешайте и тушите 3 минуты.",
                "cooking_time": 20,
                "image": "recipes/udon.jpg",
            },
        )
        if created:
            recipe.tags.add(tags[0], tags[5])
            for name, amount in [
                ("лук репчатый", 50),
                ("морковь", 50),
                ("перец болгарский", 50),
                ("растительное масло рафинированное", 2),
                ("соевый соус", 30),
                ("соль", 1),
                ("лапша для лагмана", 200),
            ]:
                RecipeIngredient.objects.get_or_create(
                    recipe=recipe,
                    ingredient=ingredients_map[name],
                    amount=amount,
                )
            self.stdout.write("✅ Рецепт 'Лапша удон' создан")

        self.stdout.write(self.style.SUCCESS("✅ Все 13 рецептов загружены!"))

        print("\n🔍 Проверка пользователей:")
        for u in User.objects.all():
            print(f" - {u.username} | superuser={u.is_superuser}")
