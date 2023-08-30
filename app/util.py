import re


def read_file(filename):
    """Read a file and return its content."""
    with open(filename, "r") as file:
        return file.read()

def check_date_format(s):
    """Check if a string matches the date format DD.MM.YY."""
    pattern = r'^\d{2}\.\d{2}\.\d{2}$'
    return bool(re.match(pattern, s))

def pt_in_2_value(value):
    """Convert pt and in values to pt."""
    suffix = value[-2:]
    core = int(value[:-2])
    if suffix == 'pt':
        return core
    elif suffix == 'in':
        return core * 72
    else:
        return ValueError

def find_all_date_y(results):
    y_positions = []
    for item in results:
        text = item['text']
        x = item['position']['margin-left']
        y = item['position']['margin-top']
        if check_date_format(text) and x >= 0 and y >= 0:
            y_positions.append(y)
            # print(text, y)

    y_positions = sorted(list(set(y_positions)))
    return y_positions