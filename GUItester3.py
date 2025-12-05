# main.py - пример интеграции
import customtkinter as ctk
from tester2 import VoiceSynthesizer
from voice_gui_integration import VoiceSettingsPanel


class AudioAssistantApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Audio Assistant with Silero TTS")
        self.root.geometry("800x700")

        # Инициализация синтезатора
        self.voice_synth = VoiceSynthesizer()

        # Создание GUI
        self.create_gui()

    def create_gui(self):
        # Основной контейнер
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая панель - основное управление
        left_panel = ctk.CTkFrame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Правая панель - настройки голоса
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Создаем панель настроек голоса
        self.voice_panel = VoiceSettingsPanel(
            right_panel,
            self.voice_synth,
            on_settings_change=self.on_voice_settings_change
        )

        # Основные элементы управления
        self.create_main_controls(left_panel)

        # Горячие клавиши
        self.setup_hotkeys()

    def create_main_controls(self, parent):
        # Заголовок
        title = ctk.CTkLabel(
            parent,
            text="🎙️ Аудио Ассистент",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Статус ассистента
        self.status_label = ctk.CTkLabel(
            parent,
            text="Статус: Ожидание",
            font=ctk.CTkFont(size=14)
        )
        self.status_label.pack(pady=10)

        # Основная кнопка
        self.assistant_button = ctk.CTkButton(
            parent,
            text="🎤 Запуск ассистента",
            command=self.toggle_assistant,
            height=50,
            font=ctk.CTkFont(size=16)
        )
        self.assistant_button.pack(pady=20, padx=20, fill="x")

        # Быстрые команды
        quick_frame = ctk.CTkFrame(parent)
        quick_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(
            quick_frame,
            text="Быстрые команды:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        commands = [
            ("Приветствие", "Привет! Как дела?"),
            ("Время", "Сейчас 12:30"),
            ("Погода", "На улице 20 градусов, солнечно"),
            ("Английский", "Hello! How are you today?")
        ]

        for cmd_text, speak_text in commands:
            btn = ctk.CTkButton(
                quick_frame,
                text=cmd_text,
                command=lambda t=speak_text: self.speak_command(t),
                width=120
            )
            btn.pack(side="left", padx=5, pady=5)

        # Консоль вывода
        console_frame = ctk.CTkFrame(parent)
        console_frame.pack(fill="both", expand=True, pady=20, padx=20)

        ctk.CTkLabel(
            console_frame,
            text="Консоль:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=(10, 5))

        self.console_text = ctk.CTkTextbox(
            console_frame,
            height=150
        )
        self.console_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        self.root.bind('<Control-s>', lambda e: self.voice_synth.stop())
        self.root.bind('<Control-t>', lambda e: self.test_voice())
        self.root.bind('<Control-1>', lambda e: self.set_voice('aidar', 'ru'))
        self.root.bind('<Control-2>', lambda e: self.set_voice('baya', 'ru'))
        self.root.bind('<Control-3>', lambda e: self.set_voice('en_0', 'en'))
        self.root.bind('<Control-4>', lambda e: self.set_voice('en_1', 'en'))

    def toggle_assistant(self):
        """Переключение состояния ассистента"""
        # Здесь будет логика включения/выключения ассистента
        pass

    def speak_command(self, text):
        """Произнесение команды"""
        self.log_to_console(f"🗣️ Произношу: {text[:50]}...")

        # Запускаем в отдельном потоке
        import threading
        thread = threading.Thread(
            target=self.voice_synth.speak,
            args=(text,),
            daemon=True
        )
        thread.start()

    def test_voice(self):
        """Тестирование голоса"""
        self.voice_synth.speak("Тест синтеза речи. Работает отлично!")

    def set_voice(self, voice, language):
        """Быстрая установка голоса"""
        self.voice_synth.set_voice(voice, language)
        self.log_to_console(f"Голос изменен: {voice} ({language})")

    def on_voice_settings_change(self):
        """Обработка изменения настроек голоса"""
        self.log_to_console("Настройки голоса обновлены")

    def log_to_console(self, message):
        """Логирование в консоль"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console_text.insert("end", f"[{timestamp}] {message}\n")
        self.console_text.see("end")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AudioAssistantApp()
    app.run()