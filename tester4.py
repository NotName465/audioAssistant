import pyautogui
import time
import webbrowser
import os
import json
import torch
import sounddevice as sd
import random


# Загрузка конфигурации
def load_config():
    """Загружает конфигурацию из config.json"""
    config_path = "config.json"
    default_config = {
        "selected_microphone": "",
        "selected_voice": 1  # По умолчанию голос baya (индекс 1)
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Объединяем с дефолтными значениями на случай отсутствия ключей
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        else:
            # Создаем файл с дефолтной конфигурацией
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"Создан файл конфигурации: {config_path}")
            return default_config
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        return default_config

# Загружаем конфиг при старте
config = load_config()
SELECTED_VOICE = config.get("selected_voice", 1)

# Класс для отслеживания последних сообщений
class MessageHistory:
    def __init__(self, history_size=5):
        self.history = []
        self.history_size = history_size
        self.voice_history = []  # История голосов

    def add_message(self, message, voice):
        """Добавляет сообщение в историю"""
        self.history.append(message)
        self.voice_history.append(voice)

        # Ограничиваем размер истории
        if len(self.history) > self.history_size:
            self.history.pop(0)
            self.voice_history.pop(0)

    def get_unique_message(self, messages, voice):
        """
        Возвращает уникальное сообщение, которого не было в истории
        Если все сообщения были в истории, возвращает случайное
        """
        # Фильтруем сообщения, которых нет в истории
        unique_messages = [msg for msg in messages if msg not in self.history]

        if unique_messages:
            # Выбираем случайное уникальное сообщение
            selected = random.choice(unique_messages)
        else:
            # Если все сообщения были в истории, очищаем историю и выбираем случайное
            self.history.clear()
            self.voice_history.clear()
            selected = random.choice(messages)

        # Добавляем выбранное сообщение в историю
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
    print("✅ Модель успешно загружена")
except Exception as e:
    print(f"❌ Ошибка загрузки модели: {e}")
    raise


