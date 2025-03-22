from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkImage, CTkScrollbar, CTkScrollableFrame, StringVar
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
from customtkinter import ThemeManager

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

# todo: D0D0D0 default debug text color
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Picture Encoder')       # pic n code | picencode
        self.geometry('1080x800+189+64')
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
        # self.current_mode = 'init'
        self.current_mode = 'encode'
        # self.path_to_diff = ''      # TODO trace add here or find a way to trigger logic when overwritten
        # self.create_diff_frame = None

    def init_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.image_mainframe_bg = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\background.png')
        self.image_encode_button = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\encode_button.png')
        self.image_decode_button = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\decode_button.png')
        # self.image_placeholder = tk.PhotoImage(file=base_dir + '\\assets\\image_placeholder.png')
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

    def encode_switch_frame_onclick(self, event):
        if event.x < 225 and self.current_mode == 'decode':
            self.update_switch_button_state('encode')
        elif event.x > 225 and self.current_mode == 'encode':
            self.update_switch_button_state('decode')

    def update_switch_button_state(self, state):
        if state == 'encode':
            # show the encode state (change toggle)
            self.current_mode = 'encode'
            self.encode_frame_left.configure(bg_color='#FFFFFF')
            self.encode_frame_right.configure(bg_color='#1A93CF')
            self.encode_label.configure(bg_color='#7DC9EF')
            self.decode_label.configure(bg_color='#1A93CF')
            self.encode_label.configure(font=('Google Sans Text', 30, 'bold'))
            self.decode_label.configure(font=('Google Sans Text', 30))
            
            self.encode_frame_left.place(x=0, y=0)
            self.encode_frame_center.place(x=50, y=0)
            self.encode_frame_right.place(x=100, y=0)
            self.encode_label.place(x=50, y=14)
            self.decode_label.place(x=280, y=14)
            
        elif state == 'decode':
            # show the decode state (change toggle)
            self.current_mode = 'decode'
            self.encode_frame_left.configure(bg_color='#1A93CF')
            self.encode_frame_right.configure(bg_color='#FFFFFF')
            self.encode_label.configure(bg_color='#1A93CF')
            self.decode_label.configure(bg_color='#7DC9EF')
            self.encode_label.configure(font=('Google Sans Text', 30))
            self.decode_label.configure(font=('Google Sans Text', 30, 'bold'))
        
            self.encode_frame_left.place(x=225, y=0)
            self.encode_frame_center.place(x=280, y=0)
            self.encode_frame_right.place(x=325, y=0)
            self.encode_label.place(x=50, y=14)
            self.decode_label.place(x=280, y=14)


    def draw_gui(self):
        # apply styling
        ttk_styling = ttk.Style()
        ttk_styling.configure('BlackFrame.TFrame', background=style.frame_background_color)
        ttk_styling.configure('BlackCheckbutton.TCheckbutton', foreground=style.text_color, font=style.default_font, background=style.background_color)
        ttk_styling.map('BlackCheckbutton.TCheckbutton',
            background=[('active', style.background_color)],
            foreground=[('active', style.text_color)])
        
        # adding background
        self.background_label = tk.Label(self, image=self.image_mainframe_bg)
        self.background_label.place(relwidth=1, relheight=1)
        
        # encode/decode switch button
        switch_button_frame = CTkFrame(self, width=450, height=65, fg_color='#1A93CF', corner_radius=60, bg_color='#FFFFFF')
        switch_button_frame.pack_propagate(False)
        switch_button_frame.pack(padx=0, pady=30)
        
        self.encode_frame_left = CTkFrame(switch_button_frame, width=100, height=64, fg_color='#7DC9EF', corner_radius=60, bg_color='#FFFFFF')
        self.encode_frame_right = CTkFrame(switch_button_frame, width=125, height=64, fg_color='#7DC9EF', corner_radius=60, bg_color='#1A93CF')
        self.encode_frame_center = CTkFrame(switch_button_frame, width=75, height=64, fg_color='#7DC9EF', corner_radius=0, bg_color='#7DC9EF')
        self.encode_label = CTkLabel(switch_button_frame, text='Encoder', font=('Google Sans Text', 30), bg_color='#7DC9EF', text_color='#FFFFFF')
        self.decode_label = CTkLabel(switch_button_frame, text='Decoder', font=('Google Sans Text', 30), bg_color='#7DC9EF', text_color='#FFFFFF')
        
        switch_button_frame.bind("<Button-1>", self.encode_switch_frame_onclick)
        self.encode_label.bind("<Button-1>", lambda event: self.update_switch_button_state('encode'))
        self.decode_label.bind("<Button-1>", lambda event: self.update_switch_button_state('decode'))
        
        self.update_switch_button_state('encode')

        # draw debug/log window        
        debug_frame_beautifier = CTkFrame(self, width=1040, height=180, fg_color='#22272D', corner_radius=15, bg_color='#FFFFFF') # debug_frame * 1.06
        debug_frame = CTkFrame(debug_frame_beautifier, width=1030, height=162, fg_color='#22272D', corner_radius=15, bg_color='#22272D')
        
        self.debug = scrolledtext.ScrolledText(
            master=debug_frame,
            wrap=tk.WORD,
            borderwidth=0,
            font=style.log_font,
            fg='#D0D0D0',
            bg='#22272D')
        
        debug_frame_beautifier.pack_propagate(False)
        debug_frame.pack_propagate(False)
        
        debug_frame_beautifier.place(x=20, y=600)
        debug_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.debug.tag_configure("sel", background='#22272D', foreground='#FFFFFF')
        self.debug.pack(fill="both", expand=True)
        self.debug.vbar.pack_forget()
        
        custom_vbar = CTkScrollbar(
            master=debug_frame_beautifier,
            width=8,
            height=170,
            border_spacing=0,
            corner_radius=10,
            fg_color='#393c43',
            button_color='#7a7d8c',
            button_hover_color='#9598a6',
            orientation="vertical",
            command=self.debug.yview)
        self.debug.config(yscrollcommand=custom_vbar.set)
        custom_vbar.pack(side=tk.RIGHT, padx=8)
        
        
# remove from here
def start_app():
    App = GUI()
    App.draw_gui()
    App.mainloop()

if __name__ == '__main__':
    start_app()
