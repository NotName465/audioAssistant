import subprocess
import sys
import shutil
import os
import zipfile
import requests
from pathlib import Path
import tempfile
import json

from audioAssistant.build_complete2 import restore_backup_files


def install_torch_cpu():
    """Устанавливает torch CPU версию если нужно"""
    print("🔧 Проверяю установку torch...")

    try:
        import torch
        print(f"✅ Torch уже установлен: {torch.__version__}")
        return True
    except ImportError:
        print("⚠️  Torch не установлен, устанавливаю CPU версию...")

        try:
            # Устанавливаем torch без CUDA (меньше зависимостей)
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "torch", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu",
                "--quiet"
            ], check=True)

            print("✅ Torch CPU установлен")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка установки torch: {e}")
            return False


def create_torch_stub_if_needed():
    """Создает заглушку для torch если он не установится"""
    stub_content = '''
# Torch stub module for PyInstaller
# Real torch should be installed via pip

import sys
import warnings

class TorchStub:
    def __getattr__(self, name):
        warnings.warn(f"Using torch stub for {name}. Install torch properly.")
        return TorchStub()

    def __call__(self, *args, **kwargs):
        return TorchStub()

# Create stub modules
sys.modules['torch'] = TorchStub()
sys.modules['torchaudio'] = TorchStub()

# Stub functions
def noop(*args, **kwargs):
    return TorchStub()

# Minimal API for common torch usage
class TensorStub:
    pass

class nn:
    class Module:
        pass

# Provide some common attributes
torch = TorchStub()
torch.Tensor = TensorStub
torch.tensor = noop
torch.load = lambda x: {}
torch.save = noop
torch.nn = nn
torch.cuda = TorchStub()
torch.cuda.is_available = lambda: False
torchaudio = TorchStub()
'''

    stub_path = "torch_stub.py"

    # Проверяем, есть ли импорт torch в файлах
    has_torch_import = False
    for filename in ["FuncLib.py", "main.py", "GUI.py"]:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                if "import torch" in f.read() or "from torch" in f.read():
                    has_torch_import = True
                    break

    if has_torch_import:
        with open(stub_path, 'w', encoding='utf-8') as f:
            f.write(stub_content)
        print("📝 Создана заглушка torch_stub.py")
        return stub_path

    return None


def patch_files_for_torch():
    """Патчит файлы для работы с torch в PyInstaller"""
    patches_applied = []

    # Патч для FuncLib.py
    if os.path.exists("FuncLib.py"):
        with open("FuncLib.py", 'r', encoding='utf-8') as f:
            content = f.read()

        # Заменяем прямой импорт на условный
        if "import torch" in content:
            patched_content = '''try:
    import torch
    import torchaudio
except ImportError:
    # Stub для сборки
    class TorchStub:
        def __getattr__(self, name):
            return TorchStub()
        def __call__(self, *args, **kwargs):
            return TorchStub()

    torch = TorchStub()
    torchaudio = TorchStub()
    torch.__version__ = "stub"
    torchaudio.__version__ = "stub"

    print("⚠️  Torch используется в режиме заглушки")

''' + content

            # Делаем backup
            shutil.copy("FuncLib.py", "FuncLib.py.backup")

            with open("FuncLib.py", 'w', encoding='utf-8') as f:
                f.write(patched_content)

            patches_applied.append("FuncLib.py")
            print("✅ Исправлен FuncLib.py для работы с torch")

    return patches_applied


def collect_torch_dependencies():
    """Собирает все зависимости torch для PyInstaller"""
    dependencies = []

    # Основные модули torch
    torch_modules = [
        'torch',
        'torch._C',
        'torch.nn',
        'torch.nn.functional',
        'torch.nn.modules',
        'torch.nn.parameter',
        'torch.optim',
        'torch.utils',
        'torch.utils.data',
        'torchvision',
        'torchaudio',
        'torchaudio.backend',
        'torchaudio.functional',
        'torchaudio.datasets',
        'numpy',
        'numpy.core._multiarray_umath',
        'numpy.core._dtype_ctypes',
    ]

    # Добавляем как hidden imports
    for module in torch_modules:
        dependencies.append(f"--hidden-import={module}")

    # Собираем данные torch
    dependencies.append("--collect-data=torch")
    dependencies.append("--collect-binaries=torch")

    return dependencies


