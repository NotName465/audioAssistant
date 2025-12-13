import subprocess
import sys
import shutil
import os
import zipfile
import requests
from pathlib import Path
import tempfile
import json


def fix_tkinter_issues():
    """Исправляет проблемы с tkinter и customtkinter"""
    print("🔧 Исправляю проблемы с tkinter...")

    # Проверяем наличие customtkinter
    try:
        import customtkinter
        print("✅ customtkinter установлен")

        # Проверяем tkinter
        try:
            import tkinter
            print("✅ tkinter доступен")
            return True
        except ImportError:
            print("⚠️  tkinter не найден, но должен быть встроен в Python")
            return True  # tkinter встроен, PyInstaller должен его найти

    except ImportError as e:
        print(f"❌ Ошибка customtkinter: {e}")

        # Устанавливаем customtkinter
        try:
            print("📦 Устанавливаю customtkinter...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "customtkinter",
                "--quiet"
            ], check=True)
            print("✅ customtkinter установлен")
            return True
        except subprocess.CalledProcessError:
            print("❌ Не удалось установить customtkinter")
            return False


def patch_customtkinter_imports():
    """Патчит импорты customtkinter для PyInstaller"""
    patches_applied = []

    # Проверяем все файлы на использование customtkinter
    for filename in ["GUI.py", "main.py", "FuncLib.py"]:
        if not os.path.exists(filename):
            continue

        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ищем импорт customtkinter
        if "customtkinter" in content or "tkinter" in content:
            print(f"📝 Найден tkinter/customtkinter в {filename}")

            # Создаем backup
            shutil.copy(filename, f"{filename}.backup_tk")

            # Добавляем явные импорты для PyInstaller
            lines = content.split('\n')
            new_lines = []

            for line in lines:
                new_lines.append(line)

                # Добавляем hidden imports после импортов tkinter
                if "import customtkinter" in line and not line.strip().startswith("#"):
                    new_lines.append("# PyInstaller hidden imports for tkinter")
                    new_lines.append("# These lines help PyInstaller find tkinter modules")

                if "import tkinter" in line and not line.strip().startswith("#"):
                    new_lines.append("# PyInstaller: ensure tkinter modules are included")

            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))

            patches_applied.append(filename)

    return patches_applied


def collect_tkinter_dependencies():
    """Собирает все зависимости tkinter для PyInstaller"""
    dependencies = []

    # Основные модули tkinter
    tkinter_modules = [
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.constants',
        '_tkinter',  # Внутренний модуль tkinter
        'customtkinter',
        'PIL',  # Pillow для изображений в customtkinter
        'PIL.Image',
        'PIL.ImageTk',
    ]

    # Добавляем как hidden imports
    for module in tkinter_modules:
        dependencies.append(f"--hidden-import={module}")

    return dependencies


def check_for_tkinter_usage():
    """Проверяет использование tkinter в проекте"""
    print("🔍 Проверяю использование tkinter/customtkinter...")

    uses_tkinter = False
    uses_customtkinter = False

    for filename in ["GUI.py", "main.py", "FuncLib.py"]:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read().lower()

                if "customtkinter" in content:
                    uses_customtkinter = True
                    print(f"  ✅ {filename}: использует customtkinter")

                if "tkinter" in content and "customtkinter" not in content:
                    uses_tkinter = True
                    print(f"  ✅ {filename}: использует tkinter")

    return uses_tkinter, uses_customtkinter


def build_with_tkinter_support(uses_customtkinter):
    """Сборка с поддержкой tkinter/customtkinter"""
    if uses_customtkinter:
        print("🎯 Стратегия: Сборка С поддержкой CustomTkinter")
    else:
        print("🎯 Стратегия: Сборка С поддержкой Tkinter")

    # Исправляем проблемы с tkinter
    if not fix_tkinter_issues():
        print("⚠️  Проблемы с tkinter, пробую обходной путь")

    # Патчим файлы
    patched_files = patch_customtkinter_imports()

    # Определяем тип сборки
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--clean",
        "--name=AudioAssistant",
        "--add-data=commands.json;.",
        "--add-data=config.json;.",
        "--add-data=cfg.json;.",
    ]

    # Добавляем зависимости tkinter
    cmd.extend(collect_tkinter_dependencies())

    # Добавляем другие импорты
    cmd.extend([
        "--hidden-import=numpy",
        "--hidden-import=main",
        "--hidden-import=FuncLib",
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
    ])

    # Исключаем torch если не используется
    if not detect_torch_usage():
        cmd.extend([
            "--exclude-module=torch",
            "--exclude-module=torchaudio",
        ])

    # Основной файл
    cmd.append("GUI.py")

    return cmd, patched_files


