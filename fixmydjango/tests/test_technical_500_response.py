import sys
import pytest
from django.core.urlresolvers import reverse
from django.views.debug import technical_500_response
from termcolor import colored
import requests

from fixmydjango import (
    FIX_MY_DJANGO_MESSAGE, FIX_MY_DJANGO_MESSAGE_PLAIN,
    FIX_MY_DJANGO_MESSAGE_TO_ADMIN, FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN)
from fixmydjango.tests.utils import format_template


@pytest.mark.usefixtures('settings', 'mock_api_response', 'mocker', 'rf', 'capsys')
def test_technical_500_response(settings, mock_api_response, mocker, rf, capsys):
    settings.DEBUG = True
    settings.FIX_MY_DJANGO_ADMIN_MODE = True
    test_data_url = 'http://www.fixmydjango.com/test-server'
    admin_url = 'http://www.fixmydjango.com/test-server/admin'

    try:
        raise ValueError("test")
    except:
        exc_info = sys.exc_info()

    def clean_traceback(tb):
        # remove \r
        tb = tb.replace('\r', '')
        # remove empty lines
        tb_lines = [line for line in tb.split('\n')
                    if line.strip()]
        return '\n'.join(tb_lines)
    mocker.patch('fixmydjango.is_django_exception', return_value=True)
    mocker.patch('fixmydjango.clean_traceback', side_effect=clean_traceback)
    mocker.patch('fixmydjango.sanitize_traceback', side_effect=lambda x: x)
    mocker.patch(
        'fixmydjango.ExceptionReporterPatch._get_fix_my_django_admin_url',
        return_value=admin_url)

    request = rf.get(reverse('test-error'))
    response = technical_500_response(request, *exc_info)

    assert response.status_code == 500
    assert format_template(
        FIX_MY_DJANGO_MESSAGE,
        {'url': test_data_url, 'is_admin_mode': True, 'admin_url': admin_url}
    ) in response.content

    out, err = capsys.readouterr()
    assert out == colored(FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=test_data_url), 'yellow') + '\n'


@pytest.mark.usefixtures('settings', 'mock_api_response_empty', 'mocker', 'rf', 'capsys')
def test_technical_500_response_empty(settings, mock_api_response_empty, mocker, rf, capsys):
    settings.DEBUG = True
    settings.FIX_MY_DJANGO_ADMIN_MODE = True
    admin_url = 'http://www.fixmydjango.com/test-server/admin'

    try:
        raise ValueError("test")
    except:
        exc_info = sys.exc_info()

    def clean_traceback(tb):
        # remove \r
        tb = tb.replace('\r', '')
        # remove empty lines
        tb_lines = [line for line in tb.split('\n')
                    if line.strip()]
        return '\n'.join(tb_lines)
    mocker.patch('fixmydjango.is_django_exception', return_value=True)
    mocker.patch('fixmydjango.clean_traceback', side_effect=clean_traceback)
    mocker.patch('fixmydjango.sanitize_traceback', side_effect=lambda x: x)
    mocker.patch(
        'fixmydjango.ExceptionReporterPatch._get_fix_my_django_admin_url',
        return_value=admin_url)

    request = rf.get(reverse('test-error'))
    response = technical_500_response(request, *exc_info)

    assert response.status_code == 500
    assert FIX_MY_DJANGO_MESSAGE_TO_ADMIN.format(admin_url=admin_url).encode('utf-8') in response.content

    out, err = capsys.readouterr()
    assert out == colored(FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN.format(admin_url=admin_url), 'yellow') + '\n'


@pytest.mark.usefixtures('settings', 'mocker', 'rf', 'capsys')
def test_technical_500_response_not_django(settings, mocker, rf, capsys):
    settings.DEBUG = True
    test_data_url = 'http://www.fixmydjango.com/test-server'

    try:
        raise ValueError("test")
    except:
        exc_info = sys.exc_info()

    def clean_traceback(tb):
        # remove \r
        tb = tb.replace('\r', '')
        # remove empty lines
        tb_lines = [line for line in tb.split('\n')
                    if line.strip()]
        return '\n'.join(tb_lines)
    mocker.patch('fixmydjango.is_django_exception', return_value=False)
    mocker.spy(requests, 'get')

    request = rf.get(reverse('test-error'))
    response = technical_500_response(request, *exc_info)

    assert requests.get.call_count == 0

    assert response.status_code == 500
    assert format_template(FIX_MY_DJANGO_MESSAGE, {'url': test_data_url}) not in response.content

    out, err = capsys.readouterr()
    assert out == ''
