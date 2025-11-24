import soundcard as sc

# Получить все микрофоны
microphones = sc.all_microphones()

print("Доступные микрофоны:")
for mic in microphones:
    print(f"ID: {mic.id}")
    print(f"Название: {mic.name}")
    print(f"Каналы: {mic.channels}")
    print("-" * 30)

# Получить микрофон по умолчанию
default_mic = sc.default_microphone()
print(f"Микрофон по умолчанию: {default_mic.name}")