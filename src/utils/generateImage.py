import PIL
from PIL import Image
import math


class ImageGenerator:
    def __init__(self):
        self.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
        self.GLOBAL_INDEX_RGB = 0
        self.image = Image.new(mode="RGB", size=(5,5))
        self.WIDTH = self.image.size[0]
        self.HEIGHT = self.image.size[1]
        self.PIXEL_COUNT = self.WIDTH * self.HEIGHT
        self.WATERMARK_KEY_DEFAULT = "1"
        self.WATERMARK_KEY_ENCODE = "2"
    def update_globals(self):
        if self.GLOBAL_INDEX_RGB == 2:
            new_width = (self.GLOBAL_INDEX_IMAGE[0] + 1) % self.WIDTH
            new_heigth = self.GLOBAL_INDEX_IMAGE[1]
            if new_width == 0:
                new_heigth += 1
            # update global variable
            self.GLOBAL_INDEX_IMAGE = (new_width, new_heigth)
        self.GLOBAL_INDEX_RGB = (self.GLOBAL_INDEX_RGB + 1) % 3
    
    def get_ppercent_used(self):
        return round(((self.GLOBAL_INDEX_IMAGE[1] - 1) / self.HEIGHT) + (self.GLOBAL_INDEX_IMAGE[0] / (self.PIXEL_COUNT)), 2)

    # -----------------------------------------------------ENCODING------------------------------------------------------------------
        
    def dec_string(self,text): #nums to encoded nums
        res=''
        incrementNum=0 

        listed_dec_char=list(str(text))
        while '0' in listed_dec_char:
            incrementNum+=1
            for digit in range(len(listed_dec_char)):
                listed_dec_char[digit]=str((int(listed_dec_char[digit])+1)%10)
        dec_char = ''.join(listed_dec_char)
        if incrementNum==0:
            incrementNum=9
        res=res+str(len(dec_char))+str(incrementNum)+dec_char
        return res 

    def encode_text(self, text,is_watermark): #BUG
        dec_text=''
        if not is_watermark:
            for char in text:
                dec_text+=self.dec_string(ord(char))
        else:
            dec_text=self.dec_string(text)
        text_index=0
        current_pixel=[0,0,0]
        while text_index < len(dec_text):
            if int(dec_text[text_index:text_index+3])<=255:
                num=int(dec_text[text_index:text_index+3])
                text_index += 3
            else:
                num=int(dec_text[text_index:text_index+2])
                text_index += 2
            self.update_globals()
            current_pixel[self.GLOBAL_INDEX_RGB]=num
            
            
            if current_pixel[2]!=0:
                self.image.putpixel(self.GLOBAL_INDEX_IMAGE, tuple(current_pixel))
                current_pixel=[0,0,0]
        self.update_globals()
        self.image.putpixel(self.GLOBAL_INDEX_IMAGE, tuple(current_pixel))
                

    def encode_watermark(self, text, type):
        #watermark_charcount = str(len(text))
        watermark_charcount = str(len(text))
        if type == 'DEFAULT':
            watermark=self.WATERMARK_KEY_DEFAULT+watermark_charcount
            self.encode_text(watermark,True)

        elif type == 'ENCODE':
            watermark=self.WATERMARK_KEY_ENCODE+watermark_charcount
            self.encode_text(watermark,True) # TODO it might fuck up with RSA here, changes are required
        else:
            pass

    def generate_image(self,text,type):
        # encode the watermark
        self.encode_watermark(text, type)

        # encode the text
        self.encode_text(text,False)

    '''
    # WORK IN PROGRESS           

    def create_image(self,s):
        while s%3!=0:
            s+=1
        size=math.ceil(math.sqrt(s/3))
        self.image = Image.new(mode="RGB", size=(size,size))
        self.WIDTH = self.image.size[0]
        self.HEIGHT = self.image.size[1]
        self.PIXEL_COUNT = self.WIDTH * self.HEIGHT
    '''

    # -----------------------------------------------------DECODING------------------------------------------------------------------

    def get_image_text(self):
        dec_chars=''
        for i in range(self.PIXEL_COUNT*3):
            current_pixel = list(self.image.getpixel(self.GLOBAL_INDEX_IMAGE))
            current_channel = current_pixel[self.GLOBAL_INDEX_RGB]
            dec_chars+=str(current_channel)
            self.update_globals()
            
            
        return dec_chars

        
    def read_character(self, char_decs, decrementNum):
        listed_dec_char=list(char_decs)
        decrementNum=int(decrementNum)
        if decrementNum == 9:
            decrementNum = 0
        
        while decrementNum:
            for digit in range(len(listed_dec_char)):
                listed_dec_char[digit]=str((int(listed_dec_char[digit])-1)%10)
            decrementNum-=1
        dec_char = ''.join(listed_dec_char)
        return dec_char
        


    def decode(self):
        encoded_bits=self.get_image_text()
        watermark=self.read_character(encoded_bits[3:3+int(encoded_bits[1])],encoded_bits[2])
        if watermark[0] == self.WATERMARK_KEY_DEFAULT:
            type='DEFAULT'
        elif watermark[0] == self.WATERMARK_KEY_ENCODE:
            type='ENCODE'
        char_count=int(watermark[1:9])

        image_text = ''
        current_char_count=4+int(encoded_bits[1])
        while char_count:
            
            
            char_size=int(encoded_bits[current_char_count])
            char_zeroes=int(encoded_bits[current_char_count+1])
            char_string=encoded_bits[current_char_count+2:current_char_count+char_size+2]
            current_character=self.read_character(char_string,char_zeroes)
            image_text+=chr(int(current_character))
            current_char_count+=len(char_string)+2
            char_count-=1
        return image_text


if __name__ == '__main__':
    IM = ImageGenerator()
    text = r"""gaby douaihy est le meilleur"""
    IM.generate_image(text,'DEFAULT')
    IM.image.show()
    IM.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
    IM.GLOBAL_INDEX_RGB = 0
    
    print('decoded: '+IM.decode())
