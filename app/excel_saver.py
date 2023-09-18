import pandas as pd
from openpyxl import Workbook, load_workbook
import os

def write_df_to_excel(filename, df, serial_number, model, date):
    # Check if the file already exists
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active

    # Write individual cells in the first four rows
    ws['A1'] = 'ООО "ТД"Карелия Неруд"'
    ws['A2'] = 'Серийный номер:'
    ws['A3'] = 'Модель:'
    ws['A4'] = 'Квитанция взвешивания от:'

    ws['B4'] = date

    # Write the header (column names) starting from row 5
    for col, column_name in enumerate(df.columns):
        ws.cell(row=5, column=col + 1, value=column_name)

    # Now write the DataFrame data starting from row 6
    for index, row_data in enumerate(df.values):
        for col, data in enumerate(row_data):
            ws.cell(row=index + 6, column=col + 1, value=data)

    # Save the workbook
    wb.save(filename)

if __name__ == "__main__":
    # Example usage:
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    write_df_to_excel("your_file.xlsx", df)