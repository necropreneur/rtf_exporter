import pandas as pd
# import matplotlib.pyplot as plt
import os
import xml.etree.ElementTree as ET
import re

from .xml2object import PositionExtractor
from .util import find_all_date_y
from .df_fixer import fix_dataframe
from .excel_saver import write_df_to_excel

COLUMNS = ["№", "Дата", "Время", "№ вагона", "Вид груза", "Груз-сть",
               "Брутто", "Тара", "Нетто", "Пр|Нд", "Скор.", "Тел. 1", "Тел. 2"]
COLUMNS_TO_FIX = ["№ вагона", "Вид груза"]

def update_positions_based_on_page(results):
    # Update positions based on page number.
    unique_pages = len(set([item['page'] for item in results]))
    page_offset = 0

    for page in range(1, unique_pages + 1):
        page_data = [item for item in results if item['page'] == page]
        date_y_values = find_all_date_y(page_data)
        if not date_y_values:  # Check if the list is empty
            continue
        y_offset = min(date_y_values)

        for item in results:
            if item['page'] == page:
                item['position']['margin-top'] += -y_offset + page_offset

        page_data = [item for item in results if item['page'] == page]
        page_offset += max(find_all_date_y(page_data)) + 15


# def draw_plot(results, x_borders, y_borders):
#     # Plot positions on canvas.
#     plt.figure(figsize=(10, 10))

#     for item in results:
#         x = item['position']['margin-left']
#         y = item['position']['margin-top']
#         if item['page'] == 1:
#             plt.scatter(x, y, color='blue')
#         elif item['page'] == 2:
#             plt.scatter(x, y, color='green')

#     # Draw several vertical and horizontal lines
#     for x_line in x_borders:  # You can change these values to your needs
#         plt.axvline(x=x_line, color='red', linestyle='--', linewidth=0.8)

#     for y_line in y_borders:  # Again, adjust these values as needed
#         plt.axhline(y=y_line, color='red', linestyle='--', linewidth=0.8)

#     # This will make the top left corner (0,0) as is common with many graphics systems
#     plt.gca().invert_yaxis()
#     plt.title('Positions on Canvas')
#     plt.xlabel('X Coordinate')
#     plt.ylabel('Y Coordinate')
#     plt.grid(True)
#     plt.show()

def get_borders(results):
    date_to_y_positions = find_all_date_y(results)

    x_borders = [x - 4 for x in [0, 42, 81, 120, 163,
                                 294, 331, 366, 400, 439, 485, 517, 553, 600]]
    y_borders = [y - 4 for y in [*date_to_y_positions,
                                 max(date_to_y_positions) + 15]]
    return x_borders, y_borders


def populate_dataframe(results, x_borders, y_borders):
    # Populate DataFrame based on positions and borders.
    global COLUMNS
    df = pd.DataFrame(columns=COLUMNS)
    # print(x_borders, y_borders)

    for yi, y in enumerate(y_borders[:-1]):
        for xi, x in enumerate(x_borders[:-1]):
            cell_text = ''

            for item in results:
                ml = item['position']['margin-left']
                mt = item['position']['margin-top']

                if ml >= x and ml < x_borders[xi + 1] and mt >= y and mt < y_borders[yi + 1]:
                    cell_text += item['text'] + ' '

            cell_text = cell_text.rstrip()
            if xi < len(COLUMNS):
                column_name = COLUMNS[xi]
                if len(df) <= yi:
                    df.loc[yi] = [None] * len(COLUMNS)
                df.at[yi, column_name] = cell_text

    return df


def extract_date_from_xml(file_path: str) -> str:
    # Parse the XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define the regular expression pattern for extracting the date and time
    pattern = r"Квитанция взвешивания от (\d{2}.\d{2}.\d{2} \d{2}:\d{2})"

    for elem in root.iter():
        if elem.tag.endswith("t") and elem.text:  # Check that <w:t> has text content
            match = re.search(pattern, elem.text)
            if match:
                date_str = match.group(1)
                return date_str  # Return the date

    return ''  # In case no date is found

# def extract_operator_from_xml(file_path: str) -> None:
#     # Parse the XML
#     tree = ET.parse(file_path)
#     root = tree.getroot()

#     for elem in root.iter():
#         if elem.tag.endswith("t") and elem.text:  # Check that <w:t> has text content
#             if "Оператор:" in elem.text:
#                 print(elem.text)
#                 break
#             print(elem.text)

def extract_operator_from_xml(file_path: str) -> None:
    # Parse the XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    operator_found = False
    next_elements = []
    
    # Iterate through elements to find the "Оператор:" text and collect next 2 elements
    for elem in root.iter():
        if elem.tag.endswith("t") and elem.text: 
            if operator_found and len(next_elements) < 2:
                next_elements.append(elem.text.strip())
            if elem.text == "Оператор:":
                operator_found = True
    
    # Check collected elements
    # print(f"Collected elements after 'Оператор:': {next_elements}")
    
    # Validate using regex and print if correct
    if len(next_elements) == 2:
        name_pattern = re.compile(r'^\w+$')
        initials_pattern = re.compile(r'^[А-Яа-я]\.[А-Яа-я]\.$')
        
        if name_pattern.match(next_elements[0]) and initials_pattern.match(next_elements[1]):
            # print("Name:", next_elements[0].strip())
            # print("Initials:", next_elements[1].strip())
            return f"{next_elements[0].strip()} {next_elements[1].strip()}"
        else:
            # print("Pattern didn't match for the next elements after 'Оператор:'")
            return ""



def main(file_path: str):
    tree = ET.parse(file_path)
    root = tree.getroot()

    extractor = PositionExtractor(root)
    results = extractor.extract_positions_from_xml()
    update_positions_based_on_page(results)

    x_borders, y_borders = get_borders(results)

    # draw_plot(results, x_borders, y_borders)

    df = populate_dataframe(results, x_borders, y_borders)

    df = fix_dataframe(df, COLUMNS_TO_FIX)

    # Modify the output filename based on the input file_path
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(os.path.dirname(file_path), base_name + ".xlsx")

    company = 'ООО "ТД"Карелия Неруд"'
    serial_number = '16262'
    model = 'ДО-150Т-1(0,56)-100'
    date = extract_date_from_xml(file_path)
    operator = extract_operator_from_xml(file_path)

    write_df_to_excel(output_path, df, company, serial_number, model, date, operator)


if __name__ == "__main__":
    main('../files/экспорт.xml')
