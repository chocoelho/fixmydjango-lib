import json
import responses
import pytest
from django.conf import settings


TEST_JSON_RESPONSE = [{
    'id': 1,
    'url': 'http://www.fixmydjango.com/test-server',
    'exception_type': 'ValueError',
    'error_message': 'test',
    'raised_by': 'test.py',
    'raised_by_line': 1,
    'django_version': '1.8'
}]


@pytest.yield_fixture(scope='function')
def mock_api_response():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET,
                 settings.FIX_MY_DJANGO_API_BASE_URL + '/api/search/',
                 body=json.dumps(TEST_JSON_RESPONSE), status=200,
                 content_type='application/json')
        yield TEST_JSON_RESPONSE
