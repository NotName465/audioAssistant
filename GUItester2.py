import customtkinter as ctk

# Настройка внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Создание главного окна
root = ctk.CTk()
root.configure(fg_color="#783518")
root.title("AudioAssistant")
root.geometry('400x600')
root.resizable(False, False)

# Цвета
BGColorForFirstButtoms = "#1A1A1A"
BGcolorForSettings = "#262626"

# Переменные для анимации
settings_visible = False
animation_running = False

# Создание выдвижной панели настроек
settings_panel = ctk.CTkFrame(root,
                              fg_color="#ff0000",  # Яркий цвет для теста
                              width=300,
                              height=600,
                              corner_radius=0)
settings_panel.place(x=-300, y=0, relwidth=0.75)  # relwidth для относительной ширины


# Функция для показа/скрытия панели настроек
def toggle_settings():
    global settings_visible, animation_running

    print(f"Функция toggle_settings вызвана! settings_visible: {settings_visible}")

    if animation_running:
        print("Анимация уже запущена, пропускаем")
        return

    animation_running = True

    if settings_visible:
        # Скрываем панель
        print("Скрываем панель...")
        hide_settings()
    else:
        # Показываем панель
        print("Показываем панель...")
        show_settings()


def show_settings():
    """Показывает панель настроек"""
    global settings_visible, animation_running

    def animate_show(frame=0):
        current_x = -300 + (frame * 15)  # 300 / 20 = 15
        settings_panel.place(x=current_x, y=0, relwidth=0.75)

        print(f"Показ: frame={frame}, x={current_x}")

        if frame < 20:  # 300px / 15 = 20 frames
            root.after(16, lambda: animate_show(frame + 1))
        else:
            settings_panel.place(x=0, y=0, relwidth=0.75)
            settings_visible = True
            animation_running = False
            print("Панель показана!")

    animate_show()


def hide_settings():
    """Скрывает панель настроек"""
    global settings_visible, animation_running

    def animate_hide(frame=0):
        current_x = 0 - (frame * 15)  # 300 / 20 = 15
        settings_panel.place(x=current_x, y=0, relwidth=0.75)

        print(f"Скрытие: frame={frame}, x={current_x}")

        if frame < 20:  # 300px / 15 = 20 frames
            root.after(16, lambda: animate_hide(frame + 1))
        else:
            settings_panel.place(x=-300, y=0, relwidth=0.75)
            settings_visible = False
            animation_running = False
            print("Панель скрыта!")

    animate_hide()


# Альтернативный вариант с pack (более надежный)
def toggle_settings_pack():
    """Альтернативная версия с использованием pack"""
    global settings_visible

    print(f"Pack версия: settings_visible={settings_visible}")

    if settings_visible:
        # Скрываем панель
        settings_panel.pack_forget()
        settings_visible = False
        print("Панель скрыта (pack)")
    else:
        # Показываем панель
        settings_panel.pack(side="left", fill="y", before=content_frame)
        settings_visible = True
        print("Панель показана (pack)")


# Создание содержимого панели настроек
def create_settings_content():
    # Заголовок настроек
    settings_title = ctk.CTkLabel(settings_panel,
                                  text="Настройки",
                                  text_color="white",
                                  font=ctk.CTkFont(size=20, weight="bold"))
    settings_title.pack(pady=20)

    # Разделитель
    separator = ctk.CTkFrame(settings_panel, height=2, fg_color="#444444")
    separator.pack(fill="x", padx=20, pady=10)

    # Настройка темы
    theme_label = ctk.CTkLabel(settings_panel,
                               text="Тема приложения:",
                               text_color="white",
                               font=ctk.CTkFont(size=14))
    theme_label.pack(anchor="w", padx=20, pady=(20, 5))

    theme_var = ctk.StringVar(value="dark")

    def change_theme(theme):
        ctk.set_appearance_mode(theme)

    theme_frame = ctk.CTkFrame(settings_panel, fg_color="transparent")
    theme_frame.pack(fill="x", padx=20, pady=5)

    dark_radio = ctk.CTkRadioButton(theme_frame, text="Тёмная", variable=theme_var,
                                    value="dark", command=lambda: change_theme("dark"))
    dark_radio.pack(side="left", padx=(0, 10))

    light_radio = ctk.CTkRadioButton(theme_frame, text="Светлая", variable=theme_var,
                                     value="light", command=lambda: change_theme("light"))
    light_radio.pack(side="left")

    # Кнопка закрытия настроек
    close_button = ctk.CTkButton(settings_panel,
                                 text="Закрыть",
                                 command=toggle_settings,
                                 fg_color="#ff4444",
                                 hover_color="#cc0000",
                                 height=35)
    close_button.pack(pady=20)

    # Тестовая кнопка для pack версии
    pack_button = ctk.CTkButton(settings_panel,
                                text="Тест Pack версии",
                                command=toggle_settings_pack,
                                fg_color="#00aaff",
                                hover_color="#0088cc",
                                height=35)
    pack_button.pack(pady=10)


