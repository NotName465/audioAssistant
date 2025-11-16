from tkinter import *
import tksvg
from pygame.examples.cursors import image
from tksvg import SvgImage

root = Tk()

root['bg'] = "#783518"
root.title("Нарды")
root.geometry('400x600')
root.resizable(width=False, height=False)


BGColorForFirstButtoms = "#1A1A1A"
BGcolorForSettings = "#262626"

# Убрать рамку окна(True)
root.overrideredirect(False)


title_bar = Frame(root, bg=BGColorForFirstButtoms, height=30)
title_bar.pack(fill=X)

# Кнопка закрытия в своем заголовке
close_btn = Button(title_bar, text="X", command=root.destroy,
                     bg=BGColorForFirstButtoms, border=0,fg = "White",)
close_btn.pack(side=RIGHT, padx=1)

full_cr_btm = Button(title_bar, text="[]",
                     bg=BGColorForFirstButtoms, border=0,fg="White")
full_cr_btm.pack(side=RIGHT)


close = Button(title_bar, text="--",
                     bg='#1A1A1A', border=0)
close.pack(side=RIGHT,)
close.configure(fg="White")



NameProject = Label(title_bar, text = "AudioAssistant",bg=BGColorForFirstButtoms, border=0,fg="White",padx= 7)
NameProject.pack(side=LEFT)
SettingsBar = Frame(root, bg=BGcolorForSettings, height=10)
SettingsBar.pack(fill=X)

BlackGear = SvgImage(file="IMGS/GEAR.svg")
WhiteGear = SvgImage(file="IMGS/whiteGear.svg")
comandList = SvgImage(file="IMGS/comList.svg")
BlackGear2 = SvgImage(file="IMGS/blackGear2.svg")


SetBut = Button(SettingsBar, image=BlackGear2, text="Настройки", compound=LEFT,
                     bg=BGcolorForSettings, border=0,fg="White",padx= 5)
SetBut.pack(side=RIGHT)

ComList = Button(SettingsBar,image=comandList, text="Команды", compound=LEFT,
                     bg=BGcolorForSettings, border=0,fg="White",padx= 5)
ComList.pack(side=RIGHT)

Rus = Label(SettingsBar, text="Сделано в России",bg=BGcolorForSettings, fg="White",padx= 7,border=0)
Rus.pack(side=LEFT)





def move_window(event):
    root.geometry(f"+{event.x_root}+{event.y_root}")

title_bar.bind('<B1-Motion>', move_window)



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