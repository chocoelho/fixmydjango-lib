import re

from boltons.tbutils import ParsedException

_exception_re = re.compile(r'^([^\d\W][\w\.]*)+(: .*)?$')
_file_line_re_text = r'^File \".+\", line \d+, in .+$'
_file_line_re = re.compile(_file_line_re_text)


def split_and_strip_tb_lines(tb):
    # remove \r
    tb = tb.replace('\r', '')

    # remove empty lines
    tb_lines = [line for line in tb.split('\n')
                if line.strip()]

    return tb_lines


def is_django_exception(tb_lines):
    last_file_line = tb_lines[-3]
    django_index = last_file_line.find('/django/')
    return django_index != -1


def clean_traceback(tb):
    tb_lines = split_and_strip_tb_lines(tb)

    first_line_should_be = 'Traceback (most recent call last):'

    if first_line_should_be not in tb_lines:
        raise ValueError(
            "Malformed traceback: first line must be "
            "exactly equal to '{}' "
            "(no spaces around)".format(first_line_should_be))

    first_line_index = len(tb_lines) - tb_lines[::-1].index(first_line_should_be) - 1
    tb_lines = tb_lines[first_line_index:]

    last_line = tb_lines[-1] = tb_lines[-1].lstrip()
    exception_re_match = _exception_re.match(last_line)
    if not exception_re_match:
        raise ValueError(
            "Malformed traceback: last line must be "
            "exception type and message")

    file_lines = tb_lines[1:-1:2]

    for i, line in enumerate(file_lines):
        if not _file_line_re.match(line.strip()):
            raise ValueError(
                "Malformed traceback: line {} (1-indexed) "
                "doesn't matches regex {}".format(i * 2 + 2,
                                                  _file_line_re_text))

    if not is_django_exception(tb_lines):
        raise ValueError(
            "Invalid traceback: exception not thrown by Django")

    # try to parse
    tb = '\n'.join(tb_lines)
    ParsedException.from_string(tb)
    return tb


def sanitize_traceback(clean_tb):
    tb_sanitized_splitted = []
    file_re = re.compile(
        r'File \".+\",')
    deps_file_re = re.compile(
        r'File \".*((?:python.+)+?.+site-packages.+)\",')
    line_number_re = re.compile(
        r'line \d+, in .+')
    prev_line_was_pvt_file = False

    for tb_line in clean_tb.split('\n'):
        if not prev_line_was_pvt_file:
            file_re_match = file_re.search(tb_line)

            if file_re_match:
                deps_file_re_match = deps_file_re.search(tb_line)

                if deps_file_re_match:
                    prev_line_was_pvt_file = False
                    tb_line = deps_file_re.sub(
                        r'File "\1",',
                        tb_line)
                else:
                    prev_line_was_pvt_file = True
                    tb_line = file_re.sub(
                        'File "private.py",',
                        tb_line)
                    tb_line = line_number_re.sub(
                        'line 1, in private_function',
                        tb_line)
        else:  # prev_line_was_pvt_file
            prev_line_was_pvt_file = False
            tb_line = re.sub(
                r'(\s+).+',
                r'\1private_function()',
                tb_line)

        tb_sanitized_splitted.append(tb_line)

    return '\n'.join(tb_sanitized_splitted)


def extract_traceback_info(tb):
    parsed_traceback = ParsedException.from_string(tb).to_dict()
    last_frame = parsed_traceback['frames'][-1]
    last_frame_filepath = last_frame['filepath']

    return {
        'parsed_traceback': parsed_traceback,
        'raised_by': last_frame_filepath[last_frame_filepath.index('django/'):],
        'raised_by_line': int(last_frame['lineno'])
    }


def clean_exception_type(exception):
    return exception.split('.')[-1]