# Верхняя панель заголовка
title_bar = ctk.CTkFrame(root, fg_color=BGColorForFirstButtoms, height=30, corner_radius=0)
title_bar.pack(fill="x", padx=0, pady=0)

# Контейнер для кнопок управления окном
buttons_frame = ctk.CTkFrame(title_bar, fg_color=BGColorForFirstButtoms, height=30, corner_radius=0)
buttons_frame.pack(side="right", padx=0)

# Кнопка закрытия
close_btn = ctk.CTkButton(buttons_frame,
                          text="X",
                          command=root.destroy,
                          fg_color=BGColorForFirstButtoms,
                          hover_color="#FF4444",
                          width=30,
                          height=30,
                          corner_radius=0)
close_btn.pack(side="right", padx=1)

NameProject = ctk.CTkLabel(title_bar,
                           text="AudioAssistant",
                           text_color="white",
                           fg_color=BGColorForFirstButtoms,
                           font=ctk.CTkFont(size=12, weight="bold"))
NameProject.pack(side="left", padx=10)

SettingsBar = ctk.CTkFrame(root,
                           fg_color=BGcolorForSettings,
                           height=40,
                           corner_radius=0)
SettingsBar.pack(fill="x", padx=0, pady=0)

# Контейнер для кнопок настроек
settings_buttons_frame = ctk.CTkFrame(SettingsBar,
                                      fg_color=BGcolorForSettings,
                                      height=40,
                                      corner_radius=0)
settings_buttons_frame.pack(side="right", padx=0)

# Кнопка настроек - используем place версию
SetBut = ctk.CTkButton(settings_buttons_frame,
                       text="⚙️ Настройки (Place)",
                       command=toggle_settings,
                       fg_color=BGcolorForSettings,
                       hover_color="#444444",
                       text_color="white",
                       height=30,
                       corner_radius=2)
SetBut.pack(side="right", padx=2)

# Кнопка для pack версии
SetButPack = ctk.CTkButton(settings_buttons_frame,
                           text="⚙️ Настройки (Pack)",
                           command=toggle_settings_pack,
                           fg_color=BGcolorForSettings,
                           hover_color="#444444",
                           text_color="white",
                           height=30,
                           corner_radius=2)
SetButPack.pack(side="right", padx=2)

Rus = ctk.CTkLabel(SettingsBar,
                   text="Сделано в России",
                   text_color="white",
                   fg_color=BGcolorForSettings,
                   font=ctk.CTkFont(size=10))
Rus.pack(side="left", padx=10)

# Основная область контента
content_frame = ctk.CTkFrame(root,
                             fg_color="#783518",
                             corner_radius=0)
content_frame.pack(fill="both", expand=True, padx=0, pady=0)

# Пример добавления контента
welcome_label = ctk.CTkLabel(content_frame,
                             text="Добро пожаловать в AudioAssistant!",
                             text_color="white",
                             font=ctk.CTkFont(size=16, weight="bold"))
welcome_label.pack(pady=50)

# Тестовые кнопки
test_button_place = ctk.CTkButton(content_frame,
                                  text="🎬 Тест Place анимации",
                                  command=toggle_settings,
                                  fg_color="#00aa00",
                                  hover_color="#008800")
test_button_place.pack(pady=10)

test_button_pack = ctk.CTkButton(content_frame,
                                 text="🎬 Тест Pack анимации",
                                 command=toggle_settings_pack,
                                 fg_color="#aa00aa",
                                 hover_color="#880088")
test_button_pack.pack(pady=10)

# Создаем содержимое панели настроек
create_settings_content()

root.mainloop()