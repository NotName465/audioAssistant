import customtkinter as ctk
import json
import os
import tkinter as tk

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
commands_visible = False
show_animation_id = None
hide_animation_id = None
current_panel = None

# Создание выдвижных панелей
settings_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=400,
                              height=600,
                              corner_radius=0)

commands_panel = ctk.CTkFrame(root,
                              fg_color="#2b2b2b",
                              width=400,
                              height=600,
                              corner_radius=0)

# Изначально скрываем панели
settings_panel.place(x=-400, y=0)
commands_panel.place(x=-400, y=0)
settings_panel.lower()
commands_panel.lower()


def load_commands_from_json():
    """Загружает команды из файла commands.json"""
    try:
        json_path = "audioAssistant/commands.json"

        if not os.path.exists(json_path):
            print("Json файл не подгружен")
            return []

        if os.path.getsize(json_path) == 0:
            print("Json файл не подгружен")
            return []

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        commands = data.get("commands", [])
        if not commands:
            print("Json файл не подгружен")
            return []

        return commands

    except Exception as e:
        print(f"Json файл не подгружен: {e}")
        return []


# Функции для показа/скрытия панелей с анимацией
def toggle_settings():
    global settings_visible, commands_visible, current_panel

    if commands_visible:
        hide_commands_with_animation()
        root.after(250, show_settings_with_animation)
    elif settings_visible:
        hide_settings_with_animation()
    else:
        show_settings_with_animation()


def toggle_commands():
    global settings_visible, commands_visible, current_panel

    if settings_visible:
        hide_settings_with_animation()
        root.after(250, show_commands_with_animation)
    elif commands_visible:
        hide_commands_with_animation()
    else:
        show_commands_with_animation()


def show_settings_with_animation():
    global settings_visible, show_animation_id, hide_animation_id, current_panel

    if hide_animation_id:
        root.after_cancel(hide_animation_id)
        hide_animation_id = None

    settings_panel.lift()
    current_panel = settings_panel

    def animate_show(frame=0):
        global show_animation_id
        current_x = -400 + (frame * 20)
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            show_animation_id = root.after(16, lambda: animate_show(frame + 1))
        else:
            settings_panel.place(x=0, y=0)
            settings_visible = True
            show_animation_id = None

    animate_show()


def hide_settings_with_animation():
    global settings_visible, hide_animation_id, show_animation_id

    if show_animation_id:
        root.after_cancel(show_animation_id)
        show_animation_id = None

    def animate_hide(frame=0):
        global hide_animation_id
        current_x = 0 - (frame * 20)
        settings_panel.place(x=current_x, y=0)

        if frame < 20:
            hide_animation_id = root.after(16, lambda: animate_hide(frame + 1))
        else:
            settings_panel.place(x=-400, y=0)
            settings_panel.lower()
            settings_visible = False
            hide_animation_id = None

    animate_hide()


def show_commands_with_animation():
    global commands_visible, show_animation_id, hide_animation_id, current_panel

    if hide_animation_id:
        root.after_cancel(hide_animation_id)
        hide_animation_id = None

    commands_panel.lift()
    current_panel = commands_panel

    def animate_show(frame=0):
        global show_animation_id
        current_x = -400 + (frame * 20)
        commands_panel.place(x=current_x, y=0)

        if frame < 20:
            show_animation_id = root.after(16, lambda: animate_show(frame + 1))
        else:
            commands_panel.place(x=0, y=0)
            commands_visible = True
            show_animation_id = None

    animate_show()


def hide_commands_with_animation():
    global commands_visible, hide_animation_id, show_animation_id

    if show_animation_id:
        root.after_cancel(show_animation_id)
        show_animation_id = None

    def animate_hide(frame=0):
        global hide_animation_id
        current_x = 0 - (frame * 20)
        commands_panel.place(x=current_x, y=0)

        if frame < 20:
            hide_animation_id = root.after(16, lambda: animate_hide(frame + 1))
        else:
            commands_panel.place(x=-400, y=0)
            commands_panel.lower()
            commands_visible = False
            hide_animation_id = None

    animate_hide()


# Функции для кнопок "Назад"
def back_to_main_from_settings():
    hide_settings_with_animation()


def back_to_main_from_commands():
    hide_commands_with_animation()


