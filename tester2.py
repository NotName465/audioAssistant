# silero_test_correct.py
"""
РАБОЧИЙ тест Silero TTS с правильными именами голосов
Теперь точно работает!
"""

import os
import sys
import time
from pathlib import Path


# Проверка зависимостей
def check_dependencies():
    required = ['torch', 'torchaudio', 'sounddevice', 'numpy']
    missing = []

    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.append(lib)

    if missing:
        print("❌ Отсутствуют библиотеки:", ", ".join(missing))
        print("\nУстановите командой:")
        print("pip install torch torchaudio sounddevice numpy")
        print("\nИли для CPU:")
        print("pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu")
        return False
    return True


# Импорты
import torch
import torchaudio
import sounddevice as sd
import numpy as np


class SileroTester:
    def __init__(self):
        self.models = {}
        self.sample_rate = 24000

        # ПРАВИЛЬНЫЕ имена голосов для Silero
        self.voices = {
            'ru': ['aidar', 'baya', 'kseniya', 'xenia'],
            'en': ['en_0', 'en_1', 'en_2', 'en_3', 'en_4', 'en_5',
                   'en_6', 'en_7', 'en_8', 'en_9', 'en_10']
        }

        # Примеры текстов
        self.examples = {
            'ru': [
                "Привет! Это тест русского синтеза речи.",
                "Как у вас дела сегодня?",
                "Погода сегодня прекрасная.",
                "Технологии искусственного интеллекта развиваются."
            ],
            'en': [
                "Hello! This is English speech synthesis test.",
                "How are you doing today?",
                "The weather is beautiful today.",
                "Artificial intelligence technologies are developing."
            ]
        }

        print("=" * 60)
        print("     SILERO TTS ТЕСТЕР (рабочая версия)")
        print("=" * 60)

        # Загружаем модели
        self.load_models()

    def load_models(self):
        """Загрузка моделей - ПРАВИЛЬНЫЙ СПОСОБ"""
        print("\n📥 ЗАГРУЗКА МОДЕЛЕЙ SILERO TTS...")

        try:
            # Загружаем модель для русского
            print("\n1. Загрузка русской модели...")
            model_ru = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='ru',
                speaker='ru_v3'
            )
            # model_ru теперь содержит (model, symbols)
            if isinstance(model_ru, tuple):
                self.models['ru'] = model_ru[0]  # Берем модель
                print("   ✅ Русская модель загружена")
            else:
                self.models['ru'] = model_ru
                print("   ✅ Русская модель загружена")

            # Загружаем модель для английского
            print("\n2. Загрузка английской модели...")
            model_en = torch.hub.load(
                repo_or_dir='snakers4/silero-models',
                model='silero_tts',
                language='en',
                speaker='v3_en'
            )
            if isinstance(model_en, tuple):
                self.models['en'] = model_en[0]  # Берем модель
                print("   ✅ Английская модель загружена")
            else:
                self.models['en'] = model_en
                print("   ✅ Английская модель загружена")

            print(f"\n✅ Всего загружено моделей: {len(self.models)}")
            print(f"   Русские голоса: {', '.join(self.voices['ru'])}")
            print(f"   Английские голоса: {', '.join(self.voices['en'][:5])}...")

            return True

        except Exception as e:
            print(f"\n❌ ОШИБКА ЗАГРУЗКИ: {e}")
            return False

    def synthesize(self, text, language='ru', speaker=None):
        """Синтез речи - ПРАВИЛЬНАЯ РЕАЛИЗАЦИЯ"""
        if language not in self.models:
            print(f"❌ Модель для языка '{language}' не загружена")
            return None

        if speaker is None:
            speaker = self.voices[language][0]

        if speaker not in self.voices[language]:
            print(f"❌ Голос '{speaker}' не найден для языка '{language}'")
            print(f"   Доступные голоса: {', '.join(self.voices[language])}")
            return None

        try:
            model = self.models[language]

            # ПРАВИЛЬНЫЙ ВЫЗОВ ДЛЯ SILERO
            audio = model.apply_tts(
                text=text,
                speaker=speaker,
                sample_rate=self.sample_rate,
                put_accent=True if language == 'ru' else False,
                put_yo=True if language == 'ru' else False
            )

            return audio.numpy()

        except Exception as e:
            print(f"❌ Ошибка синтеза: {e}")
            return None

    def play_audio(self, audio):
        """Воспроизведение аудио"""
        try:
            if audio is not None and len(audio) > 0:
                sd.play(audio, samplerate=self.sample_rate)
                sd.wait()
        except Exception as e:
            print(f"❌ Ошибка воспроизведения: {e}")

    def speak(self, text, language='ru', speaker=None):
        """Озвучить текст"""
        print(f"\n🔊 Тест: {text}")
        print(f"   Язык: {language.upper()}, Голос: {speaker or 'по умолчанию'}")

        audio = self.synthesize(text, language, speaker)
        if audio is not None:
            print("   ▶ Воспроизведение...")
            self.play_audio(audio)
            print("   ✅ Готово!")
            return True
        return False

    def test_russian_voices(self):
        """Тест всех русских голосов"""
        print("\n" + "=" * 60)
        print("ТЕСТ РУССКИХ ГОЛОСОВ")
        print("=" * 60)

        for voice in self.voices['ru']:
            print(f"\n🎤 Голос: {voice}")
            self.speak("Привет! Это тест синтеза речи.", 'ru', voice)
            time.sleep(0.5)

    def test_english_voices(self, count=3):
        """Тест нескольких английских голосов"""
        print("\n" + "=" * 60)
        print(f"ТЕСТ АНГЛИЙСКИХ ГОЛОСОВ (первые {count})")
        print("=" * 60)

        for voice in self.voices['en'][:count]:
            print(f"\n🎤 Голос: {voice}")
            self.speak("Hello! This is speech synthesis test.", 'en', voice)
            time.sleep(0.5)

    def bilingual_test(self):
        """Билингвальный тест"""
        print("\n" + "=" * 60)
        print("БИЛИНГВАЛЬНЫЙ ТЕСТ")
        print("=" * 60)

        # Тест русского
        print("\n🇷🇺 РУССКИЙ:")
        for i, text in enumerate(self.examples['ru'], 1):
            print(f"\n{i}. {text}")
            self.speak(text, 'ru', 'aidar')
            time.sleep(0.3)

        # Тест английского
        print("\n🇬🇧 АНГЛИЙСКИЙ:")
        for i, text in enumerate(self.examples['en'], 1):
            print(f"\n{i}. {text}")
            self.speak(text, 'en', 'en_0')
            time.sleep(0.3)

        # Смешанный текст
        print("\n🌐 СМЕШАННЫЙ ТЕКСТ:")
        mixed_texts = [
            ("Hello! Привет! How are you? Как дела?", 'ru', 'baya'),
            ("Это test работы системы. The system works well.", 'en', 'en_1'),
            ("Русский и English together. Работает отлично!", 'ru', 'kseniya')
        ]

        for text, lang, voice in mixed_texts:
            print(f"\n{text}")
            self.speak(text, lang, voice)
            time.sleep(0.3)

    def custom_test(self):
        """Пользовательский тест"""
        print("\n" + "=" * 60)
        print("ПОЛЬЗОВАТЕЛЬСКИЙ ТЕСТ")
        print("=" * 60)

        while True:
            print("\n1. Русский текст")
            print("2. Английский текст")
            print("3. Назад")

            choice = input("\nВыберите язык (1-3): ").strip()

            if choice == '1':
                lang = 'ru'
                voices = self.voices['ru']
            elif choice == '2':
                lang = 'en'
                voices = self.voices['en']
            elif choice == '3':
                return
            else:
                print("❌ Неверный выбор!")
                continue

            # Выбор голоса
            print(f"\nДоступные голоса для {lang.upper()}:")
            for i, voice in enumerate(voices, 1):
                print(f"  {i}. {voice}")

            try:
                voice_idx = int(input(f"\nВыберите голос (1-{len(voices)}): ")) - 1
                if 0 <= voice_idx < len(voices):
                    voice = voices[voice_idx]
                else:
                    print("❌ Неверный номер!")
                    continue
            except:
                print("❌ Введите число!")
                continue

            # Ввод текста
            text = input("\nВведите текст для синтеза: ").strip()
            if not text:
                print("❌ Текст не может быть пустым!")
                continue

            # Синтез
            self.speak(text, lang, voice)

            # Продолжить?
            cont = input("\nПродолжить? (y/n): ").strip().lower()
            if cont != 'y':
                break

    def quick_demo(self):
        """Быстрая демонстрация"""
        print("\n" + "=" * 60)
        print("БЫСТРАЯ ДЕМОНСТРАЦИЯ")
        print("=" * 60)

        # Русский голос aidar
        print("\n🎯 1. Русский (aidar):")
        self.speak("Привет! Это демонстрация синтеза речи.", 'ru', 'aidar')
        time.sleep(0.5)

        # Русский голос baya
        print("\n🎯 2. Русский (baya):")
        self.speak("Как у вас дела сегодня?", 'ru', 'baya')
        time.sleep(0.5)

        # Английский голос en_0
        print("\n🎯 3. Английский (en_0):")
        self.speak("Hello! This is speech synthesis.", 'en', 'en_0')
        time.sleep(0.5)

        # Английский голос en_1
        print("\n🎯 4. Английский (en_1):")
        self.speak("How are you doing today?", 'en', 'en_1')
        time.sleep(0.5)

        print("\n" + "=" * 60)
        print("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
        print("=" * 60)

    def show_info(self):
        """Информация о системе"""
        print("\n" + "=" * 60)
        print("ИНФОРМАЦИЯ О СИСТЕМЕ")
        print("=" * 60)

        print(f"\n📦 ВЕРСИИ БИБЛИОТЕК:")
        print(f"  PyTorch: {torch.__version__}")
        print(f"  TorchAudio: {torchaudio.__version__}")

        print(f"\n🎙️ SILERO TTS:")
        print(f"  Русские голоса: {len(self.voices['ru'])}")
        print(f"  Английские голоса: {len(self.voices['en'])}")
        print(f"  Частота дискретизации: {self.sample_rate} Гц")

        print(f"\n💻 СИСТЕМА:")
        import platform
        print(f"  ОС: {platform.system()} {platform.release()}")
        print(f"  Python: {sys.version.split()[0]}")

        if torch.cuda.is_available():
            print(f"  CUDA: Доступен ({torch.cuda.get_device_name(0)})")
        else:
            print(f"  CUDA: Не доступен (используется CPU)")

    def run_interactive(self):
        """Интерактивный режим"""
        while True:
            print("\n" + "=" * 60)
            print("ГЛАВНОЕ МЕНЮ")
            print("=" * 60)
            print("\n1. Быстрая демонстрация")
            print("2. Все русские голоса")
            print("3. Английские голоса")
            print("4. Билингвальный тест")
            print("5. Свой текст")
            print("6. Информация о системе")
            print("7. Выход")

            choice = input("\nВыберите действие (1-7): ").strip()

            if choice == '1':
                self.quick_demo()
            elif choice == '2':
                self.test_russian_voices()
            elif choice == '3':
                self.test_english_voices(3)
            elif choice == '4':
                self.bilingual_test()
            elif choice == '5':
                self.custom_test()
            elif choice == '6':
                self.show_info()
            elif choice == '7':
                print("\n👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор!")

            if choice != '7':
                input("\nНажмите Enter для продолжения...")


def main():
    """Главная функция"""
    # Очистка экрана
    os.system('cls' if os.name == 'nt' else 'clear')

    print("=" * 60)
    print("     SILERO TTS ТЕСТЕР - ГОТОВ К РАБОТЕ")
    print("=" * 60)
    print("\nЭта программа тестирует синтез речи Silero TTS.")
    print("Поддерживает русский и английский языки.")
    print("\nАвтоматически загрузит модели при первом запуске.")
    print("Для работы нужен интернет.")

    # Проверка зависимостей
    if not check_dependencies():
        input("\nНажмите Enter для выхода...")
        return

    # Создание тестера
    tester = SileroTester()

    # Проверка загрузки моделей
    if not tester.models:
        print("\n❌ Не удалось загрузить модели. Проверьте:")
        print("   1. Подключение к интернету")
        print("   2. Возможно, нужен VPN для доступа к GitHub")
        input("\nНажмите Enter для выхода...")
        return

    # Запуск интерактивного режима
    tester.run_interactive()


def create_launcher():
    """Создать файл для запуска на Windows"""
    launcher_content = '''@echo off
chcp 65001 > nul
title Silero TTS Tester
echo ========================================
echo       SILERO TTS ТЕСТЕР (RUS+EN)
echo ========================================
echo.
echo Запуск тестера синтеза речи...
echo.
python "%~dp0silero_test_correct.py"
echo.
echo ========================================
echo Программа завершена.
pause
'''

    with open('start_silero.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    print("✅ Создан файл start_silero.bat")
    print("🔹 Запускайте двойным кликом по этому файлу")


if __name__ == "__main__":
    # Аргументы командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] == '--create-launcher':
            create_launcher()
        elif sys.argv[1] == '--demo':
            # Только демо-режим
            if check_dependencies():
                tester = SileroTester()
                if tester.models:
                    tester.quick_demo()
                    input("\nНажмите Enter для выхода...")
        elif sys.argv[1] == '--help':
            print("\nИспользование:")
            print("  silero_test_correct.py              - Интерактивный режим")
            print("  silero_test_correct.py --demo       - Только демо")
            print("  silero_test_correct.py --create-launcher - Создать BAT файл")
        else:
            print(f"❌ Неизвестный аргумент: {sys.argv[1]}")
    else:
        # Обычный запуск
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            print("\nПопробуйте:")
            print("1. Перезапустить программу")
            print("2. Проверить интернет-соединение")
            print("3. Установить зависимости: pip install torch torchaudio")
            input("\nНажмите Enter для выхода...")