import json
import responses
import pytest
from django.conf import settings


TEST_JSON_RESPONSE = {
    "error_post_list": [
        {
            "id": 8,
            "url": "http://www.fixmydjango.com/1/",
            "exception_type": "DataError",
            "error_message": "value too long for type character varying(100)",
            "raised_by": "django/db/backends/util.py",
            "raised_by_line": 56,
            "django_version": "1.6"
        }
    ],
    "list_url": "http://www.fixmydjango.com/test-server"
}

TEST_JSON_RESPONSE_EMPTY = {
    "error_post_list": [],
    "list_url": "http://www.fixmydjango.com/test-server"
}


@pytest.yield_fixture(scope='function')
def mock_api_response():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET,
                 settings.FIX_MY_DJANGO_API_BASE_URL + '/api/search/',
                 body=json.dumps(TEST_JSON_RESPONSE), status=200,
                 content_type='application/json')
        yield TEST_JSON_RESPONSE


@pytest.yield_fixture(scope='function')
def mock_api_response_empty():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET,
                 settings.FIX_MY_DJANGO_API_BASE_URL + '/api/search/',
                 body=json.dumps(TEST_JSON_RESPONSE_EMPTY), status=200,
                 content_type='application/json')
        yield TEST_JSON_RESPONSE
