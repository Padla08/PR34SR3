import tkinter as tk
from tkinter import messagebox
import socket
import json
import random
import string
import threading
import time
import os  # Импортируем модуль os для работы с путями

# Константы для подключения к серверу
HOST = 'localhost'
PORT = 7432

# Загрузка конфигурационного файла
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Функция для отправки запроса на сервер и получения ответа
def send_query(query):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(query.encode('utf-8'))
        response = s.recv(1024).decode('utf-8')
    return response

# Функция для генерации случайного ключа
def generate_key(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Функция для сохранения пароля в файл
def save_password_to_file(password):
    with open('password.txt', 'w') as password_file:
        password_file.write(password)

# Функция для проверки логина и пароля
def check_login(username, key):
    query = f"SELECT * FROM user WHERE username = '{username}' AND key = '{key}'"
    response = send_query(query)
    return response != "Table not found: user" and response != ""

# Функция для регистрации нового пользователя
def register_user(username, key):
    query = f"INSERT INTO user VALUES {username} {key} 0 0 0 0"
    response = send_query(query)
    if "INSERT query processed." in response:
        messagebox.showinfo("Успех", "Пользователь успешно зарегистрирован!")
    else:
        messagebox.showerror("Ошибка", "Ошибка при регистрации пользователя.")

# Функция для выполнения запроса и добавления результата в лог
def execute_query(query, log_text):
    if not query:
        messagebox.showwarning("Внимание", "Запрос не может быть пустым")
        return

    try:
        response = send_query(query)
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"Запрос: {query}\n")
        log_text.insert(tk.END, f"Результат: {response}\n\n")
        log_text.config(state=tk.DISABLED)
        log_text.yview(tk.END)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при выполнении запроса: {e}")

