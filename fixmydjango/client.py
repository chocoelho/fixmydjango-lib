import requests
from django.conf import settings


base_url = getattr(
    settings,
    'FIX_MY_DJANGO_API_BASE_URL',
    'http://www.fixmydjango.com')


def search_exceptions(exception_type, raised_by, raised_by_line='',
                      django_version='', base_url=base_url):
    path = '/api/search/'

    return requests.get(base_url + path, params={
        'exception_type': exception_type,
        'raised_by': raised_by,
        'raised_by_line': raised_by_line,
        'django_version': django_version
    }, headers={
        'Accept': 'application/json'
    }).json()
