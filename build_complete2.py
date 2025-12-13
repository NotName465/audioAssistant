import subprocess
import sys
import shutil
import os
import zipfile
import requests
from pathlib import Path


def download_vosk_model():
    """Скачивает модель Vosk если она отсутствует"""
    model_name = "vosk-model-small-ru-0.22"
    model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"
    model_dir = "models"
    model_path = os.path.join(model_dir, model_name)

    if os.path.exists(model_path):
        print(f"✅ Модель Vosk найдена: {model_path}")
        return model_path

    print(f"📥 Модель Vosk не найдена, скачиваю...")
    print(f"🌐 URL: {model_url}")

    try:
        os.makedirs(model_dir, exist_ok=True)

        # Скачиваем модель
        response = requests.get(model_url, stream=True, timeout=60)
        response.raise_for_status()

        zip_path = os.path.join(model_dir, f"{model_name}.zip")

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"📦 Архив скачан: {zip_path}")

        # Распаковываем
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(model_dir)

        # Удаляем архив
        os.remove(zip_path)

        # Проверяем распакованные файлы
        if os.path.exists(model_path):
            print(f"✅ Модель Vosk установлена: {model_path}")
            return model_path
        else:
            # Пробуем найти любую распакованную модель
            for item in os.listdir(model_dir):
                item_path = os.path.join(model_dir, item)
                if os.path.isdir(item_path) and "vosk-model" in item:
                    print(f"⚠️  Найдена другая модель: {item_path}")
                    return item_path

            print("❌ Не удалось найти распакованную модель")
            return None

    except Exception as e:
        print(f"❌ Ошибка загрузки модели Vosk: {e}")
        print("💡 Скачайте модель вручную с: https://alphacephei.com/vosk/models")
        print("💡 Распакуйте в папку models/")
        return None


def check_and_fix_vosk_import():
    """Проверяет и исправляет импорт Vosk если нужно"""
    # Проверяем main.py на импорт vosk
    main_py = "main.py"

    if not os.path.exists(main_py):
        return "no_main"

    with open(main_py, 'r', encoding='utf-8') as f:
        content = f.read()

    has_vosk_import = "import vosk" in content or "from vosk" in content

    if not has_vosk_import:
        return "no_vosk"

    # Проверяем есть ли модель vosk
    model_path = download_vosk_model()

    if model_path:
        return "with_model"
    else:
        print("⚠️  Vosk импортируется, но модель не найдена")
        print("📝 Создаю заглушку для vosk...")

        # Создаем временную заглушку для vosk
        create_vosk_stub()
        return "with_stub"


def create_vosk_stub():
    """Создает заглушку для vosk если модель не найдена"""
    vosk_stub = """
# Vosk stub - временная заглушка для сборки
# Для работы скачайте модель с https://alphacephei.com/vosk/models

import warnings
warnings.warn("Vosk model not found. Please download from https://alphacephei.com/vosk/models")

class Model:
    def __init__(self, model_path):
        raise ImportError("Vosk model not found. Download from https://alphacephei.com/vosk/models")

class KaldiRecognizer:
    def __init__(self, *args, **kwargs):
        raise ImportError("Vosk model not found. Download from https://alphacephei.com/vosk/models")

def SetLogLevel(level):
    pass
"""

    stub_path = "vosk_stub.py"
    with open(stub_path, 'w', encoding='utf-8') as f:
        f.write(vosk_stub)

    # Если есть import vosk в main.py, заменяем на нашу заглушку
    with open("main.py", 'r', encoding='utf-8') as f:
        content = f.read()

    # Добавляем условный импорт
    if "import vosk" in content:
        new_content = content.replace(
            "import vosk",
            """try:
    import vosk
except ImportError:
    from vosk_stub import Model, KaldiRecognizer, SetLogLevel
    vosk = type('VoskModule', (), {
        'Model': Model,
        'KaldiRecognizer': KaldiRecognizer,
        'SetLogLevel': SetLogLevel
    })()"""
        )

        with open("main.py", 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("✅ Создана заглушка для Vosk")
        return True

    return False


def build_with_vosk(model_path=None):
    """Сборка с поддержкой Vosk"""

    # Основная команда PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name=AudioAssistant",
        "--add-data=commands.json;.",
        "--add-data=config.json;.",
        "--add-data=cfg.json;.",
        "--hidden-import=numpy",
        "--hidden-import=main",
        "--hidden-import=FuncLib",
        "--hidden-import=PyQt5",
        "--hidden-import=vosk",
        "--exclude-module=torch",
        "--exclude-module=torchaudio",
    ]

    # Если есть модель Vosk, добавляем ее
    if model_path and os.path.exists(model_path):
        # Для Windows нужно использовать правильный разделитель
        dest_path = f"models/{os.path.basename(model_path)}"
        cmd.append(f"--add-data={model_path};{dest_path}")
        print(f"📁 Добавляю модель Vosk: {model_path}")

    # Добавляем сбор данных для vosk
    cmd.append("--collect-data=vosk")
    cmd.append("--collect-binaries=vosk")

    # Основной файл
    cmd.append("GUI.py")

    return cmd


