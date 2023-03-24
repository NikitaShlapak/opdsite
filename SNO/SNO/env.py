from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '123'
DEBUG = False


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '123'
EMAIL_HOST_PASSWORD = '123'
EMAIL_PORT = 123
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ['opd.iate.obninsk.ru','127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '123',
        'USER': '123',
        'PASSWORD': '123',
        'HOST': '123',
        'PORT': '',
    }
}
