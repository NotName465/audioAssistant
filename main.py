import vosk
import pyaudio
import json
import os
import webbrowser
import time
from FuncLib import open_browser_and_search
from FuncLib import remove_keywords, close_tab, new_tab, go_to_tab


def openBrowser(browserUrl: str = ""):
    try:
        os.startfile(browserUrl)
    except:
        webbrowser.open("http://yandex.ru")

def Sorter(text: str):
    sorted_text = text.split(" ")
    return sorted_text

def forClose(Url: str):
    return Url.split('\\')[-1]
def Starter(text: list, browserUrl: str = ""):
    browserUrl = r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe"
    dotaName = r"C:\Users\user\Desktop\Dota 2.url"

    text_str = " ".join(text).lower()

    if "открой" in text_str and "браузер" in text_str:
        openBrowser(browserUrl)
        print("Открываю браузер")
    elif "закрой" in text_str and "браузер" in text_str:
        os.system(f"taskkill /f /im {forClose(browserUrl)}")
        print("Закрываю браузер")
    elif "открой" in text_str and "доту" in text_str:
        os.startfile(dotaName)
        print("Открываю Dota 2")
    elif "закрой" in text_str and "доту" in text_str:
        os.system(f"taskkill /f /im dota2.exe")
        print("Закрываю Dota 2")
    elif "найди" in text_str and "в" in text_str and "интернете":

        open_browser_and_search(browserUrl, remove_keywords(text_str))
    elif "закрой" in text_str and "вкладку" in text_str:
        close_tab()
    elif "создай" in text_str and "вкладку" in text_str:
        new_tab()
    elif "открой" in text_str and "вкладку" in text_str:
        go_to_tab(remove_keywords(text_str))



def VoiceActive(activation_word="ассистент"):

    MODEL_PATH = r"C:\Users\user\PycharmProjects\audioAssistant\vosk-model-small-ru-0.22"

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