def build_with_torch_support():
    """Сборка с полной поддержкой torch"""
    print("🎯 Стратегия: Сборка С поддержкой Torch")

    # Устанавливаем torch если нужно
    if not install_torch_cpu():
        print("⚠️  Не удалось установить torch, использую заглушку")
        create_torch_stub_if_needed()

    # Патчим файлы
    patched_files = patch_files_for_torch()

    # Основная команда
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # ВАЖНО: папкой, torch плохо работает в onefile!
        "--windowed",
        "--clean",
        "--name=AudioAssistant",
        "--add-data=commands.json;.",
        "--add-data=config.json;.",
        "--add-data=cfg.json;.",
    ]

    # Добавляем зависимости torch
    cmd.extend(collect_torch_dependencies())

    # Добавляем другие импорты
    cmd.extend([
        "--hidden-import=main",
        "--hidden-import=FuncLib",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
    ])

    # Добавляем исключения для уменьшения размера
    cmd.extend([
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=pandas",
        "--exclude-module=tkinter",
    ])

    # Основной файл
    cmd.append("GUI.py")

    return cmd, patched_files


def build_without_torch():
    """Сборка без torch"""
    print("🎯 Стратегия: Сборка БЕЗ Torch")

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
        "GUI.py"
    ]

    return cmd, []


def detect_torch_usage():
    """Определяет использование torch в проекте"""
    print("🔍 Анализирую использование torch...")

    torch_used = False
    torch_files = []

    for filename in ["FuncLib.py", "main.py", "GUI.py"]:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

                # Проверяем импорт
                if "import torch" in content or "from torch" in content:
                    torch_used = True
                    torch_files.append(filename)

                    # Проверяем использование функций torch
                    torch_functions = ["torch.", "nn.", "Tensor", "tensor(", "torch.load", "torch.save"]
                    for func in torch_functions:
                        if func in content:
                            print(f"  ✅ {filename}: использует torch")
                            break
                    else:
                        print(f"  ⚠️  {filename}: импортирует torch, но не использует")

    if torch_used:
        print(f"\n📊 Torch используется в {len(torch_files)} файлах")
        return True
    else:
        print("📊 Torch не используется")
        return False


