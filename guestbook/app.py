from flask import Flask, render_template, request, redirect, session
from database import init_db, get_all_messages, add_message

app = Flask(__name__)
# ОБЯЗАТЕЛЬНО: задаём секретный ключ для работы сессий (Задание В)
app.secret_key = 'super_secret_key_123' 

init_db()


@app.route('/')
def index():
    """Главная страница: показывает все сообщения."""
    messages = get_all_messages()
    
    # --- ЗАДАНИЕ Д: Дата по-русски ---
    months = {
        '01': 'января', '02': 'февраля', '03': 'марта', '04': 'апреля',
        '05': 'мая', '06': 'июня', '07': 'июля', '08': 'августа',
        '09': 'сентября', '10': 'октября', '11': 'ноября', '12': 'декабря'
    }
    
    # Создаём новый список с преобразованными сообщениями
    formatted_messages = []
    for msg in messages:
        # Преобразуем sqlite3.Row в словарь
        msg_dict = dict(msg)
        
        # Разбиваем дату '2026-05-28' на части
        year, month, day = msg_dict['created_at'].split('-')
        
        # Создаём новую дату в русском формате
        msg_dict['created_at'] = f"{int(day)} {months[month]} {year} г."
        
        # Добавляем в новый список
        formatted_messages.append(msg_dict)
    
    return render_template('index.html', messages=formatted_messages)


@app.route('/add', methods=['POST'])
def add():
    """Обрабатывает отправку нового сообщения."""
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    # Проверяем, что оба поля не пустые
    if name and message:
        add_message(name, message)
        session['success'] = True  # Сохраняем флаг успеха
        return redirect('/')
    
    # --- ЗАДАНИЕ Г: Если поля пустые ---
    # Не делаем redirect, а возвращаем страницу с ошибкой
    # Передаём messages=get_all_messages(), чтобы список не пропал
    return render_template('index.html', messages=get_all_messages(), error=True)


if __name__ == '__main__':
    app.run(debug=True)