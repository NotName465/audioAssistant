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

# Создание выдвижной панели настроек на всё окно
settings_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=400,
                              height=600,
                              corner_radius=0)

# Изначально скрываем панель и опускаем её
settings_panel.place(x=-400, y=0)
settings_panel.lower()  # Опускаем под все остальные виджеты


# Функция для показа/скрытия панели настроек с анимацией
def toggle_settings():
    global settings_visible, animation_running

    if animation_running:
        return

    if settings_visible:
        hide_settings_with_animation()
    else:
        show_settings_with_animation()


def show_settings_with_animation():
    """Плавно показывает панель настроек на всё окно"""
    global settings_visible, animation_running

    animation_running = True
    settings_panel.lift()  # Поднимаем на верхний слой перед анимацией

    def animate_show(frame=0):
        current_x = -400 + (frame * 20)
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            root.after(16, lambda: animate_show(frame + 1))
        else:
            settings_panel.place(x=0, y=0)
            settings_visible = True
            animation_running = False

    animate_show()


def hide_settings_with_animation():
    """Плавно скрывает панель настроек (обратная анимация)"""
    global settings_visible, animation_running

    animation_running = True

    def animate_hide(frame=0):
        current_x = 0 - (frame * 20)  # Двигаем от 0 до -400
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            root.after(16, lambda: animate_hide(frame + 1))
        else:
            settings_panel.place(x=-400, y=0)
            settings_panel.lower()  # Опускаем под все остальные виджеты
            settings_visible = False
            animation_running = False

    animate_hide()


# Функция для кнопки "Назад" - использует ту же анимацию скрытия
def back_to_main():
    """Кнопка назад - плавно скрывает панель настроек"""
    hide_settings_with_animation()


