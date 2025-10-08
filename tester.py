import subprocess

import psutil
import ctypes
import os
import time
import pyperclip


def is_app_running(app_path):
    """Проверяет, запущено ли приложение по его пути"""
    try:
        # Нормализуем путь для сравнения
        target_path = os.path.abspath(app_path).lower()

        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                process_exe = process.info['exe']
                if process_exe and os.path.abspath(process_exe).lower() == target_path:
                    print(f"✅ Приложение запущено (PID: {process.info['pid']})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        print("❌ Приложение не запущено")
        return False

    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
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

        if(is_app_running(browser_path)):
            restore_browser_window()
        else:
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

open_browser_and_search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Нарды онлайн")
