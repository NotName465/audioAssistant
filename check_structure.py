import os

print("📁 Проверка структуры проекта:")
print("=" * 40)

files = [
    "GUI.py",
    "main.py",
    "FuncLib.py",
    "commands.json",
    "config.json",
    "cfg.json"
]

all_ok = True
for file in files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - НЕ НАЙДЕН!")
        all_ok = False

print("=" * 40)
if all_ok:
    print("🎯 Все файлы на месте! Можно собирать.")
else:
    print("⚠️  Не все файлы найдены!")

print(f"\n📂 Текущая папка: {os.getcwd()}")