# Создание содержимого панели настроек
def create_settings_content():
    # Верхняя панель настроек
    settings_title_bar = ctk.CTkFrame(settings_panel,
                                      fg_color=BGColorForFirstButtoms,
                                      height=30,
                                      corner_radius=0)
    settings_title_bar.pack(fill="x", padx=0, pady=0)

    # Заголовок в панели настроек
    settings_title = ctk.CTkLabel(settings_title_bar,
                                  text="Настройки AudioAssistant",
                                  text_color="white",
                                  fg_color=BGColorForFirstButtoms,
                                  font=ctk.CTkFont(size=12, weight="bold"))
    settings_title.pack(side="left", padx=10)

    # Кнопка "Назад" с плавной анимацией
    settings_back_btn = ctk.CTkButton(settings_title_bar,
                                      text="← Назад",
                                      command=back_to_main,
                                      fg_color=BGColorForFirstButtoms,
                                      hover_color="#444444",
                                      text_color="white",
                                      height=25,
                                      corner_radius=0)
    settings_back_btn.pack(side="right", padx=10)

    # Основное содержимое настроек
    settings_content = ctk.CTkFrame(settings_panel,
                                    fg_color="#2b2b2b",
                                    corner_radius=0)
    settings_content.pack(fill="both", expand=True, padx=20, pady=20)

    # Заголовок настроек
    main_title = ctk.CTkLabel(settings_content,
                              text="Настройки приложения",
                              text_color="white",
                              font=ctk.CTkFont(size=24, weight="bold"))
    main_title.pack(pady=(0, 30))

    # Секция внешнего вида
    appearance_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    appearance_frame.pack(fill="x", pady=(0, 20))

    appearance_label = ctk.CTkLabel(appearance_frame,
                                    text="Внешний вид",
                                    text_color="white",
                                    font=ctk.CTkFont(size=18, weight="bold"))
    appearance_label.pack(anchor="w", padx=15, pady=10)

    # Настройка темы
    theme_label = ctk.CTkLabel(appearance_frame,
                               text="Цветовая тема:",
                               text_color="white",
                               font=ctk.CTkFont(size=14))
    theme_label.pack(anchor="w", padx=20, pady=(10, 5))

    theme_var = ctk.StringVar(value="dark")

    def change_theme(theme):
        ctk.set_appearance_mode(theme)

    theme_frame = ctk.CTkFrame(appearance_frame, fg_color="transparent")
    theme_frame.pack(fill="x", padx=20, pady=5)

    dark_radio = ctk.CTkRadioButton(theme_frame, text="Тёмная", variable=theme_var,
                                    value="dark", command=lambda: change_theme("dark"))
    dark_radio.pack(side="left", padx=(0, 20))

    light_radio = ctk.CTkRadioButton(theme_frame, text="Светлая", variable=theme_var,
                                     value="light", command=lambda: change_theme("light"))
    light_radio.pack(side="left")

    # Секция звука
    sound_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    sound_frame.pack(fill="x", pady=(0, 20))

    sound_label = ctk.CTkLabel(sound_frame,
                               text="Звук",
                               text_color="white",
                               font=ctk.CTkFont(size=18, weight="bold"))
    sound_label.pack(anchor="w", padx=15, pady=10)

    # Громкость микрофона
    mic_label = ctk.CTkLabel(sound_frame,
                             text="Громкость микрофона:",
                             text_color="white",
                             font=ctk.CTkFont(size=14))
    mic_label.pack(anchor="w", padx=20, pady=(10, 5))

    mic_slider = ctk.CTkSlider(sound_frame,
                               from_=0, to=100,
                               number_of_steps=100,
                               width=350)
    mic_slider.set(80)
    mic_slider.pack(padx=20, pady=5)

    # Громкость системы
    system_label = ctk.CTkLabel(sound_frame,
                                text="Громкость системы:",
                                text_color="white",
                                font=ctk.CTkFont(size=14))
    system_label.pack(anchor="w", padx=20, pady=(20, 5))

    system_slider = ctk.CTkSlider(sound_frame,
                                  from_=0, to=100,
                                  number_of_steps=100,
                                  width=350)
    system_slider.set(70)
    system_slider.pack(padx=20, pady=5)

    # Секция уведомлений
    notifications_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    notifications_frame.pack(fill="x", pady=(0, 20))

    notifications_label = ctk.CTkLabel(notifications_frame,
                                       text="Уведомления",
                                       text_color="white",
                                       font=ctk.CTkFont(size=18, weight="bold"))
    notifications_label.pack(anchor="w", padx=15, pady=10)

    # Переключатели уведомлений
    notifications_switch1 = ctk.CTkSwitch(notifications_frame,
                                          text="Звуковые уведомления",
                                          text_color="white",
                                          font=ctk.CTkFont(size=14))
    notifications_switch1.pack(anchor="w", padx=20, pady=10)

    notifications_switch2 = ctk.CTkSwitch(notifications_frame,
                                          text="Всплывающие уведомления",
                                          text_color="white",
                                          font=ctk.CTkFont(size=14))
    notifications_switch2.pack(anchor="w", padx=20, pady=10)

    # Кнопки действий
    buttons_frame = ctk.CTkFrame(settings_content, fg_color="transparent")
    buttons_frame.pack(fill="x", pady=20)

    save_button = ctk.CTkButton(buttons_frame,
                                text="Сохранить настройки",
                                fg_color="#00aa00",
                                hover_color="#008800",
                                height=40,
                                font=ctk.CTkFont(size=14, weight="bold"))
    save_button.pack(side="left", padx=(0, 10), fill="x", expand=True)

    reset_button = ctk.CTkButton(buttons_frame,
                                 text="Сбросить",
                                 fg_color="#ff4444",
                                 hover_color="#cc0000",
                                 height=40,
                                 font=ctk.CTkFont(size=14))
    reset_button.pack(side="right", fill="x", expand=True)


# Верхняя панель заголовка основного окна
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

# Кнопка настроек с анимацией
SetBut = ctk.CTkButton(settings_buttons_frame,
                       text="⚙️ Настройки",
                       command=toggle_settings,
                       fg_color=BGcolorForSettings,
                       hover_color="#444444",
                       text_color="white",
                       height=30,
                       corner_radius=2)
SetBut.pack(side="right", padx=2)

# Кнопка команд
ComList = ctk.CTkButton(settings_buttons_frame,
                        text="📋 Команды",
                        fg_color=BGcolorForSettings,
                        hover_color="#444444",
                        text_color="white",
                        height=30,
                        corner_radius=2)
ComList.pack(side="right", padx=0)

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

# Создаем содержимое панели настроек
create_settings_content()

root.mainloop()