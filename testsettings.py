import random


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

# Django 1.10 cannot close sockets quick enough while running tox
# to prevent conflicts we will use a random port
FIX_MY_DJANGO_API_BASE_URL = 'http://localhost:' + str(random.randint(8100, 8900))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
