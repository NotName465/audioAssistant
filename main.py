import vosk
import pyaudio
import json
import time
from FuncLib import (
    open_browser_and_search, remove_keywords, close_tab, new_tab,
    go_to_tab, scroll_up, scroll_down, volume_down, volume_up, mute,
    open_browser, close_browser, open_dota, close_dota, for_close,
    right, left, down, up, left_click, double_click, right_click,
    extract_number_from_text, word_to_number,
    BROWSER_PATH, DOTA_PATH
)


def Sorter(text: str):
    sorted_text = text.split(" ")
    return sorted_text


def Starter(text: list):
    text_str = " ".join(text).lower()

    # Загружаем команды из JSON
    with open('commands.json', 'r', encoding='utf-8') as f:
        commands_config = json.load(f)

    # Ищем подходящую команду
    for command in commands_config['commands']:
        if all(keyword in text_str for keyword in command['keywords']):
            print(f"🎯 Выполняю: {command['name']}")
            execute_command(command, text)
            return

    print("❌ Команда не распознана")


def execute_command(command, text_list):
    """Выполняет команду на основе конфигурации"""
    text_str = " ".join(text_list).lower()

    # Словарь функций
    functions = {
        'openBrowser': open_browser,
        'closeBrowser': close_browser,
        'openDota': open_dota,
        'closeDota': close_dota,
        'open_browser_and_search': lambda query: open_browser_and_search(BROWSER_PATH, query),
        'close_tab': close_tab,
        'new_tab': new_tab,
        'go_to_tab': go_to_tab,
        'scroll_down': scroll_down,
        'scroll_up': scroll_up,
        'mute': mute,
        'volume_down': volume_down,
        'volume_up': volume_up,
        'right': right,
        'left': left,
        'down': down,
        'up': up,
        'left_click': left_click,
        'double_click': double_click,
        'right_click': right_click,
    }

    # Подготавливаем аргументы
    args = []
    for arg in command['args']:
        if arg == 'remove_keywords(text_str)':
            args.append(remove_keywords(text_str))
        elif arg == 'text_str':
            args.append(text_str)
        elif arg == 'extract_number(text_list)':
            # Извлекаем число из текста для функций перемещения
            pixels = extract_number_from_text(text_list)
            args.append(pixels)
        elif arg == 'browserUrl':
            args.append(BROWSER_PATH)
        else:
            args.append(arg)

    # Вызываем функцию
    try:
        func = functions[command['function']]
        func(*args)
    except KeyError:
        print(f"❌ Функция {command['function']} не найдена")
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")


def VoiceActive(activation_word="ассистент"):
    MODEL_PATH = r"vosk-model-small-ru-0.22"

    print("Загружаем модель...")
    model = vosk.Model(MODEL_PATH)

    # Настраиваем микрофон
    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024
    )

    # Создаем два распознавателя
    activation_recognizer = vosk.KaldiRecognizer(model, 16000)
    main_recognizer = vosk.KaldiRecognizer(model, 16000)

    print(f"Ожидание ключевого слова: '{activation_word}'")

    try:
        while True:
            # ФАЗА 1: Быстрый поиск ключевого слова
            activation_detected = False

            while not activation_detected:
                data = stream.read(512, exception_on_overflow=False)

                if activation_recognizer.AcceptWaveform(data):
                    result = json.loads(activation_recognizer.Result())
                    text = result.get('text', '').lower()

                    if activation_word in text:
                        activation_detected = True
                        break

            # ФАЗА 2: Полное распознавание команды
            print("Слушаю")

            # Сбрасываем распознаватель для чистого начала
            main_recognizer = vosk.KaldiRecognizer(model, 16000)

            silence_timeout = 0
            max_silence = 10  # 10 секунды тишины для завершения

            while silence_timeout < max_silence:
                data = stream.read(2048, exception_on_overflow=False)

                if main_recognizer.AcceptWaveform(data):
                    result = json.loads(main_recognizer.Result())
                    text = result.get('text', '')

                    if text:
                        print(f"Распознано: {text}")
                        processed_text = Sorter(text)
                        print(processed_text)
                        Starter(processed_text)
                        silence_timeout = 0
                    else:
                        silence_timeout += 0.5
                else:
                    partial = json.loads(main_recognizer.PartialResult())
                    partial_text = partial.get('partial', '')
                    if partial_text:
                        print(f"Говорите...: {partial_text}")
                        silence_timeout = 0
                    else:
                        silence_timeout += 0.2

                time.sleep(0.1)

            print("Возврат к ожиданию ключевого слова...")
            activation_recognizer = vosk.KaldiRecognizer(model, 16000)

    except KeyboardInterrupt:
        print("\nДо свидания!")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()


class EnhancedVoiceRecognizer:
    def __init__(self, model_path):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.enhancement_dict = {
            "дух машины": [" духмашины", "машинный дух", "дух машине", "дух машину"],
            "машинный дух": ["машинные дух"],
            "вкладку": ["вклад куб"],
        }


if __name__ == "__main__":
    VoiceActive("один")