# Окно входа
def login_window():
    login_root = tk.Toplevel(root)
    login_root.title("Вход")
    login_root.geometry("400x300")
    login_root.resizable(False, False)

    username_label = tk.Label(login_root, text="Имя пользователя:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)

    key_label = tk.Label(login_root, text="Ключ:")
    key_label.pack(pady=5)
    key_entry = tk.Entry(login_root, show="*")
    key_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        key = key_entry.get()
        if not username or not key:
            messagebox.showwarning("Внимание", "Пожалуйста, заполните все поля.")
            return
        if check_login(username, key):
            login_root.destroy()
            open_trading_interface(username, key)
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или ключ.")

    login_button = tk.Button(login_root, text="Войти", command=login)
    login_button.pack(pady=10)

    def register():
        login_root.destroy()
        register_window()

    register_button = tk.Button(login_root, text="Регистрация", command=register)
    register_button.pack(pady=10)

    # Скрытая кнопка для режима торговых дродеков
    def open_droid_mode():
        login_root.destroy()
        open_droid_interface()

    droid_mode_button = tk.Button(login_root, text="Режим торговых дродеков", command=open_droid_mode)
    droid_mode_button.pack(pady=10)

# Окно регистрации
def register_window():
    register_root = tk.Toplevel(root)
    register_root.title("Регистрация")
    register_root.geometry("300x400")
    register_root.resizable(False, False)

    username_label = tk.Label(register_root, text="Имя пользователя:")
    username_label.pack(pady=5)
    username_entry = tk.Entry(register_root)
    username_entry.pack(pady=5)

    key_label = tk.Label(register_root, text="Ключ:")
    key_label.pack(pady=5)
    key_entry = tk.Entry(register_root, show="*")
    key_entry.pack(pady=5)

    def generate_key_and_register():
        username = username_entry.get()
        key = generate_key()
        key_entry.delete(0, tk.END)
        key_entry.insert(0, key)
        save_password_to_file(key)  # Сохраняем пароль в файл
        register_user(username, key)

    generate_key_button = tk.Button(register_root, text="Сгенерировать ключ", command=generate_key_and_register)
    generate_key_button.pack(pady=10)

    def register():
        username = username_entry.get()
        key = key_entry.get()
        if not username or not key:
            messagebox.showwarning("Внимание", "Пожалуйста, заполните все поля.")
            return
        save_password_to_file(key)  # Сохраняем пароль в файл
        register_user(username, key)

    register_button = tk.Button(register_root, text="Зарегистрироваться", command=register)
    register_button.pack(pady=10)

    def back_to_login():
        register_root.destroy()
        login_window()

    back_button = tk.Button(register_root, text="Назад", command=back_to_login)
    back_button.pack(pady=10)

# Торговый интерфейс
def open_trading_interface(username, key):
    trading_root = tk.Toplevel(root)
    trading_root.title("Торговый интерфейс")
    trading_root.geometry("1280x720")
    trading_root.resizable(False, False)

    frame = tk.Frame(trading_root)
    frame.pack(pady=10)

    user_key_label = tk.Label(frame, text="Ключ пользователя:")
    user_key_label.grid(row=0, column=0, padx=5, pady=5)
    user_key_entry = tk.Entry(frame)
    user_key_entry.insert(0, key)
    user_key_entry.grid(row=0, column=1, padx=5, pady=5)

    pair_id_label = tk.Label(frame, text="ID пары:")
    pair_id_label.grid(row=1, column=0, padx=5, pady=5)
    pair_id_entry = tk.Entry(frame)
    pair_id_entry.grid(row=1, column=1, padx=5, pady=5)

    quantity_label = tk.Label(frame, text="Количество:")
    quantity_label.grid(row=2, column=0, padx=5, pady=5)
    quantity_entry = tk.Entry(frame)
    quantity_entry.grid(row=2, column=1, padx=5, pady=5)

    price_label = tk.Label(frame, text="Цена:")
    price_label.grid(row=3, column=0, padx=5, pady=5)
    price_entry = tk.Entry(frame)
    price_entry.grid(row=3, column=1, padx=5, pady=5)

    order_type_var = tk.StringVar(value="buy")
    order_type_buy = tk.Radiobutton(frame, text="Купить", variable=order_type_var, value="buy")
    order_type_buy.grid(row=4, column=0, padx=5, pady=5)
    order_type_sell = tk.Radiobutton(frame, text="Продать", variable=order_type_var, value="sell")
    order_type_sell.grid(row=4, column=1, padx=5, pady=5)

    create_order_button = tk.Button(frame, text="Создать заказ", command=lambda: create_order(user_key_entry, pair_id_entry, quantity_entry, price_entry, order_type_var, log_text))
    create_order_button.grid(row=5, column=0, padx=5, pady=5)

    get_orders_button = tk.Button(frame, text="Получить заказы", command=lambda: get_orders(log_text))
    get_orders_button.grid(row=6, column=0, padx=5, pady=5)

    get_lots_button = tk.Button(frame, text="Получить лоты", command=lambda: get_lots(log_text))
    get_lots_button.grid(row=6, column=1, padx=5, pady=5)

    get_pairs_button = tk.Button(frame, text="Получить пары", command=lambda: get_pairs(log_text))
    get_pairs_button.grid(row=7, column=0, padx=5, pady=5)

    get_balance_button = tk.Button(frame, text="Получить баланс", command=lambda: get_balance(user_key_entry, log_text))
    get_balance_button.grid(row=7, column=1, padx=5, pady=5)

    close_orders_button = tk.Button(frame, text="Закрыть заказы", command=lambda: close_order(log_text))
    close_orders_button.grid(row=8, column=0, padx=5, pady=5)

    log_label = tk.Label(trading_root, text="Лог:")
    log_label.pack(pady=5)

    log_text = tk.Text(trading_root, width=80, height=20, state=tk.DISABLED)  
    log_text.pack(pady=5)

    # Функция для отправки сообщения в чат
    def send_message():
        message = chat_entry.get("1.0", tk.END).strip()
        if message:
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"[{username}]: {message}\n")
            chat_text.config(state=tk.DISABLED)
            chat_entry.delete("1.0", tk.END)
            chat_text.yview(tk.END)  

    # Функция для очистки чата
    def clear_chat():
        chat_text.config(state=tk.NORMAL)
        chat_text.delete(1.0, tk.END)
        chat_text.config(state=tk.DISABLED)

    # Создание чата
    chat_frame = tk.Frame(trading_root)
    chat_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

    chat_label = tk.Label(chat_frame, text="Чат:")
    chat_label.pack(pady=5)

    chat_text = tk.Text(chat_frame, width=80, height=10, state=tk.DISABLED)  
    chat_text.pack(pady=5)

    chat_entry = tk.Text(chat_frame, width=80, height=5)  
    chat_entry.pack(pady=5)

    send_button = tk.Button(chat_frame, text="Отправить", command=send_message)
    send_button.pack(pady=5)

    clear_button = tk.Button(chat_frame, text="Очистить чат", command=clear_chat)
    clear_button.pack(pady=5)

    # Добавление неизменяемого текстового бокса для отображения ника
    username_display_label = tk.Label(trading_root, text="Ваш ник:")
    username_display_label.pack(pady=5)

    username_display_text = tk.Text(trading_root, width=20, height=1, state=tk.DISABLED)
    username_display_text.pack(pady=5)
    username_display_text.config(state=tk.NORMAL)
    username_display_text.insert(tk.END, username)
    username_display_text.config(state=tk.DISABLED)

