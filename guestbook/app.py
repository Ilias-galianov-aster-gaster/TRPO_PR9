from flask import Flask, render_template, request, redirect, session
from database import (
    init_db, get_all_messages, add_message, delete_message,
    get_message_count, delete_all_messages, check_user
)
from datetime import date

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'   # обязательно для сессий

init_db()  # создаёт таблицы, если их нет


# Форматирование дат (вывод на русском, флаг свежести)
def format_messages(messages):
    today = date.today().isoformat()
    months = {
        '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
        '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
        '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
    }
    formatted = []
    for msg in messages:
        msg_dict = dict(msg)
        raw_date = msg_dict['created_at']
        year, month, day = raw_date.split('-')
        msg_dict['created_at_ru'] = f"{int(day)} {months[month]} {year} г."
        msg_dict['is_fresh'] = (raw_date == today)
        formatted.append(msg_dict)
    return formatted


# ---------- Главная страница ----------
@app.route('/')
def index():
    messages = get_all_messages()
    total_count = get_message_count()
    return render_template('index.html',
                           messages=format_messages(messages),
                           total_count=total_count,
                           logged_in=session.get('logged_in', False),
                           username=session.get('username'))


# ---------- Добавление сообщения ----------
@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    if name and message:
        add_message(name, message)
        session['success'] = True
        return redirect('/')
    # Если поля пустые – показываем ошибку
    messages = get_all_messages()
    total_count = get_message_count()
    return render_template('index.html',
                           messages=format_messages(messages),
                           total_count=total_count,
                           error=True,
                           logged_in=session.get('logged_in', False),
                           username=session.get('username'))


# ---------- Удаление одного сообщения (только для авторизованных) ----------
@app.route('/delete/<int:message_id>')
def delete(message_id):
    if not session.get('logged_in'):
        return redirect('/login')
    delete_message(message_id)
    return redirect('/')


# ---------- Сортировка (задание А) ----------
@app.route('/sort/newest')
def sort_newest():
    from database import get_db_connection
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html',
                           messages=format_messages(messages),
                           total_count=get_message_count(),
                           logged_in=session.get('logged_in', False),
                           username=session.get('username'))

@app.route('/sort/oldest')
def sort_oldest():
    from database import get_db_connection
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at ASC').fetchall()
    conn.close()
    return render_template('index.html',
                           messages=format_messages(messages),
                           total_count=get_message_count(),
                           logged_in=session.get('logged_in', False),
                           username=session.get('username'))


# ---------- Удаление всех сообщений (задание В) ----------
@app.route('/delete-all')
def delete_all_page():
    return render_template('delete_all.html')

@app.route('/delete-all-confirm', methods=['POST'])
def delete_all_confirm():
    delete_all_messages()
    return redirect('/')


# ---------- Авторизация (задание №12) ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if check_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect('/')
        else:
            error = 'Неверный логин или пароль'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)