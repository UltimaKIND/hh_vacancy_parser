import psycopg2

class DBManager:
    def __init__(self, connection_details, frame, create_table):
        self.user = connection_details['login']
        self.password = connection_details['password']
        self.host = connection_details['host']
        self.port = connection_details['port']
        self.dbname = connection_details['db_name']
        self.frame = frame
        self.table = None
        self.create_table = create_table

    def connect(self):
        self.conn = psycopg2.connect(dbname=self.dbname, host=self.host, port=self.port, user=self.user, password=self.password)
        self.cursor = self.conn.cursor()

    def commit_and_close_connection(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def fill_tables(self, get_vacancies, COMPANIES_LIST):
        data = get_vacancies(COMPANIES_LIST)
        self.connect()
        vacancies = data.get('vacancies')
        companies = data.get('companies')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS companies(company_id INTEGER NOT NULL PRIMARY KEY, company_name VARCHAR(100)) ;')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS vacancies(vacancy_id INTEGER NOT NULL PRIMARY KEY, company_id INTEGER NOT NULL REFERENCES companies (company_id), vacancy_name VARCHAR(100), salary INTEGER NOT NULL, url TEXT);')
        self.cursor.execute('TRUNCATE companies CASCADE;')
        self.cursor.execute('TRUNCATE vacancies;')
        for company in companies:
            self.cursor.execute('INSERT INTO companies VALUES(%s, %s);', company)
        for vacancy in vacancies:
            self.cursor.execute('INSERT INTO vacancies VALUES(%s, %s, %s, %s, %s);', vacancy)
        self.commit_and_close_connection()

    def companies_and_vacancies_count(self):
        self.connect()

        self.cursor.execute("SELECT companies.company_name, COUNT(*) FROM companies JOIN vacancies USING(company_id) GROUP BY companies.company_name;")
        heading = ('company_name', 'Vacancies_quantity')
        data = self.cursor.fetchall()
        self.commit_and_close_connection()
        self.table = self.create_table(self.frame, data, heading, self.table)

    def get_all_vacancies(self):
        self.connect()
        self.cursor.execute("SELECT * FROM vacancies;")
        heading = ('vacancy_id', 'company_id', 'vacancy_name', 'salary', 'url')
        data = self.cursor.fetchall()
        self.commit_and_close_connection()
        self.table = self.create_table(self.frame, data, heading, self.table)

    def get_avg_salary(self):
        self.connect()
        self.cursor.execute("SELECT companies.company_name, AVG(vacancies.salary) FROM companies JOIN vacancies USING(company_id) GROUP BY companies.company_name;")
        heading = ('company_name', 'avg_salary')
        data = self.cursor.fetchall()
        self.commit_and_close_connection()
        self.table = self.create_table(self.frame, data, heading, self.table)

    def get_vacancies_with_higher_salary(self):
        self.connect()
        self.cursor.execute("SELECT * FROM vacancies WHERE salary > (SELECT AVG(salary) FROM vacancies);")
        heading = ('vacancy_id', 'company_id', 'vacancy_name', 'salary', 'url')
        data = self.cursor.fetchall()
        self.commit_and_close_connection()
        self.table = self.create_table(self.frame, data, heading, self.table)

    def get_vacancies_with_keyword(self, func):
        keyword = f"'%{func()}%'"
        self.connect()
        self.cursor.execute(f"SELECT * FROM vacancies WHERE vacancy_name LIKE({keyword});")
        heading = ('vacancy_id', 'company_id', 'vacancy_name', 'salary', 'url')
        data = self.cursor.fetchall()
        self.commit_and_close_connection()
        self.table = self.create_table(self.frame, data, heading, self.table)

        




        



