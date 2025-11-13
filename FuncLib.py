import psutil
import ctypes
import os
import time
import pyperclip
import webbrowser
import pyautogui

# Инициализация WinAPI
user32 = ctypes.windll.user32
VK_CONTROL = 0x11
VK_RETURN = 0x0D
VK_V = 0x56
VK_W = 0x57
VK_T = 0x54
KEYEVENTF_KEYUP = 0x0002

def is_app_running(app_path):
    """Проверяет, запущено ли приложение по его пути"""
    try:
        # Нормализуем путь для сравнения
        target_path = os.path.abspath(app_path).lower()

        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_exe = process.info['exe']
                if process_exe and os.path.abspath(process_exe).lower() == target_path:
                    print(f"Приложение запущено (PID: {process.info['pid']})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print("Приложение не запущено")
        return False

    except Exception as e:
        print(f"Ошибка проверки: {e}")
        return False

def restore_browser_window():
    """Специальная функция для восстановления окна браузера"""
    user32 = ctypes.windll.user32

    def enum_windows(hwnd, param):
        try:
            # Проверяем видимость
            if not user32.IsWindowVisible(hwnd):
                return True

            # Получаем заголовок
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                title = buffer.value

                # Ищем окна браузера по заголовку
                if title and any(keyword in title for keyword in ['Yandex', 'Яндекс Браузер', 'Opera', 'Chrome', 'Firefox', 'Edge']):
                    print(f"Найден браузер: {title}")

                    if user32.IsIconic(hwnd):
                        user32.ShowWindow(hwnd, 9)

                    user32.SetForegroundWindow(hwnd)
                    return False
        except:
            pass
        return True

    callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_windows)
    user32.EnumWindows(callback, 0)


def open_browser_and_search(browser_path: str, search_query: str):
    """Открывает браузер и вставляет текст в поисковую строку"""

    try:
        # Сохраняем исходное содержимое буфера обмена
        original_clipboard = pyperclip.paste()
        # print(f"Сохранено исходное содержимое буфера: '{original_clipboard}'")

        # Копируем поисковый запрос в буфер обмена
        pyperclip.copy(search_query)
        # print(f"Поисковый запрос скопирован: '{search_query}'")

        if(is_app_running(browser_path)):
            restore_browser_window()
        else:
            try:
                os.startfile(browser_path)
            except:
                webbrowser.open("http://yandex.ru")
            time.sleep(1)
        # Фокус на адресную строку
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        # Вставляем текст из буфера обмена (Ctrl+V)
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)

        # Нажатие Enter
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

        time.sleep(1)

        # Восстановление исходного содержимого буфера обмена
        pyperclip.copy(original_clipboard)

        print("Поиск успешно выполнен!")
        return True

    except Exception as e:
        print(f"Ошибка: {e}")
        # Пытаемся восстановить буфер в случае ошибки
        try:
            pyperclip.copy(original_clipboard)
            print(f"🔄 Буфер восстановлен после ошибки")
        except:
            pass
        return False



def remove_keywords(input_string, remove_all=True, case_sensitive=False):
    keywords_dict = {
        "browser": ['найди', "в", "интернете"],
        "go_to_tab": ["открой", "вкладку"]
    }

    if not case_sensitive:
        # Приводим к нижнему регистру для сравнения, но сохраняем оригинал для результата
        original_string = input_string
        input_string_lower = input_string.lower()
        keywords_dict_lower = {key: [word.lower() for word in words]
                               for key, words in keywords_dict.items()}
    else:
        original_string = input_string
        input_string_lower = input_string
        keywords_dict_lower = keywords_dict

    # Собираем все ключевые слова
    all_keywords = []
    for words in keywords_dict_lower.values():
        if isinstance(words, list):
            all_keywords.extend(words)

    # Разбиваем строку на слова с сохранением разделителей
    words = original_string.split()
    words_lower = input_string_lower.split()

    removed_words = []
    result_words = []

    for i, word in enumerate(words):
        word_lower = words_lower[i]
        word_removed = False

        # Проверяем, является ли текущее слово ключевым
        if remove_all:
            # Удаляем все ключевые слова
            if word_lower not in all_keywords:
                result_words.append(word)
            else:
                removed_words.append(word)
        else:
            # Удаляем только первое ключевое слово
            if word_lower in all_keywords and not removed_words:
                removed_words.append(word)
                word_removed = True
            else:
                result_words.append(word)

    # Собираем обратно в строку
    result = ' '.join(result_words)

    return result


