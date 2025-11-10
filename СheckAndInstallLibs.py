import subprocess
import sys

ALL_IMPORTS = {
    # main.py
    'speech_recognition': 'speechrecognition',
    'pyttsx3': 'pyttsx3',
    'pyaudio': 'pyaudio',
    'requests': 'requests',
    'pygame': 'pygame',
    'dotenv': 'python-dotenv',
    'vosk': 'vosk',
    'sounddevice': 'sounddevice',

    # FuncLib.py
    'pycaw.pycaw': 'pycaw',
    'comtypes': 'comtypes',
    'psutil': 'psutil',

    # commands.py
    'bs4': 'beautifulsoup4',
    'urllib3': 'urllib3',

    # Встроенные библиотеки (для информации)
    'os': 'built-in',
    'sys': 'built-in',
    'json': 'built-in',
    'time': 'built-in',
    'math': 'built-in',
    'random': 'built-in',
    'threading': 'built-in',
    'subprocess': 'built-in',
    'datetime': 'built-in',
    'webbrowser': 'built-in',
    'wave': 'built-in',
    'ctypes': 'built-in',
}


def install_package(package_name):

    try:
        print(f"📦 Устанавливаю {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} успешно установлен")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки {package_name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка при установке {package_name}: {e}")
        return False


def check_and_install_imports():
    """Проверяет и автоматически устанавливает недостающие библиотеки"""
    print("🔍 Проверка ВСЕХ импортов проекта...")
    print("=" * 70)

    external_missing = []
    built_in_ok = []
    installed_now = []

    for import_name, package_name in ALL_IMPORTS.items():
        try:
            # Чистим имя для импорта
            clean_import = import_name.split('.')[0]
            __import__(clean_import)

            if package_name == 'built-in':
                built_in_ok.append(import_name)
            else:
                print(f"✅ {import_name:20} -> {package_name}")

        except ImportError as e:
            if package_name != 'built-in':
                print(f"❌ {import_name:20} -> {package_name} - ОШИБКА: {e}")
                external_missing.append((import_name, package_name))

    # Автоматическая установка недостающих библиотек
    if external_missing:
        print(f"\n⚠️  Обнаружено {len(external_missing)} отсутствующих библиотек")
        print("🚀 Начинаю автоматическую установку...")
        print("-" * 50)

        for import_name, package_name in external_missing:
            if install_package(package_name):
                installed_now.append((import_name, package_name))

        # Повторная проверка после установки
        if installed_now:
            print("\n" + "=" * 50)
            print("🔄 Повторная проверка установленных библиотек...")
            print("=" * 50)

            still_missing = []
            for import_name, package_name in installed_now:
                try:
                    clean_import = import_name.split('.')[0]
                    __import__(clean_import)
                    print(f"✅ {import_name:20} -> Успешно установлен и загружен")
                except ImportError as e:
                    print(f"❌ {import_name:20} -> Все еще не доступен: {e}")
                    still_missing.append((import_name, package_name))

            if still_missing:
                print(f"\n💥 Не удалось установить {len(still_missing)} библиотек:")
                for import_name, package_name in still_missing:
                    print(f"   ❌ {import_name} -> {package_name}")

    # Вывод итогов
    print("\n" + "=" * 70)
    print("📊 ИТОГИ:")

    if built_in_ok:
        print(f"✅ Встроенные библиотеки Python ({len(built_in_ok)}): готовы")

    total_external = len([p for p in ALL_IMPORTS.values() if p != 'built-in'])
    missing_count = len([im for im, pkg in external_missing if (im, pkg) not in installed_now])

    print(f"✅ Внешние библиотеки: {total_external - missing_count}/{total_external} установлено")

    if missing_count == 0:
        print("🎉 Все библиотеки установлены! Проект готов к работе.")
        return True
    else:
        print(f"💥 Осталось проблем: {missing_count} библиотек не установлено")
        print("\n🔧 Ручная установка:")
        for import_name, package_name in external_missing:
            if (import_name, package_name) not in installed_now:
                print(f"   pip install {package_name}")
        return False


# def create_requirements_file():
#     """Создает файл requirements.txt с текущими зависимостями"""
#     requirements_content = """# Requirements for audioAssistant project
# # Generated automatically
# # pip install -r requirements.txt - ручная установка.
# # Основные библиотеки для голосового помощника
# speechrecognition==3.10.0
# pyttsx3==2.90
# pyaudio==0.2.11
# requests==2.31.0
# pygame==2.5.2
# python-dotenv==1.0.0
#
# # Для оффлайн распознавания речи
# vosk==0.3.45
# sounddevice==0.4.6
#
# # Для управления громкостью Windows
# pycaw==2023.8.23
# comtypes==1.1.14
#
# # Дополнительные утилиты
# psutil==5.9.6
# beautifulsoup4==4.12.2
# urllib3==2.0.7
# """

    # try:
    #     with open('requirements.txt', 'w', encoding='utf-8') as f:
    #         f.write(requirements_content)
    #     print("📄 Файл requirements.txt создан/обновлен")
    # except Exception as e:
    #     print(f"❌ Ошибка создания requirements.txt: {e}")



def startCheckLibs():
    print("🚀 AudioAssistant - Установщик зависимостей")
    print("=" * 70)

    # Проверяем и устанавливаем библиотеки
    success = check_and_install_imports()

    # # Создаем файл requirements.txt
    # create_requirements_file()

    # Финальное сообщение
    if success:
        print("\n🎯 ВСЕ ГОТОВО! Запускаю голосовой помощник:")
        print("...")
        print("...")
        print("...")
        return True
    else:
        print("\n⚠️  Есть проблемы с установкой. Проверьте вывод выше.")
        return False
