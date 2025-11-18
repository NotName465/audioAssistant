import customtkinter as ctk
from tksvg import SvgImage

# Настройка внешнего вида
ctk.set_appearance_mode("dark")  # Темная тема
ctk.set_default_color_theme("blue")  # Цветовая тема

# Создание главного окна
root = ctk.CTk()
root.configure(fg_color="#783518")  # Фон окна
root.title("Нарды")
root.geometry('400x600')
root.resizable(False, False)

# Цвета
BGColorForFirstButtoms = "#1A1A1A"
BGcolorForSettings = "#262626"

BlackGear = SvgImage(file="IMGS/GEAR.svg")
WhiteGear = SvgImage(file="IMGS/whiteGear.svg")
comandList = SvgImage(file="IMGS/comList.svg")
BlackGear2 = SvgImage(file="IMGS/blackGear2.svg")


# В CustomTkinter нет overrideredirect, но можно сделать кастомную рамку
# root.overrideredirect(False) - не нужно в CTk

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


SetBut = ctk.CTkButton(settings_buttons_frame,
                      text="Настройки",
                      fg_color=BGcolorForSettings,
                      hover_color="#444444",
                      text_color="white",
                      height=30,
                      corner_radius=2,
                      image = BlackGear2,
                      )
SetBut.pack(side="right", padx=2)


ComList = ctk.CTkButton(settings_buttons_frame,
                       text="Команды",
                       fg_color=BGcolorForSettings,
                       hover_color="#444444",
                       text_color="white",
                       height=30,
                       corner_radius=2,
                       image = comandList,)
ComList.pack(side="right", padx=0)

Rus = ctk.CTkLabel(SettingsBar,
                  text="Сделано в России",
                  text_color="white",
                  fg_color=BGcolorForSettings,
                  font=ctk.CTkFont(size=10))
Rus.pack(side="left", padx=10)

# Основная область контента (можно добавить ваш контент здесь)
content_frame = ctk.CTkFrame(root,
                            fg_color="#783518",
                            corner_radius=0)
content_frame.pack(fill="both", expand=True, padx=0, pady=0)

# Пример добавления контента
# welcome_label = ctk.CTkLabel(content_frame,
#                             text="Добро пожаловать в AudioAssistant!",
#                             text_color="white",
#                             font=ctk.CTkFont(size=16, weight="bold"))
# welcome_label.pack(pady=50)
# Создание выдвижной панели настроек (изначально скрыта за левым краем)


root.mainloop()