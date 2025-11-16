from tkinter import *
from tkinter import ttk

root = Tk()

root['bg'] = "#2b2b2b"  # Тёмный фон как у многих аудио-контроллеров
root.title = "Rusar Audio Controller"
root.geometry('400x500')
root.resizable(width=False, height=False)

# Убрать рамку окна
root.overrideredirect(True)

# Создаем верхнюю панель
title_bar = Frame(root, bg='#1a1a1a', height=30)
title_bar.pack(fill=X)
title_bar.pack_propagate(False)

# Заголовок в верхней панели
title_label = Label(title_bar, text="Rusar Audio Controller",
                   bg='#1a1a1a', fg='#ffffff', font=("Arial", 10))
title_label.pack(side=LEFT, padx=10)

# Кнопка закрытия
close_btn = Button(title_bar, text="×", command=root.destroy,
                  bg='#1a1a1a', fg='#ffffff', border=0,
                  font=("Arial", 16), cursor="hand2")
close_btn.pack(side=RIGHT, padx=10)

# Функции для перемещения окна
start_x, start_y = 0, 0

def start_move(event):
    global start_x, start_y
    start_x = event.x_root
    start_y = event.y_root

def move_window(event):
    global start_x, start_y
    delta_x = event.x_root - start_x
    delta_y = event.y_root - start_y
    x = root.winfo_x() + delta_x
    y = root.winfo_y() + delta_y
    root.geometry(f"+{x}+{y}")
    start_x = event.x_root
    start_y = event.y_root

title_bar.bind('<Button-1>', start_move)
title_bar.bind('<B1-Motion>', move_window)

# Основной контент
main_frame = Frame(root, bg='#2b2b2b')
main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

# Секция "Макрофон"
mic_frame = Frame(main_frame, bg='#2b2b2b')
mic_frame.pack(fill=X, pady=(0, 20))

Label(mic_frame, text="Макрофон", bg='#2b2b2b', fg='#ffffff',
      font=("Arial", 14, "bold")).pack(anchor=W)

Label(mic_frame, text="Макрофон гарантуры\n(Rusar Audio Controller)",
      bg='#2b2b2b', fg='#cccccc', font=("Arial", 10),
      justify=LEFT).pack(anchor=W, pady=(5, 0))

# Секция "Нейросети"
ai_frame = Frame(main_frame, bg='#2b2b2b')
ai_frame.pack(fill=X, pady=(0, 20))

Label(ai_frame, text="Нейросети", bg='#2b2b2b', fg='#ffffff',
      font=("Arial", 14, "bold")).pack(anchor=W)

# Контейнер для кнопок нейросетей
ai_buttons_frame = Frame(ai_frame, bg='#2b2b2b')
ai_buttons_frame.pack(fill=X, pady=(10, 0))

# Кнопка "Распознать"
recognize_btn = Label(ai_buttons_frame, text="Распознать",
                     bg='#404040', fg='#ffffff',
                     font=("Arial", 10, "bold"),
                     padx=20, pady=10, cursor="hand2")
recognize_btn.pack(side=LEFT, padx=(0, 10))

# Кнопка "Упаковать"
pack_btn = Label(ai_buttons_frame, text="Упаковать",
                bg='#404040', fg='#ffffff',
                font=("Arial", 10, "bold"),
                padx=20, pady=10, cursor="hand2")
pack_btn.pack(side=LEFT)

# Секция "Ресурсы"
resources_frame = Frame(main_frame, bg='#2b2b2b')
resources_frame.pack(fill=X, pady=(0, 20))

Label(resources_frame, text="Ресурсы", bg='#2b2b2b', fg='#ffffff',
      font=("Arial", 14, "bold")).pack(anchor=W)

# Индикатор RAM
ram_frame = Frame(resources_frame, bg='#2b2b2b')
ram_frame.pack(fill=X, pady=(10, 0))

Label(ram_frame, text="RAM", bg='#2b2b2b', fg='#cccccc',
      font=("Arial", 10)).pack(side=LEFT)

# Прогресс-бар для RAM
ram_progress = ttk.Progressbar(ram_frame, orient=HORIZONTAL,
                              length=200, mode='determinate',
                              style="Custom.Horizontal.TProgressbar")
ram_progress.pack(side=LEFT, padx=(10, 5))
ram_progress['value'] = 37  # 0.37mb из условного максимума

ram_label = Label(ram_frame, text="0.37mb", bg='#2b2b2b', fg='#cccccc',
                 font=("Arial", 9))
ram_label.pack(side=LEFT, padx=(5, 0))

# Нижняя панель с информацией
bottom_frame = Frame(main_frame, bg='#2b2b2b')
bottom_frame.pack(side=BOTTOM, fill=X, pady=(20, 0))

# Информация об авторских правах
copyright_text = """© 2023. Автор проекта: Abraham Tupakov
Github репозиторий проекта."""

Label(bottom_frame, text=copyright_text, bg='#2b2b2b', fg='#888888',
      font=("Arial", 8), justify=CENTER).pack(pady=10)

# Стиль для прогресс-бара
style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.Horizontal.TProgressbar",
                troughcolor='#404040',
                background='#4CAF50',
                bordercolor='#2b2b2b',
                lightcolor='#4CAF50',
                darkcolor='#4CAF50')

# Функция для центрирования окна
def center_window(window, width=None, height=None):
    window.update_idletasks()
    if width is None or height is None:
        width = window.winfo_width()
        height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

center_window(root)

root.mainloop()