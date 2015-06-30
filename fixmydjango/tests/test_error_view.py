import pytest
import requests
from pytest_django import live_server_helper
from django.core.urlresolvers import reverse
from termcolor import colored

from fixmydjango import FIX_MY_DJANGO_MESSAGE, FIX_MY_DJANGO_MESSAGE_PLAIN
from django.conf import settings as testsettings


@pytest.fixture(scope='session')
def api_live_server(request):
    # for mocking /api/search/ with 'test-api' endpoint of test_urls.py
    server = live_server_helper.LiveServer(
        testsettings.FIX_MY_DJANGO_API_BASE_URL.replace('http://', ''))
    request.addfinalizer(server.stop)
    return server


@pytest.mark.usefixtures('settings', 'api_live_server', 'live_server', 'capsys')
def test_error_view(settings, api_live_server, live_server, capsys):
    settings.DEBUG = True
    test_data_url = 'http://www.fixmydjango.com/test-server'

    # need to use live_server, because
    # test client launches exceptions thrown inside views
    response = requests.get(live_server.url + reverse('test-error'))

    assert response.status_code == 500
    assert FIX_MY_DJANGO_MESSAGE.format(url=test_data_url).encode('utf-8') in response.content

    out, err = capsys.readouterr()
    assert out == colored(FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=test_data_url), 'yellow') + '\n'
