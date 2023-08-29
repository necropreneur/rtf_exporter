import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
import xml.etree.ElementTree as ET
import re

# Read the contents of the file


def check_date_format(s):
    pattern = r'^\d{2}\.\d{2}\.\d{2}$'
    return bool(re.match(pattern, s))


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

# print(find_all_date_y())


def pt_in_2_value(value: str) -> int:
    suffix = value[-2:]
    core = int(value[:-2])
    if suffix == 'pt':
        return core
    elif suffix == 'in':
        return core * 72
    else:
        return ValueError


# Read the contents of the file
with open("clear_position.txt", "r") as file:
    data = file.read()

# Find all the y-positions corresponding to dates in the specified format
date_pattern = r'(\d{2}\.\d{2}\.\d{2})\s+Position: \d+pt (\d+\.?\d*)pt'
matches = re.findall(date_pattern, data)

# Grouping y-positions by date
date_to_y_positions = []
for date, y in matches:
    date_to_y_positions.append(float(y))
date_to_y_positions = sorted(list(set(date_to_y_positions)))
print(date_to_y_positions)


# Parse the XML
tree = ET.parse('экспорт.xml')
root = tree.getroot()

# Define the XML namespaces used in your XML
namespaces = {
    'v': 'urn:schemas-microsoft-com:vml',
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

WRITE = False
# min_y = min(find_all_date_y(results))
# print(min_y)
# y_offset = min_y
page = 0
# Iterate over the text boxes in the XML and extract position and text
results = []
for rect in root.findall(".//v:rect", namespaces):
    style = rect.get('style')
    # Extract position data from style attribute
    position_data = {}
    for pair in style.split(';'):
        name, _, value = pair.partition(':')
        position_data[name] = value

    # Get text data
    text_content = rect.find(".//w:t", namespaces)
    if text_content is not None:
        text = text_content.text

        if 'Страница' in text:
            WRITE = False
            # reset this result y values to start from 0 by finding the smallest y and subtracting it from every y value
            # add y_offset ()
            # min_y = min(find_all_date_y(results))
            # print(min_y)
            # y_offset = min_y

        if WRITE:
            ml = pt_in_2_value(position_data['margin-left'])
            mt = pt_in_2_value(position_data['margin-top'])
            w = pt_in_2_value(position_data['width'])
            h = pt_in_2_value(position_data['height'])

            if not (ml >= 0 and mt >= 0 and w >= 0 and h >= 0):
                continue

            position = {'margin-left': ml,
                        'margin-top': mt,
                        'width': w,
                        'height': h}

            results.append({
                'text': text,
                'position': position,
                'page': page
            })

        if text == ' 2':
            WRITE = True
            page += 1

# Print the results
results_backup = deepcopy(results)
for item in results:
    print(item['text'])
    print("Position:", item['position']['margin-left'],
          item['position']['margin-top'], item['page'])


unique_pages = len(set([item['page'] for item in results]))

page_offset = 0

for page in list(range(1, unique_pages+1)):
    page_data = [item for item in results if item['page'] == page]
    all_date_y = find_all_date_y(page_data)
    y_offset = min(all_date_y)

    for item in results:
        if item['page'] == page:
            item['position']['margin-top'] += -y_offset + page_offset

    page_data = [item for item in results if item['page'] == page]
    all_date_y = find_all_date_y(page_data)
    page_offset += max(all_date_y)+15

# Print the results
for item in results:
    print(item['text'])
    print("Position:", item['position']['margin-left'],
          item['position']['margin-top'], item['page'])


# Split the x and y coordinates
# x_coords = [float(x) for x, _ in positions]
# y_coords = [float(y) for _, y in positions]

# Normalize if necessary (depending on the size of your canvas and the range of your coordinates)
# Here, as an example, I'm multiplying by a factor for visualization. Adjust as needed.
x_coords = [item['position']['margin-left'] for item in results]
y_coords = [item['position']['margin-top'] for item in results]

plt.figure(figsize=(10, 10))
# plt.scatter(x_coords, y_coords)
# Plot points with color based on 'page'
for item in results:
    x = item['position']['margin-left']
    y = item['position']['margin-top']
    if item['page'] == 1:
        plt.scatter(x, y, color='blue')
    elif item['page'] == 2:
        plt.scatter(x, y, color='green')

date_to_y_positions = find_all_date_y(results)

x_borders = [x - 4 for x in [0, 42, 81, 120, 163,
                             298, 331, 374, 408, 443, 485, 517, 553, 600]]
y_borders = [*date_to_y_positions, max(date_to_y_positions) + 15]
print(y_borders)

# Draw several vertical and horizontal lines
for x_line in x_borders:  # You can change these values to your needs
    plt.axvline(x=x_line, color='red', linestyle='--', linewidth=0.8)

for y_line in y_borders:  # Again, adjust these values as needed
    plt.axhline(y=y_line, color='red', linestyle='--', linewidth=0.8)


# Set x-axis limits
# plt.xlim(0, 25)

# This will make the top left corner (0,0) as is common with many graphics systems
plt.gca().invert_yaxis()
plt.title('Positions on Canvas')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.grid(True)
plt.show()


# List of desired column names
columns = ["№", "Дата", "Время", "№ вагона", "Вид груза", "Груз-сть",
           "Брутто", "Тара", "Нетто", "Пр|Нд", "Скор.", "Тел. 1", "Тел. 2"]
# Create an empty DataFrame with desired column names
df = pd.DataFrame(columns=columns)

# Assuming y_borders and x_borders are defined elsewhere
# Assuming results is defined elsewhere

for yi, y in enumerate(y_borders[:-1]):
    for xi, x in enumerate(x_borders[:-1]):
        # Initialize an empty string to collect all item texts within the cell
        cell_text = ''

        for item in results:
            ml = item['position']['margin-left']
            mt = item['position']['margin-top']

            if ml >= x and ml < x_borders[xi+1] and mt >= y and mt < y_borders[yi+1]:
                # Concatenate item text to the cell_text
                cell_text += item['text'] + ' '

        # Remove trailing space
        cell_text = cell_text.rstrip()

        # Update DataFrame cell at (yi, xi) with the cell_text
        if xi < len(columns):
            column_name = columns[xi]
            if len(df) <= yi:
                df.loc[yi] = [None] * len(columns)  # Add a new row if required
            df.at[yi, column_name] = cell_text

# Show the DataFrame
df
