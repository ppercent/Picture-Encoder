from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkImage, CTkScrollbar, CTkOptionMenu, CTkSwitch, CTkScrollableFrame, StringVar
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
        self.output_format_var = tk.StringVar(self)
        self.use_alpha_var = StringVar(value="off")

        # globals
        # self.current_mode = 'init'
        self.current_mode = 'encode'
        self.formats = ('PNG', 'TIFF', 'TGA', 'WebP')
        # self.path_to_diff = ''      # TODO trace add here or find a way to trigger logic when overwritten
        # self.create_diff_frame = None

    def init_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.image_mainframe_bg = tk.PhotoImage(file=base_dir + '\\assets\\background.png')
        # self.image_encode_button = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\encode_button.png')
        # self.image_decode_button = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\decode_button.png')
        self.image_placeholder = tk.PhotoImage(file=base_dir + '\\assets\\image_placeholder.png')
        self.save_image = tk.PhotoImage(file=base_dir + '\\assets\\save.png')
        self.preview_image = tk.PhotoImage(file=base_dir + '\\assets\\show.png')
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
            
            # load encode frames
            self.draw_encode_frames()
            
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
            
            # load decode frames & hide encode frames
            self.hide_encode_frames()
            
    
    def init_encode_frames(self):
        '''This method is called to initialize the layout of the encode UI'''
        # setup encode mainframes || ONLY PACK/UNPACK MAINFRAMES
        self.encode_input_mainframe = CTkFrame(self, width=500, height=455, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')       # first frame in the encode section
        self.encode_options_mainframe = CTkFrame(self, width=500, height=160, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')       # second frame in the encode section
        self.encode_image_output_preview_mainframe = CTkFrame(self, width=400, height=270, fg_color='#f1efef', corner_radius=15, bg_color='#FFFFFF')     # third frame in the encode section
        self.encode_image_button_mainframe = CTkFrame(self, width=105, height=138, fg_color='#7dc9ef', corner_radius=30, bg_color='#1a93cf') # ONLY PACK THIS AFTER RESULTS ARE DONE
        
        self.encode_input_mainframe.pack_propagate(False)
        self.encode_options_mainframe.pack_propagate(False)
        self.encode_image_output_preview_mainframe.pack_propagate(False)
        self.encode_image_button_mainframe.pack_propagate(False)

        # create the widgets of the first mainframe
        encode_input_textbox = CTkTextbox(
            master=self.encode_input_mainframe,
            height=150,
            width=450,
            wrap=tk.WORD,
            font=('SF Pro', 15),
            border_spacing=0,
            corner_radius=10,
            fg_color='#f1efef',
            text_color='#000000',
            border_color='#D9D9D9',
            border_width=1)
            
        encode_input_image_frame = CTkFrame(
            master=self.encode_input_mainframe,
            width=450,
            height=200,
            fg_color='#f1efef',
            corner_radius=15,
            bg_color='#D9D9D9')
            
        encode_input_image_frame.pack_propagate(False)
            
        encode_input_image_placeholder = tk.Label(encode_input_image_frame, image=self.image_placeholder)
        encode_input_image_label = tk.Label(encode_input_image_frame, font=('SF Pro', 10, "bold"), text="Collez une image pour un encodage indétectable\nou laissez vide pour générer une image (plus d'espace pour encoder)")
        # TODO make encode_input_image_label text change color when you hover the frame/label, so the user knows you can click it (and it would open file explorer) AND implement image paste from clipboard
        
        encode_input_encode_button = CTkButton(self.encode_input_mainframe, fg_color='#1a93cf', hover_color='#33a7de', height=50, text='Commencer à encoder', font=('Google Sans Text', 25, 'bold'), corner_radius=60)
        
        # pack widgets on the first frame of the encode section
        encode_input_textbox.pack(pady=25)
        encode_input_textbox.insert("0.0", "Entrez le texte à encoder...")
        
        encode_input_image_placeholder.place(x=190, y=40)
        encode_input_image_label.place(x=2, y=110)
        encode_input_image_frame.pack()
        
        encode_input_encode_button.pack(side='bottom', pady=8)
        
        
        # create the widgets of the second mainframe TODO rename with this pattern: encode_options_do_something -> do_something (remove useless crap & cleanup) && args orders && add_field ? && add on focus for textbox
        encode_options_title_label = ttk.Label(self.encode_options_mainframe, text='Options', font=('Consolas', 20, 'bold'), foreground='#000000', background='#D9D9D9')
        
        encode_options_output_name_label = ttk.Label(self.encode_options_mainframe, text='Nom de sortie', font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        encode_options_output_name_field = CTkEntry(
            master=self.encode_options_mainframe,
            height=25,
            width=210,
            border_width=1,
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            placeholder_text='image_classique',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            font=("Segoe UI", 13),
            corner_radius=5)
        encode_options_output_name_field.bind("<FocusIn>", lambda e: self.on_focus_in_callback(e, encode_options_output_name_field))
        encode_options_output_name_field.bind("<FocusOut>", lambda e: self.on_focus_out_callback(e, encode_options_output_name_field))
        
        encode_options_output_format_label = ttk.Label(self.encode_options_mainframe, text='Format de sortie: ', font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        encode_options_output_format_option_menu = ttk.OptionMenu(self.encode_options_mainframe, self.output_format_var, self.formats[0], *self.formats)
        
        encode_options_should_use_alpha_label = ttk.Label(self.encode_options_mainframe, text="Encoder avec RGBA", font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        encode_options_should_use_alpha_switch = CTkSwitch(
            self.encode_options_mainframe,
            text='',
            button_color='#949494',
            button_hover_color='#A8A8A8',
            progress_color='#63c58c',
            corner_radius=60,
            variable=self.use_alpha_var,
            onvalue='on',
            offvalue='off', width=40, height=25)
        
        # pack widgets on the second frame of the encode section
        encode_options_title_label.pack(pady=4)
        
        encode_options_output_name_label.place(x=10, y=50)
        encode_options_output_name_field.place(x=10, y=75)

        encode_options_output_format_label.place(x=10, y=110)
        encode_options_output_format_option_menu.place(x=160, y=112)
        
        encode_options_should_use_alpha_label.place(x=250, y=110)
        encode_options_should_use_alpha_switch.place(x=440, y=112)
        
        
        # create the widgets of the third mainframe
        encode_image_placeholder = tk.Label(self.encode_image_output_preview_mainframe, image=self.image_placeholder)
        encode_image_placeholder_label = tk.Label(self.encode_image_output_preview_mainframe, font=('SF Pro', 12, "bold"), text="Image de sortie") #TODO add the aspect ratio of the selected image && its dimensions
        
        
        # pack widgets on the third frame of the encode section
        encode_image_placeholder.place(x=168, y=103)
        encode_image_placeholder_label.place(x=140, y=180)
        
        
        # create the widgets of the fourth mainframe
        encode_image_preview_button = tk.Button(self.encode_image_button_mainframe, relief='flat', bd=0, activebackground='#7dc9ef', background='#7dc9ef', highlightthickness=0, image=self.preview_image)
        encode_image_save_button = tk.Button(self.encode_image_button_mainframe, relief='flat', bd=0, activebackground='#7dc9ef', background='#7dc9ef', highlightthickness=0, image=self.save_image)
        
        # pack widgets on the fourth frame of the encode section
        encode_image_preview_button.pack(side='top', pady=3)
        encode_image_save_button.pack(side='bottom', pady=3)
    
    def draw_encode_frames(self):
        self.encode_input_mainframe.place(x=20, y=125)
        self.encode_options_mainframe.place(x=560, y=125)
        self.encode_image_output_preview_mainframe.place(x=560, y=310)
        self.encode_image_button_mainframe.place(x=975, y=344)
        
    def hide_encode_frames(self):
        self.encode_input_mainframe.place_forget()
        self.encode_options_mainframe.place_forget()
        self.encode_image_output_preview_mainframe.place_forget()
        self.encode_image_button_mainframe.place_forget()
        
    def on_focus_in_callback(self, event, CTkEntry):
        CTkEntry.configure(border_color='#3498db')

    def on_focus_out_callback(self, event, CTkEntry):
        CTkEntry.configure(border_color='#c7c7c7')

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
        
        # initialize the encode/decode pannels TODO DRAW THEM THEN UNDRAW THEM SO IT DOESNT GLITCH OUT
        self.init_encode_frames()
        
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
        
        self.update_switch_button_state('decode')
        
        
        # decode mainframe ----------------------
        # setup decode mainframes || ONLY PACK/UNPACK MAINFRAMES
        self.decode_input_mainframe = CTkFrame(self, width=500, height=455, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF') 
        self.decode_options_mainframe = CTkFrame(self, width=500, height=160, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')

        self.decode_input_mainframe.pack_propagate(False)
        self.decode_options_mainframe.pack_propagate(False)

        # create the widgets of the first mainframe
        decode_input_image_frame = CTkFrame(
            master=self.decode_input_mainframe,
            width=450,
            height=350,
            fg_color='#f1efef',
            corner_radius=15,
            bg_color='#D9D9D9')
            
        decode_input_image_frame.pack_propagate(False)
            
        decode_input_image_placeholder = tk.Label(decode_input_image_frame, image=self.image_placeholder)
        decode_input_image_label = tk.Label(decode_input_image_frame, font=('SF Pro', 10, "bold"), text="Collez une image pour la décoder")

        decode_input_decode_button = CTkButton(self.decode_input_mainframe, fg_color='#1a93cf', hover_color='#33a7de', height=50, text='Commencer à decoder', font=('Google Sans Text', 25, 'bold'), corner_radius=60)
        
        # pack widgets on the first frame of the decode section
        decode_input_image_placeholder.place(x=190, y=130)#40
        decode_input_image_label.place(x=120, y=200)
        decode_input_image_frame.pack(pady=20)

        decode_input_decode_button.pack(side='bottom', pady=8)

        # pack frames TODO use different function for that
        self.decode_input_mainframe.place(x=20, y=125)
        
        
        
        
        # draw debug/log window TODO add the methods for adding/replacing lines (and put default text color in style class for the debug too) && make overall cleanup && fix font class   
        debug_frame_beautifier = CTkFrame(self, width=1040, height=180, fg_color='#22272D', corner_radius=15, bg_color='#FFFFFF')
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
