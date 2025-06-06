import sqlite3

def get_connection():
    return sqlite3.connect("library.db")

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, author TEXT, genre TEXT,
            year INTEGER, total_copies INTEGER, available_copies INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Readers (
            reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT, phone TEXT, email TEXT, registration_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER, reader_id INTEGER,
            loan_date TEXT, return_date TEXT, is_returned INTEGER,
            FOREIGN KEY(book_id) REFERENCES Books(book_id),
            FOREIGN KEY(reader_id) REFERENCES Readers(reader_id)
        )
    ''')

    conn.commit()
    conn.close()
