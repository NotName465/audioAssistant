import customtkinter as ctk
import json
import os
import tkinter as tk
import soundcard as sc

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


def get_available_microphones():
    """Получает список доступных микрофонов"""
    try:
        microphones = sc.all_microphones()
        mic_list = []

        for mic in microphones:
            # Ограничиваем длину названия для удобства отображения
            name = mic.name
            if len(name) > 50:
                name = name[:47] + "..."

            mic_info = {
                'id': mic.id,
                'name': name,
                'full_name': mic.name,
                'channels': mic.channels
            }
            mic_list.append(mic_info)

        return mic_list
    except Exception as e:
        print(f"Ошибка получения микрофонов: {e}")
        return []


def get_default_microphone():
    """Получает микрофон по умолчанию"""
    try:
        default_mic = sc.default_microphone()
        return {
            'id': default_mic.id,
            'name': default_mic.name,
            'channels': default_mic.channels
        }
    except Exception as e:
        print(f"Ошибка получения микрофона по умолчанию: {e}")
        return None


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


# Создание содержимого панели настроек с ВЕРТИКАЛЬНЫМ СКРОЛЛБАРОМ
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

    # Основной контейнер для скроллинга настроек
    settings_scroll_container = ctk.CTkFrame(settings_panel,
                                             fg_color="#2b2b2b",
                                             corner_radius=0)
    settings_scroll_container.pack(fill="both", expand=True, padx=0, pady=0)

    # Создаем Canvas для скроллинга настроек
    settings_canvas = tk.Canvas(settings_scroll_container,
                                bg="#2b2b2b",
                                highlightthickness=0,
                                height=550)
    settings_canvas.pack(side="left", fill="both", expand=True)

    # Вертикальный скроллбар для настроек
    settings_v_scrollbar = ctk.CTkScrollbar(settings_scroll_container,
                                            orientation="vertical",
                                            command=settings_canvas.yview)
    settings_v_scrollbar.pack(side="right", fill="y")

    # Настраиваем canvas
    settings_canvas.configure(yscrollcommand=settings_v_scrollbar.set)

    # Создаем фрейм для содержимого настроек внутри canvas
    settings_content = ctk.CTkFrame(settings_canvas,
                                    fg_color="#2b2b2b",
                                    corner_radius=0)

    # Создаем окно в canvas для нашего фрейма
    settings_canvas.create_window((0, 0), window=settings_content, anchor="nw")

    # Функции для работы скроллинга настроек
    def on_settings_frame_configure(event):
        """Обновляем scrollregion когда меняется размер фрейма настроек"""
        settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))

    def on_settings_canvas_configure(event):
        """Обновляем ширину фрейма при изменении размера canvas"""
        settings_canvas.itemconfig(settings_canvas.find_all()[0], width=event.width)

    # Привязываем события
    settings_content.bind("<Configure>", on_settings_frame_configure)
    settings_canvas.bind("<Configure>", on_settings_canvas_configure)

    # Заголовок настроек
    main_title = ctk.CTkLabel(settings_content,
                              text="Настройки приложения",
                              text_color="white",
                              font=ctk.CTkFont(size=24, weight="bold"))
    main_title.pack(pady=(20, 30))

    # Секция аудио устройств
    audio_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    audio_frame.pack(fill="x", padx=20, pady=(0, 20))

    audio_label = ctk.CTkLabel(audio_frame,
                               text="Аудио устройства",
                               text_color="white",
                               font=ctk.CTkFont(size=18, weight="bold"))
    audio_label.pack(anchor="w", padx=15, pady=10)

    # Выбор микрофона
    mic_label = ctk.CTkLabel(audio_frame,
                             text="Микрофон:",
                             text_color="white",
                             font=ctk.CTkFont(size=14))
    mic_label.pack(anchor="w", padx=20, pady=(10, 5))

    # Получаем доступные микрофоны
    microphones = get_available_microphones()
    default_mic = get_default_microphone()

    # Создаем выпадающий список микрофонов
    mic_var = ctk.StringVar()

    if microphones:
        mic_names = [mic['name'] for mic in microphones]
        if default_mic:
            # Находим индекс микрофона по умолчанию
            default_name = default_mic['name']
            if len(default_name) > 50:
                default_name = default_name[:47] + "..."

            if default_name in mic_names:
                mic_var.set(default_name)
            else:
                mic_var.set(mic_names[0])
        else:
            mic_var.set(mic_names[0])
    else:
        mic_names = ["Микрофоны не найдены"]
        mic_var.set(mic_names[0])

    mic_combobox = ctk.CTkComboBox(audio_frame,
                                   values=mic_names,
                                   variable=mic_var,
                                   state="readonly",
                                   width=350)
    mic_combobox.pack(padx=20, pady=5)

    # Информация о выбранном микрофоне
    mic_info_label = ctk.CTkLabel(audio_frame,
                                  text="",
                                  text_color="#cccccc",
                                  font=ctk.CTkFont(size=11),
                                  justify="left")
    mic_info_label.pack(anchor="w", padx=20, pady=(0, 10))

    # Функция для показа информации о микрофоне
    def show_mic_info():
        selected_mic_name = mic_var.get()
        if microphones and selected_mic_name != "Микрофоны не найдены":
            selected_mic = None
            for mic in microphones:
                if mic['name'] == selected_mic_name:
                    selected_mic = mic
                    break

            if selected_mic:
                info_text = f"ID: {selected_mic['id']}\nКаналы: {selected_mic['channels']}"
                mic_info_label.configure(text=info_text)
            else:
                mic_info_label.configure(text="Информация не доступна")
        else:
            mic_info_label.configure(text="")

    # Функция обновления списка микрофонов
    def refresh_microphones():
        nonlocal microphones
        # Сбрасываем текст информации
        mic_info_label.configure(text="")

        microphones = get_available_microphones()
        if microphones:
            mic_names = [mic['name'] for mic in microphones]
            mic_combobox.configure(values=mic_names)
            if mic_names:
                mic_var.set(mic_names[0])
        else:
            mic_combobox.configure(values=["Микрофоны не найдены"])
            mic_var.set("Микрофоны не найдены")

    # Кнопка обновления списка микрофонов
    refresh_mic_btn = ctk.CTkButton(audio_frame,
                                    text="Обновить список микрофонов",
                                    command=refresh_microphones,
                                    fg_color="#444444",
                                    hover_color="#555555",
                                    height=30)
    refresh_mic_btn.pack(padx=20, pady=(5, 10))

    # Кнопка показа информации о микрофоне
    mic_info_btn = ctk.CTkButton(audio_frame,
                                 text="Показать информацию",
                                 command=show_mic_info,
                                 fg_color="#555555",
                                 hover_color="#666666",
                                 height=25)
    mic_info_btn.pack(padx=20, pady=(0, 10))

    # Секция внешнего вида
    appearance_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    appearance_frame.pack(fill="x", padx=20, pady=(0, 20))

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

    # Секция звука
    sound_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    sound_frame.pack(fill="x", padx=20, pady=(0, 20))

    sound_label = ctk.CTkLabel(sound_frame,
                               text="Звук",
                               text_color="white",
                               font=ctk.CTkFont(size=18, weight="bold"))
    sound_label.pack(anchor="w", padx=15, pady=10)

    # Громкость микрофона
    mic_volume_label = ctk.CTkLabel(sound_frame,
                                    text="Громкость микрофона:",
                                    text_color="white",
                                    font=ctk.CTkFont(size=14))
    mic_volume_label.pack(anchor="w", padx=20, pady=(10, 5))

    mic_volume_slider = ctk.CTkSlider(sound_frame,
                                      from_=0, to=100,
                                      number_of_steps=100,
                                      width=350)
    mic_volume_slider.set(80)
    mic_volume_slider.pack(padx=20, pady=5)

    # Громкость системы
    system_volume_label = ctk.CTkLabel(sound_frame,
                                       text="Громкость системы:",
                                       text_color="white",
                                       font=ctk.CTkFont(size=14))
    system_volume_label.pack(anchor="w", padx=20, pady=(20, 5))

    system_volume_slider = ctk.CTkSlider(sound_frame,
                                         from_=0, to=100,
                                         number_of_steps=100,
                                         width=350)
    system_volume_slider.set(70)
    system_volume_slider.pack(padx=20, pady=5)

    # Секция уведомлений
    notifications_frame = ctk.CTkFrame(settings_content, fg_color="#333333")
    notifications_frame.pack(fill="x", padx=20, pady=(0, 20))

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
    buttons_frame.pack(fill="x", padx=20, pady=20)

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

    # Настраиваем canvas
    canvas.configure(yscrollcommand=v_scrollbar.set)

    # Размещаем элементы ГРИДАМИ для правильного расположения
    canvas.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")

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