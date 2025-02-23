import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox

# === Глобальные переменные процессов ===
parser1_process = None  # Процесс `parser.py`
parser2_process = None  # Процесс `parser2.py`

# === Функция для запуска `parser.py` ===
def start_parser():
    global parser1_process
    if parser1_process is None or parser1_process.poll() is not None:
        messagebox.showinfo("Парсер", "🚀 Начинаем парсинг username (`parser.py`)...")
        parser1_process = subprocess.Popen(["python", "parser.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        messagebox.showwarning("Ошибка", "❌ `parser.py` уже запущен!")

# === Функция для остановки `parser.py` и запуска `parser2.py` ===
def stop_parser1_and_start_parser2():
    global parser1_process, parser2_process
    if parser1_process and parser1_process.poll() is None:
        messagebox.showinfo("Остановка", "⏸️ Останавливаем `parser.py` и запускаем `parser2.py`...")
        parser1_process.terminate()  # Завершаем `parser.py`
        parser1_process.wait()  # Ждем завершения
    if parser2_process is None or parser2_process.poll() is not None:
        parser2_process = subprocess.Popen(["python", "parser2.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        messagebox.showwarning("Ошибка", "❌ `parser2.py` уже запущен!")

# === Функция для выхода из приложения ===
def exit_app():
    global parser1_process, parser2_process
    if parser1_process and parser1_process.poll() is None:
        parser1_process.terminate()  # Останавливаем `parser.py`
    if parser2_process and parser2_process.poll() is None:
        parser2_process.terminate()  # Останавливаем `parser2.py`
    root.destroy()  # Закрываем GUI

# === Создаем GUI с `tkinter` ===
root = tk.Tk()
root.title("Управление парсингом")
root.geometry("400x200")
root.resizable(False, False)

# === Кнопки управления ===
btn_start_parser = tk.Button(root, text="🚀 Начать парсинг (parser.py)", command=start_parser, height=2, width=40)
btn_stop_and_start = tk.Button(root, text="⏸️ Остановить parser.py и запустить parser2.py", command=stop_parser1_and_start_parser2, height=2, width=40)
btn_exit = tk.Button(root, text="❌ Выход", command=exit_app, height=2, width=40)

# === Размещение кнопок ===
btn_start_parser.pack(pady=10)
btn_stop_and_start.pack(pady=10)
btn_exit.pack(pady=10)

# === Запуск GUI ===
root.mainloop()
