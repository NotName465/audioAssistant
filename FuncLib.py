import pyautogui
import time
import webbrowser
import os
import json
import torch
import sounddevice as sd


print("Загрузка модели...")
model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='ru_v3'
)


def speak(text, voice: int = 0):
    """
    Синтезировать и воспроизвести русскую речь

    voice: 'aidar', 'baya', 'kseniya', 'xenia'
    """
    voices = ['aidar', 'baya', 'kseniya', 'xenia']
    audio = model.apply_tts(
        text=text,
        speaker=voices[voice],
        sample_rate=24000,
        put_accent=True,
        put_yo=True
    )

    sd.play(audio.numpy(), samplerate=24000)
    sd.wait()



def open_browser_and_search(browser_path, search_query):
    """Открывает браузер и выполняет поиск"""
    try:
        # Открываем браузер
        os.startfile(browser_path)
        time.sleep(2)  # Ждем загрузки браузера

        # Открываем новую вкладку (Ctrl+T)
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)

        # Фокусируемся на адресной строке (Ctrl+L)
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        # Вводим поисковый запрос
        pyautogui.write(f'{search_query}')
        pyautogui.press('enter')

    except Exception as e:
        print(f"Ошибка при поиске: {e}")


def remove_keywords(text):
    """Удаляет ключевые слова из текста для получения чистого запроса"""
    keywords_to_remove = ['найди', 'в', 'интернете', 'открой', 'закрой', 'создай', 'прокрути', 'включи', 'выключи',
                          'громче', 'тише']
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in keywords_to_remove]
    return ' '.join(filtered_words)


def close_tab():
    """Закрывает текущую вкладку браузера"""
    pyautogui.hotkey('ctrl', 'w')


def new_tab():
    """Открывает новую вкладку браузера"""
    pyautogui.hotkey('ctrl', 't')


def go_to_tab(tab_number):
    """Переходит на указанную вкладку браузера"""
    try:
        tab_num = int(tab_number)
        if 1 <= tab_num <= 8:
            pyautogui.hotkey('ctrl', str(tab_num))
    except ValueError:
        print("Номер вкладки должен быть числом")


def scroll_down():
    """Прокручивает страницу вниз"""
    pyautogui.scroll(-3)


def scroll_up():
    """Прокручивает страницу вверх"""
    pyautogui.scroll(3)


def volume_up():
    """Увеличивает громкость"""
    pyautogui.press('volumeup')


def volume_down():
    """Уменьшает громкость"""
    pyautogui.press('volumedown')


def mute():
    """Включает/выключает звук"""
    pyautogui.press('volumemute')


# НОВЫЕ ФУНКЦИИ ДЛЯ ОТКРЫТИЯ/ЗАКРЫТИЯ ФАЙЛОВ
def AbsolutStarter(file_path: str = ""):
    """
    Открывает файл с помощью системного приложения по умолчанию в Windows.
    """
    if not file_path:
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        # Проверяем существование файла
        if not os.path.isfile(file_path):
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return

        print(f"Открытие файла: {os.path.basename(file_path)}")
        os.startfile(file_path)
        print(f"Файл успешно открыт: {file_path}")

    except Exception as e:
        print(f"ОШИБКА при открытии файла: {e}")


def AbsolutCloser(file_path: str = ""):
    """
    Закрывает приложение в Windows.
    Работает с путями к .exe файлам.
    """
    if not file_path:
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        # Получаем только имя файла для taskkill
        process_name = os.path.basename(file_path)

        # Убедимся, что у процесса есть расширение .exe
        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'

        # Выполняем команду закрытия процесса
        result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")

        if result == 0:
            print(f"Процесс {process_name} успешно завершен")
        else:
            print(f"Не удалось завершить процесс {process_name}. Возможно, процесс не запущен.")

    except Exception as e:
        print(f"ОШИБКА при закрытии приложения: {e}")

