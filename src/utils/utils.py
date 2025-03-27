from PIL import Image
import math


class ImageManager:
    def __init__(self, GUI):
        self.image = None
        self.GUI = GUI
        self.WATERMARK_KEY_DEFAULT = "001101110000110101011101"
        self.WATERMARK_KEY_ENCODE = "100100001000101101011000"
        self.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
        self.GLOBAL_INDEX_RGB = 0
        self.MAX_RGB_INDEX = 2
        # self.print_image_loaded()

    def print_image_loaded(self):
        # change this to GUI.debug later
        print('[+] ... (todo later) image.png loaded!!')
        print('   ➤  image size: ', self.WIDTH, 'x', self.HEIGHT)
        print('   ➤  pixel count: ', self.PIXEL_COUNT)
        print('   ➤  writable size: ', (self.PIXEL_COUNT * 3) / 8 / 1000, 'kb of text.')

    def get_max_character_count_estimation(self):
        bits_count = self.PIXEL_COUNT * 3 - 48
        return math.ceil((bits_count - ((bits_count / 8) * 2)) / 8)

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
        # print(f'\n[+] Started encoding {len(bits)} bits -> {bits}')
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
        self.GLOBAL_INDEX_RGB = 0
        self.GLOBAL_INDEX_IMAGE = (0, 0)

    def encode_watermark(self, text, type, uses_rsa, uses_alpha):
        # watermark 24 bits + character count 24 bits + is using rsa 1 bit + is using alpha 1 bit
        # the watermark is encoded  WITHOUT the use of alpha
        
        watermark_charcount = format(len(text), '024b')
        uses_alpha = '1' if uses_alpha else '0'
        uses_rsa = '1' if uses_rsa else '0'
        
        if type == 'DEFAULT':
            # 24 bits watermark
            self.encode_bits(self.WATERMARK_KEY_DEFAULT)
            
            # 24 bits character count
            self.encode_bits(watermark_charcount)
            
            # 1 bit is using rsa
            self.encode_bits(uses_rsa)
            
            # 1 bit is using rsa
            self.encode_bits(uses_alpha)
            
        elif type == 'ENCODE':
            # 24 bits watermark
            self.encode_bits(self.WATERMARK_KEY_ENCODE)
            
            # 24 bits character count
            self.encode_bits(watermark_charcount)    # TODO it might fuck up with RSA here, changes are required
            
            # 1 bit is using rsa
            self.encode_bits(uses_rsa)
            
            # 1 bit is using rsa
            self.encode_bits(uses_alpha)
        else:
            print('... dont be stupid')

    def encode_text(self, text):
        for char in text:
            bytes, byte_len_indicator = self.get_binary_form(char)
            self.encode_bits(byte_len_indicator)
            self.encode_bits(bytes)

    def encode_image(self, text, type, uses_rsa, uses_alpha):
        # encode the watermark
        self.encode_watermark(text, type, uses_rsa, uses_alpha)

        # encode the text
        self.MAX_RGB_INDEX = 3 if uses_alpha else 2
        self.encode_text(text)
        print('[+] Image encoding is done...')
    
    def is_encoding_valid(self):
        watermark = self.read_bits(24)
        print('watermark: ', watermark)
        if watermark == self.WATERMARK_KEY_DEFAULT:
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
            return (uses_rsa, uses_alpha, char_count, 0)
        return (0, 0, 0, 1)


    def decode_image(self):
        # get type and char_count using the watermark
        uses_rsa, uses_alpha, char_count, error_code = self.decode_watermark()
        # self.GUI.show_decrypt_fields
        # fetches private key
        private_key = r'MzA4Nzg0ODE5MjUzMzUxNTk3NjA1NDEyODI2ODUxNzQ0ODQ0NzE1MTkxNzMwNTM2ODMxNTg2OTUzMzk0OTQ0Nzg3Njc1NTQzNzU5ODc1MzcwNTI2OTU1NjA2MzI2NjMwNTc1MDg5NjA5MTE2MTE0MTcyMTkzMDc0MTY2NTczNTcxMDA4OTczNDAwNjg5MTY2NTk1NjIxODYyODk5NTY1NjQ1OTc5MDAyNzgyNzIzMzA4NDA4ODUxNzQ3NTI1MTAzMDY4MjY3OTEzMDI5MTY5NDI0OTAwMzAwNzgxNTU3OTE4NTY4MTA4MzE1MzQ1Nzg2NzIzMDUwMTk2OTczNjYyOTM1OTg4MzE2ODg2NTcwMTY2ODcwODcwODQ4Mjk5MjEzNDMxNzQwNTI4MTE1ODMwNzM2NTIxODcwODMzMjU2ODA3ODcwMjA1MTMwNjQ4NTM0OTM1OTMxNTI2OTkzODQ0MzAxNjAyNjUzMzk2OTY1MzU2NTA3MTI1OTIzNTEzOTE3MjQ2ODY1OTg5MTE2MTg0OTAzNzk2MTAzNTA4NDkwNTU5MzkwMDA1MTU5MzMzOTY5ODYwNTEyMDIxNDE1Nzk0NjAwMDI2NjM5Mjg2Njg2MjE0MjI2MjgwNzQ5MDYyNjc5NTA2MTg3NDY4NzYxMzEyMTM3Mjg3MjIyNDc1NTI1MDU5MjA0NjM3OTA3MDk4MjM3MjY2MDgyNzE1NTExOTkyNDg0MjYxNTg0NDQ5OTExMzE3OTQyMzY3NDA5MTc5MTkwMzEwOTMyODc5NjU4NDA5MjIzNTI0MjAwMzY4OTM5MzE0Njg3NzM1NSw0ODc4MjMyMjU0MTQwMjg4MjIyMDEyMTI1MjAxODE0NTU5ODM5MjExMzY4MTYwMzg4Mjk1ODkyNjY3MzQ1NDM0MjI5MDYzODEzMzk2MDM3Mzc2NjgyNTg5OTA5NTYzODYyNTY0MzQ4NjU4MjY5MzY2MDE3NTYxMDU5Nzc5Mzg3NDg3NTQwMjc3NDg2NDA4NDM2NDgxNjgxODc5NjAxODUwOTgyOTQ3ODUxNTE4MjcxMjYyNjc2NzI3MTUxOTM4ODU0OTk5MDQzMDY5NzQ4NzEyNzMzMjI5ODIzNTAzMjI1NzY1ODI4MjI5NTQ2OTEyNDUyNjE3MDg0NDU5NTUzNTc3MDU0NjA3MTU3MjM3MjQ2MzQ1OTI2MDc4MDE4NzY5NDkwMjA3NTAzOTcwNzc1MjMxNjc5Myw5NDk0Nzc2MDczNTg1MTg2NTM4MTU3MjY4OTE5MzA1NzUwMTg1OTkxMTEzMzkxOTU3Njk2NjY1MTMzODkzNjA4MTI1OTYxNjIxMjY5MjY2MTg0NzQ3NTYwNTI1NjMyNTc5MDE0MDY1NDA1MDIxNzA2NTM5NDI4NDExNTc0NDU2NDY2MDUwMDI4MTI0NzE5MjkxNDc3NTMwNTY3MDEzOTc2OTMzMjU5OTg1MDY1MzM0OTY0MDE1MDc3NzI4NDI3MzI0MDY3NDQ1Njc3MTI2Mzc3ODU0ODQ3NzY4MjE2NTY5MjczNTU3MjM2MDc4MzY3MDM4MjA5NzMyMzQ3NjU5ODMzNzQwNTcyOTQxMzg0ODE0MTg3ODM2NDE1NTk4NTAwMTIxOTE1MTE1NTE4NTEwNzk2MjA5Nw=='
        
        image_text = self.get_image_text(char_count)
        print(image_text)
        # return image_text

if __name__ == '__main__':
    IM = ImageManager(0)
    IM.set_image(r'utils\todecode.PNG')
    # text = 'please work ? like actually bro'
    # IM.encode_image(text, 'DEFAULT', False, True)
    # IM.image.save('alphas.png', format='PNG')
    
    IM.decode_image()
    # print(IM.get_ppercent_used(), r'% of the image used.')
    # print(IM.GLOBAL_INDEX_IMAGE)
    # print('width: ', IM.WIDTH)
    # print('heigth: ', IM.HEIGHT)
    # print('count: ', IM.PIXEL_COUNT)
