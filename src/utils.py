from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
import src.aes128
import json, os, requests
import psycopg2
from src.entry_with_placeholder import EntryWithPlaceholder
from src.db_manager import DBManager

COMPANIES_LIST = [{'name': 'Альфа-банк', 'id': '80'}, 
        {'name': 'Т-банк', 'id': '78638'},
        {'name': 'БАНК УРАЛСИБ', 'id': '89'},
        {'name': 'Почта банк', 'id': '1049556'},
        {'name': 'СБЕР', 'id': '3529'},
        {'name': 'Газпромбанк', 'id': '3388'},
        {'name': 'Центральный банк Российской Федерации', 'id': '47858'},
        {'name': 'ОТП банк', 'id': '4394'},
        {'name': 'Банк ВТБ', 'id': '4181'},
        {'name': 'МТС Финтех', 'id': '4496'}]

def get_vacancies_from(companies_list):
    '''
    получает списки компаний и их вакансий
    '''
    url = 'https://api.hh.ru/employers'
    headers = {'User-Agent': 'HH-User_Agent'}
    params = {'page': 0, 'per_page':100}
    params_v = {'page': 0, 'per_page': 100, 'only_with_salary': True} 
    companies = []
    vacancies = []
    for company in companies_list:
        vacancies_list = []
        response = requests.get(f'{url}/{company.get("id")}', headers=headers, params=params)
        founded_company = response.json()
        company_data = [int(founded_company.get('id')), founded_company.get('name')]
        companies.append(company_data)
        response = requests.get(founded_company.get('vacancies_url'), headers=headers, params=params_v)
        founded_vacancies = response.json().get('items')
        vacancies_data = []
        for vacancy in founded_vacancies:
            if vacancy['salary']['from'] is None:
                salary = int(vacancy['salary']['to'])
            else:
                salary = int(vacancy['salary']['from'])

                vacancies_data.append([int(vacancy.get('id')),
                                   int(vacancy.get('employer').get('id')),
                                   vacancy.get('name'),
                                   salary,
                                   vacancy.get('alternate_url')])

        vacancies.extend(vacancies_data)
    return {'companies': companies, 'vacancies': vacancies}

def create_table(frame, data, heading, table):
    '''
    создает таблицу в окне
    '''
    if table is not None:
        table.destroy()
    columns = heading
    tree = ttk.Treeview(frame, columns=columns, show='headings')
    tree.pack(fill=BOTH, expand=1)
    for element in columns:
        tree.heading(element, text=element, anchor=W)
    
    for value in data:
        tree.insert("", END, values=value)
    return tree
        
def save_conn_details(conn_details, key, path):
    '''
    шифрует и сохраняет данные подключения
    '''
    data = conn_details
    blocks = []
    while data:
        if len(data)>16:
            blocks.append([ord(symbol) for symbol in list(data[:16])])
            data = data[16:]
        elif len(data) == 16:
                blocks.append([ord(symbol) for symbol in list(data)])
                data = []
        else:
            rest = 16 - len(data)
            piece = [0] * rest
            piece[0] = 1
            blocks.append([ord(symbol) for symbol in list(data[:])])
            blocks[-1].extend(piece)
            break
    chiper = []
    for block in blocks:
        chiper.extend(src.aes128.encrypt(block, key))
    binary = []
    for symbol in chiper:
        bin_formated = format(symbol, 'b')
        if len(bin_formated) == 8:
            binary += bin_formated
        else:
            rest = 8 - len(bin_formated)
            binary += (rest*'0') + (bin_formated)
            
    with open(path, 'w') as f:
        f.writelines(binary)

def get_conn_details(key, path):
    '''
    читает и дешифрует данные подключения
    '''
    data = None
    with open(path, 'r') as f:
        data = f.read()
    encrypted_symbols = []
    while True:
        if len(data) > 8:
            encrypted_symbols.append(int(data[:8], base=2))
            data = data[8:]
        else:
            encrypted_symbols.append(int(data[:], base=2))
            break
    blocks = []
    while True:
        if len(encrypted_symbols) > 16:
            blocks.append(encrypted_symbols[:16])
            encrypted_symbols = encrypted_symbols[16:]
        else:
            blocks.append(encrypted_symbols[:])
            break
    message = []
    for block in blocks:
        message.extend(src.aes128.decrypt(block, key))
    while True:
        if message[-1] == 1:
            message.pop()
            break
        message.pop()
    message = ''.join(map(chr, message))

    return message
    
