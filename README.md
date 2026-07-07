# User Microservice

Микросервис для регистрации и управления пользователями.  
Реализован на **FastAPI** с использованием **PostgreSQL** и **SQLAlchemy**.  
Администратор создаётся автоматически из данных `.env` файла.

---

## 🚀 Возможности

### 👤 Пользователи
- Регистрация нового пользователя
- Получение собственного профиля
- Обновление профиля (имя, отчество, фамилия, email, пароль)
- Удаление профиля (пометка `is_active = False`, без физического удаления)

### 🛡️ Администратор
- Создаётся автоматически при запуске сервиса из `.env`
- Может:
  - Регистрировать новых пользователей (как обычных, так и администраторов)
  - Обновлять данные пользователей (имя, email, пароль)
  - Менять роль пользователя
  - Восстанавливать удалённых пользователей (`is_active = True`)
  - Удалять пользователей (пометка `is_active = False`)
  - Получать список всех пользователей
  - Имеет весь функционал, доступный обычным пользователям

---

## 🔒 Авторизация и доступ
- Доступ к эндпоинтам администратора закрыт для обычных пользователей
  - При отсутствии прав администратора → **403 Forbidden**
  - При отсутствии аутентификации → **401 Unauthorized**
- Удалённые пользователи (`is_active = False`) не могут пройти аутентификацию

---

## ⚙️ Запуск проекта

### 1. Настройка окружения
Отредактируйте файл `template.env` и укажите параметры:
```env
DB_HOST = "<YOUR_DB_HOST>"
DB_PORT = <YOUR_DB_PORT>
DB_NAME = "<YOUR_DB_NAME>"
DB_USER = "<YOUR_DB_USERNAME>"
DB_PASSWORD = "<YOUR_DB_PASSWORD>"

TEST_DB_HOST = <TEST_DB_HOST>
TEST_DB_PORT = <TEST_DB_PORT>
TEST_DB_NAME = <TEST_DB_NAME>
TEST_DB_USER = <TEST_DB_USERNAME>
TEST_DB_PASSWORD = <TEST_DB_PASSWORD>

admin_email = "<admin@email.com>"
admin_password = "<AdminPassword12345!>"
admin_first_name = "<admin_first_name>"
admin_middle_name = "<admin_middle_name>"
admin_last_name = "<admin_last_name>"
```
Переименуйте файл в `.env`

# Сборка и запуск
```shell
make build
make up
```

# Остановка контейнера
```shell
make down
```

# Перезапуск контейнера
```shell
make restart
```

# Вход в контейнер
```shell
make app-shell   # войти в контейнер приложения
make db-shell    # войти в контейнер базы данных
make db-psql     # подключиться к Postgres через psql
```

# Очистка
```shell
make clean   # удалить контейнеры и тома
make prune   # удалить контейнеры, тома и образы
```

# 📚 API эндпоинты
## 🔑 Profile v1
• POST /api/v1/profiles — Login  
• DELETE /api/v1/profiles/ — Logout
---
## 🛡️ Admin
• GET /api/v1/admin/users/ — Get Users  
• POST /api/v1/admin/users/ — Create User  
• PATCH /api/v1/admin/users/ — Update User  
• GET /api/v1/admin/users/{user_id} — Get User By Id  
• DELETE /pi/v1/admin/users/{user_id} — Delete User  
---
## 👤 User v1
• POST /api/v1/users — Create User  
• GET /api/v/users/me — Get Profile  
• PATCH /api/v1/users/me — Update Profile  
• DELETE /api/v1/users/me — Delete User  
---