def restore_patched_files(patched_files):
    """Восстанавливает запатченные файлы"""
    for filename in patched_files:
        backup_file = f"{filename}.backup"
        if os.path.exists(backup_file):
            shutil.copy(backup_file, filename)
            os.remove(backup_file)
            print(f"📋 Восстановлен: {filename}")


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

    # Определяем использование torch
    uses_torch = detect_torch_usage()

    # Проверяем Vosk
    vosk_status = check_and_fix_vosk_import()

    # Создаем backup файлов
    backup_files = backup_and_restore_files()

    try:
        # Выбираем стратегию сборки
        if uses_torch:
            cmd, patched_files = build_with_torch_support()
            build_type = "with_torch"
        else:
            cmd, patched_files = build_without_torch()
            build_type = "without_torch"

        print(f"\n🚀 Команда сборки:")
        print("   " + " ".join(cmd[:8]) + "...")

        # 1. Сборка exe
        print("\n🔨 Запускаю сборку...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Ошибка сборки:")
            print(result.stderr[:500])  # Показываем первые 500 символов ошибки

            # Если ошибка с torch, пробуем без него
            if "torch" in result.stderr and build_type == "with_torch":
                print("\n🔄 Пробую сборку БЕЗ torch...")
                restore_patched_files(patched_files)
                cmd, patched_files = build_without_torch()
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"❌ Ошибка сборки без torch:")
                    print(result.stderr[:500])
                    return

        print("✅ Сборка PyInstaller завершена!")

        # Определяем папку с результатом
        if "--onedir" in cmd:
            dist_dir = "dist/AudioAssistant"
            exe_name = "AudioAssistant.exe"
        else:
            dist_dir = "dist"
            exe_name = "AudioAssistant.exe"

        os.makedirs(dist_dir, exist_ok=True)

        # 2. Копируем все необходимые файлы
        print("\n📂 Копирую дополнительные файлы...")

        files_to_copy = [
            "commands.json",
            "config.json",
            "cfg.json",
        ]

        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, dist_dir)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} не найден")

        # 3. Копируем модель Vosk если есть
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

        # 4. Создаем конфигурационный файл для пользователя
        create_user_config(dist_dir, build_type, vosk_status)

        # 5. Создаем README
        create_readme(dist_dir, build_type, vosk_status)

        # 6. Показываем результат
        show_build_result(dist_dir, build_type)

    finally:
        # Всегда восстанавливаем файлы
        print("\n📋 Восстанавливаю исходные файлы...")
        restore_backup_files(backup_files)
        restore_patched_files(patched_files)

        # Удаляем временные файлы
        temp_files = ["vosk_stub.py", "torch_stub.py"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def create_user_config(dist_dir, build_type, vosk_status):
    """Создает конфигурационный файл для пользователя"""
    config = {
        "build_info": {
            "build_type": build_type,
            "has_torch": build_type == "with_torch",
            "has_vosk": vosk_status in ["with_model", "with_stub"],
            "vosk_status": vosk_status,
            "date": os.path.getctime("dist/AudioAssistant.exe") if os.path.exists("dist/AudioAssistant.exe") else None
        },
        "requirements": {
            "torch": "Установите через: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu" if build_type == "with_torch" else "Не требуется",
            "vosk": "Скачайте модель с https://alphacephei.com/vosk/models" if vosk_status == "with_stub" else "Включено в сборку" if vosk_status == "with_model" else "Не используется"
        }
    }

    config_path = os.path.join(dist_dir, "build_info.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

    print(f"  ✅ Конфиг создан: build_info.json")


def create_readme(dist_dir, build_type, vosk_status):
    """Создает README файл"""

    # Раздел про torch
    if build_type == "with_torch":
        torch_note = """
## 🧠 Машинное обучение (PyTorch)
Программа использует PyTorch для обработки аудио.
Torch включен в сборку (CPU версия).
"""
    else:
        torch_note = """
## 🧠 Машинное обучение (PyTorch)
PyTorch не используется в этой сборке.
"""

    # Раздел про vosk
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

{torch_note}
{vosk_note}
## ⚙️ Настройка
- Отредактируйте `commands.json` - добавьте свои команды
- Отредактируйте `config.json` - настройки программы
- Отредактируйте `cfg.json` - дополнительные настройки

## 🎯 Горячие клавиши
По умолчанию: Ctrl+Alt+A

## 📊 Информация о сборке
Детали сборки в файле `build_info.json`

## ❓ Помощь
При проблемах:
1. Проверьте наличие всех .json файлов
2. Запустите от имени администратора
3. Проверьте доступ к микрофону
4. Если ошибка torch - установите: pip install torch torchaudio

## 📞 Поддержка
GitHub: https://github.com/NotName465/audioAssistant
"""

    readme_path = os.path.join(dist_dir, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"  ✅ README.txt создан")


def show_build_result(dist_dir, build_type):
    """Показывает результат сборки"""
    if build_type == "with_torch":
        exe_path = os.path.join(dist_dir, "AudioAssistant.exe")
    else:
        exe_path = os.path.join(dist_dir, "AudioAssistant.exe")

    print("\n" + "=" * 50)

    if os.path.exists(exe_path):
        # Получаем размер
        if build_type == "with_torch":
            # Для папки считаем общий размер
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(dist_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            size_mb = total_size / (1024 * 1024)
            print(f"📦 Собрано как ПАПКА (torch требует этого)")
        else:
            size_bytes = os.path.getsize(exe_path)
            size_mb = size_bytes / (1024 * 1024)
            print(f"📦 Собрано как ОДИН ФАЙЛ")

        print("✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 50)
        print(f"📁 Папка: {dist_dir}/")
        print(f"🚀 Файл: AudioAssistant.exe")
        print(f"📊 Размер: {size_mb:.2f} MB")

        if build_type == "with_torch":
            print(f"🔧 Тип: С поддержкой PyTorch")
        else:
            print(f"🔧 Тип: Без PyTorch")

        print("\n📋 Содержимое:")
        for item in sorted(os.listdir(dist_dir)):
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


# Добавляем недостающие функции (из предыдущего кода)
def download_vosk_model():
    """Скачивает модель Vosk если она отсутствует"""
    # ... (код из предыдущего ответа) ...
    return None


def check_and_fix_vosk_import():
    """Проверяет и исправляет импорт Vosk если нужно"""
    # ... (код из предыдущего ответа) ...
    return "no_vosk"


def backup_and_restore_files():
    """Создает backup файлов и восстанавливает их после сборки"""
    return []


if __name__ == "__main__":
    build_complete()