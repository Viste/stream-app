import locale

import markdown


def markdown_format(text):
    return markdown.markdown(text, extensions=['extra', 'smarty'])


def number_format(value):
    return locale.format_string("%d", value, grouping=True)
