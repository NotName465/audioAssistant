import ctypes
import time
import threading


class VolumeDetector:
    def __init__(self):
        self.estimated_volume = 50
        self.last_volume_change = time.time()

    def volume_up(self):
        """Увеличить громкость и запомнить изменение"""
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
        self.estimated_volume = min(100, self.estimated_volume + 2)
        self.last_volume_change = time.time()

    def volume_down(self):
        """Уменьшить громкость и запомнить изменение"""
        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
        self.estimated_volume = max(0, self.estimated_volume - 2)
        self.last_volume_change = time.time()

    def set_volume(self, percent):
        """Установить громкость через эмуляцию клавиш"""
        current = self.estimated_volume

        if percent > current:
            # Увеличиваем громкость
            steps = (percent - current) // 2
            for _ in range(steps):
                self.volume_up()
                time.sleep(0.05)
        else:
            # Уменьшаем громкость
            steps = (current - percent) // 2
            for _ in range(steps):
                self.volume_down()
                time.sleep(0.05)

        self.estimated_volume = percent

    def get_volume(self):
        """Получить предполагаемую громкость"""
        return self.estimated_volume


# Использование
volume_detector = VolumeDetector()
print(f"Предполагаемая громкость: {volume_detector.get_volume()}%")

# Установить на 80%
volume_detector.set_volume(80)
print(f"Новая громкость: {volume_detector.get_volume()}%")