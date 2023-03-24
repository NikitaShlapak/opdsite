from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-2^s_8f-+m&v4882wlctonrwr*2f#mgfw!7h2em^8jf0^7f2psg'
DEBUG = True



EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '123'
EMAIL_HOST_PASSWORD = '123'
EMAIL_PORT = 123
EMAIL_USE_TLS = True


ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',

    }
}
