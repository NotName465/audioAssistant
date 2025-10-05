import ctypes
import subprocess
import time
# Взаимодействие с выводчиком текста (0)
# Взаимодействие с раскладкой (1)



# Настройка ctypes для работы с Win32 API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Константы
VK_SHIFT = 0x10 # (0)
VK_CONTROL = 0x11 # (0)
VK_RETURN = 0x0D # (0)
VK_SPACE = 0x20 # (0)
KEYEVENTF_KEYUP = 0x0002 # (0)

WM_INPUTLANGCHANGEREQUEST = 0x0050 # (1)
WM_INPUTLANGCHANGE = 0x0051 # (1)
# Раскладки
LAYOUTS = {
    'EN': 0x409,
    'RU': 0x419,
}


def get_keyboard_layout(): # (1)
    """Получить текущую раскладку клавиатуры"""
    hwnd = user32.GetForegroundWindow()
    thread_id = kernel32.GetCurrentThreadId()
    layout_id = user32.GetKeyboardLayout(thread_id)

    # Младшее слово содержит код языка
    lang_id = layout_id & 0xFFFF

    if lang_id == 0x409:  # Английский
        return "EN"
    elif lang_id == 0x419:  # Русский
        return "RU"
    else:
        return f"Unknown: {hex(lang_id)}"


def track_layout_changes(): # (1)
    """Отслеживать изменения раскладки"""
    last_layout = get_keyboard_layout()
    print(f"Текущая раскладка: {last_layout}")

    try:
        while True:
            current_layout = get_keyboard_layout()
            if current_layout != last_layout:
                print(f"Раскладка изменена: {last_layout} -> {current_layout}")
                last_layout = current_layout
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Отслеживание остановлено")


def set_keyboard_layout(layout_name): # (1)
    """Установить указанную раскладку клавиатуры"""
    try:
        if layout_name.upper() not in LAYOUTS:
            print(f"Неизвестная раскладка: {layout_name}")
            print(f"Доступные раскладки: {', '.join(LAYOUTS.keys())}")
            return False

        layout_code = LAYOUTS[layout_name.upper()]
        hwnd = user32.GetForegroundWindow()

        # Пытаемся сменить раскладку
        result = user32.PostMessageW(
            hwnd,
            0x0050,  # WM_INPUTLANGCHANGEREQUEST
            0,  # wParam
            layout_code  # lParam - код раскладки
        )

        if result:
            print(f"Раскладка успешно изменена на: {layout_name}")
            return True
        else:
            print("Не удалось изменить раскладку")
            return False

    except Exception as e:
        print(f"Ошибка при смене раскладки: {e}")
        return False


def send_russian_text_simple(text): # (0)
    """Простой ввод русского текста"""
    for char in text:
        if char == ' ':
            user32.keybd_event(VK_SPACE, 0, 0, 0)
            user32.keybd_event(VK_SPACE, 0, KEYEVENTF_KEYUP, 0)
        else:
            # Для русских букв просто отправляем скан-коды
            # Это сработает если в системе включена русская раскладка
            vk_code = user32.VkKeyScanW(ord(char))
            user32.keybd_event(vk_code & 0xFF, 0, 0, 0)
            user32.keybd_event(vk_code & 0xFF, 0, KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)


def Searcher(browser_path: str, search_query: str): # (0)
    """Запускает браузер и вводит русский запрос"""

    subprocess.Popen([browser_path])
    time.sleep(1)

    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(ord('L'), 0, 0, 0)
    user32.keybd_event(ord('L'), 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)

    send_russian_text_simple(search_query)
    time.sleep(0.5)

    user32.keybd_event(VK_RETURN, 0, 0, 0)
    user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)

set_keyboard_layout("RU")

Searcher(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Нарды")