from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkImage, CTkScrollableFrame, StringVar
# from utils.tooltip import CustomTooltipLabel
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import ttk
import threading
from PIL import Image, ImageTk
import queue
from time import sleep
import tkinter as tk
import os

class style:
    text_color = '#ffffff'
    text_color_button = '#e9e2d4'
    # border_color = '#8b6e67'
    background_color = '#2C2C2C'

    field_foreground_color = '#2E2E2E'
    field_border_color = '#444444'

    button_background_color = '#3A3A3A'
    button_background_hover_color = '#4A4A4A'
    button_border_color = '#555555'

    frame_background_color = '#353535'
    child_frame_background_color = '#242424'

    default_font = ('SF Pro', 12)
    default_font_upscaled = ('Calibri', 15)
    # caption_font = ('SF Pro', 12, 'bold')
    caption_font = ('Google Sans Text', 13)
    tooltip_font = ('Consolas', 11)
    title_font = ('Consolas', 13)
    title_font_upscaled = ('Consolas', 16)
    log_font = ('SF Pro', 11)


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Picture Encoder')       # pic n code | picencode
        self.geometry('1200x800+189+64')
        self.resizable(False, False)
        self.configure(bg=style.background_color)
        self.init_variables()
        self.init_images()

    def init_variables(self):
        # entries
        # self.diff_name_var = StringVar(value='diff_name')
        # self.diff_output_path_var = StringVar(value='path/to/diff.huda')
        # self.primary_dump_path_var = StringVar(value='path/to/primary/dump.json')
        # self.secondary_dump_path_var = StringVar(value='path/to/secondary/dump.json')
        # self.primary_binexport_path_var = StringVar(value='path/to/primary/binexport.binexport')
        # self.secondary_binexport_path_var = StringVar(value='path/to/secondary/binexport.binexport')

        # globals
        # self.path_to_diff = ''      # TODO trace add here or find a way to trigger logic when overwritten
        # self.create_diff_frame = None
        pass

    def init_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.image_placeholder = tk.PhotoImage(file=base_dir + '\\assets\\image_placeholder.png')
        # self.iconbitmap(base_dir + '\\assets\\icon.ico')
        # self.enter_icon = tk.PhotoImage(file=base_dir + '\\assets\\enter.png')
        # self.icon = tk.PhotoImage(file=base_dir + '\\assets\\icon.png')
        # icon = Image.open(base_dir + "\\assets\\icon.png")
        # icon = ImageTk.PhotoImage(icon)
        # self.wm_iconphoto(True, icon)

    def draw_textbox(self):
        # widgets
        textbox = CTkTextbox(self, height=550, width=450, wrap=tk.WORD, font=style.default_font_upscaled, corner_radius=10, fg_color=style.frame_background_color, border_color=style.frame_background_color, border_width=1)
        textbox_title = ttk.Label(self, text='Texte à encoder', font=style.title_font_upscaled, foreground=style.text_color, background=style.background_color)

        textbox.pack(anchor='w', padx=5, pady=50)
        textbox_title.place(x=130, y=17)

    def draw_gui(self):
        # apply styling
        ttk_styling = ttk.Style()
        ttk_styling.configure('BlackFrame.TFrame', background=style.frame_background_color)
        ttk_styling.configure('BlackCheckbutton.TCheckbutton', foreground=style.text_color, font=style.default_font, background=style.background_color)
        ttk_styling.map('BlackCheckbutton.TCheckbutton',
            background=[('active', style.background_color)],
            foreground=[('active', style.text_color)])
        
        # draw text box
        # self.draw_textbox()

        # draw placeholder image
        test = tk.Label(self, image=self.image_placeholder, text='')
        test.pack(anchor='e')

        # draw debug/log window
        self.debug = scrolledtext.ScrolledText(
            master=self,
            wrap=tk.WORD,
            state='disabled',
            height=11,
            width=147,
            font=style.log_font,
            fg=style.text_color,
            bg='black')
        
        self.debug.tag_configure("sel", background='black', foreground=style.text_color)
        self.debug.place(x=1, y=605)



# remove from here
def start_app():
    App = GUI()
    App.draw_gui()
    App.mainloop()

if __name__ == '__main__':
    start_app()
