from PIL import Image
import math

from crypto.rsa import decrypt, decode_text

        
class ImageManager:
    def __init__(self, GUI):
        self.image = None
        self.GUI = GUI
        self.WATERMARK_KEY = "001101110000110101011101"
        self.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
        self.GLOBAL_INDEX_RGB = 0
        self.MAX_RGB_INDEX = 2
        self.ENCODED_CHARACTERS_COUNTER = 0

    def get_ppercent_used(self):
        return round(((self.GLOBAL_INDEX_IMAGE[1] - 1) / self.HEIGHT) + (self.GLOBAL_INDEX_IMAGE[0] / (self.PIXEL_COUNT)), 2)

    def get_binary_form(self, letter):
        if len(letter) != 1:
            return None

        encoded = letter.encode('utf-8')
        bytes = ''
        byte_len = 0
        for byte in encoded:
            bytes += format(byte, '08b')
            byte_len += 1
        return [bytes, str(format(byte_len - 1, '02b'))]
    
    def increment_channel(self, channel):
        return channel - 1 if channel == 255 else channel + 1

    def update_globals(self):
        if self.GLOBAL_INDEX_RGB == self.MAX_RGB_INDEX:
            new_width = (self.GLOBAL_INDEX_IMAGE[0] + 1) % self.WIDTH
            new_heigth = self.GLOBAL_INDEX_IMAGE[1]
            if new_width == 0:
                new_heigth += 1
            
            # update global variable
            self.GLOBAL_INDEX_IMAGE = (new_width, new_heigth)
        self.GLOBAL_INDEX_RGB = (self.GLOBAL_INDEX_RGB + 1) % (self.MAX_RGB_INDEX + 1)

        # if self.GLOBAL_INDEX_IMAGE[1] > self.HEIGHT:
            # pass
            #schedule stop process

    def encode_bit(self, bit):
        '''Encodes bit into the channel of a pixel (using RGB) where an even represents 0 and odd represents 1.'''
        # get current pixel & color channel
        if self.GLOBAL_INDEX_IMAGE[0] >= self.WIDTH or self.GLOBAL_INDEX_IMAGE[1] >= self.HEIGHT:
            raise IndexError("index dimension error: out of bound")
            
        current_pixel = list(self.image.getpixel(self.GLOBAL_INDEX_IMAGE))
        current_channel = current_pixel[self.GLOBAL_INDEX_RGB]

        # set color channel
        if (bit == '0' and current_channel % 2 != 0) or (bit == '1' and current_channel % 2 != 1):
            current_channel = self.increment_channel(current_channel)

        # update image
        current_pixel[self.GLOBAL_INDEX_RGB] = current_channel
        self.image.putpixel(self.GLOBAL_INDEX_IMAGE, tuple(current_pixel))

        # update globals
        self.update_globals()

    def encode_bits(self, bits):
        for bit in bits:
            self.encode_bit(bit)

    def read_bits(self, bit_count, bits=''):
        # recursive checks
        if bit_count <= 0:
            return bits
        
        # get current pixel & color channel
        current_pixel = list(self.image.getpixel(self.GLOBAL_INDEX_IMAGE))
        current_channel = current_pixel[self.GLOBAL_INDEX_RGB]
        
        # update globals
        self.update_globals()
        
        # make recursive calls
        if current_channel % 2 == 0:
            return self.read_bits(bit_count - 1, bits + '0')
        else:
            return self.read_bits(bit_count - 1, bits + '1')

    def set_image(self, image_path):
        self.image = Image.open(image_path)
        self.image = self.image.convert('RGBA')
        self.WIDTH = self.image.size[0]
        self.HEIGHT = self.image.size[1]
        self.PIXEL_COUNT = self.WIDTH * self.HEIGHT
        self.reset_globals()

    def encode_watermark(self, text, uses_rsa, uses_alpha):
        # watermark 24 bits + character count 24 bits + is using rsa 1 bit + is using alpha 1 bit
        # the watermark is encoded  WITHOUT the use of alpha channels
        
        watermark_charcount = format(len(text), '024b')
        uses_alpha = '1' if uses_alpha else '0'
        uses_rsa = '1' if uses_rsa else '0'
        
        # 24 bits watermark
        self.encode_bits(self.WATERMARK_KEY)
            
        # 24 bits character count
        self.encode_bits(watermark_charcount)
            
        # 1 bit is using rsa
        self.encode_bits(uses_rsa)
            
        # 1 bit is using rsa
        self.encode_bits(uses_alpha)
            

    def encode_text(self, text):
        for char in text:
            bytes, byte_len_indicator = self.get_binary_form(char)
            self.encode_bits(byte_len_indicator)
            self.encode_bits(bytes)
            self.ENCODED_CHARACTERS_COUNTER += 1

    def reset_globals(self):
        self.GLOBAL_INDEX_RGB = 0
        self.GLOBAL_INDEX_IMAGE = (0, 0)
        self.ENCODED_CHARACTERS_COUNTER = 0

    def encode_image(self, text, uses_rsa, uses_alpha):
        # reset globals
        self.reset_globals()
        try:
            # encode the watermark
            self.encode_watermark(text, uses_rsa, uses_alpha)
        
            # encode the text
            self.MAX_RGB_INDEX = 3 if uses_alpha else 2
            self.encode_text(text)
            
            coef = 4 if uses_alpha == 1 else 3
            heigth_index = 0 if self.GLOBAL_INDEX_IMAGE[1] == 0 else (self.GLOBAL_INDEX_IMAGE[1] - 1)
            width_add = 0 if self.GLOBAL_INDEX_IMAGE[0] == 0 else (self.GLOBAL_INDEX_IMAGE[0] - 1)
            rgb_add = self.GLOBAL_INDEX_RGB + 1
            
            bits_used = (((heigth_index * self.WIDTH) + width_add) * 3) + rgb_add
            bits_total = self.HEIGHT * self.WIDTH * coef
            ppercent_used = round((bits_used / bits_total) * 100, 2)
            self.GUI.add_line(f"Image encodée avec succès! ~{ppercent_used}% de l'image a été utilisé pour encoder le texte", "green")
            self.GUI.add_line("Utiliser le bouton 'enregistrer' sur la droite pour sauvegarder l'image encodée.", "green")  
            self.GUI.add_line("")
            return 0
        except IndexError as e:
            ppercent_encoded = round((self.ENCODED_CHARACTERS_COUNTER / len(text)) * 100, 2)
            self.GUI.add_line(f"Erreur lors de l'encodage: l'image selectionnée ne peut pas contenir les données à encoder.", 'red')
            self.GUI.add_line(f"{self.ENCODED_CHARACTERS_COUNTER}/{len(text)} (~{ppercent_encoded}%) du texte a été encodé et a saturé l'image.", 'red')
            self.GUI.add_line("")
            self.ENCODED_CHARACTERS_COUNTER = 0
        return 1
    
    def is_encoding_valid(self):
        watermark = self.read_bits(24)
        if watermark == self.WATERMARK_KEY:
            return True
        else:
            return False
    
    def read_character(self, bits, byte_len=8):
        # check for a correct length
        if len(bits) % byte_len != 0:
            return ''
        
        # reach the character
        try:
            byte_count = len(bits) // byte_len
            byte_array = int(bits, 2).to_bytes(byte_count, 'big')
            return byte_array.decode('utf-8')
        except:
            # TODO GUI.debug prints
            return ''

    def get_image_text(self, char_count):
        image_text = ''

        while char_count:
            # get the following character size (00 -> 1 byte | 01 -> 2 bytes | 10 -> 3 bytes | 11 -> 4 bytes), encoding: utf-8
            byte_len_indicator = self.read_bits(2)
            current_character = ''

            # get the current character
            if byte_len_indicator == '00':
                current_character = self.read_character(self.read_bits(8))
            elif byte_len_indicator == '01':
                current_character = self.read_character(self.read_bits(16))
            elif byte_len_indicator == '10':
                current_character = self.read_character(self.read_bits(24))
            elif byte_len_indicator == '11':
                current_character = self.read_character(self.read_bits(32))

            # update loop state
            image_text += current_character
            char_count -= 1
        
        return image_text
    
    def decode_watermark(self):
        if self.is_encoding_valid():
            char_count = int(self.read_bits(24), 2)     # the character count is encoded following the 3 bytes watermark (which is the same size, 3 bytes)
            uses_rsa = int(self.read_bits(1), 2)
            uses_alpha = int(self.read_bits(1), 2)
            self.MAX_RGB_INDEX = 3 if uses_alpha else 2
            return (uses_rsa, uses_alpha, char_count, 0, self.GLOBAL_INDEX_IMAGE, self.GLOBAL_INDEX_RGB)
        return (0, 0, 0, 1, (0, 0), 0)

    def decode_image(self, uses_rsa, uses_alpha, char_count, index, index_rgb, private_key=''):
        self.GLOBAL_INDEX_IMAGE = index
        self.GLOBAL_INDEX_RGB = index_rgb
        self.MAX_RGB_INDEX = 3 if uses_alpha == 1 else 2
        image_text = self.get_image_text(char_count)
        
        if uses_rsa == 1:
            try:
                image_text = decrypt(image_text, decode_text(private_key))
                self.GUI.decode_output_textbox_rsa.configure(state='normal')
                self.GUI.decode_output_textbox_rsa.delete("0.0", "end")
                self.GUI.decode_output_textbox_rsa.insert('0.0', image_text)
                self.GUI.decode_output_textbox_rsa.configure(state='disabled')
            except Exception as e:
                self.GUI.add_line(f'Erreur lors de la décryption RSA du texte: {e}', 'red')
        
        self.GUI.decode_output_textbox.configure(state='normal')
        self.GUI.decode_output_textbox.delete("0.0", "end")
        self.GUI.decode_output_textbox.insert('0.0', image_text)
        self.GUI.decode_output_textbox.configure(state='disabled')
        self.GUI.add_line('Decodage terminé :3','green')

# for scientific research purposes only
if __name__ == '__main__':
    IM = ImageManager(0)
    IM.set_image(r'input.png')

    text = r'''some very very secret text'''
    IM.encode_image(text, False, True)
    IM.image.save('alphas.png', format='PNG')
    
    # IM.decode_image()
    # print(IM.get_ppercent_used(), r'% of the image used.')
