import customtkinter as ctk
import json
import tkinter as tk
import soundcard as sc
import subprocess
import threading
import io
import pyperclip
import sys
import os
import main, FuncLib
import zipfile
import urllib.request
from urllib.error import URLError, HTTPError
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from FuncLib import speak

    USE_FUNCLIB_SPEAK = True
except ImportError as e:
    print(f"Ошибка импорта FuncLib: {e}")
    USE_FUNCLIB_SPEAK = False
    # Если нет FuncLib, будем использовать fallback
    from gtts import gTTS
    import pygame

# Настройка внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Создание главного окна
root = ctk.CTk()
root.configure(fg_color="#783518")
root.title("AudioAssistant")
root.geometry('400x600')
root.resizable(False, False)

# Цвета
BGColorForFirstButtoms = "#1A1A1A"
BGcolorForSettings = "#262626"

# Переменные для анимации
settings_visible = False
commands_visible = False
show_animation_id = None
hide_animation_id = None
current_panel = None

# Переменные для управления помощником
assistant_process = None
assistant_thread = None
is_assistant_running = False
assistant_status = "stopped"  # stopped, starting, running, stopping
waiting_for_keyword = False

# Создание выдвижных панелей - ОБЕ ВО ВЕСЬ ЭКРАН
settings_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=400,
                              height=600,
                              corner_radius=0)

commands_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=400,
                              height=600,
                              corner_radius=0)

# Изначально скрываем панели
settings_panel.place(x=-400, y=0)
commands_panel.place(x=-400, y=0)
settings_panel.lower()
commands_panel.lower()


# Класс для круговой кнопки запуска (УВЕЛИЧЕННЫЙ РАЗМЕР)
class CircularAssistantButton(ctk.CTkFrame):
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.status = "stopped"  # stopped, starting, running, stopping
        self.is_pressed = False

        # Увеличиваем размер кнопки
        self.configure(fg_color="transparent", width=160, height=160)
        self.pack_propagate(False)

        # Canvas для рисования круга (увеличиваем размер)
        self.canvas = tk.Canvas(self, width=160, height=160,
                                highlightthickness=0, bg="#783518")
        self.canvas.pack()

        # Привязываем события мыши
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.draw_button()

    def draw_button(self):
        self.canvas.delete("all")

        # Цвета в зависимости от статуса
        if self.status == "stopped":
            outer_color = "#4682B4"  # Steel blue
            inner_color = "#F0F0F0"  # Light gray
            text_color = "white"
            text = "ЗАПУСК"  # Русский текст
        elif self.status == "starting":
            outer_color = "#FF8C00"  # Dark orange
            inner_color = "#FFD700"  # Gold
            text_color = "white"
            text = "ЗАГРУЗКА"  # Русский текст
        elif self.status == "running":
            outer_color = "#32CD32"  # Lime green
            inner_color = "#00FF00"  # Bright green
            text_color = "white"
            text = "РАБОТАЕТ"  # Русский текст
        elif self.status == "stopping":
            outer_color = "#FF4500"  # Orange red
            inner_color = "#FF0000"  # Bright red
            text_color = "white"
            text = "ОСТАНОВКА"  # Русский текст
        else:
            outer_color = "#4682B4"
            inner_color = "#F0F0F0"
            text_color = "white"
            text = "ЗАПУСК"

        # Эффект нажатия
        if self.is_pressed:
            offset = 2
        else:
            offset = 0

        # Внешний круг (увеличиваем размер)
        self.canvas.create_oval(10 + offset, 10 + offset, 150 + offset, 150 + offset,
                                fill=outer_color, outline="#1E1E1E", width=3)

        # Внутренний круг (увеличиваем размер)
        self.canvas.create_oval(40 + offset, 40 + offset, 120 + offset, 120 + offset,
                                fill=inner_color, outline="")

        # Текст (увеличиваем шрифт)
        self.canvas.create_text(80 + offset, 80 + offset, text=text,
                                fill=text_color, font=("Arial", 12, "bold"))

    def on_click(self, event):
        self.is_pressed = True
        self.draw_button()

    def on_release(self, event):
        self.is_pressed = False
        self.draw_button()
        if self.command:
            self.command()

    def set_status(self, status):
        self.status = status
        self.draw_button()


# Класс для перехвата вывода консоли
class ConsoleOutput(io.StringIO):
    def __init__(self, text_widget, original_stdout, status_callback):
        super().__init__()
        self.text_widget = text_widget
        self.original_stdout = original_stdout
        self.status_callback = status_callback

    def write(self, text):
        # Выводим в оригинальную консоль
        self.original_stdout.write(text)

        # Добавляем в текстовый виджет GUI
        self.text_widget.insert("end", text)
        self.text_widget.see("end")
        self.text_widget.update_idletasks()

        # Проверяем, не появилась ли ключевая фраза
        if "Ожидание ключевого слова:" in text or "ожидание ключевого слова:" in text:
            self.status_callback("running")

    def flush(self):
        self.original_stdout.flush()


# Функция для тестирования голоса
def test_voice(voice_id, voice_name):
    """Проигрывает тестовое сообщение для выбранного голоса"""
    if USE_FUNCLIB_SPEAK:
        # Используем функцию speak из FuncLib
        try:
            if voice_id == 0:
                text = f"Я {voice_name} и это первый голос"
            elif voice_id == 1:
                text = f"Я {voice_name} и это второй голос"
            elif voice_id == 2:
                text = f"Я {voice_name} и это третий голос"
            elif voice_id == 3:
                text = f"Я {voice_name} и это четвёртый голос"
            else:
                text = f"Я {voice_name} и это голос номер {voice_id + 1}"

            # Используем функцию speak из FuncLib
            speak(text, voice=voice_id)

        except Exception as e:
            print(f"Ошибка воспроизведения голоса через FuncLib: {e}")
            fallback_voice_test(voice_id, voice_name)
    else:
        fallback_voice_test(voice_id, voice_name)


def fallback_voice_test(voice_id, voice_name):
    """Fallback функция тестирования голоса если FuncLib не доступен"""
    try:
        if voice_id == 0:
            text = f"Я {voice_name} и это первый голос"
        elif voice_id == 1:
            text = f"Я {voice_name} и это второй голос"
        elif voice_id == 2:
            text = f"Я {voice_name} и это третий голос"
        elif voice_id == 3:
            text = f"Я {voice_name} и это четвёртый голос"
        else:
            text = f"Я {voice_name} и это голос номер {voice_id + 1}"

        # Создаем временный файл
        tts = gTTS(text=text, lang='ru')
        tts.save("test_voice.mp3")

        # Проигрываем
        pygame.mixer.init()
        pygame.mixer.music.load("test_voice.mp3")
        pygame.mixer.music.play()

        # Ждём окончания
        while pygame.mixer.music.get_busy():
            pass

        # Удаляем временный файл
        os.remove("test_voice.mp3")

    except Exception as e:
        print(f"Ошибка воспроизведения голоса (fallback): {e}")


# Функция для скачивания и распаковки большой модели распознавания
def download_large_model():
    """Скачивает большую модель распознавания, распаковывает и удаляет архив"""
    try:
        # URL большой модели
        model_url = "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"

        # Пути
        models_dir = "models"
        zip_path = os.path.join(models_dir, "vosk-model-ru-0.42.zip")

        # Создаем папку models если не существует
        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)
            console_text.insert("end", f"📁 Создана папка: {models_dir}\n")

        # Проверяем, не существует ли уже модель
        expected_dir = os.path.join(models_dir, "vosk-model-ru-0.42")
        if os.path.exists(expected_dir):
            console_text.insert("end", "⚠️ Большая модель уже установлена!\n")
            return

        console_text.insert("end", "⬇️ Начинаю загрузку большой модели...\n")
        console_text.insert("end", f"📥 Ссылка: {model_url}\n")
        console_text.insert("end", f"📁 Сохраняю в: {zip_path}\n")

        # Функция для отображения прогресса в мегабайтах
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size

            # Конвертируем в мегабайты
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)

            # Рассчитываем проценты
            percent = min(100, int(downloaded * 100 / total_size))

            # Обновляем прогресс каждые 10 блоков
            if block_num % 10 == 0:
                # Форматируем с 2 знаками после запятой
                downloaded_str = f"{downloaded_mb:.2f}"
                total_str = f"{total_mb:.2f}"

                console_text.insert("end", f"📥 Загружено: {percent}% ({downloaded_str}/{total_str} МБ)\n")
                console_text.see("end")

        # Скачиваем файл
        urllib.request.urlretrieve(model_url, zip_path, show_progress)
        console_text.insert("end", "✅ Файл успешно скачан!\n")

        # Распаковываем
        console_text.insert("end", "📦 Распаковываю архив...\n")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(models_dir)
        console_text.insert("end", "✅ Архив успешно распакован!\n")

        # Удаляем zip файл
        os.remove(zip_path)
        console_text.insert("end", "🗑️ Архив удален\n")

        # Проверяем что распаковалось
        if os.path.exists(expected_dir):
            console_text.insert("end", f"✅ Модель успешно установлена в: {expected_dir}\n")
        else:
            # Ищем что распаковалось
            extracted_items = os.listdir(models_dir)
            console_text.insert("end", f"📁 В папке models теперь: {extracted_items}\n")

        console_text.insert("end", "✅ Готово! Модель установлена.\n")

        # Обновляем список моделей в настройках
        refresh_models_list()

    except HTTPError as e:
        console_text.insert("end", f"❌ Ошибка HTTP при скачивании: {e.code} {e.reason}\n")
    except URLError as e:
        console_text.insert("end", f"❌ Ошибка сети: {e.reason}\n")
    except zipfile.BadZipFile:
        console_text.insert("end", "❌ Ошибка: поврежденный zip файл\n")
    except Exception as e:
        console_text.insert("end", f"❌ Неожиданная ошибка: {str(e)}\n")


# Функции для управления голосовым помощником
def start_assistant():
    global is_assistant_running, assistant_status, assistant_process, assistant_thread, waiting_for_keyword

    if is_assistant_running:
        return

    assistant_status = "starting"
    waiting_for_keyword = False
    circular_btn.set_status("starting")
    status_label.configure(text="Статус: Загрузка...")

    # Очищаем консоль перед запуском
    console_text.delete("1.0", "end")
    console_text.insert("end", "=== Запуск Audio Assistant ===\n")

    # Запускаем в отдельном потоке
    assistant_thread = threading.Thread(target=run_assistant, daemon=True)
    assistant_thread.start()


