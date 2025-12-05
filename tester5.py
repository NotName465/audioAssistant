import pyautogui
import time
import webbrowser
import os
import json
import torch
import sounddevice as sd
import random

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

    voice: 0 - 'aidar', 1 - 'baya', 2 - 'kseniya', 3 - 'xenia'
    """
    voices = ['aidar', 'baya', 'kseniya', 'xenia']

    voice_name = voices[voice]

    try:
        audio = model.apply_tts(
            text=text,
            speaker=voice_name,
            sample_rate=24000,
            put_accent=True,
            put_yo=True
        )
        sd.play(audio.numpy(), samplerate=24000)
        sd.wait()
    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")


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

        # Случайное сообщение об успехе
        messages = [
            "Ищу информацию по вашему запросу.",
            "Выполняю поиск в интернете.",
            "Загружаю результаты поиска."
        ]
        speak(random.choice(messages), voice=-1)

    except Exception as e:
        error_messages = [
            "Не удалось выполнить поиск.",
            "Возникла ошибка при открытии браузера.",
            "Поиск не удался, проверьте подключение."
        ]
        speak(random.choice(error_messages), voice=-1)
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

    # Случайное сообщение об успехе
    messages = [
        "Вкладка закрыта.",
        "Закрываю текущую вкладку.",
        "Вкладка успешно закрыта."
    ]
    speak(random.choice(messages), voice=-1)


def new_tab():
    """Открывает новую вкладку браузера"""
    pyautogui.hotkey('ctrl', 't')

    # Случайное сообщение об успехе
    messages = [
        "Новая вкладка открыта.",
        "Создаю чистую вкладку.",
        "Открываю новую вкладку для работы."
    ]
    speak(random.choice(messages), voice=-1)


def go_to_tab(tab_number):
    """Переходит на указанную вкладку браузера"""
    try:
        tab_num = int(tab_number)
        if 1 <= tab_num <= 8:
            pyautogui.hotkey('ctrl', str(tab_num))

            # Случайное сообщение об успехе
            messages = [
                f"Перехожу на вкладку номер {tab_num}.",
                f"Переключаюсь на {tab_num} вкладку.",
                f"Вкладка {tab_num} теперь активна."
            ]
            speak(random.choice(messages), voice=-1)
        else:
            speak("Можно переключаться только между первыми восемью вкладками.", voice=-1)
    except ValueError:
        error_messages = [
            "Номер вкладки должен быть числом.",
            "Пожалуйста, укажите цифру от одного до восьми.",
            "Не понимаю номер вкладки, используйте цифры."
        ]
        speak(random.choice(error_messages), voice=-1)
        print("Номер вкладки должен быть числом")


def scroll_down():
    """Прокручивает страницу вниз"""
    pyautogui.scroll(-3)

    # Случайное сообщение об успехе
    messages = [
        "Прокручиваю вниз.",
        "Листаю страницу ниже.",
        "Спускаюсь по странице."
    ]
    speak(random.choice(messages), voice=-1)


def scroll_up():
    """Прокручивает страницу вверх"""
    pyautogui.scroll(3)

    # Случайное сообщение об успехе
    messages = [
        "Прокручиваю вверх.",
        "Листаю страницу выше.",
        "Поднимаюсь по странице."
    ]
    speak(random.choice(messages), voice=-1)


def volume_up():
    """Увеличивает громкость"""
    pyautogui.press('volumeup')

    # Случайное сообщение об успехе
    messages = [
        "Увеличиваю громкость.",
        "Становится громче.",
        "Прибавляю звук."
    ]
    speak(random.choice(messages), voice=-1)


def volume_down():
    """Уменьшает громкость"""
    pyautogui.press('volumedown')

    # Случайное сообщение об успехе
    messages = [
        "Уменьшаю громкость.",
        "Становится тише.",
        "Убавляю звук."
    ]
    speak(random.choice(messages), voice=-1)


def mute():
    """Включает/выключает звук"""
    pyautogui.press('volumemute')

    # Случайное сообщение об успехе
    messages = [
        "Переключаю звук.",
        "Включаю или выключаю звук.",
        "Изменяю состояние звука."
    ]
    speak(random.choice(messages), voice=-1)


# НОВЫЕ ФУНКЦИИ ДЛЯ ОТКРЫТИЯ/ЗАКРЫТИЯ ФАЙЛОВ
def AbsolutStarter(file_path: str = ""):
    """
    Открывает файл с помощью системного приложения по умолчанию в Windows.
    """
    if not file_path:
        error_messages = [
            "Не указан путь к файлу.",
            "Для открытия файла нужен его путь.",
            "Пожалуйста, укажите что открывать."
        ]
        speak(random.choice(error_messages), voice=-1)
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        # Проверяем существование файла
        if not os.path.isfile(file_path):
            error_messages = [
                f"Файл не найден: {os.path.basename(file_path)}",
                f"Не могу найти файл {os.path.basename(file_path)}",
                f"Файл {os.path.basename(file_path)} отсутствует."
            ]
            speak(random.choice(error_messages), voice=-1)
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return

        print(f"Открытие файла: {os.path.basename(file_path)}")

        # Случайное сообщение перед открытием
        messages_before = [
            f"Открываю файл {os.path.basename(file_path)}.",
            f"Запускаю {os.path.basename(file_path)}.",
            f"Начинаю открытие {os.path.basename(file_path)}."
        ]
        speak(random.choice(messages_before), voice=-1)

        os.startfile(file_path)

        # Случайное сообщение об успехе
        messages_success = [
            f"Файл успешно открыт.",
            f"{os.path.basename(file_path)} запущен.",
            f"Открытие завершено успешно."
        ]
        speak(random.choice(messages_success), voice=-1)

        print(f"Файл успешно открыт: {file_path}")

    except Exception as e:
        error_messages = [
            f"Не удалось открыть файл.",
            f"Возникла ошибка при запуске.",
            f"Не могу открыть этот файл."
        ]
        speak(random.choice(error_messages), voice=-1)
        print(f"ОШИБКА при открытии файла: {e}")


def AbsolutCloser(file_path: str = ""):
    """
    Закрывает приложение в Windows.
    Работает с путями к .exe файлам.
    """
    if not file_path:
        error_messages = [
            "Не указан путь к файлу для закрытия.",
            "Для закрытия нужен путь к приложению.",
            "Пожалуйста, укажите что закрывать."
        ]
        speak(random.choice(error_messages), voice=-1)
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        # Получаем только имя файла для taskkill
        process_name = os.path.basename(file_path)

        # Убедимся, что у процесса есть расширение .exe
        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'

        # Случайное сообщение перед закрытием
        messages_before = [
            f"Пытаюсь закрыть {process_name}.",
            f"Завершаю процесс {process_name}.",
            f"Выполняю закрытие {process_name}."
        ]
        speak(random.choice(messages_before), voice=-1)

        # Выполняем команду закрытия процесса
        result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")

        if result == 0:
            success_messages = [
                f"Процесс {process_name} успешно завершен.",
                f"{process_name} закрыт.",
                f"Приложение {process_name} остановлено."
            ]
            speak(random.choice(success_messages), voice=-1)
            print(f"Процесс {process_name} успешно завершен")
        else:
            error_messages = [
                f"Не удалось завершить {process_name}.",
                f"{process_name} возможно не запущен.",
                f"Не могу найти процесс {process_name}."
            ]
            speak(random.choice(error_messages), voice=-1)
            print(f"Не удалось завершить процесс {process_name}. Возможно, процесс не запущен.")

    except Exception as e:
        error_messages = [
            "Ошибка при закрытии приложения.",
            "Не удалось завершить процесс.",
            "Возникла непредвиденная ошибка."
        ]
        speak(random.choice(error_messages), voice=-1)
        print(f"ОШИБКА при закрытии приложения: {e}")


# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ С ГОЛОСОВЫМ ВЫВОДОМ

def open_website(url):
    """Открывает указанный веб-сайт"""
    try:
        webbrowser.open(url)

        # Случайное сообщение об успехе
        messages = [
            f"Открываю сайт {url}",
            f"Загружаю {url}",
            f"Перехожу на {url}"
        ]
        speak(random.choice(messages), voice=-1)

    except Exception as e:
        error_messages = [
            "Не удалось открыть сайт.",
            "Ошибка при открытии веб-страницы.",
            "Проверьте правильность адреса сайта."
        ]
        speak(random.choice(error_messages), voice=-1)
        print(f"Ошибка при открытии сайта: {e}")

