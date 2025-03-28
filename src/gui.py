from customtkinter import CTkEntry, CTkButton, CTkFrame, CTkLabel, CTkTextbox, CTkScrollbar, CTkSwitch, StringVar
from tkinter import scrolledtext
from PIL import Image, ImageTk
from tkinter import ttk, filedialog
import tkinter as tk
import os
import re

from crypto.rsa import generate_keys, encrypt, decode_text
from utils.utils import ImageManager


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('CitrusCrypt')
        self.geometry('1080x800+189+64')
        self.resizable(False, False)
        self.configure(bg='#2C2C2C')
        self.ImageManager = ImageManager(self)
        self.init_variables()
        self.init_images()

    def init_variables(self):
        '''Initializes every global variables used for the GUI'''

        # string variables
        self.output_format_var = tk.StringVar(self)
        self.rsa_size_var = tk.StringVar(self)
        self.public_key_var = tk.StringVar(self)
        self.private_key_var = tk.StringVar(self)
        self.output_name_var = tk.StringVar(value='image_classique')
        self.decrypt_private_key_var = tk.StringVar(self)
        self.use_alpha_var = StringVar(value="off")
        self.use_rsa_var = StringVar(value="off")
        
        # globals variables
        self.current_mode = 'encode'
        self.formats = ('png', 'bmp', 'tiff', 'tga')
        self.rsa_sizes = ('128', '256', '512', '1024')
        self.has_generated_keys = False
        self.encoded_image_generated = False
        self.image_to_encode_path = None
        self.image_to_decode_path = None
        self.uses_rsa = None

    def init_images(self):
        '''Initializes & allocate every images used for the GUI'''

        # load all assets
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon = Image.open(base_dir + "\\assets\\icon.png")
        icon = ImageTk.PhotoImage(icon)
        self.wm_iconphoto(True, icon)
        self.image_mainframe_bg = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\background.png')
        self.image_placeholder = tk.PhotoImage(file=base_dir + '\\assets\\image_placeholder.png')
        self.save_image = tk.PhotoImage(file=base_dir + '\\assets\\save.png')
        self.copy_image = tk.PhotoImage(file=base_dir + '\\assets\\copy.png')
        self.preview_image = tk.PhotoImage(file=base_dir + '\\assets\\show.png')
        
    def init_encode_frames(self):
        '''This method is called to initialize the layout of the encode UI and prevent unwanted lags'''

        # setup encode mainframes => only these are being packed/unpacked
        self.encode_input_mainframe = CTkFrame(                 # first frame in the encode section
            master=self,
            width=500,
            height=455,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',       
            corner_radius=15)
        
        self.encode_options_mainframe = CTkFrame(               # second frame in the encode section
            master=self,
            width=500,
            height=175,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',      
            corner_radius=15)
        self.encode_image_output_preview_mainframe = CTkFrame(  # third frame in the encode section
            master=self,
            width=400,
            height=270,
            fg_color='#f1efef',
            bg_color='#FFFFFF',
            corner_radius=15)
        self.encode_image_button_mainframe = CTkFrame(          # fourth frame in the encode section
            master=self,
            width=105,
            height=138,
            fg_color='#7dc9ef',
            bg_color='#1a93cf',
            corner_radius=30)
        
        self.encode_input_mainframe.pack_propagate(False)
        self.encode_options_mainframe.pack_propagate(False)
        self.encode_image_output_preview_mainframe.pack_propagate(False)
        self.encode_image_button_mainframe.pack_propagate(False)

        # create the widgets of the first mainframe
        self.encode_input_textbox = CTkTextbox(
            master=self.encode_input_mainframe,
            width=450,
            height=150,
            font=('SF Pro', 15),
            fg_color='#f1efef',
            text_color='#000000',
            border_color='#D9D9D9',
            wrap=tk.WORD,
            border_spacing=0,
            corner_radius=10,
            border_width=1)
            
        encode_input_image_frame = CTkFrame(
            master=self.encode_input_mainframe,
            width=450,
            height=200,
            fg_color='#f1efef',
            bg_color='#D9D9D9',
            cursor='hand2',
            corner_radius=15)
            
        encode_input_image_frame.pack_propagate(False)
            
        encode_input_image_placeholder = tk.Label(
            master=encode_input_image_frame,
            image=self.image_placeholder)
        encode_input_image_label = tk.Label(
            master=encode_input_image_frame,
            font=('SF Pro', 10, "bold"),
            text="Choisir une image dans laquelle encoder votre message")

        self.original_image_label = tk.Label(master=encode_input_image_frame)
        
        # setup the callbacks
        for input_image_frame_widget in [encode_input_image_frame, encode_input_image_placeholder, encode_input_image_label]:
            input_image_frame_widget.bind('<Button-1>', lambda e: self.load_input_image(encode_input_image_frame, [encode_input_image_placeholder, encode_input_image_label], 'encode_input'))
            input_image_frame_widget.bind("<Enter>", lambda e: self.image_frame_widget_on_enter(encode_input_image_label, encode_input_image_frame))
            input_image_frame_widget.bind("<Leave>", lambda e: self.image_frame_widget_on_leave(encode_input_image_label, encode_input_image_frame))
        
        encode_input_encode_button = CTkButton(
            master=self.encode_input_mainframe,
            height=50,
            font=('Google Sans Text', 25, 'bold'),
            text='Commencer à encoder',
            fg_color='#1a93cf',
            hover_color='#33a7de',
            corner_radius=60,
            command=lambda: self.button_start_encoding_callback())
        
        self.character_indicator_label = ttk.Label(
            master=self.encode_input_mainframe,
            font=('SF Pro', 10, 'bold'),
            foreground='#000000',
            background='#D9D9D9')
        
        # pack widgets on the first frame of the encode section
        self.encode_input_textbox.pack(pady=25)
        self.encode_input_textbox.insert("0.0", "Entrez le texte à encoder...")
        self.encode_input_textbox.bind("<KeyRelease>", lambda event: self.update_char_indicator())
        self.update_char_indicator()
        self.character_indicator_label.place(x=22, y=2)
        
        encode_input_image_placeholder.place(x=190, y=40)
        encode_input_image_label.place(x=50, y=110)
        encode_input_image_frame.pack()
        
        encode_input_encode_button.pack(side='bottom', pady=8)
        
        # create the widgets of the second mainframe
        encode_options_title_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('Consolas', 17, 'bold'),
            text='Options',
            foreground='#000000',
            background='#D9D9D9')
        
        encode_options_output_name_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('SF Pro', 14),
            text='Nom de sortie',
            foreground='#000000',
            background='#D9D9D9')
        self.encode_options_output_name_field = CTkEntry(
            master=self.encode_options_mainframe,
            width=210,
            height=25,
            font=("Segoe UI", 13),
            text_color='#2C3E50',
            fg_color='#FFFFFF',
            bg_color='#D9D9D9',
            border_color='#c7c7c7',
            border_width=1,
            textvariable=self.output_name_var,
            corner_radius=5)
        self.encode_options_output_name_field.bind("<FocusIn>", lambda e: self.on_focus_in_callback(e, self.encode_options_output_name_field))
        self.encode_options_output_name_field.bind("<FocusOut>", lambda e: self.on_focus_out_callback(e, self.encode_options_output_name_field))
        
        encode_options_output_format_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('SF Pro', 14),
            text='Format de sortie: ',
            foreground='#000000',
            background='#D9D9D9')
        encode_options_output_format_option_menu = ttk.OptionMenu(
            self.encode_options_mainframe,
            self.output_format_var,
            self.formats[0],
            *self.formats)
        
        encode_options_should_use_alpha_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('SF Pro', 14),
            text="Encoder avec RGBA",
            foreground='#000000',
            background='#D9D9D9')
        encode_options_should_use_alpha_switch = CTkSwitch(
            master=self.encode_options_mainframe,
            width=40,
            height=25,
            text='',
            button_color='#949494',
            button_hover_color='#A8A8A8',
            progress_color='#63c58c',
            corner_radius=60,
            onvalue='on',
            offvalue='off',
            variable=self.use_alpha_var,
            command=lambda: self.update_char_indicator())
        
        encode_options_separation_bar_frame = CTkFrame(
            master=self.encode_options_mainframe,
            width=3,
            height=200,
            fg_color='black',
            bg_color='#D9D9D9',
            corner_radius=15)
        
        encode_options_rsa_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('SF Pro', 14),
            text="Encrypter avec RSA",
            foreground='#000000',
            background='#D9D9D9')
        encode_options_rsa_switch = CTkSwitch(
            self.encode_options_mainframe,
            width=40,
            height=25,
            text='',
            button_color='#949494',
            button_hover_color='#A8A8A8',
            progress_color='#63c58c',
            corner_radius=60,
            onvalue='on',
            offvalue='off',
            variable=self.use_rsa_var,
            command=lambda: self.rsa_switch_callback())
        
        # pack widgets on the second frame of the encode section
        encode_options_title_label.pack(anchor='w', padx=75, pady=4)
        
        encode_options_output_name_label.place(x=10, y=40)
        self.encode_options_output_name_field.place(x=10, y=65)

        encode_options_output_format_label.place(x=10, y=100)
        encode_options_output_format_option_menu.place(x=160, y=102)
        
        encode_options_should_use_alpha_label.place(x=10, y=137)
        encode_options_should_use_alpha_switch.place(x=200, y=139)
        
        encode_options_separation_bar_frame.place(x=240, y=0)
       
        encode_options_rsa_label.place(x=253, y=10)
        encode_options_rsa_switch.place(x=447, y=12)
        
        # create the widgets of the third mainframe
        self.encode_image_placeholder = tk.Label(
            master=self.encode_image_output_preview_mainframe,
            image=self.image_placeholder)
        self.encode_image_placeholder_label = tk.Label(
            master=self.encode_image_output_preview_mainframe,
            font=('SF Pro', 12, "bold"),
            text="Image de sortie")
        self.encoded_image_preview_label = tk.Label(master=self.encode_image_output_preview_mainframe)
        
        # pack widgets on the third frame of the encode section
        self.encode_image_placeholder.place(x=168, y=103)
        self.encode_image_placeholder_label.place(x=140, y=180)
        
        # create the widgets of the fourth mainframe
        encode_image_preview_button = tk.Button(
            master=self.encode_image_button_mainframe, 
            activebackground='#7dc9ef',
            background='#7dc9ef',
            relief='flat',
            bd=0,
            highlightthickness=0,
            image=self.preview_image,
            command=lambda: self.image_preview_button_callback('show'))
        encode_image_save_button = tk.Button(
            master=self.encode_image_button_mainframe,
            activebackground='#7dc9ef',
            background='#7dc9ef',
            relief='flat',
            bd=0,
            highlightthickness=0,
            image=self.save_image,
            command=lambda: self.image_preview_button_callback('save'))       
       
        # pack widgets on the fourth frame of the encode section
        encode_image_preview_button.pack(side='top', pady=3)
        encode_image_save_button.pack(side='bottom', pady=3)

    def init_rsa_options(self):
        '''This method is called to initialize the layout of the RSA options and prevent unwanted lags'''

        # init widgets
        self.encode_options_rsa_gen_key_pair_button = CTkButton(
            master=self.encode_options_mainframe,
            height=20,
            font=('Google Sans Text', 13, 'bold'),
            text='générer une paire de clés',
            fg_color='#1a93cf',
            hover_color='#33a7de',
            corner_radius=60,
            command=lambda: self.get_key_pair_callback())
        self.encode_options_rsa_size_option_menu = ttk.OptionMenu(
            self.encode_options_mainframe,
            self.rsa_size_var,
            self.rsa_sizes[3],
            *self.rsa_sizes)
        
        self.encode_options_rsa_public_key_label = ttk.Label(self.encode_options_mainframe, text='Clé publique', font=('SF Pro', 12), foreground='#000000', background='#D9D9D9')
        self.encode_options_rsa_public_key_field = CTkEntry(
            master=self.encode_options_mainframe,
            width=210,
            height=25,
            font=("Segoe UI", 13),
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            border_width=1,
            corner_radius=5,
            textvariable=self.public_key_var)
        
        self.encode_options_rsa_private_key_label = ttk.Label(
            master=self.encode_options_mainframe,
            font=('SF Pro', 12),
            text='Clé privée',
            foreground='#000000',
            background='#D9D9D9')
        self.encode_options_rsa_private_key_field = CTkEntry(
            master=self.encode_options_mainframe,
            width=210,
            height=25,
            font=("Segoe UI", 13),
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            border_width=1,
            corner_radius=5,
            textvariable=self.private_key_var)
        
    def init_decode_options_and_output(self):
        '''This method is called to initialize the layout of the decode options & output and prevent unwanted lags (separate from the decode input field)'''

        # mainframe
        self.decode_output_mainframe = CTkFrame(
            master=self,
            width=500,
            height=455,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',
            corner_radius=15)
        
        self.decode_output_mainframe.pack_propagate(False)

        # widgets
        decode_ouput_label = ttk.Label(
            master=self.decode_output_mainframe,
            font=('Consolas', 20, 'bold'),
            text='Texte décodé',
            foreground='#000000',
            background='#D9D9D9')
        self.decode_output_textbox = CTkTextbox( #500x325
            master=self.decode_output_mainframe,
            width=450,
            height=387,
            font=('SF Pro', 15),
            fg_color='#f1efef',
            text_color='#000000',
            border_color='#D9D9D9',
            state=tk.DISABLED,
            wrap=tk.WORD,
            border_spacing=0,
            border_width=1,
            corner_radius=10)
        
        encode_image_copy_button = tk.Button(
            master=self.decode_output_mainframe,
            activebackground='#d9d9d9',
            background='#d9d9d9',
            relief='flat',
            highlightthickness=0,
            bd=0,
            image=self.copy_image,
            command=lambda: self.copy_decode_output_textbox())
        
        # place widgets
        decode_ouput_label.pack(pady=4)
        self.decode_output_textbox.pack()
        self.decode_output_textbox.configure(state='normal')
        self.decode_output_textbox.insert("0.0", "Nothing here...")
        self.decode_output_textbox.configure(state='disabled')
        encode_image_copy_button.place(x=450, y=5)

    def init_decode_options_and_output_rsa(self):
        '''This method is called to initialize the layout of the decode options & output with RSA fields and prevent unwanted lags (separate from the decode input field)'''

        # mainframes
        self.decode_options_rsa_mainframe = CTkFrame(
            master=self,
            width=500,
            height=105,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',
            corner_radius=15)
        self.decode_output_rsa_mainframe = CTkFrame(
            master=self,
            width=500,
            height=325,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',
            corner_radius=15)

        self.decode_options_rsa_mainframe.pack_propagate(False)
        self.decode_output_rsa_mainframe.pack_propagate(False)

        # widgets
        decode_options_rsa_label = ttk.Label(
            master=self.decode_options_rsa_mainframe,
            font=('Consolas', 17, 'bold'),
            text='Decryptage RSA',
            foreground='#000000',
            background='#D9D9D9')
        decode_options_key_label = ttk.Label(
            master=self.decode_options_rsa_mainframe,
            font=('SF Pro', 14),
            text='Clé privée',
            foreground='#000000',
            background='#D9D9D9')
        decode_options_output_name_field = CTkEntry(
            master=self.decode_options_rsa_mainframe,
            width=350,
            height=25,
            font=("Segoe UI", 13),
            text_color='#2C3E50',
            fg_color='#FFFFFF',
            bg_color='#D9D9D9',
            border_color='#c7c7c7',
            border_width=1,
            corner_radius=5,
            textvariable=self.decrypt_private_key_var)
        decode_options_output_name_field.bind("<FocusIn>", lambda e: self.on_focus_in_callback(e, decode_options_output_name_field))
        decode_options_output_name_field.bind("<FocusOut>", lambda e: self.on_focus_out_callback(e, decode_options_output_name_field))
        
        decode_ouput_label = ttk.Label(
            master=self.decode_output_rsa_mainframe,
            font=('Consolas', 20, 'bold'),
            text='Texte décodé',
            foreground='#000000',
            background='#D9D9D9')
        self.decode_output_textbox_rsa = CTkTextbox(
            master=self.decode_output_rsa_mainframe,
            width=450,
            height=256,
            font=('SF Pro', 15),
            text_color='#000000',
            fg_color='#f1efef',
            border_color='#D9D9D9',
            state=tk.DISABLED,
            wrap=tk.WORD,
            border_spacing=0,
            border_width=1,
            corner_radius=10)
        
        # place widgets
        decode_options_rsa_label.pack()
        decode_options_key_label.place(x=20, y=40)
        decode_options_output_name_field.place(x=20, y=65)

        decode_ouput_label.pack(pady=4)
        self.decode_output_textbox_rsa.pack()
        self.decode_output_textbox_rsa.configure(state='normal')
        self.decode_output_textbox_rsa.insert("0.0", "Nothing here...")
        self.decode_output_textbox_rsa.configure(state='disabled')

    def init_decode_frames(self):
        '''This method is called to initialize the layout of the decode mainframes and prevent unwanted lags (decode input fields)'''

        # init decode mainframes
        self.init_decode_options_and_output()
        self.init_decode_options_and_output_rsa()
        self.decode_input_mainframe = CTkFrame(
            master=self,
            width=500,
            height=455,
            fg_color='#D9D9D9',
            bg_color='#FFFFFF',
            corner_radius=15)
        
        self.decode_input_mainframe.pack_propagate(False)

        # frame 1 | widget
        decode_input_image_frame = CTkFrame(
            master=self.decode_input_mainframe,
            width=450,
            height=350,
            fg_color='#f1efef',
            bg_color='#D9D9D9',
            cursor='hand2',
            corner_radius=15)
            
        decode_input_image_frame.pack_propagate(False)
            
        decode_input_image_placeholder = tk.Label(
            master=decode_input_image_frame,
            image=self.image_placeholder)
        decode_input_image_label = tk.Label(
            master=decode_input_image_frame,
            font=('SF Pro', 10, "bold"),
            text="Choisir l'image pour la décoder")
        self.encoded_image_label = tk.Label(master=decode_input_image_frame)

        # setup the image preview callbacks (& hover effects)
        for input_image_frame_widget in [decode_input_image_frame,decode_input_image_placeholder,decode_input_image_label]:
            input_image_frame_widget.bind('<Button-1>', lambda e: self.load_input_image(decode_input_image_frame,[decode_input_image_placeholder,decode_input_image_label],'decode_input'))
            input_image_frame_widget.bind("<Enter>", lambda e: decode_input_image_label.config(fg='#4a4d50'))
            input_image_frame_widget.bind("<Leave>", lambda e: decode_input_image_label.config(fg='#000000'))

        decode_input_decode_button = CTkButton(
            master=self.decode_input_mainframe,
            height=50,
            font=('Google Sans Text', 25, 'bold'),
            text='Commencer à decoder',
            fg_color='#1a93cf',
            hover_color='#33a7de',
            corner_radius=60,
            command=lambda: self.button_start_decoding_callback())
        
        # frame 1 | placing widgets
        decode_input_image_placeholder.place(x=190, y=130)#40
        decode_input_image_label.place(x=120, y=200)
        decode_input_image_frame.pack(pady=20)

        decode_input_decode_button.pack(side='bottom', pady=8)

    def draw_gui(self):
        '''GUI drawing entry point, initialize the UI in it's encode state'''

        # adding background
        self.background_label = tk.Label(
            master=self,
            image=self.image_mainframe_bg)
        self.background_label.place(relwidth=1, relheight=1)
        
        # initialize the encode/decode pannels (to avoid lags)
        self.init_encode_frames()
        self.init_decode_frames()
        self.init_rsa_options()
        
        # encode/decode switch button
        switch_button_frame = CTkFrame(
            master=self,
            width=450,
            height=65,
            fg_color='#1A93CF',
            bg_color='#FFFFFF',
            corner_radius=60)
        switch_button_frame.pack_propagate(False)
        switch_button_frame.pack(padx=0, pady=30)
        
        self.encode_frame_left = CTkFrame(
            master=switch_button_frame,
            width=100,
            height=64,
            fg_color='#7DC9EF',
            bg_color='#FFFFFF',
            corner_radius=60)
        self.encode_frame_right = CTkFrame(
            master=switch_button_frame,
            width=125,
            height=64,
            fg_color='#7DC9EF',
            bg_color='#1A93CF',
            corner_radius=60)
        self.encode_frame_center = CTkFrame(
            master=switch_button_frame,
            width=75,
            height=64,
            fg_color='#7DC9EF',
            bg_color='#7DC9EF',
            corner_radius=0)
        self.encode_label = CTkLabel(
            master=switch_button_frame,
            font=('Google Sans Text', 30),
            text='Encoder',
            bg_color='#7DC9EF',
            text_color='#FFFFFF')
        self.decode_label = CTkLabel(
            master=switch_button_frame,
            font=('Google Sans Text', 30),
            text='Decoder',
            bg_color='#7DC9EF',
            text_color='#FFFFFF')
        
        switch_button_frame.bind("<Button-1>", self.encode_switch_frame_onclick)
        self.encode_label.bind("<Button-1>", lambda event: self.update_switch_button_state('encode'))
        self.decode_label.bind("<Button-1>", lambda event: self.update_switch_button_state('decode'))
        
        # initialize the first state on app start (encode)
        self.update_switch_button_state('encode')
        
        # draw debug/log window
        debug_frame_beautifier = CTkFrame(  # used for rounded corners
            master=self,
            width=1040,
            height=180,
            fg_color='#22272D',
            bg_color='#FFFFFF',
            corner_radius=15)
        debug_frame = CTkFrame(             # used as a container to resize scrolltext
            master=debug_frame_beautifier,
            width=1030,
            height=162,
            fg_color='#22272D',
            bg_color='#22272D',
            corner_radius=15)
        
        self.debug = scrolledtext.ScrolledText(
            master=debug_frame,
            font=('SF Pro', 11),
            fg='#D0D0D0',
            bg='#22272D',
            state=tk.DISABLED,
            wrap=tk.WORD,
            borderwidth=0)
        
        debug_frame_beautifier.pack_propagate(False)
        debug_frame.pack_propagate(False)
        
        debug_frame_beautifier.place(x=20, y=600)
        debug_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.debug.tag_configure("sel", background='#22272D', foreground='#FFFFFF')
        self.debug.pack(fill="both", expand=True)
        self.debug.vbar.pack_forget()   # the original scrolledtext.ScrolledText.vbar looks ugly, so I created one with CTk and applied the same command as the old one
        
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

    def draw_encode_frames(self):
        '''GUI method to place the encode frames on the UI'''

        self.encode_input_mainframe.place(x=20, y=125)
        self.encode_options_mainframe.place(x=560, y=125)
        self.encode_image_output_preview_mainframe.place(x=560, y=310)
        self.encode_image_button_mainframe.place(x=975, y=344)

    def hide_encode_frames(self):
        '''GUI method to hide (unplace) the encode frames'''

        self.encode_input_mainframe.place_forget()
        self.encode_options_mainframe.place_forget()
        self.encode_image_output_preview_mainframe.place_forget()
        self.encode_image_button_mainframe.place_forget()

    def draw_rsa_options(self):
        '''GUI method to place the RSA options widgets on the UI'''

        self.encode_options_rsa_gen_key_pair_button.place(x=253, y=45)
        self.encode_options_rsa_size_option_menu.place(x=442, y=45)
        self.encode_options_rsa_public_key_label.place(x=253, y=75)
        self.encode_options_rsa_public_key_field.place(x=253, y=96)
    
    def draw_rsa_options_private(self):
        '''GUI method to place the RSA private key widgets on the UI'''
        self.encode_options_rsa_private_key_label.place(x=253, y=125)
        self.encode_options_rsa_private_key_field.place(x=253, y=145)

    def hide_rsa_options(self):
        '''GUI method to hide (unplace) the RSA options widgets'''

        self.encode_options_rsa_gen_key_pair_button.place_forget()
        self.encode_options_rsa_size_option_menu.place_forget()
        self.encode_options_rsa_public_key_label.place_forget()
        self.encode_options_rsa_public_key_field.place_forget()
    
    def hide_rsa_options_private(self):
        '''GUI method to hide (unplace) the RSA private key widgets'''

        self.encode_options_rsa_private_key_label.place_forget()
        self.encode_options_rsa_private_key_field.place_forget()

    def draw_decode_frames(self, uses_rsa=False):
        '''UI method to draw the decode input fields then the corresponding (depending on uses_rsa) options & output decode fields'''

        # unplace everything
        self.hide_decode_frames()
        
        # place everything back
        self.decode_input_mainframe.place(x=20, y=125)
        if uses_rsa:
            self.decode_options_rsa_mainframe.place(x=560, y=125)
            self.decode_output_rsa_mainframe.place(x=560, y=255)
        else:
            self.decode_output_mainframe.place(x=560, y=125)

    def hide_decode_frames(self):
        '''UI method to hide the decode frames (used when switching to encoding mode)'''

        try:
            self.decode_input_mainframe.place_forget()
            self.decode_options_rsa_mainframe.place_forget()
            self.decode_output_rsa_mainframe.place_forget()
            self.decode_output_mainframe.place_forget()
        except:
            pass

    def resize(self, image: Image.Image, size: tuple):
        '''Resize an image to fit into size while keeping it's aspect ratio'''

        wpercent = (size[0] / float(image.size[0]))
        hpercent = (size[1] / float(image.size[1]))
        percent=min(wpercent,hpercent)
        wsize = int((float(image.size[0]) * float(percent)))
        hsize = int((float(image.size[1]) * float(percent)))
        image = image.resize((wsize, hsize), Image.Resampling.NEAREST)
        return image
    
    def load_input_image(self, frame: CTkFrame, widgets: list[tk.Label], type: str):
        '''Handler for image inputs, used when clicking on the empty image placeholders'''

        # get the image path
        types = [("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff;*.tif;*.webp;*tga")]
        file_path = filedialog.askopenfilename(filetypes=types)

        if not file_path:
            return
        
        # update the GUI according to the loaded image
        if type == 'encode_input':
            self.image_to_encode_path=file_path
            self.ImageManager.set_image(file_path)
            image_label = self.original_image_label
            self.update_char_indicator()
            
        elif type == 'decode_input':
            self.image_to_decode_path=file_path
            image_label = self.encoded_image_label
            
            # get the image watermark to display RSA parameters (decode only)
            self.ImageManager.set_image(file_path)
            self.uses_rsa, self.uses_alpha, self.char_count, self.error_code, self.index, self.index_rgb = self.ImageManager.decode_watermark()
            
            # draw / undraw RSA decode pannel
            if self.uses_rsa == 1 and self.error_code == 0:
                self.draw_decode_frames(True)
            elif self.uses_rsa == 0 and self.error_code == 0:
                self.draw_decode_frames()

        try:
            loaded_image = Image.open(file_path)
            
            # display image load
            bit_size = 4 if self.use_alpha_var.get() == 'on' else 3
            bytes_encodable = round(((loaded_image.size[0] * loaded_image.size[1] * bit_size) - 50) // 10)
            self.add_line(f'[+] {os.path.basename(file_path)} chargée avec succès!')
            self.add_line(f'      ➤  dimensions: {loaded_image.size[0]}x{loaded_image.size[1]}')
            self.add_line(f'      ➤  taille encodable: ~{self.format_bytes(bytes_encodable)} de texte')
            if type == 'decode_input':
                self.add_line(f'      ➤  nombre de caractères encodés: {self.char_count}')
            self.add_line('')

            # display image on the placeholder
            loaded_image = self.resize(loaded_image, (frame.cget('width'),frame.cget('height')))
            loaded_image_tk = ImageTk.PhotoImage(loaded_image)
            image_label.config(image=loaded_image_tk)
            image_label.image = loaded_image_tk
            image_label.pack(expand=True)
        
            # hide placeholder widgets
            for widget in widgets:
                widget.place_forget()
            
            # apply the callback to the newly placed image preview
            image_label.bind('<Button-1>', lambda e: self.load_input_image(frame, [], type))

        except Exception as e:
            # unknown error happened
            self.add_line(f"[-] Erreur lors du chargement de l'image: {e}", 'red')

    def image_preview_button_callback(self, button_type: str):
        '''Handler for preview/save button'''

        # check if an image has been yet generated
        if self.encoded_image_generated == True:
            
            # display the image in a new window
            if button_type == 'show':
                self.ImageManager.image.show()
            
            # saves the image in image_path
            elif button_type == 'save':          
                image_path = filedialog.askdirectory()

                if image_path:
                    try:
                        extension = self.output_format_var.get()
                        img_name = f'{self.output_name_var.get()}.{extension}'

                        # make sure the output name is valid
                        if not self.is_valid_filename(self.output_name_var.get()):
                            self.add_line(f"[-] Erreur lors de l'enregistrement de ‟{img_name}”: veuillez donner un nom valide à l'image de sortie", 'red')
                            return
                        
                        # format the image and save it
                        self.ImageManager.image.save(f"{image_path}/{img_name}", format=extension.upper())
                        self.add_line(f"[+] Image enregistrée avec succès! Chemin d'accès: {image_path}/{img_name}", 'green')

                    except Exception as e:
                        self.add_line(f"[-] Erreur lors de l'enregistrement de ‟{img_name}”: {e}", 'red')
                else:
                    self.add_line('[-] Erreur inconnue lors de la séléction du dossier de sortie', 'red')
        else:
            self.add_line(f"[*] Avertissement: l'image encodée n'a pas encore été générée...", 'orange')

    def is_valid_filename(self, file_name: str):
        '''Checks if file_name is a valid name format for filesystem in windows (and other archs)'''

        invalid_chars = r'[<>:"/\\|?*]'
        return len(re.findall(invalid_chars, file_name)) == 0
    
    def encode_switch_frame_onclick(self, event: tk.Event):
        '''Event handler for switching between encode/decode frames'''

        if event.x < 225 and self.current_mode == 'decode':
            self.update_switch_button_state('encode')
        elif event.x > 225 and self.current_mode == 'encode':
            self.update_switch_button_state('decode')

    def rsa_switch_callback(self):
        '''Event handler for the RSA switch'''

        if self.use_rsa_var.get() == 'on':
            if self.has_generated_keys:
                self.draw_rsa_options()
                self.draw_rsa_options_private()
            else:
                self.draw_rsa_options()
        else:
            self.hide_rsa_options()
            self.hide_rsa_options_private()

        # update the character indicator because it doesnt't work with RSA (needs to be disabled)
        self.update_char_indicator()

    def update_switch_button_state(self, state):
        '''Changes the state of the button and place the new context'''

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
            self.hide_decode_frames()
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
            if self.uses_rsa == 1:
                self.draw_decode_frames(True)
            else:
                self.draw_decode_frames()
                
    def button_start_encoding_callback(self):
        '''Start image encoding process with the button callback'''

        # getting the textbox data
        text_to_encode = self.encode_input_textbox.get("0.0", "end-1c")

        # make sure it can properly start the encoding process
        if not text_to_encode:
            self.add_line("Entrer du texte et une image pour commencer l'encodage", 'red')
            return
        
        if not self.image_to_encode_path:
            self.add_line("Entrer du texte et une image pour commencer l'encodage", 'red')
            return

        # handling RSA encryption & other parameters
        uses_rsa = False
        uses_alpha = True if self.use_alpha_var.get() == 'on' else False
        
        if self.use_rsa_var.get() == 'on':
            if self.encode_options_rsa_public_key_field.get():
                try:
                    uses_rsa = True
                    text_to_encode = encrypt(text_to_encode, decode_text(self.encode_options_rsa_public_key_field.get()))
                except Exception:
                    self.add_line("[-] Erreur lors de l'encryptage RSA, veuillez vérifier votre clé ou générer une nouvelle paire de clés", 'red')
                    self.add_line("[*] Tout les formats standards de clés ne sont pas supportés.", 'orange')
                    return
            else:
                self.add_line("[-] Erreur lors de l'encryptage RSA: veuillez entrer une clé.", 'red')
                return
                
        # encode the image
        error_code = self.ImageManager.encode_image(text_to_encode, uses_rsa, uses_alpha)
        
        # update image preview
        if error_code == 0:
            self.encoded_image_generated = True
            encoded_image_tk = ImageTk.PhotoImage(self.resize(self.ImageManager.image, (400,270)))
            self.encoded_image_preview_label.config(image=encoded_image_tk)
            self.encoded_image_preview_label.image = encoded_image_tk
            self.encoded_image_preview_label.pack(expand=True)
            self.encode_image_placeholder.place_forget()
            self.encode_image_placeholder_label.place_forget()

    def button_start_decoding_callback(self):
        '''Start image decoding process with the button callback'''

        # right after the image is loaded, it analyses the watermark and store the results into these global variables: error_code, uses_alpha, etc
        if self.error_code == 0:

            # decode the image using utils.py functions (the UI updates are made within decode_image)
            if self.uses_rsa == 1:
                self.ImageManager.decode_image(self.uses_rsa, self.uses_alpha, self.char_count, self.index, self.index_rgb, self.decrypt_private_key_var.get())
            else:
                self.ImageManager.decode_image(self.uses_rsa, self.uses_alpha, self.char_count, self.index, self.index_rgb)
        else:
            self.add_line("Cette image ne contient pas de texte encodé.", 'red')

    def get_key_pair_callback(self):
        '''Generate key pair button callback, calls the utils function -> which calls self.debug_draw_key_generated()'''

        generate_keys(self, int(self.rsa_size_var.get()))

    def debug_draw_key_generated(self, public_key: str, private_key: str, error=''):
        '''Draws the result of the key generation, xref-to: utils generation keys function'''

        if not error:
            self.add_line('\n', 'red')
            self.add_line('-----DEBUT CLÉ PUBLIQUE-----', 'red')
            self.add_line(public_key)
            self.add_line('-----FIN CLÉ PUBLIQUE-----', 'red')
            self.add_line('\n-----DEBUT CLÉ PRIVÉE-----', 'red')
            self.add_line(private_key)
            self.add_line('-----FIN CLÉ PRIVÉE-----\n', 'red')
            self.draw_rsa_options_private()
            self.public_key_var.set(public_key)
            self.private_key_var.set(private_key)
            self.has_generated_keys = True
        else:
            self.add_line(f'Erreur lors de la génération des clés: {error}', 'red')

    def image_frame_widget_on_enter(self, encode_input_image_label: tk.Label, encode_input_image_frame: CTkFrame):
        '''Add an hover effect to the image placeholder frames'''

        encode_input_image_label.configure(fg='#4a4d50')
        encode_input_image_frame.configure(border_width=1)
        encode_input_image_frame.configure(border_color='#b1b1b1')
    
    def image_frame_widget_on_leave(self, encode_input_image_label: tk.Label, encode_input_image_frame: CTkFrame):
        '''Reset the hover effect  to the image placeholder frames'''

        encode_input_image_label.configure(fg='#000000')
        encode_input_image_frame.configure(border_width=0)

    def on_focus_in_callback(self, event: tk.Event, entry: CTkEntry):
        '''Callback to add a focus effect in a text field'''
        entry.configure(border_color='#3498db')

    def on_focus_out_callback(self, event: tk.Event, entry: CTkEntry):
        '''Callback to remove the focus effect in a text field'''
        entry.configure(border_color='#c7c7c7')

    def update_char_indicator(self):
        '''Update the byte (character) indicator: used bytes / total bytes'''

        # handle RSA usage
        if self.use_rsa_var.get() == 'on':
            self.character_indicator_label.configure(text='N/A (RSA)')
        else:
            # calculate the needed data
            current_byte_count = len(self.encode_input_textbox.get("1.0", "end-1c").encode('utf-8'))
            
            if self.image_to_encode_path and self.ImageManager.image:
                bit_size = 4 if self.use_alpha_var.get() == 'on' else 3
                bits_available = ((self.ImageManager.WIDTH * self.ImageManager.HEIGHT * bit_size) - 50)         # -50 because the whole watermark is 50 bits
                bytes_available = bits_available // 10                                                          # all utf 8 can be considered as 8 bits subdivisions + 2 indication bits
                if self.use_alpha_var.get() == 'on':
                    bytes_available -= 1
                
                # update indicator color
                if current_byte_count > bytes_available:
                    self.character_indicator_label.configure(foreground='red')
                else:
                    self.character_indicator_label.configure(foreground='#000000')

                # update the indicator text
                self.character_indicator_label.configure(text=f'Caractères: {current_byte_count} / {bytes_available}')
            else:
                self.character_indicator_label.configure(text=f'Caractères: {current_byte_count}')

    def format_bytes(self, bytes_amount: int):  # source: claude.ai (it was 3:14am when I did this so..)
        '''Format the byte length for display purposes'''

        # Define scaling thresholds and units
        units = [
            (1_024 ** 3, 'gb'),
            (1_024 ** 2, 'mb'),
            (1_024, 'kb')
        ]
        
        # Handle zero or negative input
        if bytes_amount <= 0:
            return '0 bytes'
        
        # Find appropriate scaling
        for threshold, unit in units:
            if bytes_amount >= threshold:
                # Round to two decimal places
                scaled_value = round(bytes_amount / threshold, 2)
                return f'{scaled_value}{unit}'
        
        # If less than 1 kb, return in bytes
        return f'{bytes_amount} bytes'
    
    def add_line(self, text: str, color=None):
        '''Custom debug window method to print text (adding a line to the debug window)'''

        self.debug.configure(state='normal')
        current = int(self.debug.index(tk.END).split('.')[0]) - 1
        self.debug.insert(tk.END, text+'\n')
        line_start = f"{current}.0"
        line_end = f"{current + 1}.0"
        if color:
            self.debug.tag_add(color, line_start, line_end)
            self.debug.tag_configure(color, foreground=color)
        else:
            for tag in self.debug.tag_names(line_start):
                self.debug.tag_remove(tag, line_start, line_end)
        self.debug.yview_moveto(1.0)
        self.debug.configure(state='disabled')

    def replace_line(self, text: str, color=None):
        '''Custom debug window method to replace previous added line (replacing a line to the debug window)'''

        self.debug.configure(state='normal')
        previous_line_index = int(self.debug.index(tk.END).split('.')[0]) - 2
        self.debug.delete(f'{previous_line_index}.0', f'{previous_line_index}.0 lineend')
        self.debug.insert(f'{previous_line_index}.0', text+'\n')
        if previous_line_index == 0:
            line_start = f"{previous_line_index + 1}.0"
            line_end = f"{previous_line_index + 2}.0"
        else:
            line_start = f"{previous_line_index}.0"
            line_end = f"{previous_line_index + 1}.0"
        if color:   
            self.debug.tag_add(color, line_start, line_end)
            self.debug.tag_configure(color, foreground=color)
        else:
            for tag in self.debug.tag_names(line_start):
                self.debug.tag_remove(tag, line_start, line_end)

        self.debug.configure(state='disabled')
        self.remove_extra_empty_lines()

    def remove_extra_empty_lines(self):
        '''Custom debug window method to remove extra empty newlines when appending line into the debug window'''

        self.debug.configure(state='normal')
    
        line_count = int(self.debug.index(tk.END).split('.')[0]) - 1
    
        for line_num in range(line_count, 0, -1):
            line_content = self.debug.get(f"{line_num}.0", f"{line_num}.end")
        
            if line_content.strip():
                break
            if line_num < line_count:
                self.debug.delete(f"{line_num}.0", f"{line_num+1}.0")
        self.debug.configure(state='disabled')

    def copy_decode_output_textbox(self):
        '''Copy button callback to paste to clipboard text in the decoded text output field'''

        self.clipboard_clear()
        self.clipboard_append(self.decode_output_textbox.get("0.0", "end-1c"))
        self.update()
