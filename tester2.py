import vosk
import pyaudio
import json
import os
import webbrowser

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




def Sorter(text: list[str]):
    sorted_text = text.split(" ")
    return sorted_text
def Starter(text: str, browserUrl: str = "" ):
    browserUrl = r"C:\Users\user\PycharmProjects\audioAssistant\vosk-model-small-ru-0.22"
    forClose = browserUrl.split('\\')[-1]
    if "открой" in text and "браузер" in text:
        openBrowser(browserUrl)
    if "закрой" in text and "браузер" in text:
        closeBrowser(forClose)
    if "открой" in text and "доту" in text:
        openDota2()
    if "закрой" in text and "доту"in text:
        closeDota2()

# Укажите путь к вашей модели
MODEL_PATH = r"C:\Users\user\PycharmProjects\audioAssistant\vosk-model-small-ru-0.22"

print("🔄 Загружаем модель...")
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)

# Настраиваем микрофон
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)

print("🎤 Говорите!")

try:
    while True:
        # Читаем данные с микрофона
        data = stream.read(8192, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get('text', '')
            if text:
                print(f" {Sorter(text)}")
                Starter(Sorter(text))

except KeyboardInterrupt:
    print("\n До свидания!")

finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()


class EnhancedVoiceRecognizer: #доучивалка для словаря
    def __init__(self, model_path):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.enhancement_dict = {
            # Правильные слова: [похожие варианты]
            "гойда": ["гойда"],
            "дух машины": [" духмашины", "машинный дух", "дух машине", "дух машину"],
            "машинный дух": ["машинные дух"]
        }