import requests


def search_exceptions(exception_type, raised_by, raised_by_line='',
                      django_version='', base_url='http://www.fixmydjango.com'):
    path = '/api/search/'

    return requests.get(base_url + path, params={
        'exception_type': exception_type,
        'raised_by': raised_by,
        'raised_by_line': raised_by_line,
        'django_version': django_version
    }, headers={
        'Accept': 'application/json'
    }).json()