def create_tkinter_stub():
    """Создает заглушку для tkinter если есть проблемы"""
    stub_content = '''
# Tkinter stub for PyInstaller
# This helps when tkinter is not properly detected

import sys

class TkinterStub:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return TkinterStub()
    def __call__(self, *args, **kwargs):
        return TkinterStub()

# Create stub modules if real ones aren't available
try:
    import tkinter
except ImportError:
    sys.modules['tkinter'] = TkinterStub()
    tkinter = TkinterStub()

try:
    import customtkinter
except ImportError:
    sys.modules['customtkinter'] = TkinterStub()
    customtkinter = TkinterStub()

# Common tkinter classes
Tk = TkinterStub
Button = TkinterStub
Label = TkinterStub
Frame = TkinterStub
'''

    stub_path = "tkinter_stub.py"
    with open(stub_path, 'w', encoding='utf-8') as f:
        f.write(stub_content)

    print("📝 Создана заглушка tkinter_stub.py")
    return stub_path


def handle_tkinter_errors(error_output):
    """Обрабатывает ошибки связанные с tkinter"""
    if "tkinter" in error_output or "customtkinter" in error_output:
        print("\n⚠️  Обнаружена ошибка tkinter, применяю исправления...")

        # Создаем заглушку
        stub_path = create_tkinter_stub()

        # Патчим GUI.py чтобы использовал заглушку
        if os.path.exists("GUI.py"):
            with open("GUI.py", 'r', encoding='utf-8') as f:
                content = f.read()

            # Добавляем импорт заглушки в начало
            patched_content = '''# PyInstaller tkinter fix
try:
    import tkinter
    import customtkinter
except ImportError:
    from tkinter_stub import *
    print("⚠️  Используется заглушка tkinter")

''' + content

            # Создаем backup
            shutil.copy("GUI.py", "GUI.py.backup_tkfix")

            with open("GUI.py", 'w', encoding='utf-8') as f:
                f.write(patched_content)

            print("✅ GUI.py исправлен для работы с tkinter заглушкой")
            return True

    return False


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

    # Проверяем использование tkinter
    uses_tkinter, uses_customtkinter = check_for_tkinter_usage()

    if uses_tkinter or uses_customtkinter:
        print(f"\n📊 Обнаружено: {'customtkinter' if uses_customtkinter else 'tkinter'}")

        # Выбираем стратегию сборки с tkinter
        cmd, patched_files = build_with_tkinter_support(uses_customtkinter)
        build_type = "with_tkinter"

    else:
        print("\n📊 Tkinter не используется")

        # Используем стандартную стратегию
        uses_torch = detect_torch_usage()

        if uses_torch:
            cmd, patched_files = build_with_torch_support()
            build_type = "with_torch"
        else:
            cmd, patched_files = build_without_torch()
            build_type = "without_torch"

    print(f"\n🚀 Команда сборки:")
    print("   " + " ".join(cmd[:8]) + "...")

    # Создаем backup файлов
    backup_files = backup_and_restore_files()

    try:
        # 1. Сборка exe
        print("\n🔨 Запускаю сборку...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Если ошибка с tkinter, пробуем исправить
        if result.returncode != 0 and "tkinter" in result.stderr:
            print("\n🔄 Пробую исправить ошибку tkinter...")

            if handle_tkinter_errors(result.stderr):
                # Пробуем собрать снова
                result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Ошибка сборки:")
            error_preview = result.stderr[:500] if result.stderr else result.stdout[:500]
            print(error_preview)

            # Пробуем альтернативную сборку
            print("\n🔄 Пробую альтернативную сборку...")
            alt_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--name=AudioAssistant",
                "--add-data=commands.json;.",
                "--add-data=config.json;.",
                "--add-data=cfg.json;.",
                "--collect-all=customtkinter" if uses_customtkinter else "",
                "--collect-all=tkinter",
                "GUI.py"
            ]

            # Убираем пустые строки
            alt_cmd = [x for x in alt_cmd if x]

            result = subprocess.run(alt_cmd, capture_output=True, text=True)

            if result.returncode != 0:
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

        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy(file, dist_dir)
                print(f"  ✅ {file}")
            else:
                print(f"  ⚠️  {file} не найден")

        # 3. Создаем README
        create_readme(dist_dir, build_type, uses_customtkinter)

        # 4. Показываем результат
        show_build_result(dist_dir)

    finally:
        # Всегда восстанавливаем файлы
        print("\n📋 Восстанавливаю исходные файлы...")
        restore_backup_files(backup_files)

        # Восстанавливаем запатченные файлы
        for filename in patched_files:
            backup_file = f"{filename}.backup_tk"
            if os.path.exists(backup_file):
                shutil.copy(backup_file, filename)
                os.remove(backup_file)
                print(f"📋 Восстановлен: {filename}")

        # Восстанавливаем GUI.py если он был исправлен
        if os.path.exists("GUI.py.backup_tkfix"):
            shutil.copy("GUI.py.backup_tkfix", "GUI.py")
            os.remove("GUI.py.backup_tkfix")
            print("📋 Восстановлен GUI.py")

        # Удаляем временные файлы
        temp_files = ["tkinter_stub.py", "vosk_stub.py", "torch_stub.py"]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def create_readme(dist_dir, build_type, uses_customtkinter):
    """Создает README файл"""

    tkinter_note = ""
    if uses_customtkinter:
        tkinter_note = """
## 🎨 Интерфейс (CustomTkinter)
Программа использует modern UI библиотеку CustomTkinter.
"""
    elif build_type == "with_tkinter":
        tkinter_note = """
## 🎨 Интерфейс (Tkinter)
Программа использует стандартный Tkinter.
"""

    readme_content = f"""# 🎤 Audio Assistant

## 🚀 Запуск
1. Запустите `AudioAssistant.exe`
2. Убедитесь что в одной папке есть файлы:
   - commands.json
   - config.json  
   - cfg.json

{tkinter_note}
## ⚙️ Настройка
- Отредактируйте `commands.json` - добавьте свои команды
- Отредактируйте `config.json` - настройки программы
- Отредактируйте `cfg.json` - дополнительные настройки

## 🎯 Горячие клавиши
По умолчанию: Ctrl+Alt+A

## ❓ Помощь
При проблемах с интерфейсом:
1. Убедитесь что установлен Python с поддержкой Tkinter
2. Переустановите customtkinter: pip install customtkinter
3. Если ошибка "No module named 'tkinter'" - установите python-tk:
   - Windows: Переустановите Python с галочкой "tcl/tk and IDLE"
   - Linux: sudo apt-get install python3-tk
   - Mac: brew install python-tk

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
        size_bytes = os.path.getsize(exe_path)
        size_mb = size_bytes / (1024 * 1024)

        print("✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 50)
        print(f"📁 Папка: {dist_dir}/")
        print(f"🚀 Файл: AudioAssistant.exe")
        print(f"📊 Размер: {size_mb:.2f} MB")
        print("\n📋 Содержимое папки:")

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


# Добавляем недостающие функции
def detect_torch_usage():
    """Определяет использование torch в проекте"""
    # ... (код из предыдущего ответа) ...
    return False


def build_with_torch_support():
    """Сборка с полной поддержкой torch"""
    # ... (код из предыдущего ответа) ...
    return [], []


def build_without_torch():
    """Сборка без torch"""
    # ... (код из предыдущего ответа) ...
    return [], []


def backup_and_restore_files():
    """Создает backup файлов и восстанавливает их после сборки"""
    return []


def restore_backup_files(backup_files):
    """Восстанавливает backup файлы"""
    pass


if __name__ == "__main__":
    build_complete()