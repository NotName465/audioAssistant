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

# Создание выдвижных панелей - ОБЕ ВО ВЕСЬ ЭКРАН
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

    # ... остальное содержимое настроек (оставлю как было)
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

    # ... остальные настройки


# Создание содержимого панели команд с РАБОЧИМИ скроллбарами
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

    # Основное содержимое команд - ЗАНИМАЕТ ВСЁ ПРОСТРАНСТВО
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

    # Фрейм для скроллинга - ЗАНИМАЕТ ВСЁ ОСТАВШЕЕСЯ ПРОСТРАНСТВО
    scroll_container = ctk.CTkFrame(commands_content, fg_color="#2b2b2b")
    scroll_container.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    # Создаем Canvas и скроллбары ПРАВИЛЬНО
    canvas = tk.Canvas(scroll_container,
                       bg="#2b2b2b",
                       highlightthickness=0,
                       width=370,  # Ширина с учетом отступов
                       height=450)  # Высота для скроллинга

    # Вертикальный скроллбар
    v_scrollbar = ctk.CTkScrollbar(scroll_container,
                                   orientation="vertical",
                                   command=canvas.yview)

    # Горизонтальный скроллбар
    # h_scrollbar = ctk.CTkScrollbar(scroll_container,
    #                                orientation="horizontal",
    #                                command=canvas.xview)

    # Настраиваем canvas
    canvas.configure(yscrollcommand=v_scrollbar.set,)
                     # xscrollcommand=h_scrollbar.set)

    # Размещаем элементы ГРИДАМИ для правильного расположения
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    # h_scrollbar.grid(row=1, column=0, sticky="ew")

    # Настраиваем веса гридов
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)

    # Создаем фрейм для команд внутри canvas
    commands_frame = ctk.CTkFrame(canvas, fg_color="#2b2b2b", corner_radius=0)

    # Создаем окно в canvas
    canvas.create_window((0, 0), window=commands_frame, anchor="nw")

    # Функции для работы скроллинга
    def on_frame_configure(event):
        """Обновляем scrollregion когда меняется размер фрейма"""
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_canvas_configure(event):
        """Обновляем ширину фрейма при изменении размера canvas"""
        canvas.itemconfig(canvas.find_all()[0], width=event.width)

    # Привязываем события
    commands_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    # Заполняем командами
    if commands_list:
        for command in commands_list:
            command_frame = ctk.CTkFrame(commands_frame,
                                         fg_color="#333333",
                                         corner_radius=8)
            command_frame.pack(fill="x", pady=5, padx=0)

            name_for_gui = command.get("nameForGUI", "Неизвестная команда")
            keywords = command.get("keywords", [])
            keywords_text = ", ".join(keywords)

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