import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def number_format(value):
    return locale.format_string("%d", value, grouping=True)
