from flask import Flask, render_template, request, redirect, session
from database import (
    init_db, get_all_messages, add_message, 
    delete_message, get_message_count, delete_all_messages
)
from datetime import date


app = Flask(__name__)
app.secret_key = 'super_secret_key_123' 

init_db()


# Вспомогательная функция, чтобы не дублировать код форматирования дат
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
        # Сохраняем русскую дату для отображения
        msg_dict['created_at_ru'] = f"{int(day)} {months[month]} {year} г."
        # Сохраняем флаг свежести для CSS-класса (Задание Б)
        msg_dict['is_fresh'] = (raw_date == today)
        formatted.append(msg_dict)
    return formatted


@app.route('/')
def index():
    messages = get_all_messages()
    total_count = get_message_count()
    return render_template('index.html', messages=format_messages(messages), total_count=total_count)


@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    

    if name and message:
        add_message(name, message)
        session['success'] = True
        return redirect('/')
    

    # Задание Г: Возвращаем страницу с ошибкой, сохраняя список сообщений
    messages = get_all_messages()
    total_count = get_message_count()
    return render_template('index.html', messages=format_messages(messages), total_count=total_count, error=True)


@app.route('/delete/<int:message_id>')
def delete(message_id):
    delete_message(message_id)
    return redirect('/')


# --- ЗАДАНИЕ А: Сортировка по дате ---
@app.route('/sort/newest')
def sort_newest():
    from database import get_db_connection
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', messages=format_messages(messages), total_count=get_message_count())


@app.route('/sort/oldest')
def sort_oldest():
    from database import get_db_connection
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at ASC').fetchall()
    conn.close()
    return render_template('index.html', messages=format_messages(messages), total_count=get_message_count())


# --- ЗАДАНИЕ В: Удаление всех сообщений ---
@app.route('/delete-all')
def delete_all_page():
    return render_template('delete_all.html')


@app.route('/delete-all-confirm', methods=['POST'])
def delete_all_confirm():
    delete_all_messages()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)