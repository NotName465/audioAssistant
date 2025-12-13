import pyautogui
import time
import os
import json
import torch
import sounddevice as sd
import random


# Загрузка конфигурации голоса
def load_voice_config():
    """Загружает конфигурацию голоса из config.json"""
    config_path = "config.json"
    default_config = {
        "selected_microphone": "",
        "selected_voice": 1  # По умолчанию голос baya (индекс 1)
    }

    try:
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
            print(f"Создан файл конфигурации голоса: {config_path}")
            return default_config
    except Exception as e:
        print(f"Ошибка загрузки конфигурации голоса: {e}")
        return default_config


# Загрузка путей из cfg.json
def load_paths():
    """Загружает пути из cfg.json"""
    cfg_path = "cfg.json"
    default_paths = {
        "Путь Доты": {
            "value": r"C:\Users\user\Desktop\Dota 2.url",
            "protected": True
        },
        "Путь Браузера": {
            "value": r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe",
            "protected": True
        }
    }

    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                # Очищаем путь от лишних символов
                for key in cfg:
                    if isinstance(cfg[key], dict) and "value" in cfg[key]:
                        path_value = cfg[key]["value"]
                        # Убираем r"" если есть
                        if path_value.startswith('r"') and path_value.endswith('"'):
                            path_value = path_value[2:-1]
                        cfg[key]["value"] = path_value
                return cfg
        else:
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(default_paths, f, ensure_ascii=False, indent=2)
            print(f"Создан файл путей: {cfg_path}")
            return default_paths
    except Exception as e:
        print(f"Ошибка загрузки путей: {e}")
        return default_paths


# Загружаем конфиги
with open("config.json", "r") as f:
    voice_config = json.load(f)
SELECTED_VOICE = int(voice_config.get("selected_voice"))
paths_config = load_paths()

# Извлекаем пути из конфига
DOTA_PATH = paths_config.get("Путь Доты", {}).get("value", r"C:\Users\user\Desktop\Dota 2.url")
BROWSER_PATH = paths_config.get("Путь Браузера", {}).get("value",
                                                         r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe")


# Класс для отслеживания истории сообщений
class MessageHistory:
    def __init__(self, history_size=5):
        self.history = []
        self.history_size = history_size
        self.voice_history = []

    def add_message(self, message, voice):
        self.history.append(message)
        self.voice_history.append(voice)

        if len(self.history) > self.history_size:
            self.history.pop(0)
            self.voice_history.pop(0)

    def get_unique_message(self, messages, voice):
        unique_messages = [msg for msg in messages if msg not in self.history]

        if unique_messages:
            selected = random.choice(unique_messages)
        else:
            self.history.clear()
            self.voice_history.clear()
            selected = random.choice(messages)

        self.add_message(selected, voice)
        return selected


# Создаем глобальный объект для отслеживания истории сообщений
message_history = MessageHistory()

print("Загрузка модели Silero TTS...")
try:
    model, _ = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_tts',
        language='ru',
        speaker='ru_v3'
    )
    print("✅ Модель Silero TTS загружена")
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")
    raise


def speak(text, voice: int = None):

    voices = ['aidar', 'baya', 'kseniya', 'xenia']

    if voice is None:
        voice_idx = SELECTED_VOICE
    elif voice == -1:
        last_voice = message_history.voice_history[-1] if message_history.voice_history else SELECTED_VOICE
        available_voices = [i for i in range(len(voices)) if i != last_voice]
        voice_idx = random.choice(available_voices) if available_voices else SELECTED_VOICE
    else:
        voice_idx = voice % len(voices)

    voice_name = voices[voice_idx]

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

        message_history.voice_history.append(voice_idx)
        if len(message_history.voice_history) > 5:
            message_history.voice_history.pop(0)

    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")