def convert_to_json(data):
    '''
    конвертирует в json
    '''
    result = {}
    for key, value in data.items():
        result[key] = value.get()
    return json.dumps(result)

def convert_from_json(data):
    '''
    конвертирует из json
    '''
    return json.loads(data)

def ask(entry_window, data, conn_details, func, convert_func, main):
    '''
    запрашивает ключ
    '''
    keyword = askstring('keyword', 'enter a keyword', show='*', parent=entry_window)
    func(convert_func(data), keyword, conn_details)
    main['main_label'].configure(text='создан файл конфигурации подключения')
    main['button'].configure(text='подключиться к базе данных', command=lambda:make_connection(main['window'], main['label'], conn_details, get_conn_details, main)) 
    entry_window.destroy()

def ask_keyword():
    '''
    запрашивает поисковой запрос
    '''
    keyword = askstring('ключевое слово', 'поиск по ключевому слову')
    return keyword

def make_connection(window, label, conn_details, func, main):
    '''
    создает подключение
    '''
    keyword = askstring('keyword', 'enter a keyword', show='*', parent=window)
    con_details = convert_from_json(func(keyword, conn_details))
    try:
        label.configure(text = 'соединение с базой данных установлено')
        
        main['button'].destroy()
        main['window'].wm_attributes('-fullscreen', True)
        frame_button = ttk.Frame(master=main['window'], borderwidth=1,relief=SOLID, padding=[10, 10])
        frame_table = ttk.Frame(master=main['window'], borderwidth=1, relief=SOLID, padding=[10, 10])
        db_manager = DBManager(con_details, frame_table, create_table) 
        
        BUTTON_COMMANDS = [{'command':(lambda:db_manager.fill_tables(get_vacancies_from, COMPANIES_LIST)), 'text': 'наполнить таблицы'},
        {'command':(lambda:db_manager.companies_and_vacancies_count()), 'text': 'вывести все компании и количество вакансий'}, 
        {'command':(lambda:db_manager.get_all_vacancies()), 'text': 'вывести вакансии'}, 
        {'command':(lambda:db_manager.get_avg_salary()), 'text': 'вывести среднюю зарплату'},
        {'command':(lambda:db_manager.get_vacancies_with_higher_salary()), 'text': 'зарплата выше средней'},
        {'command':(lambda:db_manager.get_vacancies_with_keyword(ask_keyword)), 'text': 'поиск в названии'},
        {'command':(lambda:exit()), 'text': 'закрыть'} ]
        frame_button.pack(fill=X,)
        frame_table.pack(fill=X)
        for c in range(7):

            button = ttk.Button(frame_button, text=BUTTON_COMMANDS[c].get('text'), command=BUTTON_COMMANDS[c].get('command'))
            button.grid(row=0, column=c)
        for c in range(10):
            frame_button.columnconfigure(index=c, weight=1)

    except Exception as e:
        label.configure(text = e)

def construct_entry_fields(conn_details, ask, func, convert_func, main):
    '''
    создает окно с полями ввода
    '''
    entry_window = Tk()
    entry_window.title('подключение к базе данных')
    entry_window.geometry('300x300')
    fields = ['login', 'password', 'host', 'port', 'db_name']
    entry_fields = {}
    for c in range(3):
        if c == 1:
            for n, field in enumerate(fields):
                if field == 'password':
                    entry_fields[field] = EntryWithPlaceholder(entry_window, field, show='*')
                    entry_fields[field].grid(row=n, column=c, pady=[10, 0])
                else:
                    entry_fields[field] = EntryWithPlaceholder(entry_window, field)
                    entry_fields[field].grid(row=n, column=c, pady=[10, 0])

            button = ttk.Button(master=entry_window, text='Погнали', command=lambda: ask(entry_window, entry_fields, conn_details, func, convert_func, main))
            button.grid(row=5, column=c, pady=20)

    entry_window.columnconfigure(index=1, weight=1)

def check_connection(conn_details, path):
    '''
    проверка подключения
    '''
    if os.path.exists(conn_details):
        return get_conn_details(conn_details, path)
        

