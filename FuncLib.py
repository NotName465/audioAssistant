import ctypes
import subprocess
import time


class BrowserSearcher:
    """Класс для запуска браузера и ввода русских запросов"""

    # Взаимодействие с выводчиком текста (0)
    # Взаимодействие с раскладкой (1)

    def __init__(self):
        # Настройка ctypes для работы с Win32 API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        # Константы
        self.VK_SHIFT = 0x10  # (0)
        self.VK_CONTROL = 0x11  # (0)
        self.VK_RETURN = 0x0D  # (0)
        self.VK_SPACE = 0x20  # (0)
        self.KEYEVENTF_KEYUP = 0x0002  # (0)

        self.WM_INPUTLANGCHANGEREQUEST = 0x0050  # (1)
        self.WM_INPUTLANGCHANGE = 0x0051  # (1)

        # Раскладки
        self.LAYOUTS = {
            'EN': 0x409,
            'RU': 0x419,
        }

    def get_keyboard_layout(self):  # (1)
        """Получить текущую раскладку клавиатуры"""
        hwnd = self.user32.GetForegroundWindow()
        thread_id = self.kernel32.GetCurrentThreadId()
        layout_id = self.user32.GetKeyboardLayout(thread_id)

        # Младшее слово содержит код языка
        lang_id = layout_id & 0xFFFF

        if lang_id == 0x409:  # Английский
            return "EN"
        elif lang_id == 0x419:  # Русский
            return "RU"
        else:
            return f"Unknown: {hex(lang_id)}"

    def track_layout_changes(self):  # (1)
        """Отслеживать изменения раскладки"""
        last_layout = self.get_keyboard_layout()
        print(f"Текущая раскладка: {last_layout}")

        try:
            while True:
                current_layout = self.get_keyboard_layout()
                if current_layout != last_layout:
                    print(f"Раскладка изменена: {last_layout} -> {current_layout}")
                    last_layout = current_layout
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Отслеживание остановлено")

    def set_keyboard_layout(self, layout_name):  # (1)
        """Установить указанную раскладку клавиатуры"""
        try:
            if layout_name.upper() not in self.LAYOUTS:
                print(f"Неизвестная раскладка: {layout_name}")
                print(f"Доступные раскладки: {', '.join(self.LAYOUTS.keys())}")
                return False

            layout_code = self.LAYOUTS[layout_name.upper()]
            hwnd = self.user32.GetForegroundWindow()

            # Используем ActivateKeyboardLayout вместо PostMessageW
            result = self.user32.ActivateKeyboardLayout(layout_code, 0)

            if result:
                print(f"Раскладка успешно изменена на: {layout_name}")
                return True
            else:
                print("Не удалось изменить раскладку")
                return False

        except Exception as e:
            print(f"Ошибка при смене раскладки: {e}")
            return False

    def send_russian_text_simple(self, text):  # (0)
        """Простой ввод русского текста"""
        # Увеличиваем задержку для стабилизации раскладки
        time.sleep(1)

        for char in text:
            if char == ' ':
                self.user32.keybd_event(self.VK_SPACE, 0, 0, 0)
                self.user32.keybd_event(self.VK_SPACE, 0, self.KEYEVENTF_KEYUP, 0)
            else:
                # Для русских букв просто отправляем скан-коды
                # Это сработает если в системе включена русская раскладка
                vk_code = self.user32.VkKeyScanW(ord(char))
                # Нажимаем клавишу
                self.user32.keybd_event(vk_code & 0xFF, 0, 0, 0)
                self.user32.keybd_event(vk_code & 0xFF, 0, self.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)

    def search(self, browser_path: str, search_query: str):  # (0)
        """Запускает браузер и вводит русский запрос"""

        # Сначала устанавливаем русскую раскладку
        print("Устанавливаем русскую раскладку...")
        self.set_keyboard_layout("RU")

        # Даем больше времени для смены раскладки
        time.sleep(2)

        # Запускаем браузер
        subprocess.Popen([browser_path])

        # Увеличиваем время ожидания запуска браузера
        time.sleep(3)

        # Фокус на адресную строку
        self.user32.keybd_event(self.VK_CONTROL, 0, 0, 0)
        self.user32.keybd_event(ord('L'), 0, 0, 0)
        self.user32.keybd_event(ord('L'), 0, self.KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(self.VK_CONTROL, 0, self.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)

        # Вводим текст
        self.send_russian_text_simple(search_query)
        time.sleep(0.5)

        # Выполняем поиск
        self.user32.keybd_event(self.VK_RETURN, 0, 0, 0)
        self.user32.keybd_event(self.VK_RETURN, 0, self.KEYEVENTF_KEYUP, 0)


# Использование
if __name__ == "__main__":
    searcher = BrowserSearcher()
    searcher.search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Нарды")