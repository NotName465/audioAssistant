import ctypes
import subprocess
import time


class BrowserSearcher1:
    """Класс для запуска браузера и ввода запросов на русском и английском"""

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

        # Таблицы преобразования между физическими клавишами и символами
        self.EN_LAYOUT_MAP = {
            'a': 'ф', 'b': 'и', 'c': 'с', 'd': 'в', 'e': 'у', 'f': 'а', 'g': 'п', 'h': 'р', 'i': 'ш', 'j': 'о',
            'k': 'л', 'l': 'д', 'm': 'ь', 'n': 'т', 'o': 'щ', 'p': 'з', 'q': 'й', 'r': 'к', 's': 'ы', 't': 'е',
            'u': 'г', 'v': 'м', 'w': 'ц', 'x': 'ч', 'y': 'н', 'z': 'я', '[': 'х', ']': 'ъ', ';': 'ж', "'": 'э',
            ',': 'б', '.': 'ю', '`': 'ё',
            'A': 'Ф', 'B': 'И', 'C': 'С', 'D': 'В', 'E': 'У', 'F': 'А', 'G': 'П', 'H': 'Р', 'I': 'Ш', 'J': 'О',
            'K': 'Л', 'L': 'Д', 'M': 'Ь', 'N': 'Т', 'O': 'Щ', 'P': 'З', 'Q': 'Й', 'R': 'К', 'S': 'Ы', 'T': 'Е',
            'U': 'Г', 'V': 'М', 'W': 'Ц', 'X': 'Ч', 'Y': 'Н', 'Z': 'Я', '{': 'Х', '}': 'Ъ', ':': 'Ж', '"': 'Э',
            '<': 'Б', '>': 'Ю', '~': 'Ё'
        }

        self.RU_LAYOUT_MAP = {v: k for k, v in self.EN_LAYOUT_MAP.items()}

    def get_physical_key_for_char(self, char, target_layout):  # (1)
        """Получить физическую клавишу для символа в указанной раскладке"""
        if target_layout == 'RU':
            # Если хотим ввести русский символ при английской раскладке
            if char in self.RU_LAYOUT_MAP:
                return self.RU_LAYOUT_MAP[char]
        else:  # EN
            # Если хотим ввести английский символ при русской раскладке
            if char in self.EN_LAYOUT_MAP:
                return self.EN_LAYOUT_MAP[char]
        return char  # Если символ не требует преобразования

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
            return "EN"  # По умолчанию английская

    def set_keyboard_layout(self, layout_name):  # (1)
        """Установить указанную раскладку клавиатуры"""
        try:
            if layout_name.upper() not in self.LAYOUTS:
                print(f"Неизвестная раскладка: {layout_name}")
                return False

            layout_code = self.LAYOUTS[layout_name.upper()]

            # Используем ActivateKeyboardLayout
            result = self.user32.ActivateKeyboardLayout(layout_code, 0)

            if result:
                print(f"Раскладка изменена на: {layout_name}")
                return True
            else:
                print("Не удалось изменить раскладку")
                return False

        except Exception as e:
            print(f"Ошибка при смене раскладки: {e}")
            return False

    def send_text_direct(self, text):  # (0)
        """Прямой ввод текста через преобразование раскладки"""
        # Фиксируем английскую раскладку для стабильности
        self.set_keyboard_layout('EN')
        time.sleep(0.5)

        print(f"Вводим текст: '{text}'")

        for char in text:
            if char == ' ':
                self.user32.keybd_event(self.VK_SPACE, 0, 0, 0)
                self.user32.keybd_event(self.VK_SPACE, 0, self.KEYEVENTF_KEYUP, 0)
            else:
                # Определяем физическую клавишу для символа
                physical_key = self.get_physical_key_for_char(char, 'RU')

                # Определяем нужно ли нажимать Shift
                shift_pressed = char.isupper() or (physical_key != char and physical_key.isupper())

                if shift_pressed:
                    self.user32.keybd_event(self.VK_SHIFT, 0, 0, 0)
                    time.sleep(0.02)

                # Нажимаем физическую клавишу
                vk_code = self.user32.VkKeyScanW(ord(physical_key.lower()))
                self.user32.keybd_event(vk_code & 0xFF, 0, 0, 0)
                self.user32.keybd_event(vk_code & 0xFF, 0, self.KEYEVENTF_KEYUP, 0)

                if shift_pressed:
                    time.sleep(0.02)
                    self.user32.keybd_event(self.VK_SHIFT, 0, self.KEYEVENTF_KEYUP, 0)

            time.sleep(0.05)

    def send_russian_text_simple(self, text):  # (0)
        """Простой ввод русского текста (для обратной совместимости)"""
        self.send_text_direct(text)

    def search(self, browser_path: str, search_query: str):  # (0)
        """Запускает браузер и вводит запрос"""

        print(f"Запуск поиска: '{search_query}'")

        # Запускаем браузер
        subprocess.Popen([browser_path])
        time.sleep(3)

        # Фокус на адресную строку
        self.user32.keybd_event(self.VK_CONTROL, 0, 0, 0)
        self.user32.keybd_event(ord('L'), 0, 0, 0)
        self.user32.keybd_event(ord('L'), 0, self.KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(self.VK_CONTROL, 0, self.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)

        # Вводим текст прямым методом
        self.send_text_direct(search_query)
        time.sleep(0.5)

        # Выполняем поиск
        self.user32.keybd_event(self.VK_RETURN, 0, 0, 0)
        self.user32.keybd_event(self.VK_RETURN, 0, self.KEYEVENTF_KEYUP, 0)

