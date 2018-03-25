import pytest
import requests
from distutils.version import LooseVersion
from pytest_django import live_server_helper
import django
try:
    from django.core.urlresolvers import reverse
except ImportError:
    from django.urls import reverse
from termcolor import colored

from fixmydjango import FIX_MY_DJANGO_MESSAGE, FIX_MY_DJANGO_MESSAGE_PLAIN
from fixmydjango.tests.utils import format_template
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

    # this test doesn't works in Django <= 1.6,
    # because in this version live_server doesn't work with DEBUG=True.
    # see: https://github.com/fjsj/liveservererror
    if LooseVersion(django.get_version()) >= LooseVersion('1.7'):
        test_data_url = 'http://www.fixmydjango.com/test-server'

        # need to use live_server, because
        # test client launches exceptions thrown inside views
        response = requests.get(live_server.url + reverse('test-error'))

        assert response.status_code == 500
        assert format_template(FIX_MY_DJANGO_MESSAGE[0:50], {}) in response.content

        out, err = capsys.readouterr()
        assert out == colored(FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=test_data_url), 'yellow') + '\n'