def stop_assistant():
    global is_assistant_running, assistant_status, waiting_for_keyword

    if not is_assistant_running:
        return

    assistant_status = "stopping"
    waiting_for_keyword = False
    circular_btn.set_status("stopping")
    status_label.configure(text="Статус: Останавливается...")
    console_text.insert("end", "\n=== Остановка Audio Assistant ===\n")

    # Останавливаем процесс
    if assistant_process:
        assistant_process.terminate()
        try:
            assistant_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            assistant_process.kill()


def restart_assistant():
    """Перезапускает помощника"""
    global is_assistant_running

    if is_assistant_running:
        stop_assistant()
        # Ждем немного перед перезапуском
        root.after(1000, start_assistant)
    else:
        start_assistant()


def run_assistant():
    global is_assistant_running, assistant_status, assistant_process, waiting_for_keyword

    try:
        # Проверяем существование main.py
        if not os.path.exists("main.py"):
            update_status("stopped", "Ошибка: main.py не найден!")
            console_text.insert("end", "❌ ОШИБКА: файл main.py не найден!\n")
            return

        console_text.insert("end", "🔄 Запуск main.py...\n")

        # Запускаем процесс
        assistant_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Объединяем stdout и stderr
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )

        is_assistant_running = True

        # Читаем вывод в реальном времени
        for line in iter(assistant_process.stdout.readline, ''):
            if line:
                console_text.insert("end", line)
                console_text.see("end")
                console_text.update_idletasks()

                # Проверяем, не появилась ли ключевая фраза
                if "Ожидание ключевого слова:" in line or "ожидание ключевого слова:" in line:
                    waiting_for_keyword = True
                    assistant_status = "running"
                    update_status("running", "Статус: Работает")
                    console_text.insert("end", "✅ Audio Assistant запущен и ожидает команды\n")

        # Ждем завершения процесса
        return_code = assistant_process.wait()

        is_assistant_running = False
        waiting_for_keyword = False

        if return_code == 0 or return_code == 1:  # Нормальное завершение или нажатие Ctrl+C
            # Нормальное завершение
            assistant_status = "stopped"
            update_status("stopped", "Статус: Остановлен")
            console_text.insert("end", "⏹️ Работа остановлена\n")
        else:
            # Ошибка при завершении
            assistant_status = "stopped"
            update_status("stopped", "Статус: Остановлен")
            console_text.insert("end", f"⏹️ Работа остановлена (код завершения: {return_code})\n")

    except Exception as e:
        is_assistant_running = False
        waiting_for_keyword = False
        assistant_status = "stopped"
        error_msg = f"⏹️ Работа остановлена: {str(e)}\n"
        update_status("stopped", f"Статус: Остановлен")
        console_text.insert("end", error_msg)
        console_text.insert("end", "🔄 Готов к запуску\n")


def update_status(status, message):
    circular_btn.set_status(status)
    status_label.configure(text=message)


def on_circular_button_click():
    global assistant_status

    if assistant_status == "stopped":
        start_assistant()
    elif assistant_status == "running":
        stop_assistant()
    else:
        # При любом другом статусе просто останавливаем
        stop_assistant()


def handle_status_change(new_status):
    """Обрабатывает изменение статуса из консольного вывода"""
    global assistant_status
    if new_status == "running" and assistant_status == "starting":
        assistant_status = "running"
        update_status("running", "Статус: Работает")


# Функции для работы с cfg.json
def load_cfg_variables():
    """Загружает переменные из файла cfg.json"""
    try:
        cfg_path = "cfg.json"

        if not os.path.exists(cfg_path):
            # Создаем файл с пустым словарем если не существует
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            return {}

        if os.path.getsize(cfg_path) == 0:
            return {}

        with open(cfg_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    except Exception as e:
        print(f"Ошибка загрузки cfg.json: {e}")
        return {}


def save_cfg_variables(variables):
    """Сохраняет переменные в файл cfg.json"""
    try:
        cfg_path = "cfg.json"

        # Создаем директорию если не существует (исправленная версия)
        directory = os.path.dirname(cfg_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        with open(cfg_path, 'w', encoding='utf-8') as f:
            json.dump(variables, f, ensure_ascii=False, indent=2)

        print("Переменные сохранены в cfg.json")
        return True

    except Exception as e:
        print(f"Ошибка сохранения cfg.json: {e}")
        return False


# Функции для работы с config.json (голос)
def load_config():
    """Загружает конфигурацию из config.json"""
    try:
        config_path = "config.json"
        default_config = {
            "selected_microphone": "",
            "selected_voice": 1,  # По умолчанию голос Байа
            "selected_lib": "models/vosk-model-small-ru-0.22"  # Путь к модели распознавания по умолчанию
        }

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        else:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"Создан файл конфигурации: {config_path}")
            return default_config
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return default_config


def save_config(config):
    """Сохраняет конфигурацию в config.json"""
    try:
        config_path = "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("Конфигурация сохранена")
        return True
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False


# Функция для получения списка доступных моделей распознавания
def get_available_recognition_models():
    """Получает список доступных моделей из папки models"""
    models_dir = "models"
    available_models = []

    # Проверяем существование папки models
    if not os.path.exists(models_dir):
        print(f"Папка {models_dir} не найдена. Создаю...")
        os.makedirs(models_dir, exist_ok=True)
        return available_models

    # Получаем список папок в директории models
    try:
        for item in os.listdir(models_dir):
            item_path = os.path.join(models_dir, item)
            if os.path.isdir(item_path):
                # Формируем относительный путь для сохранения в config.json
                relative_path = f"models/{item}"
                available_models.append({
                    "name": item,
                    "path": relative_path,
                    "full_path": item_path
                })

        # Сортируем по имени для удобства
        available_models.sort(key=lambda x: x["name"])
        return available_models
    except Exception as e:
        print(f"Ошибка получения списка моделей: {e}")
        return available_models


# Глобальная переменная для обновления списка моделей
available_models_global = []


def refresh_models_list():
    """Обновляет список моделей и перерисовывает интерфейс"""
    global available_models_global
    available_models_global = get_available_recognition_models()

    # Здесь будет код для обновления интерфейса
    # (это будет вызвано из функции create_settings_content)


def get_variable_display_value(var_name, var_value):
    """Возвращает отображаемое значение переменной"""
    if var_value is None or var_value == "":
        return f"{var_name}: Тут пусто"
    else:
        # Убираем лишние пробелы в начале и конце
        return f"{var_name}: {var_value.strip()}"


def get_protection_status(is_protected):
    """Возвращает текст статуса защиты"""
    if is_protected:
        return "🔒 Эта переменная защищена"
    else:
        return "🔓 Эта переменная не защищена"


# Функция для потери фокуса только при клике на не-интерактивные элементы
def lose_focus_on_background(event):
    """Функция для потери фокуса при клике на фон"""
    # Получаем виджет, на который кликнули
    widget = event.widget

    # Если кликнули на фоновый элемент (Frame, Canvas и т.д.), а не на интерактивный
    if isinstance(widget, (ctk.CTkFrame, tk.Canvas, tk.Frame)):
        root.focus()


# Функция для принудительного переноса текста после 25 символов
def wrap_text(text, max_chars=25):
    """Разбивает текст на строки, перенося после max_chars символов"""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Если добавление слова превысит лимит, начинаем новую строку
        if len(current_line) + len(word) + 1 > max_chars:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " " + word
            else:
                current_line = word

    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)


# Функции для работы с буфером обмена - УДАЛЕНЫ (но функции оставлены пустыми для совместимости)
def clipboard_select_all(widget):
    """Функция оставлена для совместимости"""
    pass


def clipboard_copy(widget):
    """Функция оставлена для совместимости"""
    pass


def clipboard_paste(widget):
    """Функция оставлена для совместимости"""
    pass


# УЛУЧШЕННАЯ Функция для создания метки с автоматическим переносом текста
def create_wrapped_label(parent, text, max_chars_per_line=40, **kwargs):
    """Создает метку с автоматическим переносом текста через каждые max_chars_per_line символов"""
    # Разбиваем текст на строки
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        # Проверяем, не превысит ли добавление слова максимальную длину строки
        current_line.append(word)
        current_text = ' '.join(current_line)

        if len(current_text) > max_chars_per_line:
            if len(current_line) > 1:
                # Сохраняем строку без последнего слова
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]  # Начинаем новую строку с текущего слова
            else:
                # Если одно слово длиннее максимальной длины, разбиваем его
                if len(word) > max_chars_per_line:
                    # Разбиваем длинное слово на части
                    for i in range(0, len(word), max_chars_per_line):
                        lines.append(word[i:i + max_chars_per_line])
                    current_line = []
                else:
                    lines.append(' '.join(current_line))
                    current_line = []

    # Добавляем оставшиеся слова
    if current_line:
        lines.append(' '.join(current_line))

    # Объединяем строки
    wrapped_text = '\n'.join(lines)

    # Стандартные настройки
    defaults = {
        'text_color': "white",
        'font': ctk.CTkFont(size=12),
        'justify': "left"
    }
    # Объединяем настройки
    settings = {**defaults, **kwargs}

    label = ctk.CTkLabel(parent, text=wrapped_text, **settings)
    return label


