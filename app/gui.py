import customtkinter as ctk
# import tkinter as tk
# from tkinter import filedialog, ttk
from customtkinter import filedialog
from main import main

FILE_PATH = ''

def select_audio_file():
    global FILE_PATH
    FILE_PATH = filedialog.askopenfilename(filetypes=[("Audio Files", "*.xml")])
    if FILE_PATH != '':
        filename_label.configure(text=FILE_PATH)  # Update the label with the filename
        audio_file_btn.configure(text='Файл выбран')
        run_btn.configure(state='normal')

def run():
    try:
        main(FILE_PATH)
        filename_label.configure(text="Готово! Выберите новый файл .xml")
        audio_file_btn.configure(text='Выбрать файл')
        
    except Exception as e:
        # If there's any error in the main function, display it on the status label
        filename_label.configure(text=f"Ошибка: {e}")

    run_btn.configure(state='disabled')

app = ctk.CTk()
app.geometry("400x160")
app.title("Трансформатор в xml в таблицу xlsx")

# Label to display the filename
filename_label = ctk.CTkLabel(app, text="Выберите файл с расширением .xml")
filename_label.pack(padx=10, pady=10,)

# Button to select an audio file
audio_file_btn = ctk.CTkButton(app, text="Выбрать файл", command=select_audio_file, )
audio_file_btn.pack(pady=10)

# Run button
run_btn = ctk.CTkButton(app, text="Запуск", command=run, fg_color='green', hover_color='dark green', state='disabled')
run_btn.pack(pady=10)

app.mainloop()
