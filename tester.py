# silero_minimal.py
"""
МИНИМАЛЬНЫЙ пример синтеза русской речи через Silero TTS
Всего 30 строк кода!
"""

import torch
import sounddevice as sd

# 1. ЗАГРУЗКА МОДЕЛИ
print("Загрузка модели...")
model, _ = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language='ru',
    speaker='ru_v3'
)


# 2. ФУНКЦИЯ СИНТЕЗА
def speak(text, voice='aidar'):
    """
    Синтезировать и воспроизвести русскую речь

    voice: 'aidar', 'baya', 'kseniya', 'xenia'
    """
    audio = model.apply_tts(
        text=text,
        speaker=voice,
        sample_rate=24000,
        put_accent=True,
        put_yo=True
    )

    sd.play(audio.numpy(), samplerate=24000)
    sd.wait()


# 3. ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
if __name__ == "__main__":
    # Пример 1: Просто сказать
    speak("Привет! Это тест синтеза речи.", 'xenia')

    # Пример 2: Другой голос
    speak("Как у вас дела сегодня?", 'baya')

    # Пример 3: Длинный текст
    speak("Система работает отлично. Качество звука хорошее.", 'kseniya')