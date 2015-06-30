import pytest

from ..client import search_exceptions


@pytest.mark.usefixtures('mock_api_response')
def test_search_exceptions(mock_api_response):
    data = search_exceptions(
        exception_type='Test',
        raised_by='test.py',
        raised_by_line=1,
        django_version='1.8')

    assert data == mock_api_response