# Функции для кнопок
def create_order(user_key_entry, pair_id_entry, quantity_entry, price_entry, order_type_var, log_text):
    user_key = user_key_entry.get()
    pair_id = pair_id_entry.get()
    quantity = quantity_entry.get()
    price = price_entry.get()
    order_type = order_type_var.get()
    query = f"INSERT INTO order VALUES {user_key} {pair_id} {quantity} {price} {order_type} open"
    execute_query(query, log_text)
    check_and_close_orders(pair_id, quantity, price, log_text)

def get_orders(log_text):
    query = "SELECT * FROM order"
    execute_query(query, log_text)

def get_lots(log_text):
    query = "SELECT * FROM lot"
    execute_query(query, log_text)

def get_pairs(log_text):
    query = "SELECT * FROM pair"
    execute_query(query, log_text)

def get_balance(user_key_entry, log_text):
    user_key = user_key_entry.get()
    query = f"SELECT * FROM user_lot WHERE user_id = '{user_key}'"
    execute_query(query, log_text)

# Функция для проверки и закрытия ордеров
def check_and_close_orders(pair_id, quantity, price, log_text):
    query = f"SELECT * FROM order WHERE pair_id = '{pair_id}' AND quantity = '{quantity}' AND price = '{price}' AND status = 'open'"
    response = send_query(query)
    if response.strip():  # Проверка на пустой ответ
        try:
            orders = json.loads(response)
            if len(orders) > 1:
                for order in orders:
                    if order['type'] != orders[0]['type']:
                        close_order(order['id'], log_text)
        except json.JSONDecodeError as e:
            messagebox.showerror("Ошибка", f"Ошибка при парсинге JSON: {e}")
    else:
        messagebox.showwarning("Внимание", "Пустой ответ от сервера")

def close_order(order_id, log_text):
    query = f"UPDATE order SET status = 'closed' WHERE id = '{order_id}'"
    execute_query(query, log_text)

# Интерфейс для режима торговых дродеков
def open_droid_interface():
    droid_root = tk.Toplevel(root)
    droid_root.title("Режим торговых дродеков")
    droid_root.geometry("800x600")
    droid_root.resizable(False, False)

    log_label = tk.Label(droid_root, text="Лог:")
    log_label.pack(pady=5)

    log_text = tk.Text(droid_root, width=80, height=20, state=tk.DISABLED)  
    log_text.pack(pady=5)

    # Функция для запуска торговых роботов
    def start_droid_mode():
        def droid_worker(droid_id):
            while True:
                user_key = f"droid_{droid_id}"
                pair_id = random.choice(["rub_usd", "usd_btc", "btc_eth"])
                quantity = random.randint(1, 10)
                price = random.randint(1, 100)
                order_type = random.choice(["buy", "sell"])
                query = f"INSERT INTO order VALUES {user_key} {pair_id} {quantity} {price} {order_type} open"
                execute_query(query, log_text)
                time.sleep(random.uniform(1, 5))

        for i in range(2):
            threading.Thread(target=droid_worker, args=(i,)).start()

    start_button = tk.Button(droid_root, text="Запустить торговых дродеков", command=start_droid_mode)
    start_button.pack(pady=10)

# Создание главного окна
root = tk.Tk()
root.title("Криптобиржа")
root.geometry("1x1")
root.resizable(False, False)

# Открытие окна входа
login_window()

# Запуск главного цикла обработки событий
root.mainloop()