def speak(text, voice: int = None):
    """
    Синтезировать и воспроизвести русскую речь

    voice: None - используется голос из config.json
            0 - 'aidar', 1 - 'baya', 2 - 'kseniya', 3 - 'xenia'
           -1 - случайный голос (но не тот же самый, что был до этого)
    """
    voices = ['aidar', 'baya', 'kseniya', 'xenia']

    # Определяем какой голос использовать
    if voice is None:
        # Используем голос из конфига
        voice_idx = SELECTED_VOICE
    elif voice == -1:
        # Случайный голос, но не тот же самый что был до этого
        last_voice = message_history.voice_history[-1] if message_history.voice_history else SELECTED_VOICE
        available_voices = [i for i in range(len(voices)) if i != last_voice]
        voice_idx = random.choice(available_voices) if available_voices else SELECTED_VOICE
    else:
        voice_idx = voice % len(voices)  # Защита от выхода за границы

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

        # Сохраняем голос в историю для отслеживания
        message_history.voice_history.append(voice_idx)
        if len(message_history.voice_history) > 5:
            message_history.voice_history.pop(0)

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

        # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
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

            # Получаем уникальное сообщение
            messages = [
                f"Перехожу на вкладку номер {tab_num}.",
                f"Переключаюсь на {tab_num} вкладку.",
                f"Вкладка {tab_num} теперь активна.",
                f"Активирую вкладку {tab_num}.",
                f"Фокус на {tab_num} вкладке."
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
        print("Номер вкладки должен быть числом")


def scroll_down():
    """Прокручивает страницу вниз"""
    pyautogui.scroll(-3)

    # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
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

    # Получаем уникальное сообщение
    messages = [
        "Переключаю звук.",
        "Включаю или выключаю звук.",
        "Изменяю состояние звука.",
        "Меняю режим звука.",
        "Активирую или деактивирую звук."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


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
        # Проверяем существование файла
        if not os.path.isfile(file_path):
            error_messages = [
                f"Файл не найден: {os.path.basename(file_path)}",
                f"Не могу найти файл {os.path.basename(file_path)}",
                f"Файл {os.path.basename(file_path)} отсутствует.",
                f"Отсутствует файл: {os.path.basename(file_path)}",
                f"Путь не ведет к файлу: {os.path.basename(file_path)}"
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return

        print(f"Открытие файла: {os.path.basename(file_path)}")

        # Получаем уникальное сообщение перед открытием
        messages_before = [
            f"Открываю файл {os.path.basename(file_path)}.",
            f"Запускаю {os.path.basename(file_path)}.",
            f"Начинаю открытие {os.path.basename(file_path)}.",
            f"Загружаю {os.path.basename(file_path)}.",
            f"Инициализирую {os.path.basename(file_path)}."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        os.startfile(file_path)

        # Получаем уникальное сообщение об успехе
        messages_success = [
            f"Файл успешно открыт.",
            f"{os.path.basename(file_path)} запущен.",
            f"Открытие завершено успешно.",
            f"{os.path.basename(file_path)} готов к работе.",
            f"Приложение запущено."
        ]
        message = message_history.get_unique_message(messages_success, SELECTED_VOICE)
        speak(message, voice=None)

        print(f"Файл успешно открыт: {file_path}")

    except Exception as e:
        error_messages = [
            f"Не удалось открыть файл.",
            f"Возникла ошибка при запуске.",
            f"Не могу открыть этот файл.",
            f"Ошибка доступа к файлу.",
            f"Проблема с открытием приложения."
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
        # Получаем только имя файла для taskkill
        process_name = os.path.basename(file_path)

        # Убедимся, что у процесса есть расширение .exe
        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'

        # Получаем уникальное сообщение перед закрытием
        messages_before = [
            f"Пытаюсь закрыть {process_name}.",
            f"Завершаю процесс {process_name}.",
            f"Выполняю закрытие {process_name}.",
            f"Останавливаю {process_name}.",
            f"Завершаю работу {process_name}."
        ]
        message = message_history.get_unique_message(messages_before, SELECTED_VOICE)
        speak(message, voice=None)

        # Выполняем команду закрытия процесса
        result = os.system(f"taskkill /f /im {process_name} >nul 2>&1")

        if result == 0:
            success_messages = [
                f"Процесс {process_name} успешно завершен.",
                f"{process_name} закрыт.",
                f"Приложение {process_name} остановлено.",
                f"{process_name} завершен.",
                f"Работа {process_name} прекращена."
            ]
            message = message_history.get_unique_message(success_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Процесс {process_name} успешно завершен")
        else:
            error_messages = [
                f"Не удалось завершить {process_name}.",
                f"{process_name} возможно не запущен.",
                f"Не могу найти процесс {process_name}.",
                f"{process_name} не был запущен.",
                f"Нет активного процесса {process_name}."
            ]
            message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
            speak(message, voice=None)
            print(f"Не удалось завершить процесс {process_name}. Возможно, процесс не запущен.")

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


def open_website(url):
    """Открывает указанный веб-сайт"""
    try:
        webbrowser.open(url)

        # Получаем уникальное сообщение об успехе
        messages = [
            f"Открываю сайт {url}",
            f"Загружаю {url}",
            f"Перехожу на {url}",
            f"Запускаю {url}",
            f"Начинаю загрузку {url}"
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Не удалось открыть сайт.",
            "Ошибка при открытии веб-страницы.",
            "Проверьте правильность адреса сайта.",
            "Проблема с доступом к сайту.",
            "Не могу подключиться к указанному адресу."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при открытии сайта: {e}")


def create_file(filename):
    """Создает новый файл"""
    try:
        with open(filename, 'w') as f:
            f.write('')

        # Получаем уникальное сообщение об успехе
        messages = [
            f"Файл {filename} создан.",
            f"Создаю новый файл {filename}.",
            f"Файл {filename} готов к использованию.",
            f"Новый файл {filename} создан.",
            f"Файл {filename} успешно создан."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            f"Не удалось создать файл {filename}.",
            f"Ошибка при создании файла.",
            f"Проверьте права доступа для создания файла.",
            f"Проблема с созданием {filename}.",
            f"Невозможно создать файл {filename}."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при создании файла: {e}")


def system_sleep():
    """Переводит систему в спящий режим"""
    try:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

        # Получаем уникальное сообщение перед сном
        messages = [
            "Перевожу компьютер в спящий режим.",
            "Укладываю систему спать.",
            "Активирую режим ожидания.",
            "Перехожу в спящий режим.",
            "Выключаю экран для экономии энергии."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Не удалось перевести в спящий режим.",
            "Ошибка при активации сна.",
            "Проверьте права администратора.",
            "Проблема с переходом в спящий режим.",
            "Не удалось активировать режим ожидания."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при переводе в спящий режим: {e}")


def show_desktop():
    """Показывает рабочий стол"""
    pyautogui.hotkey('win', 'd')

    # Получаем уникальное сообщение об успехе
    messages = [
        "Показываю рабочий стол.",
        "Все окна свернуты.",
        "Перехожу на рабочий стол.",
        "Сворачиваю все окна.",
        "Рабочий стол теперь доступен."
    ]
    message = message_history.get_unique_message(messages, SELECTED_VOICE)
    speak(message, voice=None)


def take_screenshot(filename=None):
    """Делает скриншот экрана"""
    if filename is None:
        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"

    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)

        # Получаем уникальное сообщение об успехе
        messages = [
            f"Скриншот сохранен как {filename}.",
            f"Захватываю экран в {filename}.",
            f"Снимок экрана готов: {filename}.",
            f"Сохранен скриншот: {filename}.",
            f"Экран сохранен в файл {filename}."
        ]
        message = message_history.get_unique_message(messages, SELECTED_VOICE)
        speak(message, voice=None)

    except Exception as e:
        error_messages = [
            "Не удалось сделать скриншот.",
            "Ошибка при захвате экрана.",
            "Проверьте права доступа для сохранения файла.",
            "Проблема с созданием скриншота.",
            "Не могу сохранить снимок экрана."
        ]
        message = message_history.get_unique_message(error_messages, SELECTED_VOICE)
        speak(message, voice=None)
        print(f"Ошибка при создании скриншота: {e}")


def test_all_functions():
    """Тестирует все функции с голосовым сопровождением"""
    test_messages = [
        "Начинаю тестирование всех функций.",
        "Запускаю проверку работы системы.",
        "Тестирую возможности голосового помощника.",
        "Проверяю все доступные функции.",
        "Инициализирую полное тестирование системы."
    ]
    message = message_history.get_unique_message(test_messages, SELECTED_VOICE)
    speak(message, voice=None)

    # Создаем тестовый файл
    test_filename = "test_file.txt"
    create_file(test_filename)
    time.sleep(1)

    # Открываем тестовый файл
    AbsolutStarter(test_filename)
    time.sleep(2)

    # Закрываем тестовый файл
    AbsolutCloser("notepad.exe")
    time.sleep(1)

    # Удаляем тестовый файл
    try:
        os.remove(test_filename)
    except:
        pass

    # Тестируем звук
    volume_up()
    time.sleep(0.5)
    volume_down()
    time.sleep(0.5)
    mute()
    time.sleep(0.5)
    mute()  # Вернем звук обратно

    # Тестируем прокрутку
    scroll_down()
    time.sleep(0.5)
    scroll_up()

    # Получаем уникальное сообщение о завершении теста
    end_messages = [
        "Тестирование завершено успешно.",
        "Все функции работают корректно.",
        "Система готова к использованию.",
        "Проверка завершена без ошибок.",
        "Тестирование пройдено успешно."
    ]
    message = message_history.get_unique_message(end_messages, SELECTED_VOICE)
    speak(message, voice=None)


# ПРИМЕР ИСПОЛЬЗОВАНИЯ
if __name__ == "__main__":
    # Приветствие
    greetings = [
        "Здравствуйте! Я ваш голосовой помощник.",
        "Привет! Готов к работе.",
        "Добрый день! Чем могу помочь?",
        "Здравствуйте! Система активирована.",
        "Приветствую! Помощник готов к выполнению задач."
    ]
    message = message_history.get_unique_message(greetings, SELECTED_VOICE)
    speak(message, voice=None)

    # Пример открытия сайта
    open_website("https://www.google.com")
    time.sleep(3)

    # Пример создания файла
    create_file("example.txt")

    # Пример скриншота
    take_screenshot()

    # Прощание
    farewells = [
        "Работа завершена. До свидания!",
        "Выполнил все задачи. Всего доброго!",
        "Завершаю работу. Приятного дня!",
        "Работа помощника завершена. Всего хорошего!",
        "Задачи выполнены. До новых встреч!"
    ]
    message = message_history.get_unique_message(farewells, SELECTED_VOICE)
    speak(message, voice=None)