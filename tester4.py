import pyautogui
import time
import webbrowser
import subprocess


class YouTubeController:
    def __init__(self, browser_path=None):
        self.browser_path = browser_path
        self.is_playing = False

    def open_youtube(self, url="https://www.youtube.com"):
        """Открывает YouTube в браузере"""
        if self.browser_path:
            subprocess.Popen([self.browser_path, url])
        else:
            webbrowser.open(url)
        time.sleep(3)
        print("✅ YouTube открыт")

    def search_video(self, query):
        """Ищет видео на YouTube"""
        # Фокус на поисковую строку
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

        # Вводим запрос
        pyautogui.write(f"www.youtube.com/results?search_query={query.replace(' ', '+')}")
        pyautogui.press('enter')
        time.sleep(2)
        print(f"🔍 Поиск: {query}")

    def click_video(self, position=1):
        """Кликает на видео по позиции (1 - первое видео)"""
        # Примерные координаты для первого видео (зависит от разрешения экрана)
        video_positions = {
            1: (400, 400),  # Первое видео
            2: (400, 600),  # Второе видео
            3: (400, 800),  # Третье видео
        }

        if position in video_positions:
            x, y = video_positions[position]
            pyautogui.click(x, y)
            time.sleep(2)
            print(f"🎬 Открыто видео #{position}")
            self.is_playing = True
        else:
            print("❌ Позиция не найдена")

    def play_pause(self):
        """Воспроизведение/пауза"""
        pyautogui.press('k')  # Space тоже работает
        self.is_playing = not self.is_playing
        print(f"{'⏸️ Пауза' if not self.is_playing else '▶️ Воспроизведение'}")

    def volume_up(self):
        """Увеличить громкость"""
        pyautogui.press('up')
        print("🔊 Громкость +")

    def volume_down(self):
        """Уменьшить громкость"""
        pyautogui.press('down')
        print("🔉 Громкость -")

    def mute_unmute(self):
        """Включить/выключить звук"""
        pyautogui.press('m')
        print("🔇 Переключение звука")

    def skip_forward(self, seconds=10):
        """Перемотать вперед"""
        pyautogui.press('right')
        print(f"⏩ Перемотка +{seconds}сек")

    def skip_backward(self, seconds=10):
        """Перемотать назад"""
        pyautogui.press('left')
        print(f"⏪ Перемотка -{seconds}сек")

    def fullscreen(self):
        """Полноэкранный режим"""
        pyautogui.press('f')
        print("🖥️ Полноэкранный режим")

    def theater_mode(self):
        """Режим кинотеатра"""
        pyautogui.press('t')
        print("🎭 Режим кинотеатра")

    def next_video(self):
        """Следующее видео (в плейлисте)"""
        pyautogui.press('shift', 'n')
        print("⏭️ Следующее видео")

    def previous_video(self):
        """Предыдущее видео (в плейлисте)"""
        pyautogui.press('shift', 'p')
        print("⏮️ Предыдущее видео")

    def like_video(self):
        """Поставить лайк"""
        pyautogui.press('l')
        print("👍 Лайк")

    def dislike_video(self):
        """Поставить дизлайк"""
        pyautogui.press('d')
        print("👎 Дизлайк")

    def toggle_subtitles(self):
        """Включить/выключить субтитры"""
        pyautogui.press('c')
        print("📝 Субтитры")

    def increase_speed(self):
        """Увеличить скорость воспроизведения"""
        pyautogui.press('>')  # Shift + .
        print("⚡ Скорость +")

    def decrease_speed(self):
        """Уменьшить скорость воспроизведения"""
        pyautogui.press('<')  # Shift + ,
        print("🐢 Скорость -")

    def seek_to_percentage(self, percentage):
        """Перейти к определенному проценту видео"""
        # Нажимаем цифру от 0-9 для перехода к 0%-90%
        if 0 <= percentage <= 9:
            pyautogui.press(str(percentage))
            print(f"🎯 Переход к {percentage}0%")
        else:
            print("❌ Процент должен быть от 0 до 9")


# Использование
yt = YouTubeController(r"C:\Program Files\Opera GX\opera.exe")

# Открываем YouTube
yt.open_youtube()

# Ищем и открываем видео
yt.search_video("python programming")
yt.click_video(1)  # Первое видео

# Управление воспроизведением
time.sleep(2)
yt.play_pause()
time.sleep(5)

yt.volume_up()
yt.skip_forward()
yt.fullscreen()

#тайная заготовочка