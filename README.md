# 🍽️ Foodgram — платформа для публикации и поиска кулинарных рецептов

Foodgram — это веб-приложение, где пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять блюда в избранное и список покупок. Проект реализован с использованием современных технологий и развёрнут в Docker-контейнерах.

---

## 👤 Автор

**Михаил Ольховиков**  
📧 [miholxovikov92@mail.ru](mail:miholxovikov92@mail.ru)  
🌐 [GitHub](https://github.com/MikhailBigBear)

---

## ⚙️ Стек технологий

- **Python 3** — язык программирования;
- **Django** — бэкенд и ORM;
- **Django REST Framework (DRF)** — создание API;
- **PostgreSQL** — реляционная база данных;
- **Nginx** — веб‑сервер и прокси;
- **Gunicorn** — WSGI‑сервер для запуска Python‑приложений;
- **Docker / Docker Compose** — контейнеризация и оркестрация контейнеров;
- **React** — фронтенд‑фреймворк;
- **Node.js** — среда выполнения для сборки фронтенда;
- **GitHub Actions** — автоматизация CI/CD‑процессов.

---

## 🚀 Локальное развертывание

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/MikhailBigBear/foodgram.git
cd foodgram

2. Создайте файл .env в корне проекта
Пример содержимого .env:

ENV
# Django
SECRET_KEY=your_django_secret_key_here
DEBUG=False
ALLOWED_HOSTS=130.193.45.160,localhost,127.0.0.1

# База данных
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Админка
DJANGO_SUPERUSER_EMAIL=miholxovikov92@mail.ru
DJANGO_SUPERUSER_PASSWORD=2ES61200

3. Запустите проект через Docker Compose

Bash
# Перейдите в папку infra
cd infra

# Соберите и запустите контейнеры
docker compose up -d --build

4. Выполните миграции и соберите статику

Bash
# Примените миграции
docker compose exec backend python manage.py migrate --noinput

# Соберите статику
docker compose exec backend python manage.py collectstatic --noinput

# (Опционально) Загрузите тестовые данные
docker compose exec backend python manage.py fill_db

🔐 Доступ к админке

URL: http://localhost/admin/
Логин: miholxovikov92@mail.ru
Пароль: 2ES61200

🌐 Доступ к проекту

Проект доступен по IP-адресу:

👉 http://130.193.45.160

API: http://130.193.45.160/api/

Документация API: http://130.193.45.160/api/docs/

📦 CI/CD

Проект автоматически деплоится при пуше в ветку main через GitHub Actions.

Конфигурация: .github/workflows/main.yml
