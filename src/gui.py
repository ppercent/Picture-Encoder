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
from crypto.rsa import generate_keys, encrypt, decrypt, encode_base_64, decode_text
from utils.utils import ImageManager


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
        # self.rsa = RSA(self)
        self.ImageManager = ImageManager(self)
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
        self.rsa_size_var = tk.StringVar(self)
        self.public_key_var = tk.StringVar(self)
        self.private_key_var = tk.StringVar(self)
        self.output_name_var = tk.StringVar(value='image_classique')
        self.decrypt_private_key_var = tk.StringVar(self)
        
        self.use_alpha_var = StringVar(value="off")
        self.use_rsa_var = StringVar(value="off")
        self.loading_job = None
        self.key_queue = queue.Queue()
        
        # globals
        self.current_mode = 'encode'
        self.formats = ('png','jpg','jpeg', 'bmp', 'tiff', 'tif', 'webp', 'tga')
        self.rsa_sizes = ('128', '256', '512', '1024')
        self.has_generated_keys = False
        self.encoded_image_generated = False
        self.image_to_encode_path = None
        self.image_to_decode_path = None
        self.uses_rsa = None
        # self.path_to_diff = ''      # TODO trace add here or find a way to trigger logic when overwritten
        # self.create_diff_frame = None

    def init_images(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.image_mainframe_bg = tk.PhotoImage(file=base_dir + '\\assets\\Frame 1\\background.png')
        self.image_placeholder = tk.PhotoImage(file=base_dir + '\\assets\\image_placeholder.png')
        self.save_image = tk.PhotoImage(file=base_dir + '\\assets\\save.png')
        self.copy_image = tk.PhotoImage(file=base_dir + '\\assets\\copy.png')
        self.preview_image = tk.PhotoImage(file=base_dir + '\\assets\\show.png')
        # self.iconbitmap(base_dir + '\\assets\\icon.ico')
        # self.enter_icon = tk.PhotoImage(file=base_dir + '\\assets\\enter.png')
        # self.icon = tk.PhotoImage(file=base_dir + '\\assets\\icon.png')
        # icon = Image.open(base_dir + "\\assets\\icon.png")
        # icon = ImageTk.PhotoImage(icon)
        # self.wm_iconphoto(True, icon)

    def resize(self,image,size):
        wpercent = (size[0] / float(image.size[0]))
        hpercent = (size[1] / float(image.size[1]))
        percent=min(wpercent,hpercent)
        wsize = int((float(image.size[0]) * float(percent)))
        hsize = int((float(image.size[1]) * float(percent)))
        image = image.resize((wsize, hsize), Image.Resampling.NEAREST)
        return image

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

    def rsa_switch_callback(self):
        if self.use_rsa_var.get() == 'on':
            if self.has_generated_keys:
                self.draw_rsa_options()
                self.draw_rsa_options_private()
            else:
                self.draw_rsa_options()
        else:
            self.hide_rsa_options()
            self.hide_rsa_options_private()

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
        # fetching data
        text_to_encode = self.encode_input_textbox.get("1.0", "end-1c")
        if not text_to_encode:
            self.add_line("Entrer du texte", 'red')
            return
        
        if not self.image_to_encode_path:
            self.add_line("Entrer une image", 'red')
            return
            
        uses_rsa = False
        uses_alpha = True if self.use_alpha_var == 'on' else False
        
        if self.use_rsa_var.get() == 'on':
            if self.encode_options_rsa_public_key_field.get():
                uses_rsa = True
                print('encoded public key: ', self.encode_options_rsa_public_key_field.get())
                print('text: ', text_to_encode)
                print('decoded public key: ', decode_text(self.encode_options_rsa_public_key_field.get()))
                text_to_encode = encrypt(text_to_encode, decode_text(self.encode_options_rsa_public_key_field.get()))
            else:
                print('nonono')
                
        # encode the image
        self.ImageManager.set_image(self.image_to_encode_path)
        self.ImageManager.encode_image(text_to_encode, 'DEFAULT', uses_rsa, uses_alpha)
        
        # update image preview
        self.encoded_image_generated = True
        encoded_image_tk = ImageTk.PhotoImage(self.resize(self.ImageManager.image, (400,270)))
        self.encoded_image_preview_label.config(image=encoded_image_tk)
        self.encoded_image_preview_label.image = encoded_image_tk
        self.encoded_image_preview_label.pack(expand=True)
        self.add_line('Encodage terminé!','green')
        self.encode_image_placeholder.place_forget()
        self.encode_image_placeholder_label.place_forget()
        
        # options=[
        # self.rsa_size_var.get(), 
        
        # self.use_alpha_var.get(), 
        # self.use_rsa_var.get(), 

        # self.current_mode.get(),
        # self.formats.get(), 
        # self.rsa_sizes.get(),
        # ]
        # print(options)
    def load_input_image(self, frame, widgets, type):
        types = [("Images", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff;*.tif;*.webp;*tga")]
        file_path = filedialog.askopenfilename(filetypes=types) 
        if not file_path:
            return
        
        if type == 'encode_input':
            self.image_to_encode_path=file_path
            image_label = self.original_image_label
            
        elif type == 'decode_input':
            self.image_to_decode_path=file_path
            image_label = self.encoded_image_label
            
            # get the image watermark
            self.ImageManager.set_image(file_path)
            self.uses_rsa, self.uses_alpha, self.char_count, self.error_code, self.index, self.index_rgb = self.ImageManager.decode_watermark()
            
            if self.uses_rsa == 1 and self.error_code == 0:
                self.draw_decode_frames(True)
            elif self.uses_rsa == 0 and self.error_code == 0:
                self.draw_decode_frames()
                
        try:
            loaded_image = Image.open(file_path)
            self.add_line(f"Image chargée avec succès! ({loaded_image.size[0]}x{loaded_image.size[1]}) {file_path}")
            loaded_image = self.resize(loaded_image, (frame.cget('width'),frame.cget('height')))
            loaded_image_tk = ImageTk.PhotoImage(loaded_image)
            image_label.config(image=loaded_image_tk)
            image_label.image = loaded_image_tk
            image_label.pack(expand=True)
        
            for widget in widgets:
                widget.place_forget()
            
            image_label.bind('<Button-1>', lambda e: self.load_input_image(frame, [], type)) 
            
        except Exception as e:
            pass

    def init_encode_frames(self):
        '''This method is called to initialize the layout of the encode UI'''
        # setup encode mainframes || ONLY PACK/UNPACK MAINFRAMES
        self.encode_input_mainframe = CTkFrame(self, width=500, height=455, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')       # first frame in the encode section
        self.encode_options_mainframe = CTkFrame(self, width=500, height=175, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')       # second frame in the encode section
        self.encode_image_output_preview_mainframe = CTkFrame(self, width=400, height=270, fg_color='#f1efef', corner_radius=15, bg_color='#FFFFFF')     # third frame in the encode section
        self.encode_image_button_mainframe = CTkFrame(self, width=105, height=138, fg_color='#7dc9ef', corner_radius=30, bg_color='#1a93cf') # ONLY PACK THIS AFTER RESULTS ARE DONE
        
        self.encode_input_mainframe.pack_propagate(False)
        self.encode_options_mainframe.pack_propagate(False)
        self.encode_image_output_preview_mainframe.pack_propagate(False)
        self.encode_image_button_mainframe.pack_propagate(False)

        # create the widgets of the first mainframe
        self.encode_input_textbox = CTkTextbox(
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
            cursor='hand2',
            corner_radius=15,
            bg_color='#D9D9D9')
            
        encode_input_image_frame.pack_propagate(False)
            
        encode_input_image_placeholder = tk.Label(encode_input_image_frame, image=self.image_placeholder)
        encode_input_image_label = tk.Label(encode_input_image_frame, font=('SF Pro', 10, "bold"), text="Choisir une image dans laquelle encoder votre message")
        
        self.original_image_label = tk.Label(encode_input_image_frame)
        # encode_input_image_frame.bind('<Button-1>', lambda e: self.load_input_image(encode_input_image_frame,[encode_input_image_placeholder,encode_input_image_label],'encode_input'))
        
        for input_image_frame_widget in [encode_input_image_frame,encode_input_image_placeholder,encode_input_image_label]:
            input_image_frame_widget.bind('<Button-1>', lambda e: self.load_input_image(encode_input_image_frame,[encode_input_image_placeholder,encode_input_image_label],'encode_input'))
            input_image_frame_widget.bind("<Enter>", lambda e: encode_input_image_label.config(fg='#4a4d50'))
            input_image_frame_widget.bind("<Leave>", lambda e: encode_input_image_label.config(fg='#000000'))
        
        # TODO make encode_input_image_label text change color when you hover the frame/label, so the user knows you can click it (and it would open file explorer) AND implement image paste from clipboard
        
        encode_input_encode_button = CTkButton(
            master=self.encode_input_mainframe,
            fg_color='#1a93cf',
            hover_color='#33a7de',
            height=50,
            text='Commencer à encoder',
            font=('Google Sans Text', 25, 'bold'),
            corner_radius=60,
            command=lambda: self.button_start_encoding_callback())
        
        # pack widgets on the first frame of the encode section
        self.encode_input_textbox.pack(pady=25)
        self.encode_input_textbox.insert("0.0", "Entrez le texte à encoder...")
        
        encode_input_image_placeholder.place(x=190, y=40)
        encode_input_image_label.place(x=50, y=110)
        encode_input_image_frame.pack()
        
        encode_input_encode_button.pack(side='bottom', pady=8)
        
        
        # create the widgets of the second mainframe TODO rename with this pattern: encode_options_do_something -> do_something (remove useless crap & cleanup) && args orders && add_field ? && add on focus for textbox
        encode_options_title_label = ttk.Label(self.encode_options_mainframe, text='Options', font=('Consolas', 17, 'bold'), foreground='#000000', background='#D9D9D9')
        
        encode_options_output_name_label = ttk.Label(self.encode_options_mainframe, text='Nom de sortie', font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        self.encode_options_output_name_field = CTkEntry(
            master=self.encode_options_mainframe,
            height=25,
            width=210,
            border_width=1,
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            textvariable=self.output_name_var,
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            font=("Segoe UI", 13),
            corner_radius=5)
        self.encode_options_output_name_field.bind("<FocusIn>", lambda e: self.on_focus_in_callback(e, self.encode_options_output_name_field))
        self.encode_options_output_name_field.bind("<FocusOut>", lambda e: self.on_focus_out_callback(e, self.encode_options_output_name_field))
        
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
            offvalue='off',
            width=40,
            height=25)
        
        encode_options_separation_bar_frame = CTkFrame(self.encode_options_mainframe, width=3, height=200, fg_color='black', corner_radius=15, bg_color='#D9D9D9')
        
        encode_options_rsa_label = ttk.Label(self.encode_options_mainframe, text="Encrypter avec RSA", font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        encode_options_rsa_switch = CTkSwitch(
            self.encode_options_mainframe,
            text='',
            button_color='#949494',
            button_hover_color='#A8A8A8',
            progress_color='#63c58c',
            corner_radius=60,
            variable=self.use_rsa_var,
            onvalue='on',
            offvalue='off',
            width=40,
            height=25,
            command=lambda: self.rsa_switch_callback())
        
        # pack widgets on the second frame of the encode section
        encode_options_title_label.pack(anchor='w', padx=75, pady=4)
        
        encode_options_output_name_label.place(x=10, y=40)
        self.encode_options_output_name_field.place(x=10, y=65)

        encode_options_output_format_label.place(x=10, y=100)
        encode_options_output_format_option_menu.place(x=160, y=102)
        
        encode_options_should_use_alpha_label.place(x=10, y=137) #x=250, y=110
        encode_options_should_use_alpha_switch.place(x=200, y=139)
        
        encode_options_separation_bar_frame.place(x=240, y=0)
       
        encode_options_rsa_label.place(x=253, y=10)
        encode_options_rsa_switch.place(x=447, y=12)
        
        # create the widgets of the third mainframe
        self.encode_image_placeholder = tk.Label(self.encode_image_output_preview_mainframe, image=self.image_placeholder)
        self.encode_image_placeholder_label = tk.Label(self.encode_image_output_preview_mainframe, font=('SF Pro', 12, "bold"), text="Image de sortie") #TODO add the aspect ratio of the selected image && its dimensions
        self.encoded_image_preview_label = tk.Label(self.encode_image_output_preview_mainframe)
        
        # pack widgets on the third frame of the encode section
        self.encode_image_placeholder.place(x=168, y=103)
        self.encode_image_placeholder_label.place(x=140, y=180)
        
        # create the widgets of the fourth mainframe
        encode_image_preview_button = tk.Button(
            self.encode_image_button_mainframe, relief='flat',
            bd=0,
            activebackground='#7dc9ef',
            background='#7dc9ef',
            highlightthickness=0,
            image=self.preview_image,
            command=lambda: self.image_preview_button_callback('show'))
        encode_image_save_button = tk.Button(
            self.encode_image_button_mainframe,
            relief='flat',
            bd=0,
            activebackground='#7dc9ef',
            background='#7dc9ef',
            highlightthickness=0,
            image=self.save_image,
            command=lambda: self.image_preview_button_callback('save'))       
       
       
        # pack widgets on the fourth frame of the encode section
        encode_image_preview_button.pack(side='top', pady=3)
        encode_image_save_button.pack(side='bottom', pady=3)
    
    def image_preview_button_callback(self, button_type):
        if self.encoded_image_generated == True:
            if button_type == 'show':
                self.ImageManager.image.show()
                
            elif button_type == 'save':          
                image_path = filedialog.askdirectory()
                if image_path:
                    print(image_path)
                    try:
                        extension = self.output_format_var.get()
                        img_name = f'{self.output_name_var.get()}.{extension}'
                        self.ImageManager.image.save(f"{image_path}//{img_name}", format=extension.upper())
                        self.add_line(f"Image enregistrée avec succès! Chemin d'accès: {image_path}//{img_name}", 'green')
                    except Exception as e:
                        self.add_line(f"[-] Erreur lors de l'enregistrement de {img_name}: {e}", 'red')
        else:
            print("The encoded image hasn't been generated yet")
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
    
    def get_key_pair(self):
        try:
            public_key, private_key = generate_keys(int(self.rsa_size_var.get()))
            self.key_queue.put(('success', public_key, private_key))
        except Exception as e:
            self.key_queue.put(('error', str(e)))
    
    def debug_draw_key_generated(self, public_key, private_key, error=''):
        if not error:
            self.add_line('\n-----DEBUT CLÉ PUBLIQUE-----', 'red')
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
    
    def get_key_pair_callback(self):
        # pass
        # self.load_dirty_fix('Génération de la clé publique et de la clé privée')
        # threading.Thread(target=lambda: generate_keys(self, int(self.rsa_size_var.get())), daemon=True).start()
        print(generate_keys(self, int(self.rsa_size_var.get())))
        # self.check_key_generation_status()
    
    def init_rsa_options(self):
        # init widgets
        self.encode_options_rsa_gen_key_pair_button = CTkButton(
            master=self.encode_options_mainframe,
            fg_color='#1a93cf',
            hover_color='#33a7de',
            height=20,
            text='générer une paire de clés',
            font=('Google Sans Text', 13, 'bold'),
            corner_radius=60,
            command=lambda: self.get_key_pair_callback())
        self.encode_options_rsa_size_option_menu = ttk.OptionMenu(self.encode_options_mainframe, self.rsa_size_var, self.rsa_sizes[3], *self.rsa_sizes)
        
        self.encode_options_rsa_public_key_label = ttk.Label(self.encode_options_mainframe, text='Clé publique', font=('SF Pro', 12), foreground='#000000', background='#D9D9D9')
        self.encode_options_rsa_public_key_field = CTkEntry(
            master=self.encode_options_mainframe,
            height=25,
            width=210,
            border_width=1,
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            font=("Segoe UI", 13),
            corner_radius=5,
            textvariable=self.public_key_var)
        
        self.encode_options_rsa_private_key_label = ttk.Label(self.encode_options_mainframe, text='Clé privée', font=('SF Pro', 12), foreground='#000000', background='#D9D9D9')
        self.encode_options_rsa_private_key_field = CTkEntry(
            master=self.encode_options_mainframe,
            height=25,
            width=210,
            border_width=1,
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            placeholder_text='private key',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            font=("Segoe UI", 13),
            corner_radius=5,
            textvariable=self.private_key_var)
    
    def draw_rsa_options(self):
        self.encode_options_rsa_gen_key_pair_button.place(x=253, y=50)
        self.encode_options_rsa_size_option_menu.place(x=442, y=50)
        self.encode_options_rsa_public_key_label.place(x=253, y=75)
        self.encode_options_rsa_public_key_field.place(x=253, y=96)
    
    def draw_rsa_options_private(self):
        self.encode_options_rsa_private_key_label.place(x=253, y=125)
        self.encode_options_rsa_private_key_field.place(x=253, y=145)
    
    def hide_rsa_options(self):
        self.encode_options_rsa_gen_key_pair_button.place_forget()
        self.encode_options_rsa_size_option_menu.place_forget()
        self.encode_options_rsa_public_key_label.place_forget()
        self.encode_options_rsa_public_key_field.place_forget()
    
    def hide_rsa_options_private(self):
        self.encode_options_rsa_private_key_label.place_forget()
        self.encode_options_rsa_private_key_field.place_forget()
    
    def on_focus_in_callback(self, event, CTkEntry):
        CTkEntry.configure(border_color='#3498db')

    def on_focus_out_callback(self, event, CTkEntry):
        CTkEntry.configure(border_color='#c7c7c7')

    def init_decode_options_and_output_rsa(self):
        # mainframes
        self.decode_options_rsa_mainframe = CTkFrame(self, width=500, height=105, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')
        self.decode_output_rsa_mainframe = CTkFrame(self, width=500, height=325, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')

        self.decode_options_rsa_mainframe.pack_propagate(False)
        self.decode_output_rsa_mainframe.pack_propagate(False)

        # widgets
        decode_options_rsa_label = ttk.Label(self.decode_options_rsa_mainframe, text='Decryptage RSA', font=('Consolas', 17, 'bold'), foreground='#000000', background='#D9D9D9')
        decode_options_key_label = ttk.Label(self.decode_options_rsa_mainframe, text='Clé privée', font=('SF Pro', 14), foreground='#000000', background='#D9D9D9')
        decode_options_output_name_field = CTkEntry( # TODO disable depending on switch
            master=self.decode_options_rsa_mainframe,
            height=25,
            width=350,
            border_width=1,
            border_color='#c7c7c7',
            bg_color='#D9D9D9',
            textvariable=self.decrypt_private_key_var,
            # placeholder_text='[...] NjlTc2NjY4MjA2ODE5MjYxMDE0OTgyUzMTc=',
            fg_color='#FFFFFF',
            text_color='#2C3E50',
            font=("Segoe UI", 13),
            corner_radius=5)
        decode_options_output_name_field.bind("<FocusIn>", lambda e: self.on_focus_in_callback(e, decode_options_output_name_field))
        decode_options_output_name_field.bind("<FocusOut>", lambda e: self.on_focus_out_callback(e, decode_options_output_name_field))
        
        decode_ouput_label = ttk.Label(self.decode_output_rsa_mainframe, text='Texte décodé', font=('Consolas', 20, 'bold'), foreground='#000000', background='#D9D9D9')
        self.decode_output_textbox_rsa = CTkTextbox(
            master=self.decode_output_rsa_mainframe,
            height=256,
            width=450,
            wrap=tk.WORD,
            # state='disabled',
            font=('SF Pro', 15),
            border_spacing=0,
            state=tk.DISABLED,
            corner_radius=10,
            fg_color='#f1efef',
            text_color='#000000',
            border_color='#D9D9D9',
            border_width=1)
        
        # place widgets
        decode_options_rsa_label.pack()
        decode_options_key_label.place(x=20, y=40)
        decode_options_output_name_field.place(x=20, y=65)

        decode_ouput_label.pack(pady=4)
        self.decode_output_textbox_rsa.pack()
        self.decode_output_textbox_rsa.configure(state='normal')
        self.decode_output_textbox_rsa.insert("0.0", "Nothing here...")
        self.decode_output_textbox_rsa.configure(state='disabled')

    def init_decode_options_and_output(self):
        # mainframe
        self.decode_output_mainframe = CTkFrame(self, width=500, height=455, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF')
        self.decode_output_mainframe.pack_propagate(False)

        # widgets
        decode_ouput_label = ttk.Label(self.decode_output_mainframe, text='Texte décodé', font=('Consolas', 20, 'bold'), foreground='#000000', background='#D9D9D9')
        self.decode_output_textbox = CTkTextbox( #500x325
            master=self.decode_output_mainframe,
            height=387,
            width=450,
            wrap=tk.WORD,
            font=('SF Pro', 15),
            state=tk.DISABLED,
            border_spacing=0,
            corner_radius=10,
            fg_color='#f1efef',
            text_color='#000000',
            border_color='#D9D9D9',
            border_width=1,)
        encode_image_copy_button = tk.Button(
            self.decode_output_mainframe,
            relief='flat',
            bd=0,
            activebackground='#d9d9d9',
            background='#d9d9d9',
            highlightthickness=0,
            image=self.copy_image,
            command=lambda: self.copy_decode_output_textbox())
  
        # place widgets
        decode_ouput_label.pack(pady=4)
        self.decode_output_textbox.pack()
        self.decode_output_textbox.configure(state='normal')
        self.decode_output_textbox.insert("0.0", "Nothing here...")
        self.decode_output_textbox.configure(state='disabled')
        encode_image_copy_button.place(x=450, y=5)
    
    def init_decode_frames(self):
        # init decode mainframes
        self.init_decode_options_and_output()
        self.init_decode_options_and_output_rsa()
        self.decode_input_mainframe = CTkFrame(self, width=500, height=455, fg_color='#D9D9D9', corner_radius=15, bg_color='#FFFFFF') 
        self.decode_input_mainframe.pack_propagate(False)

        # frame 1 | widget
        decode_input_image_frame = CTkFrame(
            master=self.decode_input_mainframe,
            width=450,
            height=350,
            fg_color='#f1efef',
            cursor='hand2',
            corner_radius=15,
            bg_color='#D9D9D9')
            
        decode_input_image_frame.pack_propagate(False)
            
        decode_input_image_placeholder = tk.Label(decode_input_image_frame, image=self.image_placeholder)
        decode_input_image_label = tk.Label(decode_input_image_frame, font=('SF Pro', 10, "bold"), text="Choisir l'image pour la décoder")
        self.encoded_image_label = tk.Label(decode_input_image_frame)
        # decode_input_image_frame.bind('<Button-1>', lambda e: self.load_input_image(decode_input_image_frame,[decode_input_image_placeholder,decode_input_image_label],'decode_input'))

        for input_image_frame_widget in [decode_input_image_frame,decode_input_image_placeholder,decode_input_image_label]:
            input_image_frame_widget.bind('<Button-1>', lambda e: self.load_input_image(decode_input_image_frame,[decode_input_image_placeholder,decode_input_image_label],'decode_input'))
            input_image_frame_widget.bind("<Enter>", lambda e: decode_input_image_label.config(fg='#4a4d50'))
            input_image_frame_widget.bind("<Leave>", lambda e: decode_input_image_label.config(fg='#000000'))


        decode_input_decode_button = CTkButton(self.decode_input_mainframe, fg_color='#1a93cf', hover_color='#33a7de', height=50, text='Commencer à decoder', font=('Google Sans Text', 25, 'bold'), corner_radius=60, command=lambda: self.button_start_decoding_callback())
        
        # frame 1 | placing widgets
        decode_input_image_placeholder.place(x=190, y=130)#40
        decode_input_image_label.place(x=120, y=200)
        decode_input_image_frame.pack(pady=20)

        decode_input_decode_button.pack(side='bottom', pady=8)
    
    
    def button_start_decoding_callback(self):
        if self.error_code == 0:
            if self.uses_rsa == 1:
                self.ImageManager.decode_image(self.uses_rsa, self.uses_alpha, self.char_count, self.index, self.index_rgb, self.decrypt_private_key_var.get())
            else:
                self.ImageManager.decode_image(self.uses_rsa, self.uses_alpha, self.char_count, self.index, self.index_rgb)
                
    def copy_decode_output_textbox(self):
        self.clipboard_clear()
        self.clipboard_append(self.decode_output_textbox.get("0.0", "end-1c"))
        self.update()

    def draw_decode_frames(self, uses_rsa=False):
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
        try:
            self.decode_input_mainframe.place_forget()
            self.decode_options_rsa_mainframe.place_forget()
            self.decode_output_rsa_mainframe.place_forget()
            self.decode_output_mainframe.place_forget()
        except:
            pass

    def load_text_safe(self, text, frame_index=0):
        if frame_index == -1:
            return
        frames = [' ', '.', '..', '...']
        new_text = text + frames[frame_index]
        self.replace_line(new_text)
        
        frame_index = (frame_index + 1) % len(frames)
        num = 250
        if self.loading_job is None:
            frame_index = -1
            num = 0
            self.replace_line(text)
        self.loading_job = self.after(num, lambda: self.load_text_safe(text, frame_index))

    def load_dirty_fix(self, text):
        self.loading_job = 1
        self.load_text_safe(text)

    def stop_loading(self):
        if self.loading_job:
            self.after_cancel(self.loading_job)
        self.loading_job = None
        

    def remove_extra_empty_lines(self):
        self.debug.configure(state='normal')
    
        line_count = int(self.debug.index(tk.END).split('.')[0]) - 1
    
        for line_num in range(line_count, 0, -1):
            line_content = self.debug.get(f"{line_num}.0", f"{line_num}.end")
        
            if line_content.strip():
                break
            if line_num < line_count:
                self.debug.delete(f"{line_num}.0", f"{line_num+1}.0")
        self.debug.configure(state='disabled')

    def add_line(self, text, color=None):
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

    def replace_line(self, text, color=None):
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
        self.init_decode_frames()
        self.init_rsa_options()
        
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
        
        # draw debug/log window TODO add the methods for adding/replacing lines (and put default text color in style class for the debug too) && make overall cleanup && fix font class   
        debug_frame_beautifier = CTkFrame(self, width=1040, height=180, fg_color='#22272D', corner_radius=15, bg_color='#FFFFFF')           # used for rounded corners
        debug_frame = CTkFrame(debug_frame_beautifier, width=1030, height=162, fg_color='#22272D', corner_radius=15, bg_color='#22272D')    # used as a container to resize scrolltext
        
        self.debug = scrolledtext.ScrolledText(
            master=debug_frame,
            wrap=tk.WORD,
            state='disabled',
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
        
        # threading.Thread(target=lambda: self.test_todelete(3), daemon=True).start()
        # self.generate_keys(1024)
        
            
# remove from here
def start_app():
    App = GUI()
    App.draw_gui()
    App.mainloop()

if __name__ == '__main__':
    start_app()
