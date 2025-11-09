import vosk
import pyaudio
import json
import os
import webbrowser
import time
from FuncLib import open_browser_and_search, remove_keywords, close_tab, new_tab, go_to_tab, scroll_up, scroll_down, volume_down, volume_up, mute

usedComandList = []
comandPool = ('browser')
comandsForStarter = []
def openBrowser(browserUrl: str = ""):
    try:
        os.startfile(browserUrl)
    except:
        webbrowser.open("http://yandex.ru")

def Sorter(text: str):
    sorted_text = text.split(" ")
    return sorted_text

def Starter(text: list, browserUrl: str = ""):
    # Конфигурации
    browserUrl = r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe"
    dotaName = r"C:\Users\user\Desktop\Dota 2.url"

    text_str = " ".join(text).lower()

    # Загружаем команды из JSON
    with open('commands.json', 'r', encoding='utf-8') as f:
        commands_config = json.load(f)

    # Ищем подходящую команду
    for command in commands_config['commands']:
        if all(keyword in text_str for keyword in command['keywords']):
            print(f"🎯 Выполняю: {command['name']}")
            execute_command(command, text_str, browserUrl, dotaName)
            return

    print("❌ Команда не распознана")


def execute_command(command, text_str, browserUrl, dotaName):
    """Выполняет команду на основе конфигурации"""

    # Словарь функций
    functions = {
        'openBrowser': openBrowser,
        'closeBrowser': closeBrowser,
        'openDota': openDota,
        'closeDota': closeDota,
        'open_browser_and_search': open_browser_and_search,
        'close_tab': close_tab,
        'new_tab': new_tab,
        'go_to_tab': go_to_tab,
        'scroll_down': scroll_down,
        'scroll_up': scroll_up,
        'mute': mute,
        'volume_down': volume_down,
        'volume_up': volume_up
    }

    # Подготавливаем аргументы
    args = []
    for arg in command['args']:
        if arg == 'browserUrl':
            args.append(browserUrl)
        elif arg == 'remove_keywords(text_str)':
            args.append(remove_keywords(text_str))
        elif arg == 'text_str':
            args.append(text_str)
        elif arg == 'dotaName':
            args.append(dotaName)
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


# Вспомогательные функции
def closeBrowser(url):
    os.system(f"taskkill /f /im {forClose(url)}")


def openDota():
    dotaName = r"C:\Users\user\Desktop\Dota 2.url"
    os.startfile(dotaName)


def closeDota():
    os.system("taskkill /f /im dota2.exe")


def forClose(url):
    return os.path.basename(url)



def VoiceActive(activation_word="ассистент"):

    MODEL_PATH = r"C:\Users\user\Desktop\vosk-model-ru-0.42"

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
                # Используем оригинальный размер буфера для качественного распознавания
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
                    # Частичный результат (пока говорим)
                    partial = json.loads(main_recognizer.PartialResult())
                    partial_text = partial.get('partial', '')
                    if partial_text:
                        print(f"Говорите...: {partial_text}")
                        silence_timeout = 0
                    else:
                        silence_timeout += 0.2

                time.sleep(0.1)  # Небольшая пауза между проверками

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