def close_tab():
    """Закрыть текущую вкладку"""
    # pyautogui.hotkey('ctrl', 'w')
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_W, 0, 0, 0)
    user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)
    print("Вкладка закрыта")

def new_tab():
    """Новая вкладка"""
    # pyautogui.hotkey('ctrl', 't')

    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_T, 0, 0, 0)
    user32.keybd_event(VK_T, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    time.sleep(0.5)
    print("Новая вкладка создана")


def go_to_tab(tab_number, browser_path: str = " "):
    if (not is_app_running(browser_path)):
        restore_browser_window()
    else:
        try:
            os.startfile(browser_path)
        except:
            webbrowser.open("http://yandex.ru")

    # Словарь для преобразования текста в цифры
    number_words = {
        'перв': 1, 'перва': 1, 'первой': 1, 'первую': 1, 'один': 1,
        'втор': 2, 'втора': 2, 'второй': 2, 'вторую': 2, 'два': 2,
        'трет': 3, 'треть': 3, 'третий': 3, 'третью': 3, 'три': 3,
        'четверт': 4, 'четверта': 4, 'четвертой': 4, 'четвертую': 4, 'четыре': 4,
        'пят': 5, 'пята': 5, 'пятый': 5, 'пятую': 5, 'пять': 5,
        'шест': 6, 'шеста': 6, 'шестой': 6, 'шестую': 6, 'шесть': 6,
        'седьм': 7, 'седьма': 7, 'седьмой': 7, 'седьмую': 7, 'семь': 7,
        'восьм': 8, 'восьма': 8, 'восьмой': 8, 'восьмую': 8, 'восемь': 8,
        'девят': 9, 'девята': 9, 'девятый': 9, 'девятую': 9, 'девять': 9,
    }
    original_input = tab_number

    try:
        if isinstance(tab_number, int):
            final_number = tab_number

        elif isinstance(tab_number, str):
            tab_number = tab_number.lower().strip()
            if tab_number.isdigit():
                final_number = int(tab_number)
            else:
                found_number = None
                for word, number in number_words.items():
                    if word in tab_number:
                        found_number = number
                        break

                if found_number:
                    final_number = found_number
                else:
                    # Пробуем извлечь цифру из смешанного текста
                    digits = ''.join(filter(str.isdigit, tab_number))
                    if digits:
                        final_number = int(digits)
                    else:
                        print(f"Не удалось распознать номер вкладки: '{original_input}'")
                        return False

        else:
            print(f"Неподдерживаемый тип: {type(tab_number)}")
            return False

        # Проверяем диапазон
        if 1 <= final_number <= 9:
            pyautogui.hotkey('ctrl', str(final_number))
            time.sleep(0.3)
            current_tab = final_number - 1
            print(f"Перешли на {original_input} вкладку (#{final_number})")
            return True
        else:
            print(f"Номер вкладки должен быть от 1 до 9, получено: {final_number}")
            return False

    except Exception as e:
        print(f"Ошибка при переходе на вкладку '{original_input}': {e}")
        return False


def scroll_down(forScroll: int = 500):
    pyautogui.scroll(-forScroll)
    time.sleep(0.5)


def scroll_up(forScroll: int = 500):
    pyautogui.scroll(forScroll)
    time.sleep(0.5)


def volume_up():
    for i in range(5):
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        time.sleep(0.08)
    return "Громкость увеличена"


def volume_down():
    for i in range(5):
        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        time.sleep(0.08)
    return "Громкость уменьшена"


def mute():
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
    return "Звук отключен"



