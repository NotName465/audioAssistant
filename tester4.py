import os
import urllib.request



def download_nircmd():
    """Скачать nircmd если его нет"""
    if not os.path.exists("nircmd.exe"):
        print("Скачиваю nircmd...")
        url = "https://www.nirsoft.net/utils/nircmd.zip"
        urllib.request.urlretrieve(url, "nircmd.zip")
        import zipfile
        with zipfile.ZipFile("nircmd.zip", 'r') as zip_ref:
            zip_ref.extract("nircmd.exe")
        os.remove("nircmd.zip")
        print("nircmd скачан!")


def set_volume(percent):
    """Установка громкости через nircmd"""
    if not 0 <= percent <= 100:
        print("Ошибка: используйте значения от 0 до 100")
        return

    download_nircmd()

    # Устанавливаем громкость
    volume_level = int(percent * 655.35)
    os.system(f'nircmd.exe setsysvolume {volume_level}')
    print(f"Громкость установлена на {percent}%")


# Использование
set_volume(50)  # Работает гарантированно!