def build_without_vosk():
    """Сборка без Vosk (исключаем его)"""

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name=AudioAssistant",
        "--add-data=commands.json;.",
        "--add-data=config.json;.",
        "--add-data=cfg.json;.",
        "--hidden-import=numpy",
        "--hidden-import=main",
        "--hidden-import=FuncLib",
        "--hidden-import=PyQt5",
        "--exclude-module=torch",
        "--exclude-module=torchaudio",
        "--exclude-module=vosk",  # Исключаем vosk
        "GUI.py"
    ]

    return cmd


def backup_and_restore_files():
    """Создает backup файлов и восстанавливает их после сборки"""
    backup_files = []

    # Файлы для backup
    files_to_backup = ["main.py", "FuncLib.py"]

    for file in files_to_backup:
        if os.path.exists(file):
            backup_file = f"{file}.backup"
            shutil.copy(file, backup_file)
            backup_files.append((file, backup_file))
            print(f"📋 Создан backup: {backup_file}")

    return backup_files


def restore_backup_files(backup_files):
    """Восстанавливает файлы из backup"""
    for original, backup in backup_files:
        if os.path.exists(backup):
            shutil.copy(backup, original)
            os.remove(backup)
            print(f"📋 Восстановлен: {original}")


def build_complete():
    print("🔧 Полная сборка Audio Assistant")
    print("=" * 50)

    # ПРОВЕРКА: находимся ли в правильной папке?
    current_dir = os.getcwd()
    print(f"📁 Текущая папка: {current_dir}")

    if not os.path.exists("GUI.py"):
        print("❌ ОШИБКА: GUI.py не найден в текущей папке!")
        print("💡 Переместите build_complete.py в папку с GUI.py")
        return

    print("📋 Проверяю файлы проекта...")
    required_files = ["GUI.py", "main.py", "FuncLib.py",
                      "commands.json", "config.json", "cfg.json"]

    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} - не найден")

    print("\n🔍 Анализирую зависимости...")

    # Проверяем Vosk
    vosk_status = check_and_fix_vosk_import()

    # Создаем backup файлов
    backup_files = backup_and_restore_files()

    try:
        # Выбираем стратегию сборки
        if vosk_status == "with_model":
            print("\n🎯 Стратегия: Сборка С моделью Vosk")
            model_path = download_vosk_model()
            cmd = build_with_vosk(model_path)

        elif vosk_status == "with_stub":
            print("\n🎯 Стратегия: Сборка С заглушкой Vosk")
            cmd = build_with_vosk()

        elif vosk_status == "no_vosk":
            print("\n🎯 Стратегия: Сборка БЕЗ Vosk (не используется)")
            cmd = build_without_vosk()

        else:  # "no_main" или другие
            print("\n🎯 Стратегия: Базовая сборка")
            cmd = build_without_vosk()

        print(f"\n🚀 Команда сборки:")
        print("   " + " ".join(cmd[:8]) + "...")

        # 1. Сборка exe
        print("\n🔨 Запускаю сборку...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Ошибка сборки:")
            print(result.stderr[:500])  # Показываем первые 500 символов ошибки
            return

        print("✅ Сборка PyInstaller завершена!")

        # 2. Копируем все необходимые файлы в dist
        print("\n📂 Копирую дополнительные файлы...")
        dist_dir = "dist"
        os.makedirs(dist_dir, exist_ok=True)

        files_to_copy = [
            "commands.json",
            "config.json",
            "cfg.json",
        ]

        # Если есть модель Vosk, копируем ее тоже
        model_path = download_vosk_model()
        if model_path:
            model_dest = os.path.join(dist_dir, "models", os.path.basename(model_path))
            os.makedirs(os.path.dirname(model_dest), exist_ok=True)

            if os.path.exists(model_path):
                if os.path.isdir(model_path):
                    shutil.copytree(model_path, model_dest, dirs_exist_ok=True)
                else:
                    shutil.copy(model_path, model_dest)
                print(f"  ✅ Модель Vosk скопирована")

        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, dist_dir)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} не найден")

        # 3. Создаем папку для данных
        data_dir = os.path.join(dist_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        # 4. Создаем README
        create_readme(dist_dir, vosk_status)

        # 5. Показываем результат
        show_build_result(dist_dir)

    finally:
        # Всегда восстанавливаем backup файлы
        print("\n📋 Восстанавливаю исходные файлы...")
        restore_backup_files(backup_files)

        # Удаляем временные файлы
        temp_files = ["vosk_stub.py"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def create_readme(dist_dir, vosk_status):
    """Создает README файл"""

    if vosk_status == "with_model":
        vosk_note = """
## 🎤 Распознавание речи (Vosk)
Программа использует Vosk для оффлайн-распознавания речи.
Модель уже включена в сборку.
"""
    elif vosk_status == "with_stub":
        vosk_note = """
## 🎤 Распознавание речи (Vosk - требуется установка)
Для работы Vosk скачайте модель:
1. Перейдите на https://alphacephei.com/vosk/models
2. Скачайте русскую модель (например, vosk-model-small-ru-0.22)
3. Распакуйте в папку `models/` рядом с exe файлом
"""
    else:
        vosk_note = """
## 🎤 Распознавание речи
Vosk не используется в этой сборке.
"""

    readme_content = f"""# 🎤 Audio Assistant

## 🚀 Запуск
1. Запустите `AudioAssistant.exe`
2. Убедитесь что в одной папке есть файлы:
   - commands.json
   - config.json  
   - cfg.json

{vosk_note}
## ⚙️ Настройка
- Отредактируйте `commands.json` - добавьте свои команды
- Отредактируйте `config.json` - настройки программы
- Отредактируйте `cfg.json` - дополнительные настройки

## 🎯 Горячие клавиши
По умолчанию: Ctrl+Alt+A

## ❓ Помощь
При проблемах:
1. Проверьте наличие всех .json файлов
2. Запустите от имени администратора
3. Проверьте доступ к микрофону

## 📞 Поддержка
GitHub: https://github.com/NotName465/audioAssistant
"""

    readme_path = os.path.join(dist_dir, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"  ✅ README.txt создан")


def show_build_result(dist_dir):
    """Показывает результат сборки"""
    exe_path = os.path.join(dist_dir, "AudioAssistant.exe")

    print("\n" + "=" * 50)

    if os.path.exists(exe_path):
        # Получаем размер файла
        size_bytes = os.path.getsize(exe_path)
        size_mb = size_bytes / (1024 * 1024)

        print("✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 50)
        print(f"📁 Папка: {dist_dir}/")
        print(f"🚀 Файл: AudioAssistant.exe")
        print(f"📊 Размер: {size_mb:.2f} MB")
        print(f"📅 Создан: {os.path.getctime(exe_path):%Y-%m-%d %H:%M}")
        print("\n📋 Содержимое папки:")

        # Показываем файлы в папке dist
        for item in os.listdir(dist_dir):
            item_path = os.path.join(dist_dir, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
            else:
                item_size = os.path.getsize(item_path) / 1024
                print(f"  📄 {item} ({item_size:.1f} KB)")

        print("\n💡 Запустите AudioAssistant.exe для проверки")
    else:
        print("❌ ОШИБКА: EXE файл не создан!")
        print("Проверьте логи выше для диагностики")

    print("=" * 50)


if __name__ == "__main__":
    build_complete()