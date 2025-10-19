import os
import webbrowser

import pyautogui
import time
from FuncLib import is_app_running, restore_browser_window
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
        # Если уже число
        if isinstance(tab_number, int):
            final_number = tab_number

        # Если строка
        elif isinstance(tab_number, str):
            tab_number = tab_number.lower().strip()

            # Пробуем извлечь цифру из строки
            if tab_number.isdigit():
                final_number = int(tab_number)
            else:
                # Ищем текстовое представление в словаре
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
                        print(f"❌ Не удалось распознать номер вкладки: '{original_input}'")
                        return False

        else:
            print(f"❌ Неподдерживаемый тип: {type(tab_number)}")
            return False

        # Проверяем диапазон
        if 1 <= final_number <= 9:
            pyautogui.hotkey('ctrl', str(final_number))
            time.sleep(0.3)
            current_tab = final_number - 1
            print(f"🎯 Перешли на {original_input} вкладку (#{final_number})")
            return True
        else:
            print(f"❌ Номер вкладки должен быть от 1 до 9, получено: {final_number}")
            return False

    except Exception as e:
        print(f"❌ Ошибка при переходе на вкладку '{original_input}': {e}")
        return False
