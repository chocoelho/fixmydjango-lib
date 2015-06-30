import sys
import pytest
from django.core.urlresolvers import reverse
from django.views.debug import technical_500_response
from termcolor import colored

from fixmydjango import FIX_MY_DJANGO_MESSAGE, FIX_MY_DJANGO_MESSAGE_PLAIN


@pytest.mark.usefixtures('settings', 'mock_api_response', 'mocker', 'rf', 'capsys')
def test_technical_500_response(settings, mock_api_response, mocker, rf, capsys):
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
    mocker.patch('fixmydjango.is_django_exception', return_value=True)
    mocker.patch('fixmydjango.clean_traceback', side_effect=clean_traceback)
    mocker.patch('fixmydjango.sanitize_traceback', side_effect=lambda x: x)

    request = rf.get(reverse('test-error'))
    response = technical_500_response(request, *exc_info)

    assert response.status_code == 500
    assert FIX_MY_DJANGO_MESSAGE.format(url=test_data_url).encode('utf-8') in response.content

    out, err = capsys.readouterr()
    assert out == colored(FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=test_data_url), 'yellow') + '\n'