# Создание содержимого панели настроек
def create_settings_content():
    # Верхняя панель настроек
    settings_title_bar = ctk.CTkFrame(settings_panel,
                                      fg_color=BGColorForFirstButtoms,
                                      height=30,
                                      corner_radius=0)
    settings_title_bar.pack(fill="x", padx=0, pady=0)

    settings_title = ctk.CTkLabel(settings_title_bar,
                                  text="Настройки AudioAssistant",
                                  text_color="white",
                                  fg_color=BGColorForFirstButtoms,
                                  font=ctk.CTkFont(size=12, weight="bold"))
    settings_title.pack(side="left", padx=10)

    settings_back_btn = ctk.CTkButton(settings_title_bar,
                                      text="← Назад",
                                      command=back_to_main_from_settings,
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

    main_title = ctk.CTkLabel(settings_content,
                              text="Настройки приложения",
                              text_color="white",
                              font=ctk.CTkFont(size=24, weight="bold"))
    main_title.pack(pady=(0, 30))

    # ... остальное содержимое настроек
    appearance_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    appearance_frame.pack(fill="x", pady=(0, 20))

    appearance_label = ctk.CTkLabel(appearance_frame,
                                    text="Внешний вид",
                                    text_color="white",
                                    font=ctk.CTkFont(size=18, weight="bold"))
    appearance_label.pack(anchor="w", padx=15, pady=10)

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


# Создание содержимого панели команд с ИСПРАВЛЕННЫМИ скроллбарами
def create_commands_content():
    commands_list = load_commands_from_json()

    # Верхняя панель команд
    commands_title_bar = ctk.CTkFrame(commands_panel,
                                      fg_color=BGColorForFirstButtoms,
                                      height=30,
                                      corner_radius=0)
    commands_title_bar.pack(fill="x", padx=0, pady=0)

    commands_title = ctk.CTkLabel(commands_title_bar,
                                  text="Команды AudioAssistant",
                                  text_color="white",
                                  fg_color=BGColorForFirstButtoms,
                                  font=ctk.CTkFont(size=12, weight="bold"))
    commands_title.pack(side="left", padx=10)

    commands_back_btn = ctk.CTkButton(commands_title_bar,
                                      text="← Назад",
                                      command=back_to_main_from_commands,
                                      fg_color=BGColorForFirstButtoms,
                                      hover_color="#444444",
                                      text_color="white",
                                      height=25,
                                      corner_radius=0)
    commands_back_btn.pack(side="right", padx=10)

    # Основное содержимое команд
    commands_content = ctk.CTkFrame(commands_panel,
                                    fg_color="#2b2b2b",
                                    corner_radius=0)
    commands_content.pack(fill="both", expand=True, padx=0, pady=0)

    # Заголовок
    main_title = ctk.CTkLabel(commands_content,
                              text="Доступные команды",
                              text_color="white",
                              font=ctk.CTkFont(size=20, weight="bold"))
    main_title.pack(pady=(15, 15))

    # ОСНОВНОЙ КОНТЕЙНЕР ДЛЯ СКРОЛЛИНГА
    main_scroll_frame = ctk.CTkFrame(commands_content, fg_color="#2b2b2b")
    main_scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    # Фрейм для canvas и вертикального скроллбара
    canvas_frame = ctk.CTkFrame(main_scroll_frame, fg_color="#2b2b2b")
    canvas_frame.pack(fill="both", expand=True)

    # Создаем Canvas
    canvas = tk.Canvas(canvas_frame,
                       bg="#2b2b2b",
                       highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    # Вертикальный скроллбар
    v_scrollbar = ctk.CTkScrollbar(canvas_frame,
                                   orientation="vertical",
                                   command=canvas.yview)
    v_scrollbar.pack(side="right", fill="y")

    # Горизонтальный скроллбар в ОТДЕЛЬНОМ фрейме
    h_scrollbar_frame = ctk.CTkFrame(main_scroll_frame, fg_color="#2b2b2b", height=15)
    h_scrollbar_frame.pack(fill="x", side="bottom")
    h_scrollbar_frame.pack_propagate(False)  # Запрещаем изменение размера

    h_scrollbar = ctk.CTkScrollbar(h_scrollbar_frame,
                                   orientation="horizontal",
                                   command=canvas.xview)
    h_scrollbar.pack(fill="x", padx=0)

    # Настраиваем canvas
    canvas.configure(yscrollcommand=v_scrollbar.set,
                     xscrollcommand=h_scrollbar.set)

    # Создаем фрейм для команд внутри canvas
    commands_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b", corner_radius=0)

    # Создаем окно в canvas
    canvas_window = canvas.create_window((0, 0), window=commands_frame, anchor="nw")

    # Функции для работы скроллинга
    def on_frame_configure(event):
        """Обновляем scrollregion когда меняется размер фрейма"""
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        """Обновляем ширину фрейма при изменении размера canvas"""
        canvas.itemconfig(canvas_window, width=event.width)

    # Привязываем события
    commands_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Заполняем командами - делаем фрейм ШИРОКИМ для тестирования горизонтального скролла
    if commands_list:
        for command in commands_list:
            command_frame = ctk.CTkFrame(commands_frame,
                                         fg_color="#333333",
                                         corner_radius=8)
            command_frame.pack(fill="x", pady=5, padx=0)

            name_for_gui = command.get("nameForGUI", "Неизвестная команда")
            keywords = command.get("keywords", [])
            # Делаем длинный текст для тестирования горизонтального скролла
            keywords_text = ", ".join(keywords) + " " + ", ".join(keywords) + " " + ", ".join(keywords)

            name_label = ctk.CTkLabel(command_frame,
                                      text=f"• {name_for_gui}",
                                      text_color="white",
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      anchor="w")
            name_label.pack(fill="x", padx=12, pady=(8, 2))

            keywords_label = ctk.CTkLabel(command_frame,
                                          text=f"Ключевые слова: {keywords_text}",
                                          text_color="#cccccc",
                                          font=ctk.CTkFont(size=12),
                                          anchor="w")
            keywords_label.pack(fill="x", padx=12, pady=(2, 8))
    else:
        no_commands_frame = ctk.CTkFrame(commands_frame,
                                         fg_color="#333333",
                                         corner_radius=8)
        no_commands_frame.pack(fill="x", pady=5, padx=0)

        no_commands_label = ctk.CTkLabel(no_commands_frame,
                                         text="Команды не найдены. Проверьте файл commands.json",
                                         text_color="white",
                                         font=ctk.CTkFont(size=14))
        no_commands_label.pack(padx=12, pady=12)

    # Счетчик команд внизу
    commands_count = len(commands_list)
    count_frame = ctk.CTkFrame(commands_content, fg_color="#2b2b2b", height=30)
    count_frame.pack(fill="x", side="bottom", pady=(0, 5))

    count_label = ctk.CTkLabel(count_frame,
                               text=f"Всего команд: {commands_count}",
                               text_color="#aaaaaa",
                               font=ctk.CTkFont(size=12))
    count_label.pack(pady=5)


# Верхняя панель заголовка основного окна
title_bar = ctk.CTkFrame(root, fg_color=BGColorForFirstButtoms, height=30, corner_radius=0)
title_bar.pack(fill="x", padx=0, pady=0)

buttons_frame = ctk.CTkFrame(title_bar, fg_color=BGColorForFirstButtoms, height=30, corner_radius=0)
buttons_frame.pack(side="right", padx=0)

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

settings_buttons_frame = ctk.CTkFrame(SettingsBar,
                                      fg_color=BGcolorForSettings,
                                      height=40,
                                      corner_radius=0)
settings_buttons_frame.pack(side="right", padx=0)

SetBut = ctk.CTkButton(settings_buttons_frame,
                       text="⚙️ Настройки",
                       command=toggle_settings,
                       fg_color=BGcolorForSettings,
                       hover_color="#444444",
                       text_color="white",
                       height=30,
                       corner_radius=2)
SetBut.pack(side="right", padx=2)

ComList = ctk.CTkButton(settings_buttons_frame,
                        text="📋 Команды",
                        command=toggle_commands,
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

welcome_label = ctk.CTkLabel(content_frame,
                             text="Добро пожаловать в AudioAssistant!",
                             text_color="white",
                             font=ctk.CTkFont(size=16, weight="bold"))
welcome_label.pack(pady=50)

# Создаем содержимое обеих панелей
create_settings_content()
create_commands_content()

root.mainloop()