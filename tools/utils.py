import locale

def number_format(value):
    return locale.format_string("%d", value, grouping=True)
