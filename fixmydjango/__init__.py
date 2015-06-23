import traceback

from django.views import debug

from termcolor import colored

from core.sanitize_tb import is_django_exception


original_ExceptionReporter = debug.ExceptionReporter
original_TECHNICAL_500_TEMPLATE = debug.TECHNICAL_500_TEMPLATE
original_technical_500_response = debug.technical_500_response

FIX_MY_DJANGO_MESSAGE = """
    Fix My Django may have a solution for this exception! Check:
    <a href="http://fixmydjango.com" target="_blank">http://fixmydjango.com</a>
"""
FIX_MY_DJANGO_MESSAGE_PLAIN = """
    Fix My Django may have a solution for this exception! Check: http://fixmydjango.com
""".strip()


class ExceptionReporterPatch(original_ExceptionReporter):

    def get_traceback_data(self):
        c = super(ExceptionReporterPatch, self).get_traceback_data()
        tb_lines = traceback.format_exception(self.exc_type, self.exc_value, self.tb)

        if is_django_exception(tb_lines):
            c['fix_my_django_message'] = FIX_MY_DJANGO_MESSAGE
        return c


def patch_technical_500_template():
    t = original_TECHNICAL_500_TEMPLATE
    index = t.index('</pre>') + len('</pre>')
    insertion = '<h2 style="color: #44B78B;">{{ fix_my_django_message|safe }}</h2>'

    return t[:index] + insertion + t[index:]

TECHNICAL_500_TEMPLATE_PATCH = patch_technical_500_template()


def technical_500_response_patch(request, exc_type, exc_value, tb, status_code=500):
    """
    Monkey patch of django.views.debug.technical_500_response
    to show Fix My Django messages.
    """
    tb_lines = traceback.format_exception(exc_type, exc_value, tb)
    if is_django_exception(tb_lines):
        print colored(FIX_MY_DJANGO_MESSAGE_PLAIN, 'yellow')

    return original_technical_500_response(request, exc_type, exc_value, tb, status_code)


debug.ExceptionReporter = ExceptionReporterPatch
debug.TECHNICAL_500_TEMPLATE = TECHNICAL_500_TEMPLATE_PATCH
debug.technical_500_response = technical_500_response_patch
