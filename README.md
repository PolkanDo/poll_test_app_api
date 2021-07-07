# poll_test_app_api
## Запуск проекта
### Первоначальная установка
cd DRF-Poll-Test
pip install -r requirements.txt
cd backend
python manage.py migrate
python manage.py createsuperuser
Создаём супер-юзера с именем admin и паролем admin. Это имя и пароль будут использоваться в тестах (см. tests/settings.py).

## Запуск сервера
cd poll_test_app_api/myapp
python manage.py runserver
