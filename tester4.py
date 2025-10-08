# from tester import BrowserSearcher1
#
# import time
# searcher = BrowserSearcher1()
# searcher.CharChecker("Нарды DCDC")
# def CharChecker(promtForBrowser: str):
#     a = []
#     a1 = []
#     RUSSIAN_KEYBOARD_SYMBOLS_LIST = [
#         # Нижний регистр
#         'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ',
#         'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'э',
#         'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', 'ё', " ", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
#
#         # Верхний регистр
#         'Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х',
#         'Ъ','Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э',
#         'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', 'Ё'
#     ]
#     for i in range(len(promtForBrowser)):
#         a.append(promtForBrowser[i])
#         if (a[i] in RUSSIAN_KEYBOARD_SYMBOLS_LIST):
#             a1.append('RU')
#         else:
#             a1.append('EN')
#     for i in range(len(a)):
#         print(a)
#         print(a1)
# CharChecker("Нарды 123 GGGFFF")


import pyperclip
import subprocess
import time
import ctypes


def open_browser_and_search(browser_path: str, search_query: str):
    """Открывает браузер и вставляет текст в поисковую строку"""

    # Инициализация WinAPI
    user32 = ctypes.windll.user32
    VK_CONTROL = 0x11
    VK_RETURN = 0x0D
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002

    try:
        # Сохраняем исходное содержимое буфера обмена
        original_clipboard = pyperclip.paste()
        # print(f"📋 Сохранено исходное содержимое буфера: '{original_clipboard}'")

        # Копируем поисковый запрос в буфер обмена
        pyperclip.copy(search_query)
        # print(f"✅ Поисковый запрос скопирован: '{search_query}'")

        # Запускаем браузер
        # print(f"🚀 Запускаем браузер: {browser_path}")
        subprocess.Popen([browser_path])
        time.sleep(1)  # Ждем запуска браузера

        # Фокус на адресную строку (Ctrl+L)
        # print("🎯 Фокус на адресную строку...")
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(ord('L'), 0, 0, 0)
        user32.keybd_event(ord('L'), 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)

        # Вставляем текст из буфера обмена (Ctrl+V)
        # print("📝 Вставляем текст...")
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_V, 0, 0, 0)
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)

        # Выполняем поиск (Enter)
        # print("🔍 Выполняем поиск...")
        user32.keybd_event(VK_RETURN, 0, 0, 0)
        user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

        # Ждем немного перед восстановлением буфера
        time.sleep(1)

        # Восстанавливаем исходное содержимое буфера обмена
        pyperclip.copy(original_clipboard)
        # print(f"🔄 Исходное содержимое буфера восстановлено: '{original_clipboard}'")

        print("✅ Поиск успешно выполнен!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        # Пытаемся восстановить буфер в случае ошибки
        try:
            pyperclip.copy(original_clipboard)
            print(f"🔄 Буфер восстановлен после ошибки")
        except:
            pass
        return False


# Использование
if __name__ == "__main__":
    # Пример использования
    browser_path = r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe"
    search_text = "Нарды онлайн игра"

    open_browser_and_search(browser_path, search_text)
