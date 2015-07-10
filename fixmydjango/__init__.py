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
    clean_traceback, sanitize_traceback)
from .client import search_exceptions


__version__ = '0.0.9'

original_ExceptionReporter = debug.ExceptionReporter
original_TECHNICAL_500_TEMPLATE = debug.TECHNICAL_500_TEMPLATE
original_technical_500_response = debug.technical_500_response

FIX_MY_DJANGO_MESSAGE = """
    <h2 style="color: #44B78B;">
        Fix My Django may have a solution for this exception! Check:
        <a href="{{ url }}" target="_blank">{{ url }}</a>
    </h2>
    {% if is_admin_mode %}
        <h3>
            You can add this exception as a new error by
            <a href="{{ admin_url }}" target="_blank">clicking here</a>
        </h3>
    {% endif %}
"""
FIX_MY_DJANGO_MESSAGE_PLAIN = """
    Fix My Django may have a solution for this exception! Check: {url}
""".strip()
FIX_MY_DJANGO_MESSAGE_TO_ADMIN = """
    <h2 style="color: #FF0000;">
        Hey admin, Fix My Django doesn't have this error yet! Add it by
        <a href="{admin_url}" target="_blank">clicking here</a>
    </h2>
"""
FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN = """
    Hey admin, Fix My Django doesn't have this error yet! Add it on:
    {admin_url}
""".strip()


class ExceptionReporterPatch(original_ExceptionReporter):

    def _get_fix_my_django_admin_url(self, tb_info, sanitized_tb):
        return '{url}?{query}'.format(
            url='http://www.fixmydjango.com/admin/error_posts/errorpost/add/',
            query=urlencode({
                'exception_type': tb_info['parsed_traceback']['exc_type'],
                'error_message': tb_info['parsed_traceback']['exc_msg'],
                'django_version': '{0[0]}.{0[1]}'.format(django.VERSION),
                'traceback': sanitized_tb
            }))

    def get_traceback_data(self):
        c = super(ExceptionReporterPatch, self).get_traceback_data()

        try:
            tb_lines = traceback.format_exception(self.exc_type, self.exc_value, self.tb)
            tb = '\n'.join(tb_lines)

            if is_django_exception(split_and_strip_tb_lines(tb)):
                sanitized_tb = sanitize_traceback(clean_traceback(tb))
                tb_info = extract_traceback_info(sanitized_tb)
                is_admin_mode = getattr(settings, 'FIX_MY_DJANGO_ADMIN_MODE', False)
                admin_url = self._get_fix_my_django_admin_url(
                    tb_info=tb_info,
                    sanitized_tb=sanitized_tb)

                response = search_exceptions(
                    exception_type=tb_info['parsed_traceback']['exc_type'],
                    raised_by=tb_info['raised_by'],
                    raised_by_line=tb_info['parsed_traceback']['frames'][-1]['lineno'])

                if response['error_post_list']:
                    url = response['list_url']
                    message = (
                        Template(FIX_MY_DJANGO_MESSAGE).
                        render(Context({
                            'url': url,
                            'is_admin_mode': is_admin_mode,
                            'admin_url': admin_url
                        })))

                    plain_message = FIX_MY_DJANGO_MESSAGE_PLAIN.format(url=url)
                elif is_admin_mode:
                    message = FIX_MY_DJANGO_MESSAGE_TO_ADMIN.format(
                        admin_url=admin_url)
                    plain_message = FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN.format(
                        admin_url=admin_url)
                else:
                    message = None
                    plain_message = None

                if message and plain_message:
                    c['fix_my_django_message'] = message
                    print(colored(plain_message, 'yellow'))
        except Exception:
            # TODO: allow user to report bug
            # print(traceback.format_exc())
            print(colored("oops, Fix My Django got an unexpected exception", 'red'))

        return c


def patch_technical_500_template():
    t = original_TECHNICAL_500_TEMPLATE
    index = t.index('</pre>') + len('</pre>')
    insertion = '{{ fix_my_django_message|safe }}'

    return t[:index] + insertion + t[index:]


debug.ExceptionReporter = ExceptionReporterPatch
debug.TECHNICAL_500_TEMPLATE = TECHNICAL_500_TEMPLATE_PATCH = patch_technical_500_template()
