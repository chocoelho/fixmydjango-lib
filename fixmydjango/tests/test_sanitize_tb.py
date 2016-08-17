import sys
import traceback
import pytest
from boltons.tbutils import ParsedException

from ..sanitize_tb import is_django_exception, clean_traceback, sanitize_traceback, extract_traceback_info


django_tb = '''Traceback (most recent call last):
  File "python2.7/site-packages/django/core/handlers/base.py", line 139, in get_response
    response = response.render()
  File "python2.7/site-packages/django/template/response.py", line 105, in render
    self.content = self.rendered_content
  File "python2.7/site-packages/django/template/response.py", line 80, in rendered_content
    template = self.resolve_template(self.template_name)
  File "python2.7/site-packages/django/template/response.py", line 56, in resolve_template
    return loader.select_template(template)
  File "python2.7/site-packages/django/template/loader.py", line 186, in select_template
    raise TemplateDoesNotExist(', '.join(not_found))
TemplateDoesNotExist: none.html'''

django_with_private_tb = '''Traceback (most recent call last):
  File "project-name/should_hide_me.py", line 987, in should_hide_me_fn
    return should_hide_me_fn(template)
  File "/user/sys-file/python2.7/site-packages/django/template/loader.py", line 186, in select_template
    raise TemplateDoesNotExist(', '.join(not_found))
TemplateDoesNotExist: none.html'''

django_with_private_tb_sanitized = '''Traceback (most recent call last):
  File "private.py", line 1, in private_function
    private_function()
  File "python2.7/site-packages/django/template/loader.py", line 186, in select_template
    raise TemplateDoesNotExist(', '.join(not_found))
TemplateDoesNotExist: none.html'''


def get_tb_lines_of_regular_ex():
    try:
        raise ValueError("test")
    except:
        exc_info = sys.exc_info()
        tb_lines = traceback.format_exception(*exc_info)
        return tb_lines


def test_is_django_exception():
    assert is_django_exception(django_tb.split('\n'))
    assert not is_django_exception(get_tb_lines_of_regular_ex())
    assert not is_django_exception(
        django_tb.replace(
            '/django/template/loader.py',
            '/django-filter/template/loader.py').
        split('\n'))


def test_clean_traceback():
    assert django_tb == clean_traceback(django_tb)


def test_clean_traceback_accepts_ex_without_message():
    tb = django_tb.replace(
        'TemplateDoesNotExist: none.html',
        'TemplateDoesNotExist')
    clean_traceback(tb)


def test_clean_traceback_removes_crs():
    django_tb_with_cr = django_tb.replace('\n', '\r\n')
    assert django_tb != django_tb_with_cr
    assert django_tb == clean_traceback(django_tb_with_cr)


def test_clean_traceback_check_if_is_django_exception():
    tb = '\n'.join(get_tb_lines_of_regular_ex())

    with pytest.raises(ValueError) as ex:
        clean_traceback(tb)
    assert 'Invalid traceback: exception not thrown by Django' in str(ex)


def test_clean_traceback_last_line_with_message():
    tb = django_tb.replace('TemplateDoesNotExist: none.html', '123456')

    with pytest.raises(ValueError) as ex:
        clean_traceback(tb)
    assert 'Malformed traceback: last line must be' in str(ex)


def test_clean_traceback_file_lines():
    tb = django_tb.replace(
        'line 139, in get_response',
        'garbage garbage')

    with pytest.raises(ValueError) as ex:
        clean_traceback(tb)
    assert 'Malformed traceback: line 2 (1-indexed)' in str(ex)

    tb = django_tb.replace(
        'File "python2.7/site-packages/django/template/response.py"',
        'garbage garbage')

    with pytest.raises(ValueError) as ex:
        clean_traceback(tb)
    assert 'Malformed traceback: line 4 (1-indexed)' in str(ex)


def test_sanitize_traceback():
    tb = sanitize_traceback(django_with_private_tb)
    assert tb == django_with_private_tb_sanitized


def test_extract_traceback_info():
    tb_info = extract_traceback_info(django_tb)
    tb_info_expected = {
        'parsed_traceback': ParsedException.from_string(django_tb).to_dict(),
        'raised_by': 'django/template/loader.py',
        'raised_by_line': 186
    }
    assert tb_info == tb_info_expected
