import pandas as pd
import matplotlib.pyplot as plt
import re
import xml.etree.ElementTree as ET

from xml2object import PositionExtractor
import util


def update_positions_based_on_page(results):
    # Update positions based on page number.
    unique_pages = len(set([item['page'] for item in results]))
    page_offset = 0

    for page in range(1, unique_pages + 1):
        page_data = [item for item in results if item['page'] == page]
        y_offset = min(util.find_all_date_y(page_data))

        for item in results:
            if item['page'] == page:
                item['position']['margin-top'] += -y_offset + page_offset

        page_data = [item for item in results if item['page'] == page]
        page_offset += max(util.find_all_date_y(page_data)) + 15


def plot_positions(results):
    # Plot positions on canvas.
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

    date_to_y_positions = util.find_all_date_y(results)

    x_borders = [x - 4 for x in [0, 42, 81, 120, 163,
                                 298, 331, 374, 408, 443, 485, 517, 553, 600]]
    y_borders = [y - 4 for y in [*date_to_y_positions,
                                 max(date_to_y_positions) + 15]]
    print(y_borders)

    # Draw several vertical and horizontal lines
    for x_line in x_borders:  # You can change these values to your needs
        plt.axvline(x=x_line, color='red', linestyle='--', linewidth=0.8)

    for y_line in y_borders:  # Again, adjust these values as needed
        plt.axhline(y=y_line, color='red', linestyle='--', linewidth=0.8)

    # This will make the top left corner (0,0) as is common with many graphics systems
    plt.gca().invert_yaxis()
    plt.title('Positions on Canvas')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.grid(True)
    plt.show()
    return x_borders, y_borders


def populate_dataframe(results, columns, x_borders, y_borders):
    # Populate DataFrame based on positions and borders.
    df = pd.DataFrame(columns=columns)
    print(x_borders, y_borders)

    for yi, y in enumerate(y_borders[:-1]):
        for xi, x in enumerate(x_borders[:-1]):
            cell_text = ''

            for item in results:
                ml = item['position']['margin-left']
                mt = item['position']['margin-top']

                if ml >= x and ml < x_borders[xi + 1] and mt >= y and mt < y_borders[yi + 1]:
                    cell_text += item['text'] + ' '

            cell_text = cell_text.rstrip()
            if xi < len(columns):
                column_name = columns[xi]
                if len(df) <= yi:
                    df.loc[yi] = [None] * len(columns)
                df.at[yi, column_name] = cell_text

    return df


def main():
    tree = ET.parse('../экспорт.xml')
    root = tree.getroot()

    extractor = PositionExtractor(root)
    results = extractor.extract_positions_from_xml()
    update_positions_based_on_page(results)

    columns = ["№", "Дата", "Время", "№ вагона", "Вид груза", "Груз-сть",
               "Брутто", "Тара", "Нетто", "Пр|Нд", "Скор.", "Тел. 1", "Тел. 2"]

    x_borders, y_borders = plot_positions(results)

    df = populate_dataframe(results, columns, x_borders, y_borders)

    # Save the DataFrame to Excel
    df.to_excel('output.xlsx', index=False, engine='openpyxl')
    print(df)


if __name__ == "__main__":
    main()
