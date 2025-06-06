from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'секретный_ключ'

def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT, author TEXT, genre TEXT,
            year INTEGER, total_copies INTEGER, available_copies INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Readers (
            reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT, phone TEXT, email TEXT, registration_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Loans (
            loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER, reader_id INTEGER,
            loan_date TEXT, return_date TEXT, is_returned INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    books = conn.execute('SELECT * FROM Books').fetchall()
    return render_template("index.html", books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        year = request.form['year']
        copies = int(request.form['copies'])
        conn = get_db()
        conn.execute('''
            INSERT INTO Books (title, author, genre, year, total_copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, author, genre, year, copies, copies))
        conn.commit()
        flash('Книга добавлена!')
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/add_reader', methods=['GET', 'POST'])
def add_reader():
    if request.method == 'POST':
        name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']
        reg_date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db()
        conn.execute('''
            INSERT INTO Readers (full_name, phone, email, registration_date)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, reg_date))
        conn.commit()
        flash('Читатель зарегистрирован!')
        return redirect(url_for('index'))
    return render_template('add_reader.html')

@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        reader_id = int(request.form['reader_id'])
        conn = get_db()
        book = conn.execute("SELECT available_copies FROM Books WHERE book_id=?", (book_id,)).fetchone()
        if book and book['available_copies'] > 0:
            conn.execute('''
                INSERT INTO Loans (book_id, reader_id, loan_date, is_returned)
                VALUES (?, ?, ?, 0)
            ''', (book_id, reader_id, datetime.now().strftime('%Y-%m-%d')))
            conn.execute('''
                UPDATE Books SET available_copies = available_copies - 1 WHERE book_id=?
            ''', (book_id,))
            conn.commit()
            flash("Книга выдана.")
        else:
            flash("Нет доступных экземпляров.")
        return redirect(url_for('index'))
    return render_template('issue_book.html')

@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        loan_id = int(request.form['loan_id'])
        conn = get_db()
        loan = conn.execute("SELECT * FROM Loans WHERE loan_id=? AND is_returned=0", (loan_id,)).fetchone()
        if loan:
            conn.execute("UPDATE Loans SET is_returned=1, return_date=? WHERE loan_id=?",
                         (datetime.now().strftime('%Y-%m-%d'), loan_id))
            conn.execute("UPDATE Books SET available_copies = available_copies + 1 WHERE book_id=?",
                         (loan['book_id'],))
            conn.commit()
            flash("Книга возвращена.")
        else:
            flash("Запись не найдена или уже возвращена.")
        return redirect(url_for('index'))
    return render_template('return_book.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
