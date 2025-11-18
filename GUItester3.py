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

# Создание выдвижной панели настроек с указанием размеров в конструкторе
settings_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=300,  # Размеры указываем здесь
                              height=600,
                              corner_radius=0)


# Функция для показа/скрытия панели настроек с анимацией
def toggle_settings():
    global settings_visible

    if settings_visible:
        # Плавно скрываем панель
        hide_settings_with_animation()
    else:
        # Плавно показываем панель
        show_settings_with_animation()


def show_settings_with_animation():
    """Плавно показывает панель настроек"""
    global settings_visible

    # Сначала размещаем панель скрытой слева
    settings_panel.place(x=-300, y=0)
    settings_panel.lift()  # Поднимаем на верхний слой

    def animate_show(frame=0):
        current_x = -300 + (frame * 15)  # Двигаем от -300 до 0
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            root.after(16, lambda: animate_show(frame + 1))
        else:
            settings_visible = True

    animate_show()


def hide_settings_with_animation():
    """Плавно скрывает панель настроек"""
    global settings_visible

    def animate_hide(frame=0):
        current_x = 0 - (frame * 15)  # Двигаем от 0 до -300
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            root.after(16, lambda: animate_hide(frame + 1))
        else:
            settings_panel.place_forget()
            settings_visible = False

    animate_hide()


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

    # Настройка звука
    sound_label = ctk.CTkLabel(settings_panel,
                               text="Громкость:",
                               text_color="white",
                               font=ctk.CTkFont(size=14))
    sound_label.pack(anchor="w", padx=20, pady=(20, 5))

    volume_slider = ctk.CTkSlider(settings_panel,
                                  from_=0, to=100,
                                  number_of_steps=100,
                                  width=250)
    volume_slider.set(70)
    volume_slider.pack(padx=20, pady=5)

    # Переключатель уведомлений
    notifications_switch = ctk.CTkSwitch(settings_panel,
                                         text="Включить уведомления",
                                         text_color="white",
                                         font=ctk.CTkFont(size=14))
    notifications_switch.pack(anchor="w", padx=20, pady=20)

    # Кнопка закрытия настроек
    close_button = ctk.CTkButton(settings_panel,
                                 text="Закрыть",
                                 command=toggle_settings,
                                 fg_color="#ff4444",
                                 hover_color="#cc0000",
                                 height=35)
    close_button.pack(pady=20)


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

# Кнопка развернуть/свернуть
full_cr_btm = ctk.CTkButton(buttons_frame,
                            text="□",
                            fg_color=BGColorForFirstButtoms,
                            hover_color="#444444",
                            width=30,
                            height=30,
                            corner_radius=0)
full_cr_btm.pack(side="right", padx=1)

# Кнопка свернуть
minimize_btn = ctk.CTkButton(buttons_frame,
                             text="—",
                             fg_color=BGColorForFirstButtoms,
                             hover_color="#444444",
                             width=30,
                             height=30,
                             corner_radius=0)
minimize_btn.pack(side="right", padx=1)

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