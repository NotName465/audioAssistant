from tester import BrowserSearcher1
import time
searcher = BrowserSearcher1()

# Тестовые примеры
searcher.search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Нарды онлайн")  # Русский
time.sleep(5)

searcher.search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Python code")  # Английский
time.sleep(5)

searcher.search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Python программирование")  # Смешанный
time.sleep(5)

searcher.search(r"C:\Users\user\AppData\Local\Programs\Opera GX\opera.exe", "Test Тест")  # Чередование