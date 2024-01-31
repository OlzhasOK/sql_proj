import telebot
import psycopg2
from datetime import datetime, timedelta

bot_token = '6889040155:AAFTKWxZhRA6Ny6iTBHNLbd56I1_QDR1kmQ'
bot = telebot.TeleBot(bot_token)

db_params = {
    'host': 'localhost',
    'database': 'project_database',
    'user': 'PostgreSQL',
    'password': 'PostgreSQL',
    'port': '5432',

}

try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    cursor.execute('SET client_encoding = \'LATIN1\';')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reminders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            task TEXT,
            reminder_time TIMESTAMP
        )
    ''')
    conn.commit()

except Exception as connection_error:
    print(f"Ошибка при подключении к базе данных: {connection_error}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    task = message.text
    reminder_time = datetime.now() + timedelta(hours=6)  # Первое напоминание через 6 часов

    insert_query = 'INSERT INTO Reminders (user_id, task, reminder_time) VALUES (%s, %s, %s)'
    try:
        cursor.execute(insert_query, (user_id, task, reminder_time))
        conn.commit()
        print("Задача успешно добавлена в базу данных.")
        bot.send_message(message.chat.id, "Задача успешно добавлена. Я напомню вам о ней через 6, 12, 18 и 24 часа.")
    except Exception as insert_error:
        print(f"Ошибка при записи в базу данных: {insert_error}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")

def send_reminders():
    select_query = 'SELECT id, user_id, task FROM Reminders WHERE reminder_time <= %s'
    current_time = datetime.now()

    cursor.execute(select_query, (current_time,))
    reminders = cursor.fetchall()

    for reminder in reminders:
        user_id, task_id, task = reminder[1], reminder[0], reminder[2]
        bot.send_message(user_id, f"Напоминание: {task}")

        new_reminder_time = current_time + timedelta(hours=6)
        update_query = 'UPDATE Reminders SET reminder_time = %s WHERE id = %s'
        cursor.execute(update_query, (new_reminder_time, task_id))
        conn.commit()

if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as bot_error:
        print(f"Ошибка при запуске бота: {bot_error}")
    finally:
        cursor.close()
        conn.close()