def num_to_words_ru(num):
    """Преобразует число в слова на русском"""
    if num == 0:
        return "ноль"

    units = {
        1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять"
    }

    teens = {
        10: "десять", 11: "одиннадцать", 12: "двенадцать", 13: "тринадцать",
        14: "четырнадцать", 15: "пятнадцать", 16: "шестнадцать",
        17: "семнадцать", 18: "восемнадцать", 19: "девятнадцать"
    }

    tens = {
        20: "двадцать", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
        60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят", 90: "девяносто"
    }

    hundreds = {
        100: "сто", 200: "двести", 300: "триста", 400: "четыреста",
        500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот",
        900: "девятьсот"
    }

    if num in units:
        return units[num]
    elif num in teens:
        return teens[num]
    elif num in tens:
        return tens[num]
    elif num in hundreds:
        return hundreds[num]

    result = []

    if num >= 1000:
        thou = num // 1000
        if thou == 1:
            result.append("тысяча")
        elif thou == 2:
            result.append("две тысячи")
        elif thou == 3:
            result.append("три тысячи")
        elif thou == 4:
            result.append("четыре тысячи")
        elif thou == 5:
            result.append("пять тысяч")
        elif thou == 6:
            result.append("шесть тысяч")
        elif thou == 7:
            result.append("семь тысяч")
        elif thou == 8:
            result.append("восемь тысяч")
        else:
            return f"{num_to_words_ru(thou)} тысяч"
        num %= 1000

    if num >= 100:
        hundreds_part = (num // 100) * 100
        if hundreds_part in hundreds:
            result.append(hundreds[hundreds_part])
        num %= 100

    if num >= 20:
        tens_part = (num // 10) * 10
        if tens_part in tens:
            result.append(tens[tens_part])
        num %= 10

    if num >= 10:
        if num in teens:
            result.append(teens[num])
        num = 0

    if num > 0:
        result.append(units[num])

    return " ".join(result)


# Создаем полный словарь всех чисел от 1 до 8000
word_to_digit = {}

for i in range(1, 8001):
    word = num_to_words_ru(i)
    word_to_digit[word] = i

    # Добавляем варианты без пробелов
    without_spaces = word.replace(" ", "")
    if without_spaces != word:
        word_to_digit[without_spaces] = i

    # Добавляем варианты с дефисами
    with_hyphen = word.replace(" ", "-")
    if with_hyphen != word:
        word_to_digit[with_hyphen] = i


def word_to_number(word):
    """Преобразует слово в число"""
    word = word.strip().lower()

    # Прямой поиск в словаре
    if word in word_to_digit:
        return word_to_digit[word]

    return None


def extract_number_from_text(text_list):
    """Извлекает число из списка слов"""
    # Очищаем от слов "пикселей", "пикселя", "пиксель"
    clean_words = []
    for word in text_list:
        if isinstance(word, str):
            clean_word = word.lower().replace("пикселей", "").replace("пикселя", "").replace("пиксель", "").strip()
            if clean_word:
                clean_words.append(clean_word)

    # Пробуем найти числа разной длины (от 4 до 1 слов)
    for start in range(len(clean_words)):
        for length in range(min(4, len(clean_words) - start), 0, -1):  # От 4 до 1
            phrase = " ".join(clean_words[start:start + length])
            number = word_to_number(phrase)

            if number is not None:
                return number

    def get_cursor_movement():
        try:
            with open('cfg.json', 'r', encoding='utf-8') as f:
                v = json.load(f).get("Перемещение курсора(в пикселях)", {}).get("value", "").strip()
                if v:
                    if v.startswith('r"') and v.endswith('"'): v = v[2:-1]
                    return int(v)
        except:
            pass
        return 100
    return get_cursor_movement()


def right(pixels: int):
    """Переместить мышь вправо"""
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x + pixels, y)

        messages = [
            f"Перемещаю вправо.",
            f"Двигаю мышь вправо.",
            f"Сдвигаю курсор вправо.",
            f"Перемещение вправо.",
            f"Мышь смещена вправо."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"✅ Перемещено вправо на {pixels} пикселей")

    except Exception as e:
        error_messages = [
            "Не удалось переместить мышь вправо.",
            "Ошибка при перемещении курсора.",
            "Проблема с движением мыши.",
            "Не могу сдвинуть мышь.",
            "Ошибка перемещения."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при перемещении вправо: {e}")


def left(pixels: int):
    """Переместить мышь влево"""
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x - pixels, y)

        messages = [
            f"Перемещаю влево.",
            f"Двигаю мышь влево.",
            f"Сдвигаю курсор влево.",
            f"Перемещение влево.",
            f"Мышь смещена влево."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"✅ Перемещено влево на {pixels} пикселей")

    except Exception as e:
        error_messages = [
            "Не удалось переместить мышь влево.",
            "Ошибка при перемещении курсора.",
            "Проблема с движением мыши.",
            "Не могу сдвинуть мышь.",
            "Ошибка перемещения."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при перемещении влево: {e}")


def down(pixels: int):
    """Переместить мышь вниз"""
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x, y + pixels)

        messages = [
            f"Перемещаю вниз на.",
            f"Двигаю мышь вниз на.",
            f"Сдвигаю курсор вниз.",
            f"Перемещение вниз.",
            f"Мышь смещена вниз."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"✅ Перемещено вниз на {pixels} пикселей")

    except Exception as e:
        error_messages = [
            "Не удалось переместить мышь вниз.",
            "Ошибка при перемещении курсора.",
            "Проблема с движением мыши.",
            "Не могу сдвинуть мышь.",
            "Ошибка перемещения."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при перемещении вниз: {e}")


def up(pixels: int):
    """Переместить мышь вверх"""
    try:
        x, y = pyautogui.position()
        pyautogui.moveTo(x, y - pixels)

        messages = [
            f"Перемещаю вверх.",
            f"Двигаю мышь вверх.",
            f"Сдвигаю курсор вверх.",
            f"Перемещение вверх.",
            f"Мышь смещена вверх."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"✅ Перемещено вверх на {pixels} пикселей")

    except Exception as e:
        error_messages = [
            "Не удалось переместить мышь вверх.",
            "Ошибка при перемещении курсора.",
            "Проблема с движением мыши.",
            "Не могу сдвинуть мышь.",
            "Ошибка перемещения."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при перемещении вверх: {e}")


def left_click():
    """Левый клик мышкой"""
    try:
        pyautogui.click()

        messages = [
            "Выполняю левый клик.",
            "Кликаю левой кнопкой мыши.",
            "Совершаю клик левой кнопкой.",
            "Левый клик выполнен.",
            "Нажимаю левую кнопку мыши."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("✅ Выполнен левый клик")

    except Exception as e:
        error_messages = [
            "Не удалось выполнить клик.",
            "Ошибка при нажатии кнопки мыши.",
            "Проблема с кликом.",
            "Не могу кликнуть.",
            "Ошибка клика."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при клике: {e}")


def double_click():
    """Двойной клик мышкой"""
    try:
        pyautogui.doubleClick()

        messages = [
            "Выполняю двойной клик.",
            "Кликаю дважды левой кнопкой.",
            "Совершаю двойное нажатие.",
            "Двойной клик выполнен.",
            "Нажимаю левую кнопку дважды."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("✅ Выполнен двойной клик")

    except Exception as e:
        error_messages = [
            "Не удалось выполнить двойной клик.",
            "Ошибка при двойном нажатии.",
            "Проблема с двойным кликом.",
            "Не могу кликнуть дважды.",
            "Ошибка двойного клика."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при двойном клике: {e}")


def right_click():
    """Правый клик мышкой"""
    try:
        pyautogui.rightClick()

        messages = [
            "Выполняю правый клик.",
            "Кликаю правой кнопкой мыши.",
            "Совершаю клик правой кнопкой.",
            "Правый клик выполнен.",
            "Нажимаю правую кнопку мыши."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("✅ Выполнен правый клик")

    except Exception as e:
        error_messages = [
            "Не удалось выполнить правый клик.",
            "Ошибка при нажатии правой кнопки.",
            "Проблема с правым кликом.",
            "Не могу кликнуть правой кнопкой.",
            "Ошибка правого клика."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при правом клике: {e}")


def for_close(url):
    """Возвращает имя файла для закрытия процесса"""
    return os.path.basename(url)


def close_browser(url=""):
    """Закрывает браузер"""
    try:
        if not url:
            process_name = for_close(BROWSER_PATH)
        else:
            process_name = for_close(url)

        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'

        messages_before = [
            "Закрываю браузер.",
            "Завершаю работу браузера.",
            "Выключаю браузер.",
            "Останавливаю браузер.",
            "Завершаю процесс браузера."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")

        if result == 0:
            success_messages = [
                "Браузер успешно закрыт.",
                "Работа браузера завершена.",
                "Браузер выключен.",
                "Процесс браузера остановлен.",
                "Закрытие браузера выполнено."
            ]
            message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
            speak(message, voice=None)
        else:
            error_messages = [
                "Не удалось закрыть браузер.",
                "Браузер возможно не запущен.",
                "Процесс браузера не найден.",
                "Проблема с завершением браузера.",
                "Не могу найти запущенный браузер."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Ошибка при закрытии браузера.",
            "Не удалось завершить процесс.",
            "Возникла ошибка при выключении браузера.",
            "Проблема с закрытием браузера.",
            "Ошибка системной команды."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при закрытии браузера: {e}")


def open_dota(dota_path=""):
    """Открывает Dota 2"""
    try:
        path_to_open = dota_path if dota_path else DOTA_PATH

        if not os.path.exists(path_to_open):
            error_messages = [
                "Файл игры не найден.",
                "Не могу найти ярлык игры.",
                "Путь к игре указан неверно.",
                "Ярлык игры отсутствует.",
                "Проверьте путь к игре в настройках."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Файл не найден: {path_to_open}")
            return

        messages_before = [
            "Запускаю игру.",
            "Открываю игру.",
            "Загружаю игру.",
            "Начинаю запуск игры.",
            "Инициализирую запуск игры."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        os.startfile(path_to_open)

        success_messages = [
            "Игра запускается.",
            "Игра открывается.",
            "Игра загружается.",
            "Запуск игры выполнен.",
            "Игра начинает загрузку."
        ]
        message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Не удалось запустить игру.",
            "Ошибка при открытии игры.",
            "Проблема с запуском игры.",
            "Не могу открыть игру.",
            "Ошибка доступа к файлу игры."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при открытии Dota 2: {e}")


def close_dota():
    """Закрывает Dota 2"""
    try:
        messages_before = [
            "Закрываю игру.",
            "Завершаю игру.",
            "Выключаю игру.",
            "Останавливаю процесс игры.",
            "Завершаю работу игры."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        result = os.system("taskkill /f /im dota2.exe >nul 2>&1")

        if result == 0:
            success_messages = [
                "Игра успешно закрыта.",
                "Игра завершена.",
                "Игра выключена.",
                "Процесс игры остановлен.",
                "Закрытие игры выполнено."
            ]
            message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
            speak(message, voice=None)
        else:
            error_messages = [
                "Игра возможно не запущена.",
                "Не удалось закрыть игру.",
                "Процесс игры не найден.",
                "Проблема с завершением игры.",
                "Не могу найти запущенную игру."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Ошибка при закрытии игры.",
            "Не удалось завершить процесс.",
            "Возникла ошибка при выключении игры.",
            "Проблема с закрытием игры.",
            "Ошибка системной команды."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при закрытии Dota 2: {e}")


def open_browser_and_search(browser_path, search_query):
    """Открывает браузер и выполняет поиск"""
    try:
        actual_browser_path = browser_path if browser_path and os.path.exists(browser_path) else BROWSER_PATH

        os.startfile(actual_browser_path)
        time.sleep(2)

        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)

        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        pyautogui.write(f'{search_query}')
        pyautogui.press('enter')

        messages = [
            "Ищу информацию по вашему запросу.",
            "Выполняю поиск в интернете.",
            "Загружаю результаты поиска.",
            "Начинаю поиск в сети.",
            "Обрабатываю ваш поисковый запрос."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Не удалось выполнить поиск.",
            "Возникла ошибка при открытии браузера.",
            "Поиск не удался, проверьте подключение.",
            "Проблемы с доступом в интернет.",
            "Браузер не смог открыться."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
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

    messages = [
        "Вкладка закрыта.",
        "Закрываю текущую вкладку.",
        "Вкладка успешно закрыта.",
        "Текущее окно закрыто.",
        "Убираю активную вкладку."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def new_tab():
    """Открывает новую вкладку браузера"""
    pyautogui.hotkey('ctrl', 't')

    messages = [
        "Новая вкладка открыта.",
        "Создаю чистую вкладку.",
        "Открываю новую вкладку для работы.",
        "Добавляю свежую вкладку.",
        "Вкладка готова к использованию."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def go_to_tab(tab_number):
    """Переходит на указанную вкладку браузера"""
    try:
        tab_num = int(tab_number)
        if 1 <= tab_num <= 8:
            pyautogui.hotkey('ctrl', str(tab_num))

            messages = [
                f"Перехожу на вкладку номер {tab_num}.",
                f"Переключаюсь на вкладку {tab_num}.",
                f"Вкладка {tab_num} теперь активна.",
                f"Активирую вкладку {tab_num}.",
                f"Фокус на вкладке {tab_num}."
            ]
            message = message_history.get_unique_message(messages, SELECTED_VOICE)
            speak(message, voice=None)
        else:
            error_messages = [
                "Можно переключаться только между первыми восемью вкладками.",
                "Доступны только вкладки с первой по восьмую.",
                "Номер вкладки должен быть от одного до восьми.",
                "Пожалуйста, выберите вкладку от 1 до 8.",
                "Диапазон вкладок ограничен восемью."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
    except ValueError:
        error_messages = [
            "Номер вкладки должен быть числом.",
            "Пожалуйста, укажите цифру от одного до восьми.",
            "Не понимаю номер вкладки, используйте цифры.",
            "Введите номер вкладки цифрой.",
            "Для переключения нужна цифра от 1 до 8."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("Номер вкладки должна быть числом")


def scroll_down():
    """Прокручивает страницу вниз"""
    pyautogui.scroll(-3)

    messages = [
        "Прокручиваю вниз.",
        "Листаю страницу ниже.",
        "Спускаюсь по странице.",
        "Скроллю вниз.",
        "Перемещаюсь к нижней части."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def scroll_up():
    """Прокручивает страницу вверх"""
    pyautogui.scroll(3)

    messages = [
        "Прокручиваю вверх.",
        "Листаю страницу выше.",
        "Поднимаюсь по странице.",
        "Скроллю вверх.",
        "Возвращаюсь к началу."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def volume_up():
    """Увеличивает громкость"""
    pyautogui.press('volumeup')

    messages = [
        "Увеличиваю громкость.",
        "Становится громче.",
        "Прибавляю звук.",
        "Делаю погромче.",
        "Поднимаю уровень звука."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def volume_down():
    """Уменьшает громкость"""
    pyautogui.press('volumedown')

    messages = [
        "Уменьшаю громкость.",
        "Становится тише.",
        "Убавляю звук.",
        "Делаю потише.",
        "Снижаю уровень звука."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def mute():
    """Включает/выключает звук"""
    pyautogui.press('volumemute')

    messages = [
        "Переключаю звук.",
        "Включаю или выключаю звук.",
        "Изменяю состояние звука.",
        "Меняю режим звука.",
        "Активирую или деактивирую звук."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def open_browser(browser_path=""):
    """Открывает браузер"""
    try:
        if not browser_path or browser_path == "browserUrl":
            path_to_open = BROWSER_PATH
        else:
            path_to_open = browser_path

        if not os.path.exists(path_to_open):
            error_messages = [
                "Браузер не найден.",
                "Не могу найти файл браузера.",
                "Путь к браузеру указан неверно.",
                "Файл браузера отсутствует.",
                "Проверьте путь к браузеру в настройках."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Файл не найден: {path_to_open}")
            return

        messages_before = [
            "Открываю браузер.",
            "Запускаю браузер.",
            "Загружаю браузер.",
            "Начинаю запуск браузера.",
            "Инициализирую браузер."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        os.startfile(path_to_open)

        success_messages = [
            "Браузер запускается.",
            "Браузер открывается.",
            "Браузер загружается.",
            "Запуск браузера выполнен.",
            "Браузер начинает загрузку."
        ]
        message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Браузер успешно открыт")

    except Exception as e:
        error_messages = [
            "Не удалось запустить браузер.",
            "Ошибка при открытии браузера.",
            "Проблема с запуском браузера.",
            "Не могу открыть браузер.",
            "Ошибка доступа к файлу браузера."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при открытии браузера: {e}")


def AbsolutStarter(file_path: str = ""):
    """
    Открывает файл с помощью системного приложения по умолчанию в Windows.
    """
    if not file_path:
        error_messages = [
            "Не указан путь к файлу.",
            "Для открытия файла нужен его путь.",
            "Пожалуйста, укажите что открывать.",
            "Требуется указать путь к файлу.",
            "Не могу открыть - нет пути к файлу."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        if not os.path.isfile(file_path):
            error_messages = [
                "Файл не найден.",
                "Не могу найти файл.",
                "Файл отсутствует.",
                "Отсутствует файл.",
                "Путь не ведет к файлу."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return

        print(f"Открытие файла")

        messages_before = [
            "Открываю файл.",
            "Запускаю файл.",
            "Начинаю открытие файла.",
            "Загружаю файл.",
            "Инициализирую файл."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        os.startfile(file_path)

        messages_success = [
            "Файл успешно открыт.",
            "Файл запущен.",
            "Открытие завершено успешно.",
            "Файл готов к работе.",
            "Приложение запущено."
        ]
        message = message_history.get_unique_message(messages_success, SELECTED_VOICE)
        speak(message, voice=None)

        print(f"Файл успешно открыт")

    except Exception as e:
        error_messages = [
            "Не удалось открыть файл.",
            "Возникла ошибка при запуске.",
            "Не могу открыть этот файл.",
            "Ошибка доступа к файлу.",
            "Проблема с открытием приложения."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
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
            "Пожалуйста, укажите что закрывать.",
            "Требуется указать приложение для закрытия.",
            "Не знаю, что закрывать - нет пути."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print("ОШИБКА: Не указан путь к файлу")
        return

    try:
        process_name = os.path.basename(file_path)

        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'

        messages_before = [
            "Пытаюсь закрыть приложение.",
            "Завершаю процесс.",
            "Выполняю закрытие.",
            "Останавливаю приложение.",
            "Завершаю работу приложения."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")

        if result == 0:
            success_messages = [
                "Процесс успешно завершен.",
                "Приложение закрыто.",
                "Приложение остановлено.",
                "Завершено.",
                "Работа прекращена."
            ]
            message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Процесс успешно завершен")
        else:
            error_messages = [
                "Не удалось завершить.",
                "Приложение возможно не запущено.",
                "Не могу найти процесс.",
                "Приложение не было запущено.",
                "Нет активного процесса."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Не удалось завершить процесс. Возможно, процесс не запущен.")

    except Exception as e:
        error_messages = [
            "Ошибка при закрытии приложения.",
            "Не удалось завершить процесс.",
            "Возникла непредвиденная ошибка.",
            "Проблема с завершением приложения.",
            "Ошибка системной команды."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"ОШИБКА при закрытии приложения: {e}")