# Функция для создания многострочного текста с фиксированным количеством строк
def create_multiline_label(parent, text, max_lines=2, **kwargs):
    """Создает метки с фиксированным количеством строк"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        current_text = ' '.join(current_line)

        # Примерная оценка длины строки
        if len(current_text) > 35:  # Примерно 35 символов в строке
            if len(current_line) > 1:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
            else:
                lines.append(word)
                current_line = []

        # Если достигли максимального количества строк
        if len(lines) >= max_lines:
            # Добавляем многоточие к последней строке
            if current_line:
                last_line = ' '.join(current_line)
                if len(lines) == max_lines - 1:
                    if len(last_line) > 32:
                        lines.append(last_line[:32] + "...")
                    else:
                        lines.append(last_line)
                else:
                    if len(lines[-1]) > 32:
                        lines[-1] = lines[-1][:32] + "..."
            break

    # Добавляем оставшиеся слова, если не достигли максимума строк
    if len(lines) < max_lines and current_line:
        lines.append(' '.join(current_line))

    wrapped_text = '\n'.join(lines)

    defaults = {
        'text_color': "white",
        'font': ctk.CTkFont(size=12),
        'justify': "left"
    }
    settings = {**defaults, **kwargs}

    label = ctk.CTkLabel(parent, text=wrapped_text, **settings)
    return label


# Функция для включения горячих клавиш в полях ввода - УДАЛЕНЫ горячие клавиши
def enable_text_shortcuts(widget):
    """Функция оставлена для совместимости, но горячие клавиши удалены"""
    pass


# Остальные существующие функции...
def load_commands_from_json():
    """Загружает команды из файла commands.json"""
    try:
        json_path = "commands.json"

        if not os.path.exists(json_path):
            print("Json файл не подгружен")
            return []

        if os.path.getsize(json_path) == 0:
            print("Json файл не подгружен")
            return []

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        commands = data.get("commands", [])
        if not commands:
            print("Json файл не подгружен")
            return []

        return commands

    except Exception as e:
        print(f"Json файл не подгружен: {e}")
        return []


# Функции для показа/скрытия панелей с анимации
def toggle_settings():
    global settings_visible, commands_visible, current_panel

    if commands_visible:
        hide_commands_with_animation()
        root.after(250, show_settings_with_animation)
    elif settings_visible:
        hide_settings_with_animation()
    else:
        show_settings_with_animation()


def toggle_commands():
    global settings_visible, commands_visible, current_panel

    if settings_visible:
        hide_settings_with_animation()
        root.after(250, show_commands_with_animation)
    elif commands_visible:
        hide_commands_with_animation()
    else:
        show_commands_with_animation()


def show_settings_with_animation():
    global settings_visible, show_animation_id, hide_animation_id, current_panel

    if hide_animation_id:
        root.after_cancel(hide_animation_id)
        hide_animation_id = None

    settings_panel.lift()
    current_panel = settings_panel

    def animate_show(frame=0):
        global show_animation_id
        current_x = -400 + (frame * 20)
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            show_animation_id = root.after(16, lambda: animate_show(frame + 1))
        else:
            settings_panel.place(x=0, y=0)
            settings_visible = True
            show_animation_id = None

    animate_show()


def hide_settings_with_animation():
    global settings_visible, hide_animation_id, show_animation_id

    if show_animation_id:
        root.after_cancel(show_animation_id)
        show_animation_id = None

    def animate_hide(frame=0):
        global hide_animation_id
        current_x = 0 - (frame * 20)
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            hide_animation_id = root.after(16, lambda: animate_hide(frame + 1))
        else:
            settings_panel.place(x=-400, y=0)
            settings_panel.lower()
            settings_visible = False
            hide_animation_id = None

    animate_hide()


def show_commands_with_animation():
    global commands_visible, show_animation_id, hide_animation_id, current_panel

    if hide_animation_id:
        root.after_cancel(hide_animation_id)
        hide_animation_id = None

    commands_panel.lift()
    current_panel = commands_panel

    def animate_show(frame=0):
        global show_animation_id
        current_x = -400 + (frame * 20)
        commands_panel.place(x=current_x, y=0)

        if frame < 20:
            show_animation_id = root.after(16, lambda: animate_show(frame + 1))
        else:
            commands_panel.place(x=0, y=0)
            commands_visible = True
            show_animation_id = None

    animate_show()


def hide_commands_with_animation():
    global commands_visible, hide_animation_id, show_animation_id

    if show_animation_id:
        root.after_cancel(show_animation_id)
        show_animation_id = None

    def animate_hide(frame=0):
        global hide_animation_id
        current_x = 0 - (frame * 20)
        commands_panel.place(x=current_x, y=0)

        if frame < 20:
            hide_animation_id = root.after(16, lambda: animate_hide(frame + 1))
        else:
            commands_panel.place(x=-400, y=0)
            commands_panel.lower()
            commands_visible = False
            hide_animation_id = None

    animate_hide()


# Функции для кнопок "Назад"
def back_to_main_from_settings():
    hide_settings_with_animation()


def back_to_main_from_commands():
    hide_commands_with_animation()


# Создание содержимого панели настроек
def create_settings_content():
    # Верхняя панель настроек
    settings_title_bar = ctk.CTkFrame(settings_panel,
                                      fg_color=BGColorForFirstButtoms,
                                      height=30,
                                      corner_radius=0)
    settings_title_bar.pack(fill="x", padx=0, pady=0)

    settings_title = create_multiline_label(settings_title_bar,
                                            text="Настройки AudioAssistant",
                                            max_lines=1,
                                            text_color="white",
                                            fg_color=BGColorForFirstButtoms,
                                            font=ctk.CTkFont(size=12, weight="bold"))
    settings_title.pack(side="left", padx=10)

    settings_back_btn = ctk.CTkButton(settings_title_bar,
                                      text="← Назад",
                                      command=back_to_main_from_settings,
                                      fg_color=BGColorForFirstButtoms,
                                      hover_color="#444444",
                                      text_color="white",
                                      height=25,
                                      corner_radius=0)
    settings_back_btn.pack(side="right", padx=10)

    # Основной контейнер для скроллинга настроек
    settings_scroll_container = ctk.CTkFrame(settings_panel,
                                             fg_color="#2b2b2b",
                                             corner_radius=0)
    settings_scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

    settings_canvas = tk.Canvas(settings_scroll_container,
                                bg="#2b2b2b",
                                width=365,
                                height=550)
    settings_canvas.pack(side="left", fill="both", expand=True)

    # Вертикальный скроллбар для настроек
    settings_v_scrollbar = ctk.CTkScrollbar(settings_scroll_container,
                                            orientation="vertical",
                                            command=settings_canvas.yview)
    settings_v_scrollbar.pack(side="right", fill="y")

    # Настраиваем canvas
    settings_canvas.configure(yscrollcommand=settings_v_scrollbar.set)

    # Создаем фрейм для содержимого настроек внутри canvas
    settings_content = ctk.CTkFrame(settings_canvas,
                                    fg_color="#2b2b2b",
                                    corner_radius=0)

    # Создаем окно в canvas для нашего фрейма
    settings_canvas.create_window((0, 0), window=settings_content, anchor="nw")

    # Функции для работы скроллинга настроек
    def on_settings_frame_configure(event):
        """Обновляем scrollregion когда меняется размер фрейма настроек"""
        settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))

    def on_settings_canvas_configure(event):
        """Обновляем ширину фрейма при изменении размера canvas"""
        settings_canvas.itemconfig(settings_canvas.find_all()[0], width=event.width)

    # Привязываем события
    settings_content.bind("<Configure>", on_settings_frame_configure)
    settings_canvas.bind("<Configure>", on_settings_canvas_configure)

    # Заголовок настроек (ИСПРАВЛЕНО: используем create_multiline_label как в файле 1)
    main_title = create_multiline_label(settings_content,
                                        "Настройки приложения",
                                        max_lines=2,
                                        text_color="white",
                                        font=ctk.CTkFont(size=24, weight="bold"))
    main_title.pack(pady=(20, 30))

    # ========== 1. Сначала "Создание пользовательской функции" ==========
    functions_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    functions_frame.pack(fill="x", padx=20, pady=(0, 20))

    # ИСПРАВЛЕНО: Явное разделение на две строки с двумя метками
    functions_title_frame = ctk.CTkFrame(functions_frame, fg_color="transparent")
    functions_title_frame.pack(anchor="w", padx=15, pady=10, fill="x")

    # Первая строка: "Создание"
    functions_label_line1 = ctk.CTkLabel(functions_title_frame,
                                         text="Создание",
                                         text_color="white",
                                         font=ctk.CTkFont(size=18, weight="bold"),
                                         anchor="w")
    functions_label_line1.pack(anchor="w")

    # Вторая строка: "пользовательской функции"
    functions_label_line2 = ctk.CTkLabel(functions_title_frame,
                                         text="пользовательской функции",
                                         text_color="white",
                                         font=ctk.CTkFont(size=18, weight="bold"),
                                         anchor="w")
    functions_label_line2.pack(anchor="w")

    # Контейнер для создания функций
    create_function_frame = ctk.CTkFrame(functions_frame, fg_color="#444444")
    create_function_frame.pack(fill="x", padx=15, pady=(0, 15))

    # Поле для имени функции (с номером)
    func_name_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    func_name_frame.pack(fill="x", padx=10, pady=(10, 5))

    func_name_label = create_multiline_label(func_name_frame,
                                             "(1) Имя функции:",
                                             max_lines=1,
                                             text_color="white")
    func_name_label.pack(anchor="w")

    # Контейнер для поля ввода
    func_name_input_frame = ctk.CTkFrame(func_name_frame, fg_color="transparent")
    func_name_input_frame.pack(fill="x", pady=(5, 0))

    # Улучшенное поле ввода с поддержкой горячих клавиш
    func_name_entry = ctk.CTkEntry(func_name_input_frame,
                                   placeholder_text="Например: Открой нарды",
                                   width=300)
    func_name_entry.pack(side="left", fill="x", expand=True)
    enable_text_shortcuts(func_name_entry)

    # Поле для пути к файлу (с номером)
    file_path_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    file_path_frame.pack(fill="x", padx=10, pady=5)

    file_path_label = create_multiline_label(file_path_frame,
                                             "(2) Путь к файлу:",
                                             max_lines=1,
                                             text_color="white")
    file_path_label.pack(anchor="w")

    # Контейнер для поля ввода и кнопки вставки переменной
    file_path_input_frame = ctk.CTkFrame(file_path_frame, fg_color="transparent")
    file_path_input_frame.pack(fill="x", pady=(5, 0))

    file_path_entry = ctk.CTkEntry(file_path_input_frame,
                                   placeholder_text="C:\\Program Files\\app.exe",
                                   width=300)
    file_path_entry.pack(side="left", fill="x", expand=True)
    enable_text_shortcuts(file_path_entry)

    # Кнопка для быстрой вставки переменной
    def insert_variable_to_path():
        """Вставляет выбранную переменную в поле пути"""
        selected_var = var_combobox.get()
        if selected_var != "None" and selected_var != "Нет доступных переменных":
            current_text = file_path_entry.get()
            if current_text:
                file_path_entry.delete(0, 'end')
            file_path_entry.insert(0, f"cfg_vars['{selected_var}']")

    insert_var_btn = ctk.CTkButton(file_path_input_frame,
                                   text="{ }",
                                   width=40,
                                   command=insert_variable_to_path,
                                   fg_color="#555555",
                                   hover_color="#666666")
    insert_var_btn.pack(side="right", padx=(5, 0))

    # Поле для ключевых слов (с номером)
    keywords_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    keywords_frame.pack(fill="x", padx=10, pady=5)

    keywords_label = create_multiline_label(keywords_frame,
                                            "(3) Ключевые слова (через запятую):",
                                            max_lines=2,
                                            text_color="white")
    keywords_label.pack(anchor="w")

    # Контейнер для поля ввода
    keywords_input_frame = ctk.CTkFrame(keywords_frame, fg_color="transparent")
    keywords_input_frame.pack(fill="x", pady=(5, 0))

    keywords_entry = ctk.CTkEntry(keywords_input_frame,
                                  placeholder_text="открой, запусти, программа",
                                  width=300)
    keywords_entry.pack(side="left", fill="x", expand=True)
    enable_text_shortcuts(keywords_entry)

    # Переменные из cfg.json для выбора (с номером)
    variables_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    variables_frame.pack(fill="x", padx=10, pady=5)

    variables_label = create_multiline_label(variables_frame,
                                             "(4) Используй готовую переменную:",
                                             max_lines=2,
                                             text_color="white")
    variables_label.pack(anchor="w")

    # Получаем список переменных
    cfg_vars_for_func = load_cfg_variables()
    variable_names = list(cfg_vars_for_func.keys())

    if not variable_names:
        variable_names = ["Нет доступных переменных"]

    # Добавляем вариант "None" в начало списка
    variable_names_with_none = ["None"] + variable_names
    var_combobox = ctk.CTkComboBox(variables_frame,
                                   values=variable_names_with_none,
                                   state="readonly",
                                   width=350)
    var_combobox.pack(fill="x", pady=(5, 0))
    var_combobox.set("None")  # Устанавливаем "None" по умолчанию

    # ДОБАВЛЕНО: Поле для выбора функционала (с номером)
    functionality_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    functionality_frame.pack(fill="x", padx=10, pady=5)

    functionality_label = create_multiline_label(functionality_frame,
                                                 "(5) Функционал:",
                                                 max_lines=1,
                                                 text_color="white")
    functionality_label.pack(anchor="w")

    # Выпадающий список для выбора функционала
    functionality_options = ["None", "Открыть", "Закрыть"]
    functionality_combobox = ctk.CTkComboBox(functionality_frame,
                                             values=functionality_options,
                                             state="readonly",
                                             width=350)
    functionality_combobox.pack(fill="x", pady=(5, 0))
    functionality_combobox.set("None")  # Устанавливаем "None" по умолчанию

    # Кнопки управления
    buttons_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=10, pady=10)

    # Функция для показа уведомления об ошибки
    def show_error_message(message):
        """Показывает сообщение об ошибки"""
        error_frame = ctk.CTkFrame(create_function_frame, fg_color="#442222")
        error_frame.pack(fill="x", pady=5, padx=0)

        error_label = create_multiline_label(error_frame, message,
                                             max_lines=3,
                                             text_color="#ff8888",
                                             font=ctk.CTkFont(size=11, weight="bold"))
        error_label.pack(padx=10, pady=8)

        def remove_error():
            error_frame.destroy()

        root.after(3000, remove_error)

    # Функция для показа сообщения об успехе
    def show_success_message(message):
        success_label = create_multiline_label(create_function_frame,
                                               message,
                                               max_lines=3,
                                               text_color="#00ff00",
                                               font=ctk.CTkFont(size=12, weight="bold"))
        success_label.pack(pady=5)
        root.after(3000, success_label.destroy)

    # Функция для создания пользовательской функции
    def create_custom_function():
        func_name = func_name_entry.get().strip()
        file_path = file_path_entry.get().strip()
        keywords_text = keywords_entry.get().strip()
        selected_var = var_combobox.get()
        selected_functionality = functionality_combobox.get()

        # Проверка обязательных полей
        if not func_name:
            show_error_message("❌ Введите имя функции")
            return

        # Обязательная проверка: должен быть указан путь к файлу ИЛИ выбрана переменная
        if not file_path and (selected_var == "None" or selected_var == "Нет доступных переменных"):
            show_error_message("❌ Укажите путь к файлу или выберите переменную")
            return

        if not keywords_text:
            show_error_message("❌ Введите ключевые слова")
            return

        # Проверка поля функционала (ОБЯЗАТЕЛЬНОЕ)
        if selected_functionality == "None":
            show_error_message("❌ Выберите функционал (Открыть или Закрыть)")
            return

        # Обрабатываем ключевые слова
        keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]

        if len(keywords) == 0:
            show_error_message("❌ Введите хотя бы одно ключевое слово")
            return

        # Определяем путь к файлу
        final_file_path = file_path
        use_variable = False

        if selected_var != "None" and selected_var != "Нет доступных переменных" and selected_var in cfg_vars_for_func:
            final_file_path = f"cfg_vars['{selected_var}']"
            use_variable = True
        elif not file_path:
            show_error_message("❌ Укажите путь к файлу")
            return

        # Определяем функцию на основе выбранного функционала
        if selected_functionality == "Открыть":
            function_name = "AbsolutStarter"
            name_prefix = "custom_open"
        elif selected_functionality == "Закрыть":
            function_name = "AbsolutCloser"
            name_prefix = "custom_close"
        else:
            show_error_message("❌ Неизвестный функционал")
            return

        # Создаем команду
        command = {
            "nameForGUI": func_name,
            "name": f"{name_prefix}_{func_name.lower().replace(' ', '_')}",
            "keywords": keywords,
            "function": function_name,
            "args": [final_file_path],
            "protected": False
        }

        # Загружаем текущие команды
        commands = load_commands_from_json()

        # Проверяем, нет ли уже команды с таким именем
        existing_names = [cmd.get('name', '') for cmd in commands]
        if command['name'] in existing_names:
            show_error_message(f"❌ Функция с именем '{command['name']}' уже существует")
            return

        # Добавляем команду
        commands.append(command)

        # Сохраняем обновленные команды
        try:
            with open('commands.json', 'w', encoding='utf-8') as f:
                json.dump({"commands": commands}, f, ensure_ascii=False, indent=2)

            # Показываем сообщение об успехе
            success_msg = f"✓ Функция '{func_name}' ({selected_functionality}) создана!"
            show_success_message(success_msg)

            # Очищаем поля
            func_name_entry.delete(0, 'end')
            file_path_entry.delete(0, 'end')
            keywords_entry.delete(0, 'end')
            var_combobox.set("None")
            functionality_combobox.set("None")

            # Если ассистент запущен, перезапускаем его чтобы подхватил новые команды
            if assistant_status == "running":
                console_text.insert("end", "🔄 Обнаружены новые команды, перезапуск ассистента...\n")
                restart_assistant()

        except Exception as e:
            show_error_message(f"❌ Ошибка сохранения: {e}")

    # Функция для предложения создания переменной
    def suggest_variable_creation():
        file_path = file_path_entry.get().strip()
        if not file_path:
            show_error_message("❌ Сначала укажите путь к файлу")
            return

        # Предлагаем создать переменную
        dialog = ctk.CTkInputDialog(
            text=f"Создать переменную для пути:\n{file_path}\n\nВведите имя переменной:",
            title="Создание переменной"
        )
        var_name = dialog.get_input()

        if var_name and var_name.strip():
            var_name = var_name.strip()

            # Добавляем переменную в cfg.json
            cfg_vars = load_cfg_variables()
            cfg_vars[var_name] = {
                'value': file_path,
                'protected': False
            }

            if save_cfg_variables(cfg_vars):
                # Обновляем комбобокс
                updated_vars = list(cfg_vars.keys())
                var_combobox.configure(values=["None"] + updated_vars)
                var_combobox.set(var_name)

                # Очищаем поле пути
                file_path_entry.delete(0, 'end')

                show_success_message(f"✓ Переменная '{var_name}' создана!")
            else:
                show_error_message("❌ Ошибка создания переменной")

    # Кнопки создания
    create_buttons_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
    create_buttons_frame.pack(fill="x")

    # Кнопка "Добавить функцию" слева
    create_func_btn = ctk.CTkButton(create_buttons_frame,
                                    text="➕ Добавить функцию",
                                    command=create_custom_function,
                                    fg_color="#444444",
                                    hover_color="#555555",
                                    height=30)
    create_func_btn.pack(side="left", padx=(0, 5))

    # Кнопка "Сохранить" справа
    save_func_btn = ctk.CTkButton(create_buttons_frame,
                                  text="Сохранить",
                                  command=create_custom_function,
                                  fg_color="#00aa00",
                                  hover_color="#008800",
                                  height=30,
                                  width=120)
    save_func_btn.pack(side="left", padx=3)

    # Кнопка создания переменной
    suggest_var_btn = ctk.CTkButton(create_buttons_frame,
                                    text="Создать переменную",
                                    command=suggest_variable_creation,
                                    fg_color="#444444",
                                    hover_color="#555555",
                                    height=30)
    suggest_var_btn.pack(side="left", padx=5)

    # Кнопка очистки всех полей
    def clear_all_fields():
        func_name_entry.delete(0, 'end')
        file_path_entry.delete(0, 'end')
        keywords_entry.delete(0, 'end')
        var_combobox.set("None")
        functionality_combobox.set("None")
        show_success_message("✓ Все поля очищены")

    clear_btn = ctk.CTkButton(create_buttons_frame,
                              text="Очистить все",
                              command=clear_all_fields,
                              fg_color="#aa0000",
                              hover_color="#880000",
                              height=30)
    clear_btn.pack(side="left", padx=5)

    # Контроллер буфера обмена для блока создания функций (в одну строку)
    functions_clipboard_frame = ctk.CTkFrame(create_function_frame, fg_color="transparent")
    functions_clipboard_frame.pack(fill="x", padx=10, pady=(10, 5))

    # Список полей ввода в этом блоке с номерами для отображения в комбобоксе
    function_fields_display = [
        "(1) Имя функции",
        "(2) Путь к файлу",
        "(3) Ключевые слова",
        "(4) Функционал"  # Исправлено: было "(5) Функционал", стало "(4) Функционал"
    ]

    # Список полей ввода в этом блоке для привязки
    function_fields = [
        ("(1) Имя функции", func_name_entry),
        ("(2) Путь к файлу", file_path_entry),
        ("(3) Ключевые слова", keywords_entry),
        ("(4) Функционал", functionality_combobox)  # Исправлено: было "(5) Функционал", стало "(4) Функционал"
    ]

    # Создаем список номеров полей для выбора (с круглыми скобками)
    field_options = ["None"] + [f"({i + 1})" for i in range(len(function_fields))]
    clipboard_combobox = ctk.CTkComboBox(functions_clipboard_frame,
                                         values=field_options,
                                         state="readonly",
                                         width=100)
    clipboard_combobox.set("None")  # Устанавливаем "None" по умолчанию

    # Функция для получения выбранного поля
    def get_selected_function_field():
        selected = clipboard_combobox.get()
        if selected == "None":
            return None
        try:
            # Извлекаем номер из строки "(1)", "(2)", и т.д.
            field_index = int(selected.strip('()')) - 1
            if 0 <= field_index < len(function_fields):
                return function_fields[field_index][1]
        except:
            return None
        return None

    # Функция для показа временного сообщения
    def show_temp_message(message, color="#00ff00"):
        temp_label = create_multiline_label(functions_clipboard_frame,
                                            message,
                                            max_lines=2,
                                            text_color=color,
                                            font=ctk.CTkFont(size=10, weight="bold"))
        temp_label.pack(side="right", padx=(10, 0))

        def remove_message():
            temp_label.destroy()

        root.after(5000, remove_message)

    # Кнопка Ctrl+V с цветом фона меню настроек (ИСПРАВЛЕНО: цвет #333333 как в файле 1)
    def paste_to_selected_function_field():
        selected_field = get_selected_function_field()
        if selected_field:
            if isinstance(selected_field, ctk.CTkComboBox):
                # Для комбобокса нельзя вставить текст, показываем сообщение
                show_temp_message("❌ Нельзя вставить в выпадающий список", "#ff0000")
            elif clipboard_paste(selected_field):
                show_temp_message("✓ Вставлено")
            else:
                show_temp_message("❌ Не удалось вставить", "#ff0000")

    ctrl_v_btn = ctk.CTkButton(functions_clipboard_frame,
                               text="Ctrl + V",
                               command=paste_to_selected_function_field,
                               fg_color="#333333",  # ← ИЗМЕНЕНО: цвет как в файле 1
                               hover_color="#444444",  # ← ИЗМЕНЕНО: hover цвет как в файле 1
                               width=80,
                               height=25)
    ctrl_v_btn.pack(side="left", padx=(0, 5))

    # Кнопка "Del" для очистки выбранного поля (ИСПРАВЛЕНО: цвет #333333 как в файле 1)
    def clear_selected_field():
        selected_field = get_selected_function_field()
        if selected_field:
            if isinstance(selected_field, ctk.CTkComboBox):
                selected_field.set("None")
            else:
                selected_field.delete(0, 'end')
            show_temp_message("✓ Поле очищено")

    del_btn = ctk.CTkButton(functions_clipboard_frame,
                            text="Del",
                            command=clear_selected_field,
                            fg_color="#333333",  # ← ИЗМЕНЕНО: цвет как в файле 1
                            hover_color="#555555",  # ← ИЗМЕНЕНО: hover цвет как в файле 1
                            width=50,
                            height=25)
    del_btn.pack(side="left", padx=(0, 10))

    # Комбобокс для выбора поля справа
    clipboard_combobox.pack(side="right")

    # ========== 2. Потом "Переменные конфигурации" ==========
    variables_section_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    variables_section_frame.pack(fill="x", padx=20, pady=(0, 0))

    variables_label = create_multiline_label(variables_section_frame,
                                             text="Переменные конфигурации",
                                             max_lines=2,
                                             text_color="white",
                                             font=ctk.CTkFont(size=18, weight="bold"))
    variables_label.pack(anchor="w", padx=15, pady=10)

    # Загружаем текущие переменные
    cfg_variables = load_cfg_variables()
    variable_entries = {}  # Словарь для хранения полей ввода
    variable_frames = {}  # Словарь для хранения фреймов переменных

    # Контейнер для отображения переменных (ОТЕДЕЛЬНЫЙ ФРЕЙМ ДЛЯ ПЕРЕМЕННЫХ)
    variables_display_frame = ctk.CTkFrame(variables_section_frame, fg_color="#333333")
    variables_display_frame.pack(fill="x", padx=15, pady=(0, 15))

    # ОТДЕЛЬНЫЙ ФРЕЙМ ДЛЯ КНОПОК CTRL+V и DEL (вне фрейма переменных)
    variables_clipboard_container = ctk.CTkFrame(variables_section_frame, fg_color="transparent")
    variables_clipboard_container.pack(fill="x", padx=15, pady=(0, 10))

    # Функция для сортировки переменных (защищенные сначала)
    def sort_variables(variables_dict):
        protected_vars = {}
        unprotected_vars = {}

        for var_name, var_data in variables_dict.items():
            if var_data.get('protected', False):
                protected_vars[var_name] = var_data
            else:
                unprotected_vars[var_name] = var_data

        # Сортируем по имени внутри каждой группы
        protected_sorted = dict(sorted(protected_vars.items()))
        unprotected_sorted = dict(sorted(unprotected_vars.items()))

        return {**protected_sorted, **unprotected_sorted}

    # Функция для создания полей ввода переменных
    # Функция для создания полей ввода переменных
    def create_variable_fields():
        nonlocal cfg_variables, variable_entries, variable_frames

        # Очищаем существующие поля
        for widget in variables_display_frame.winfo_children():
            widget.destroy()

        variable_entries = {}
        variable_frames = {}

        if not cfg_variables:
            # Если переменных нет, показываем сообщение
            no_vars_label = ctk.CTkLabel(variables_display_frame,
                                         text="Переменные не добавлены",
                                         text_color="#888888",
                                         font=ctk.CTkFont(size=12))
            no_vars_label.pack(pady=20)
            return

        # Сортируем переменные: защищенные сначала
        sorted_variables = sort_variables(cfg_variables)

        # Создаем поля для каждой переменной
        for idx, (var_name, var_data) in enumerate(sorted_variables.items(), 1):
            # Извлекаем значение и защиту
            var_value = var_data.get('value', '')
            is_protected = var_data.get('protected', False)

            # Убираем лишние пробелы в начале и конце значения
            cleaned_value = var_value.strip() if var_value else ""

            # Фрейм для одной переменной
            var_frame = ctk.CTkFrame(variables_display_frame, fg_color="#444444")
            var_frame.pack(fill="x", pady=5, padx=0)
            variable_frames[var_name] = var_frame

            # Основной контейнер для верхней строки
            top_frame = ctk.CTkFrame(var_frame, fg_color="transparent")
            top_frame.pack(fill="x", padx=12, pady=(8, 5))

            # Создаем Grid для правильного расположения
            top_frame.grid_columnconfigure(0, weight=1)  # Метка занимает все доступное пространство
            top_frame.grid_columnconfigure(1, weight=0)  # Кнопка - минимальный размер

            # Метка с именем переменной и текущим значением
            value_label_text = get_variable_display_value(var_name, cleaned_value)
            if is_protected:
                display_text = f"({idx}) 🔒 {value_label_text}"
            else:
                display_text = f"({idx}) {value_label_text}"

            # Функция для автоматического переноса текста
            def wrap_text_for_label(text, max_chars=30):
                """Разбивает текст на строки для правильного отображения"""
                words = text.split()
                lines = []
                current_line = []

                for word in words:
                    current_line.append(word)
                    current_text = ' '.join(current_line)

                    if len(current_text) > max_chars:
                        if len(current_line) > 1:
                            lines.append(' '.join(current_line[:-1]))
                            current_line = [word]
                        else:
                            lines.append(word)
                            current_line = []

                if current_line:
                    lines.append(' '.join(current_line))

                return '\n'.join(lines)

            # Обернутый текст для метки
            wrapped_text = wrap_text_for_label(display_text, max_chars=25)

            # Метка с выравниванием влево и поддержкой переноса
            value_label = ctk.CTkLabel(top_frame,
                                       text=wrapped_text,
                                       text_color="white",
                                       font=ctk.CTkFont(size=12),
                                       anchor="w",
                                       justify="left",
                                       wraplength=250)  # Уменьшил ширину для переноса
            value_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

            # Кнопка удаления (крестик)
            if is_protected:
                # Защищенная переменная - серый крестик
                delete_btn = ctk.CTkButton(top_frame,
                                           text="✕",
                                           width=25,
                                           height=25,
                                           fg_color="#666666",
                                           hover_color="#666666",
                                           text_color="#999999",
                                           state="disabled")
            else:
                # Незащищенная переменная - красный крестик
                delete_btn = ctk.CTkButton(top_frame,
                                           text="✕",
                                           width=25,
                                           height=25,
                                           fg_color="#aa0000",
                                           hover_color="#cc0000",
                                           text_color="white",
                                           command=lambda name=var_name: delete_variable(name))
            delete_btn.grid(row=0, column=1, sticky="e")

            # Контейнер для поля ввода
            input_frame = ctk.CTkFrame(var_frame, fg_color="transparent")
            input_frame.pack(fill="x", padx=12, pady=(0, 8))

            # Поле ввода для изменения значения с поддержкой горячих клавиш
            entry = ctk.CTkEntry(input_frame,
                                 placeholder_text=get_protection_status(is_protected),
                                 width=300)
            entry.pack(side="left", fill="x", expand=True)
            enable_text_shortcuts(entry)

            # Если есть текущее значение, показываем его в поле ввода (без лишних пробелов)
            if cleaned_value and cleaned_value != "":
                entry.insert(0, cleaned_value)

            variable_entries[var_name] = entry

    # Функция для удаления переменной
    def delete_variable(var_name):
        nonlocal cfg_variables

        if var_name in cfg_variables:
            # Проверяем, защищена ли переменная
            if cfg_variables[var_name].get('protected', False):
                print(f"Переменная {var_name} защищена и не может быть удалена")
                return

            # Удаляем переменную
            del cfg_variables[var_name]
            # Сохраняем в файл
            save_cfg_variables(cfg_variables)
            # Пересоздаем поля
            create_variable_fields()
            # Обновляем комбобокс
            update_variables_combobox()
            print(f"Переменная {var_name} удалена")

    # Функция для добавления новой переменной
    def add_new_variable():
        nonlocal cfg_variables

        # Диалог для ввода имени новой переменной
        dialog = ctk.CTkInputDialog(text="Введите имя новой переменной:", title="Новая переменная")
        new_var_name = dialog.get_input()

        if new_var_name and new_var_name.strip():
            new_var_name = new_var_name.strip()

            # Проверяем, существует ли уже переменная с таким именем
            if new_var_name in cfg_variables:
                show_error_message(f"❌ Ошибка: Переменная '{new_var_name}' уже существует!")
                print(f"Нельзя создать переменную '{new_var_name}' - она уже существует")
                return

            # Все новые переменные создаются как незащищенные
            # Защиту можно установить только через редактирование cfg.json
            is_protected = False

            # Добавляем новую переменную с пустым значением
            cfg_variables[new_var_name] = {
                'value': "",
                'protected': is_protected
            }
            # Сохраняем в файл
            save_cfg_variables(cfg_variables)
            # Пересоздаем поля
            create_variable_fields()
            # Обновляем комбобокс
            update_variables_combobox()
            print(f"Добавлена новая переменная: {new_var_name}")

    # Функция для сохранения всех переменных
    def save_all_variables():
        nonlocal cfg_variables

        # Обновляем значения из полей ввода для ВСЕХ переменных (включая защищенные)
        for var_name, entry in variable_entries.items():
            new_value = entry.get().strip()  # Убираем пробелы в начале и конце
            cfg_variables[var_name]['value'] = new_value

            # Очищаем поле ввода после сохранения
            entry.delete(0, 'end')

        # Сохраняем в файл
        if save_cfg_variables(cfg_variables):
            # Показываем уведомление об успехе
            success_label = create_multiline_label(variables_display_frame,
                                                   "✓ Переменные сохранены!",
                                                   max_lines=2,
                                                   text_color="#00ff00",
                                                   font=ctk.CTkFont(size=12, weight="bold"))
            success_label.pack(pady=5)
            # Убираем уведомление через 2 секунды
            root.after(2000, success_label.destroy)

            # Обновляем отображаемые значения
            create_variable_fields()
            # Обновляем комбобокс
            update_variables_combobox()

    # Функция для удаления всех незащищенных переменных
    def clear_all_variables():
        nonlocal cfg_variables

        # Создаем копию словаря для итерации
        vars_to_remove = []
        for var_name, var_data in cfg_variables.items():
            if not var_data.get('protected', False):
                vars_to_remove.append(var_name)

        # Удаляем незащищенные переменные
        for var_name in vars_to_remove:
            del cfg_variables[var_name]

        save_cfg_variables(cfg_variables)
        create_variable_fields()
        # Обновляем комбобокс
        update_variables_combobox()
        print(f"Удалено {len(vars_to_remove)} незащищенных переменных")

    # Создаем начальные поля
    create_variable_fields()

    # Кнопки управления переменными
    variables_buttons_frame = ctk.CTkFrame(variables_section_frame, fg_color="transparent")
    variables_buttons_frame.pack(fill="x", padx=15, pady=10)

    add_var_btn = ctk.CTkButton(variables_buttons_frame,
                                text="➕ Добавить переменную",
                                command=add_new_variable,
                                fg_color="#444444",
                                hover_color="#555555",
                                height=30)
    add_var_btn.pack(side="left", padx=(0, 5))

    save_vars_btn = ctk.CTkButton(variables_buttons_frame,
                                  text="Сохранить",
                                  command=save_all_variables,
                                  fg_color="#00aa00",
                                  hover_color="#008800",
                                  height=30,
                                  width=120)
    save_vars_btn.pack(side="left", padx=3)

    clear_vars_btn = ctk.CTkButton(variables_buttons_frame,
                                   text="🗑️ Очистить все",
                                   command=clear_all_variables,
                                   fg_color="#aa0000",
                                   hover_color="#880000",
                                   height=30)
    clear_vars_btn.pack(side="left", padx=5)

    # Контроллер буфера обмена для блока переменных (в одну строку, ОТДЕЛЬНЫЙ ФРЕЙМ)
    # Создаем список переменных с номерами
    def update_variables_combobox():
        # Очищаем старый комбобокс если он существует
        for widget in variables_clipboard_container.winfo_children():
            widget.destroy()

        # Создаем новый фрейм для элементов буфера обмена
        variables_clipboard_frame = ctk.CTkFrame(variables_clipboard_container, fg_color="transparent")
        variables_clipboard_frame.pack(fill="x", padx=0, pady=0)

        if variable_entries:  # Только если есть переменные
            # Получаем отсортированный список переменных
            sorted_vars = sort_variables(cfg_variables)
            var_names_sorted = list(sorted_vars.keys())

            # Создаем список номеров для выбора (с круглыми скобками)
            var_options = ["None"] + [f"({i + 1})" for i in range(len(var_names_sorted))]
            var_clipboard_combobox = ctk.CTkComboBox(variables_clipboard_frame,
                                                     values=var_options,
                                                     state="readonly",
                                                     width=100)
            var_clipboard_combobox.set("None")

            # Функция для получения выбранной переменной
            def get_selected_variable_field():
                selected = var_clipboard_combobox.get()
                if selected == "None":
                    return None
                try:
                    # Извлекаем номер из строки "(1)", "(2)", и т.д.
                    field_index = int(selected.strip('()')) - 1
                    if 0 <= field_index < len(var_names_sorted):
                        var_name = var_names_sorted[field_index]
                        return variable_entries.get(var_name)
                except:
                    return None
                return None

            # Функция для показа временного сообщения
            def show_var_temp_message(message, color="#00ff00"):
                temp_label = create_multiline_label(variables_clipboard_frame,
                                                    message,
                                                    max_lines=2,
                                                    text_color=color,
                                                    font=ctk.CTkFont(size=10, weight="bold"))
                temp_label.pack(side="right", padx=(10, 0))

                def remove_message():
                    temp_label.destroy()

                root.after(5000, remove_message)

            # Кнопка Ctrl+V для переменных (ИСПРАВЛЕНО: цвет #333333 как в файле 1)
            def paste_to_selected_variable_field():
                selected_field = get_selected_variable_field()
                if selected_field:
                    if clipboard_paste(selected_field):
                        show_var_temp_message("✓ Вставлено")
                    else:
                        show_var_temp_message("❌ Не удалось вставить", "#ff0000")

            var_ctrl_v_btn = ctk.CTkButton(variables_clipboard_frame,
                                           text="Ctrl + V",
                                           command=paste_to_selected_variable_field,
                                           fg_color="#444444",  # ← ИЗМЕНЕНО: цвет как в файле 1
                                           hover_color="#444444",  # ← ИЗМЕНЕНО: hover цвет как в файле 1
                                           width=80,
                                           height=25)
            var_ctrl_v_btn.pack(side="left", padx=(0, 5))

            # Кнопка "Del" для очистки выбранного поля переменной (ИСПРАВЛЕНО: цвет #333333 как в файле 1)
            def clear_selected_variable_field():
                selected_field = get_selected_variable_field()
                if selected_field:
                    selected_field.delete(0, 'end')
                    show_var_temp_message("✓ Поле очищено")

            var_del_btn = ctk.CTkButton(variables_clipboard_frame,
                                        text="Del",
                                        command=clear_selected_variable_field,
                                        fg_color="#444444",  # ← ИЗМЕНЕНО: цвет как в файле 1
                                        hover_color="#555555",  # ← ИЗМЕНЕНО: hover цвет как в файле 1
                                        width=50,
                                        height=25)
            var_del_btn.pack(side="left", padx=(0, 10))

            # Комбобокс для выбора поля справа
            var_clipboard_combobox.pack(side="right")
        else:
            # Если нет переменных, показываем сообщение
            no_vars_clipboard_label = create_multiline_label(variables_clipboard_frame,
                                                             "Добавьте переменные для использования буфера обмена",
                                                             max_lines=2,
                                                             text_color="#888888",
                                                             font=ctk.CTkFont(size=10))
            no_vars_clipboard_label.pack(pady=5)

    # Инициализируем комбобокс для переменных
    update_variables_combobox()

    # Привязываем событие клика только к фоновым элементам
    variables_display_frame.bind("<Button-1>", lose_focus_on_background)
    variables_section_frame.bind("<Button-1>", lose_focus_on_background)

    # ========== 3. Потом "Выбор голоса приложения" ==========
    voice_section = ctk.CTkFrame(settings_content, fg_color="#333333")
    voice_section.pack(fill="x", padx=20, pady=(15, 15))

    voice_label = create_multiline_label(voice_section,
                                         text="Выбор голоса приложения",
                                         max_lines=2,
                                         text_color="white",
                                         font=ctk.CTkFont(size=18, weight="bold"))
    voice_label.pack(anchor="w", padx=20, pady=10)

    # Загружаем текущую конфигурацию голоса
    config = load_config()
    selected_voice = config.get("selected_voice", 1)

    # Голоса
    voices = [
        {"name": "Айдар", "id": 0, "description": "Мужской голос"},
        {"name": "Байа", "id": 1, "description": "Женский голос"},
        {"name": "Ксения", "id": 2, "description": "Женский голос"},
        {"name": "Хениа", "id": 3, "description": "Женский голос"}
    ]

    # Переменная для хранения выбранного голоса
    current_selected_voice = tk.IntVar(value=selected_voice)

    def save_voice_selection():
        """Сохраняет выбранный голос в config.json"""
        selected_voice_id = current_selected_voice.get()
        config["selected_voice"] = selected_voice_id
        if save_config(config):
            # Показываем уведомление об успехе
            success_label = create_multiline_label(voice_section,
                                                   f"✓ Голос '{voices[selected_voice_id]['name']}' сохранен!",
                                                   max_lines=2,
                                                   text_color="#00ff00",
                                                   font=ctk.CTkFont(size=12, weight="bold"))
            success_label.pack(pady=5)
            root.after(2000, success_label.destroy)

    # Контейнер для голосов
    voices_container = ctk.CTkFrame(voice_section, fg_color="#444444")
    voices_container.pack(fill="x", padx=15, pady=(0, 15))

    for voice in voices:
        voice_frame = ctk.CTkFrame(voices_container, fg_color="transparent")
        voice_frame.pack(fill="x", pady=5, padx=10)

        # Левая часть: радиокнопка
        left_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True)

        # Радиокнопка для выбора голоса
        radio_btn = ctk.CTkRadioButton(left_frame,
                                       text=f"{voice['name']} ({voice['description']})",
                                       variable=current_selected_voice,
                                       value=voice['id'],
                                       text_color="white",
                                       fg_color="#4682B4",
                                       hover_color="#5A9BD5",
                                       command=save_voice_selection)
        radio_btn.pack(side="left", padx=(0, 10))

        right_frame = ctk.CTkFrame(voice_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        # Зеленая кнопка "Тест"
        test_button = ctk.CTkButton(right_frame,
                                    text="Тест",
                                    width=50,
                                    height=25,
                                    fg_color="#00aa00",
                                    hover_color="#008800",
                                    text_color="white",
                                    font=ctk.CTkFont(size=10, weight="bold"),
                                    command=lambda vid=voice['id'], vname=voice['name']: test_voice(vid, vname))
        test_button.pack(side="left")

    # ========== 4. Новая секция "Модель распознавания" ==========
    model_section = ctk.CTkFrame(settings_content, fg_color="#333333")
    model_section.pack(fill="x", padx=20, pady=(0, 15))

    model_label = create_multiline_label(model_section,
                                         text="Модель распознавания",
                                         max_lines=2,
                                         text_color="white",
                                         font=ctk.CTkFont(size=18, weight="bold"))
    model_label.pack(anchor="w", padx=20, pady=10)

    # Получаем доступные модели
    available_models = get_available_recognition_models()
    selected_lib = config.get("selected_lib", "models/vosk-model-small-ru-0.22")

    # Контейнер для моделей
    models_container = ctk.CTkFrame(model_section, fg_color="#444444")
    models_container.pack(fill="x", padx=15, pady=(0, 10))

    # Контейнер для информационных сообщений
    info_container = ctk.CTkFrame(model_section, fg_color="transparent")
    info_container.pack(fill="x", padx=15, pady=(0, 10))

    # Предупреждение о больших моделях (первый абзац) - БЕЗ ЗНАКА ВОПРОСА
    warning_frame = ctk.CTkFrame(info_container, fg_color="transparent")
    warning_frame.pack(fill="x", pady=(0, 5))

    warning_text = "ВНИМАНИЕ! При использовании большой модели значительно увеличиться не только качество распознания речи, но и время запуска приложения и время обработки команд."
    warning_label = create_multiline_label(warning_frame,
                                           warning_text,
                                           max_lines=4,
                                           text_color="#ff6666",  # Красный цвет
                                           font=ctk.CTkFont(size=11, weight="bold"))  # Жирный шрифт
    warning_label.pack(anchor="w", padx=(0, 0))

    # Кнопка для скачивания большой модели
    download_button_frame = ctk.CTkFrame(model_section, fg_color="transparent")
    download_button_frame.pack(fill="x", padx=15, pady=(10, 5))

    # Функция для скачивания в отдельном потоке
    def download_large_model_thread():
        """Запускает скачивание в отдельном потоке"""
        download_thread = threading.Thread(target=download_large_model, daemon=True)
        download_thread.start()

    # Используем простой CTkButton с двумя строками через \n и настроенным anchor
    download_btn = ctk.CTkButton(download_button_frame,
                                 text="Скачать большую библиотеку\nдля распознавания",
                                 command=download_large_model_thread,
                                 fg_color="#444444",
                                 hover_color="#555555",
                                 height=50,  # Увеличиваем высоту для двух строк
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 anchor="w")  # Выравнивание по левому краю
    download_btn.pack(fill="x", pady=(5, 0))

    # Информация о большой модели
    info_large_model_frame = ctk.CTkFrame(download_button_frame, fg_color="transparent")
    info_large_model_frame.pack(fill="x", pady=(5, 0))

    large_model_info = "Размер: ~1.8 GB\nТочность: высокая\nЯзык: русский"
    large_model_label = create_multiline_label(info_large_model_frame,
                                               large_model_info,
                                               max_lines=4,
                                               text_color="#cccccc",
                                               font=ctk.CTkFont(size=10))
    large_model_label.pack(anchor="w", padx=(0, 0))

    if available_models:
        # Переменная для хранения выбранной модели
        current_selected_model = tk.StringVar(value=selected_lib)

        def save_model_selection():
            """Сохраняет выбранную модель в config.json"""
            selected_model_path = current_selected_model.get()
            config["selected_lib"] = selected_model_path
            if save_config(config):
                # Находим имя модели для отображения
                model_name = "Неизвестная модель"
                for model in available_models:
                    if model["path"] == selected_model_path:
                        model_name = model["name"]
                        break

                # Показываем уведомление об успехе
                success_label = create_multiline_label(model_section,
                                                       f"✓ Модель '{model_name}' сохранена!",
                                                       max_lines=2,
                                                       text_color="#00ff00",
                                                       font=ctk.CTkFont(size=12, weight="bold"))
                success_label.pack(pady=5)
                root.after(2000, success_label.destroy)

        for model in available_models:
            model_frame = ctk.CTkFrame(models_container, fg_color="transparent")
            model_frame.pack(fill="x", pady=3, padx=10)

            # Левая часть: радиокнопка
            left_frame = ctk.CTkFrame(model_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="both", expand=True)

            # Радиокнопка для выбора модели
            radio_btn = ctk.CTkRadioButton(left_frame,
                                           text=f"{model['name']}",
                                           variable=current_selected_model,
                                           value=model['path'],
                                           text_color="white",
                                           fg_color="#4682B4",
                                           hover_color="#5A9BD5",
                                           command=save_model_selection)
            radio_btn.pack(side="left", padx=(0, 10))

            # Устанавливаем выбранную модель
            if model['path'] == selected_lib:
                radio_btn.select()

    else:
        # Если нет доступных моделей
        no_models_frame = ctk.CTkFrame(models_container, fg_color="transparent")
        no_models_frame.pack(pady=10)

        no_models_label = create_multiline_label(no_models_frame,
                                                 "Модели не найдены",
                                                 max_lines=2,
                                                 text_color="#cccccc",
                                                 font=ctk.CTkFont(size=12))
        no_models_label.pack()

    # ========== УДАЛЕН: Блок "Устройства ввода" (микрофоны) ==========

    # Привязываем событие клика к корневому окна для потери фокуса только на фоне
    model_section.bind("<Button-1>", lose_focus_on_background)
    voice_section.bind("<Button-1>", lose_focus_on_background)
    settings_content.bind("<Button-1>", lose_focus_on_background)
    settings_canvas.bind("<Button-1>", lose_focus_on_background)
    settings_scroll_container.bind("<Button-1>", lose_focus_on_background)


# Создание содержимого панели команд
def create_commands_content():
    commands_list = load_commands_from_json()

    # Верхняя панель команд
    commands_title_bar = ctk.CTkFrame(commands_panel,
                                      fg_color=BGColorForFirstButtoms,
                                      height=30,
                                      corner_radius=0)
    commands_title_bar.pack(fill="x", padx=0, pady=0)

    commands_title = create_multiline_label(commands_title_bar,
                                            text="Команды AudioAssistant",
                                            max_lines=1,
                                            text_color="white",
                                            fg_color=BGColorForFirstButtoms,
                                            font=ctk.CTkFont(size=12, weight="bold"))
    commands_title.pack(side="left", padx=10)

    commands_back_btn = ctk.CTkButton(commands_title_bar,
                                      text="← Назад",
                                      command=back_to_main_from_commands,
                                      fg_color=BGColorForFirstButtoms,
                                      hover_color="#444444",
                                      text_color="white",
                                      height=25,
                                      corner_radius=0)
    commands_back_btn.pack(side="right", padx=10)

    # Основное содержимое команд
    commands_content = ctk.CTkFrame(commands_panel,
                                    fg_color="#2b2b2b",
                                    corner_radius=0)
    commands_content.pack(fill="both", expand=True, padx=0, pady=0)

    # Заголовок
    main_title = create_multiline_label(commands_content,
                                        text="Доступные команды",
                                        max_lines=2,
                                        text_color="white",
                                        font=ctk.CTkFont(size=20, weight="bold"))
    main_title.pack(pady=(15, 15))

    # Фрейм для скроллинга
    scroll_container = ctk.CTkFrame(commands_content, fg_color="#2b2b2b")
    scroll_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    # Создаем Canvas и скроллбары
    canvas = tk.Canvas(scroll_container,
                       bg="#2b2b2b",
                       highlightthickness=0,
                       width=370,
                       height=450)

    # Вертикальный скроллбар
    v_scrollbar = ctk.CTkScrollbar(scroll_container,
                                   orientation="vertical",
                                   command=canvas.yview)

    # Настраиваем canvas
    canvas.configure(yscrollcommand=v_scrollbar.set)

    # Размещаем элементы ГРИДАМИ для правильного расположения
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    # Настраиваем веса гридов
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)

    # Создаем фрейм для команд внутри canvas
    commands_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b", corner_radius=0)

    # Создаем окно в canvas для нашего фрейма
    canvas.create_window((0, 0), window=commands_frame, anchor="nw")

    # Функции для работы скроллинга
    def on_frame_configure(event):
        """Обновляем scrollregion когда меняется размер фрейма"""
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        """Обновляем ширину фрейма при изменении размера canvas"""
        canvas.itemconfig(canvas.find_all()[0], width=event.width)

    # Привязываем события
    commands_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Функция для удаления команды
    def delete_command(command_name, command_frame, is_protected=False):
        if is_protected:
            print(f"Команда {command_name} защищена и не может быть удалена")
            return

        # Загружаем текущие команды
        commands = load_commands_from_json()

        # Находим и удаляем команду
        updated_commands = [cmd for cmd in commands if cmd.get('name') != command_name]

        # Сохраняем обновленные команды
        try:
            with open('commands.json', 'w', encoding='utf-8') as f:
                json.dump({"commands": updated_commands}, f, ensure_ascii=False, indent=2)

            # Удаляем фрейм команды из интерфейса
            command_frame.destroy()

            # Обновляем счетчик команд
            update_commands_count()

            print(f"Команда {command_name} удалена")
        except Exception as e:
            print(f"Ошибка удаления команды: {e}")

    # Функция для обновления счетчика команд
    def update_commands_count():
        commands_count = len(load_commands_from_json())
        count_label.configure(text=f"Всего команд: {commands_count}")

    # Заполняем командами
    if commands_list:
        for command in commands_list:
            name_for_gui = command.get("nameForGUI", "Неизвестная команда")
            is_protected = command.get("protected", False)
            keywords = command.get("keywords", [])
            keywords_text = ", ".join(keywords)

            # Принудительный перенос текста после 25 символов
            wrapped_name = wrap_text(f"• {name_for_gui}", max_chars=25)
            wrapped_keywords = wrap_text(f"Ключевые слова: {keywords_text}", max_chars=25)

            # Подсчитываем количество строк в названии и ключевых словах
            name_lines_count = len(wrapped_name.split('\n'))
            keywords_lines_count = len(wrapped_keywords.split('\n'))

            # Рассчитываем высоту блока на основе количества строк
            base_height = 80
            extra_name_height = max(0, (name_lines_count - 2)) * 20
            extra_keywords_height = max(0, (keywords_lines_count - 1)) * 18
            block_height = base_height + extra_name_height + extra_keywords_height

            # Фрейм для команды с АДАПТИВНОЙ ВЫСОТОЙ
            command_frame = ctk.CTkFrame(commands_frame,
                                         fg_color="#333333",
                                         corner_radius=8,
                                         width=350,
                                         height=block_height)
            command_frame.pack(fill="x", pady=5, padx=0)
            command_frame.pack_propagate(False)

            # Основной контейнер внутри фрейма команды
            content_container = ctk.CTkFrame(command_frame, fg_color="transparent")
            content_container.pack(fill="both", expand=True, padx=12, pady=8)

            # Верхний фрейм с названием и кнопкой удаления
            top_frame = ctk.CTkFrame(content_container, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 5))

            # Левая часть - название функции с ПРИНУДИТЕЛЬНЫМ ПЕРЕНОСОМ
            name_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            name_frame.pack(side="left", fill="x", expand=True)

            # Метка с именем функции
            name_label = ctk.CTkLabel(name_frame,
                                      text=wrapped_name,
                                      text_color="white",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      anchor="w",
                                      justify="left")
            name_label.pack(fill="x", anchor="w")

            # Правая часть - кнопка удаления
            if is_protected:
                # Защищенная команда - серый крестик
                delete_btn = ctk.CTkButton(top_frame,
                                           text="✕",
                                           width=25,
                                           height=25,
                                           fg_color="#666666",
                                           hover_color="#666666",
                                           text_color="#999999",
                                           state="disabled")
            else:
                # Незащищенная команда - красный крестик
                delete_btn = ctk.CTkButton(top_frame,
                                           text="✕",
                                           width=25,
                                           height=25,
                                           fg_color="#aa0000",
                                           hover_color="#cc0000",
                                           text_color="white",
                                           command=lambda name=command.get('name'), frame=command_frame,
                                                          prot=is_protected: delete_command(name, frame, prot))
            delete_btn.pack(side="right", padx=(5, 0))

            # Нижний фрейм с ключевыми словами
            bottom_frame = ctk.CTkFrame(content_container, fg_color="transparent")
            bottom_frame.pack(fill="x")

            # Метка с ключевыми словами
            keywords_label = ctk.CTkLabel(bottom_frame,
                                          text=wrapped_keywords,
                                          text_color="#cccccc",
                                          font=ctk.CTkFont(size=12),
                                          anchor="w",
                                          justify="left")
            keywords_label.pack(fill="x", anchor="w")
    else:
        no_commands_frame = ctk.CTkFrame(commands_frame,
                                         fg_color="#333333",
                                         corner_radius=8,
                                         width=350,
                                         height=80)
        no_commands_frame.pack(fill="x", pady=5, padx=0)
        no_commands_frame.pack_propagate(False)

        no_commands_label = create_multiline_label(no_commands_frame,
                                                   "Команды не найдены. Проверьте файл commands.json",
                                                   max_lines=3,
                                                   text_color="white",
                                                   font=ctk.CTkFont(size=14))
        no_commands_label.pack(padx=12, pady=12)

    # Счетчик команд внизу
    commands_count = len(commands_list)
    count_frame = ctk.CTkFrame(commands_content, fg_color="#2b2b2b", height=30)
    count_frame.pack(fill="x", side="bottom", pady=(0, 5))

    count_label = create_multiline_label(count_frame,
                                         f"Всего команд: {commands_count}",
                                         max_lines=2,
                                         text_color="#aaaaaa",
                                         font=ctk.CTkFont(size=12))
    count_label.pack(pady=5)


# ИЗМЕНЕНО: Верхняя панель с знаками "=" вместо названия и кнопки закрытия
title_bar = ctk.CTkFrame(root, fg_color=BGColorForFirstButtoms, height=30, corner_radius=0)
title_bar.pack(fill="x", padx=0, pady=0)

# Удаляем кнопки и название, оставляем только строку с "="
equals_label = create_multiline_label(title_bar,
                                      text="=" * 50,  # 50 знаков равно для заполнения строки
                                      max_lines=1,
                                      text_color="white",
                                      fg_color=BGColorForFirstButtoms,
                                      font=ctk.CTkFont(size=12))
equals_label.pack(side="left", padx=10, fill="x", expand=True)

SettingsBar = ctk.CTkFrame(root,
                           fg_color=BGcolorForSettings,
                           height=40,
                           corner_radius=0)
SettingsBar.pack(fill="x", padx=0, pady=0)

settings_buttons_frame = ctk.CTkFrame(SettingsBar,
                                      fg_color=BGcolorForSettings,
                                      height=40,
                                      corner_radius=0)
settings_buttons_frame.pack(side="right", padx=0)

SetBut = ctk.CTkButton(settings_buttons_frame,
                       text="⚙️ Настройки",
                       command=toggle_settings,
                       fg_color=BGcolorForSettings,
                       hover_color="#444444",
                       text_color="white",
                       height=30,
                       width=125,
                       corner_radius=2)
SetBut.pack(side="right", padx=2)

ComList = ctk.CTkButton(settings_buttons_frame,
                        text="📋 Команды",
                        command=toggle_commands,
                        fg_color=BGcolorForSettings,
                        hover_color="#444444",
                        text_color="white",
                        height=30,
                        width=125,
                        corner_radius=2)
ComList.pack(side="right", padx=0)

Rus = create_multiline_label(SettingsBar,
                             text="Сделано в России",
                             max_lines=1,
                             text_color="white",
                             fg_color=BGcolorForSettings,
                             font=ctk.CTkFont(size=12))
Rus.pack(side="left", padx=10)

# Основная область контента
content_frame = ctk.CTkFrame(root,
                             fg_color="#783518",
                             corner_radius=0)
content_frame.pack(fill="both", expand=True, padx=0, pady=0)

# ИЗМЕНЕНО: Фраза "Добро пожаловать!" с функцией исчезновения через 10 секунд
welcome_label = create_multiline_label(content_frame,
                                       "Добро пожаловать!",
                                       max_lines=2,
                                       text_color="white",
                                       font=ctk.CTkFont(size=16, weight="bold"))
welcome_label.pack(pady=15)


# Функция для исчезновения приветственного сообщения
def fade_welcome_message():
    """Постепенно делает приветственное сообщение прозрачным, меняя цвет на цвет фона"""
    # Цвет фона в формате RGB
    bg_color = (120, 53, 24)  # #783518 в RGB

    # Текущий цвет текста (белый) в RGB
    text_color = (255, 255, 255)

    # Плавное изменение цвета
    for step in range(51):  # 50 шагов для плавности
        # Вычисляем промежуточный цвет
        r = int(text_color[0] + (bg_color[0] - text_color[0]) * step / 50)
        g = int(text_color[1] + (bg_color[1] - text_color[1]) * step / 50)
        b = int(text_color[2] + (bg_color[2] - text_color[2]) * step / 50)

        # Преобразуем в hex строку
        new_color = f"#{r:02x}{g:02x}{b:02x}"

        # Обновляем цвет текста
        welcome_label.configure(text_color=new_color)

        # Обновляем интерфейс и ждем немного
        root.update()
        root.after(40)  # 40ms * 50 шагов = 2 секунды анимации


# Запускаем исчезновение через 10 секунд
root.after(10000, fade_welcome_message)

# Круглая кнопка запуска помощника
circular_btn = CircularAssistantButton(content_frame, command=on_circular_button_click)
circular_btn.pack(pady=15)

# Статус помощника
status_label = create_multiline_label(content_frame,
                                      "Статус: Остановлен",
                                      max_lines=2,
                                      text_color="white",
                                      font=ctk.CTkFont(size=14))
status_label.pack(pady=5)

# Консоль вывода
console_frame = ctk.CTkFrame(content_frame, fg_color="#2b2b2b", height=200, corner_radius=0)
console_frame.pack(fill="x", padx=15, pady=15, side="bottom")

console_label = create_multiline_label(console_frame,
                                       "Консоль вывода:",
                                       max_lines=1,
                                       text_color="white",
                                       font=ctk.CTkFont(size=12, weight="bold"))
console_label.pack(anchor="w", padx=10, pady=(5, 0))

# Текстовое поле для вывода консоли
console_text = ctk.CTkTextbox(console_frame,
                              fg_color="#1a1a1a",
                              text_color="#00ff00",
                              font=ctk.CTkFont(family="Consolas", size=10),
                              height=150)
console_text.pack(fill="both", expand=True, padx=10, pady=10)
console_text.insert("1.0", "Готов к работе...\n")

# Добавляем горячие клавиши для текстового поля консоли
enable_text_shortcuts(console_text)

# Привязываем событие клика к корневому окна для потери фокуса только на фоне
root.bind("<Button-1>", lose_focus_on_background)

# Создаем содержимое обеих панелей
create_settings_content()
create_commands_content()

# Перехватываем вывод консоли
original_stdout = sys.stdout
console_output = ConsoleOutput(console_text, original_stdout, handle_status_change)
sys.stdout = console_output

root.mainloop()

# Восстанавливаем оригинальный stdout при закрытии
sys.stdout = original_stdout