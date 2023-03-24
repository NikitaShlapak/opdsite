from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '123'
DEBUG = True


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'stusciiate@gmail.com'
EMAIL_HOST_PASSWORD = '123'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
