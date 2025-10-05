import vosk
import pyaudio
import json
import os
import webbrowser
import time


def openBrowser(browserUrl: str = ""):
    try:
        os.startfile(browserUrl)
    except:
        webbrowser.open("http://yandex.ru")


def closeBrowser(closeName: str):
    os.system(f"taskkill /f /im {closeName}")


def openDota2(startFileUrl: str = ""):
    startFileUrl = r"C:\Users\user\Desktop\Dota 2.url"
    os.startfile(startFileUrl)


def closeDota2():
    DotaName = "dota2.exe"
    os.system(f"taskkill /f /im {DotaName}")


def Sorter(text: str):
    sorted_text = text.split(" ")
    return sorted_text


def Starter(text: list, browserUrl: str = ""):
    browserUrl = r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe"
    forClose = browserUrl.split('\\')[-1]

    text_str = " ".join(text).lower()

    if "открой" in text_str and "браузер" in text_str:
        openBrowser(browserUrl)
        print("Открываю браузер")
    elif "закрой" in text_str and "браузер" in text_str:
        closeBrowser(forClose)
        print("Закрываю браузер")
    elif "открой" in text_str and "доту" in text_str:
        openDota2()
        print("Открываю Dota 2")
    elif "закрой" in text_str and "доту" in text_str:
        closeDota2()
        print("Закрываю Dota 2")


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
        frames_per_buffer=1024  # Уменьшенный буфер для быстрого реагирования
    )

    # Создаем два распознавателя
    activation_recognizer = vosk.KaldiRecognizer(model, 16000)
    main_recognizer = vosk.KaldiRecognizer(model, 16000)

    print(f"🎧 Ожидание ключевого слова: '{activation_word}'")

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
                        print(f"Активировано по ключевому слову: '{activation_word}'")
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
            # Сбрасываем активационный распознаватель для следующего цикла
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
            "машинный дух": ["машинные дух"]
        }


if __name__ == "__main__":
    VoiceActive("ассистент")