from PIL import Image


class ImageManager:
    def __init__(self, image_path, GUI):
        self.image = Image.open(image_path)
        self.image.convert('RGB')
        self.GUI = GUI
        self.WATERMARK_KEY_DEFAULT = "001101110000110101011101"
        self.WATERMARK_KEY_ENCODE = "100100001000101101011000"
        self.WATERMARK_KEY_ENCODE_AND_HIDE = "100100010010111001110001"
        self.WIDTH = self.image.size[0]
        self.HEIGHT = self.image.size[1]
        self.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
        self.GLOBAL_INDEX_RGB = 0
        self.PIXEL_COUNT = self.WIDTH * self.HEIGHT
        self.print_image_loaded()

    def print_image_loaded(self):
        # change this to GUI.debug later
        print('[+] ... (todo later) image.png loaded!!')
        print('   ➤  image size: ', self.WIDTH, 'x', self.HEIGHT)
        print('   ➤  pixel count: ', self.PIXEL_COUNT)
        print('   ➤  writable size: ', (self.PIXEL_COUNT * 3) / 8 / 1000, 'kb of text.')

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
        if self.GLOBAL_INDEX_RGB == 2:
            new_width = (self.GLOBAL_INDEX_IMAGE[0] + 1) % self.WIDTH
            new_heigth = self.GLOBAL_INDEX_IMAGE[1]
            if new_width == 0:
                new_heigth += 1
            
            # update global variable
            self.GLOBAL_INDEX_IMAGE = (new_width, new_heigth)
        self.GLOBAL_INDEX_RGB = (self.GLOBAL_INDEX_RGB + 1) % 3

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
        #print(f'\n[+] Started encoding {len(bits)} bits -> {bits}')
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

    def encode_watermark(self, text, type):
        watermark_charcount = format(len(text), '024b')
        if type == 'DEFAULT':
            self.encode_bits(self.WATERMARK_KEY_DEFAULT)
            self.encode_bit(watermark_charcount)
        elif type == 'ENCODE':
            self.encode_bits(self.WATERMARK_KEY_ENCODE)
            self.encode_bit(watermark_charcount)    # TODO it might fuck up with RSA here, changes are required
        elif type == 'ENCODE_AND_HIDE':
            self.encode_bits(self.WATERMARK_KEY_ENCODE_AND_HIDE)
            self.encode_bit(watermark_charcount)
        else:
            print('... dont be stupid')

    def encode_text(self, text):
        for char in text:
            bytes, byte_len_indicator = self.get_binary_form(char)
            self.encode_bits(byte_len_indicator)
            self.encode_bits(bytes)

    def encode_image(self, text, type):
        # encode the watermark
        self.encode_watermark(text, type)

        # encode the text
        self.encode_text(text)
    
    def get_type(self):
        watermark = self.read_bits(24)
        if watermark == self.WATERMARK_KEY_DEFAULT:
            return 'DEFAULT'
        elif watermark == self.WATERMARK_KEY_DEFAULT:
            return 'ENCODE'
        elif watermark == self.WATERMARK_KEY_DEFAULT:
            return 'ENCODE_AND_HIDE'
        else:
            return 'INVALID'
    
    def decode_image(self):
        # get type and char_count using the watermark
        type = self.get_type()
        char_count = int(self.read_bits(24), 2)
        
        # 

if __name__ == '__main__':
    IM = ImageManager('edited.png', 0)
    IM.decode_image()
