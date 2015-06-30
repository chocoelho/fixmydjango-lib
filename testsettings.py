DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'fixmydjango',
)

SECRET_KEY = 'abcde12345'

ROOT_URLCONF = 'fixmydjango.tests.urls'

STATIC_URL = '/static/'

FIX_MY_DJANGO_API_BASE_URL = 'http://localhost:8100'
