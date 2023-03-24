from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2^s_8f-+m&v4882wlctonrwr*2f#mgfw!7h2em^8jf0^7f2psg'
DEBUG = False


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'stusciiate@gmail.com'
EMAIL_HOST_PASSWORD = 'rdeughmjkawljfms'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ALLOWED_HOSTS = ['opd.iate.obninsk.ru', '10.0.0.34', '10.0.0.183', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'opd',
        'USER': 'opd',
        'PASSWORD': 'Tsm4EIMXgwr9VK',
        'HOST': 'localhost',
        'PORT': '',
    }
}