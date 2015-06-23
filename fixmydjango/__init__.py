__version__ = '0.0.4'

import traceback

from django.views import debug

from termcolor import colored

from .sanitize_tb import is_django_exception, extract_traceback_info, clean_traceback, sanitize_traceback
from .client import search_exceptions


original_ExceptionReporter = debug.ExceptionReporter
original_TECHNICAL_500_TEMPLATE = debug.TECHNICAL_500_TEMPLATE
original_technical_500_response = debug.technical_500_response

FIX_MY_DJANGO_MESSAGE = """
    <h2 style="color: #44B78B;">
        Fix My Django may have a solution for this exception! Check:
        <a href="{url}" target="_blank">{url}</a>
    </h2>
"""
FIX_MY_DJANGO_MESSAGE_PLAIN = """
    Fix My Django may have a solution for this exception! Check: {url}
""".strip()
FIX_MY_DJANGO_MESSAGE_TO_ADMIN = """
    <h2 style="color: #FF0000;">
        Hey admin, Fix My Django doesn't have this error yet! Go add it in
        <a href="http://www.fixmydjango.com/admin/error_posts/errorpost/add/" target="_blank">
        http://www.fixmydjango.com/admin/error_posts/errorpost/add/</a>
    </h2>
"""
FIX_MY_DJANGO_MESSAGE_TO_ADMIN_PLAIN = """
    Fix My Django may have a solution for this exception! Check:
    http://www.fixmydjango.com/admin/error_posts/errorpost/add/
""".strip()


class ExceptionReporterPatch(original_ExceptionReporter):

    def get_traceback_data(self):
        c = super(ExceptionReporterPatch, self).get_traceback_data()

        try:
            tb_lines = traceback.format_exception(self.exc_type, self.exc_value, self.tb)

            if is_django_exception(tb_lines):
                sanitized_tb = sanitize_traceback(clean_traceback('\n'.join(tb_lines)))
                tb_info = extract_traceback_info(sanitized_tb)

                response = search_exceptions(
                    exception_type=tb_info['parsed_traceback']['exc_type'],
                    raised_by=tb_info['raised_by'])

                if len(response):
                    message = FIX_MY_DJANGO_MESSAGE.format(
                        url=response[0]['url'])
                else:
                    message = FIX_MY_DJANGO_MESSAGE_TO_ADMIN

                c['fix_my_django_message'] = message

                plain_message = FIX_MY_DJANGO_MESSAGE_PLAIN.format(
                    url=response[0]['url'])
                print colored(plain_message, 'yellow')
        except Exception:
            # TODO: allow user to report bug
            print colored("oops, Fix My Django got an unexpected exception", 'red')

        return c


def patch_technical_500_template():
    t = original_TECHNICAL_500_TEMPLATE
    index = t.index('</pre>') + len('</pre>')
    insertion = '{{ fix_my_django_message|safe }}'

    return t[:index] + insertion + t[index:]

TECHNICAL_500_TEMPLATE_PATCH = patch_technical_500_template()


# def technical_500_response_patch(request, exc_type, exc_value, tb, status_code=500):
#     """
#     Monkey patch of django.views.debug.technical_500_response
#     to show Fix My Django messages.
#     """
#     tb_lines = traceback.format_exception(exc_type, exc_value, tb)
#     if is_django_exception(tb_lines):
#         message = FIX_MY_DJANGO_MESSAGE_PLAIN.format(
#             url='http://fixmydjango.com')
#         print colored(message, 'yellow')

#     return original_technical_500_response(request, exc_type, exc_value, tb, status_code)


debug.ExceptionReporter = ExceptionReporterPatch
debug.TECHNICAL_500_TEMPLATE = TECHNICAL_500_TEMPLATE_PATCH
#debug.technical_500_response = technical_500_response_patch
