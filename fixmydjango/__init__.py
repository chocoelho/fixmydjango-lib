from __future__ import print_function, unicode_literals

import traceback

import django
from django.views import debug
from django.utils.http import urlencode
from django.conf import settings
from django.template import Template, Context

from termcolor import colored

from .sanitize_tb import (
    is_django_exception, split_and_strip_tb_lines, extract_traceback_info,
    clean_traceback, sanitize_traceback, clean_exception_type)
from .client import search_exceptions


__version__ = '0.3'

original_ExceptionReporter = debug.ExceptionReporter
original_TECHNICAL_500_TEMPLATE = debug.TECHNICAL_500_TEMPLATE
original_technical_500_response = debug.technical_500_response

FIX_MY_DJANGO_MESSAGE = """
    <h2 style="color: #44B78B;">FixMyDjango might have a solution for this error!</h2>
    {% for error in errors %}
        <h3>Django {{ error.django_version }}</h3>
        {% for answer in error.answers %}
            <b>Answer {{ forloop.counter }}</b>
            <pre>{{ answer.message }}</pre>
        {% endfor %}
    {% endfor %}

    <h3 style="display: block;">
        If none of this works, <a style="margin: 0; padding: 0;" href="{{ submission_url }}">click here</a> to request help.
        Or <a style="margin: 0; padding: 0;" href="{{ url }}" target="_blank">here</a> to add a missing answer.
    </h3>
"""
FIX_MY_DJANGO_MESSAGE_PLAIN = """
    Fix My Django may have a solution for this exception! Check: {url}
""".strip()
FIX_MY_DJANGO_MESSAGE_TO_ADMIN = """
    <h2 style="color: #FF0000;">We could not find a solution for this error in FixMyDjango</h2>
    <h3><a href="{submission_url}" target="_blank">Click here</a> request help or just add the error!<h2>
"""
FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN = """
    Hey, Fix My Django doesn't have this error yet! Add it on: {submission_url}
""".strip()
FIX_MY_DJANGO_OOPS_MESSAGE = "oops, Fix My Django got an unexpected exception"


base_url = getattr(
    settings,
    'FIX_MY_DJANGO_API_BASE_URL',
    'http://www.fixmydjango.com'
)


class ExceptionReporterPatch(original_ExceptionReporter):

    def _get_fix_my_django_submission_url(self, tb_info, sanitized_tb):
        """
        Links to the error submission url with pre filled fields
        """
        err_post_create_path = '/create/'
        url = '{0}{1}'.format(base_url, err_post_create_path)
        return '{url}?{query}'.format(
            url=url,
            query=urlencode({
                'exception_type': clean_exception_type(tb_info['parsed_traceback']['exc_type']),
                'error_message': tb_info['parsed_traceback']['exc_msg'],
                'django_version': '{0[0]}.{0[1]}'.format(django.VERSION),
                'traceback': sanitized_tb
            }))

    def best_matching_version(self, error_data):
        errors = error_data.get('error_post_list')

        index = -1
        for error in errors:
            index += 1
            version = error.get('django_version')
            if version == django.VERSION:
                break

        e = errors.pop(index)
        errors.insert(0, e)

        return errors

    def get_traceback_data(self):
        c = super(ExceptionReporterPatch, self).get_traceback_data()
        is_admin_mode = getattr(settings, 'FIX_MY_DJANGO_ADMIN_MODE', False)

        try:
            tb_lines = traceback.format_exception(self.exc_type, self.exc_value, self.tb)
            tb = '\n'.join(tb_lines)

            if is_django_exception(split_and_strip_tb_lines(tb)):
                sanitized_tb = sanitize_traceback(clean_traceback(tb))
                tb_info = extract_traceback_info(sanitized_tb)
                submission_url = self._get_fix_my_django_submission_url(
                    tb_info=tb_info,
                    sanitized_tb=sanitized_tb)

                response = search_exceptions(
                    exception_type=clean_exception_type(tb_info['parsed_traceback']['exc_type']),
                    raised_by=tb_info['raised_by'],
                    raised_by_line=tb_info['parsed_traceback']['frames'][-1]['lineno'])

                if response['error_post_list']:
                    url = response['list_url']
                    message = (
                        Template(FIX_MY_DJANGO_MESSAGE).
                        render(Context({
                            'url': url,
                            'errors': self.best_matching_version(response),
                            'submission_url': submission_url
                        })))

                    plain_message = FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=url)
                else:
                    message = FIX_MY_DJANGO_MESSAGE_TO_ADMIN.format(
                        submission_url=submission_url)
                    plain_message = FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN.format(
                        submission_url=submission_url)

                c['fix_my_django_message'] = message
                print(colored(plain_message, 'yellow'))
        except Exception:
            if is_admin_mode:
                print(traceback.format_exc())
            print(colored(FIX_MY_DJANGO_OOPS_MESSAGE, 'red'))

        return c


def patch_technical_500_template():
    t = original_TECHNICAL_500_TEMPLATE

    insertion = '{{ fix_my_django_message|safe }}'
    html = t.split('</div>')
    html.insert(1, insertion)

    return '</div>'.join(html)


debug.ExceptionReporter = ExceptionReporterPatch
debug.TECHNICAL_500_TEMPLATE = TECHNICAL_500_TEMPLATE_PATCH = patch_technical_500_template()
