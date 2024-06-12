import os
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
from src import aes128
from src.entry_with_placeholder import EntryWithPlaceholder
import src.utils as utils

conn_details = './data/conn_details'
if os.path.isdir('./data'):
    pass
else:
    os.system('mkdir ./data')

window = Tk()
window.title('главное окно окно')
window.geometry('500x500')

main_label = ttk.Label()
main_button = ttk.Button(master=window)
second_label = ttk.Label()
sql_response = ttk.Label()

main_label.pack()
main_button.pack()
second_label.pack()

main = {'window':window, 'main_label':main_label, 'button':main_button, 'label':second_label, 'response':sql_response}
if os.path.exists(conn_details):
    main_label.configure(text='обнаружен файл с информацией о подключении')
    main_button.configure(text='проверка подключения', command=lambda: utils.make_connection(window, main_label, conn_details, utils.get_conn_details, main))
else:
    main_label.configure(text='файл с информацией о подключении не обнаружен')
    main_button.configure(text='подключиться к базе данных', command=lambda: utils.construct_entry_fields(conn_details, utils.ask, utils.save_conn_details, utils.convert_to_json, main))

window.mainloop()


