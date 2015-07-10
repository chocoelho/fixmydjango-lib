from django.template import Template, Context


def format_template(tmpl_str, context):
    return (Template(tmpl_str).
            render(Context(context))).encode('utf-8')
