
import PIL
from PIL import Image
import math


class ImageGenerator:
    def __init__(self):
        self.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
        self.GLOBAL_INDEX_RGB = 0
        self.image = Image.new(mode="RGB", size=(10,10))
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

    def encode_text(self, text,is_watermark): #DE LA MERDE POURQUOI CA ENCODE DES 0
        dec_text=''

        if not is_watermark:
            for char in text:
                dec_text+=self.dec_string(ord(char))
        else:
            dec_text=self.dec_string(text)
        
        text_index=0
        pixels=[]
        current_pixel=[0,0,0]
        
        while text_index < len(dec_text):
            
            next_3_digits=int(dec_text[text_index:text_index+3])
            next_2_digits=int(dec_text[text_index:text_index+2])
            
            if next_3_digits<=255:
                num=next_3_digits
                text_index += 3
            else:
                num=next_2_digits
                text_index += 2
            
            self.update_globals()
            current_pixel[self.GLOBAL_INDEX_RGB]=num
            
            if current_pixel[2]!=0:
                pixels.append(current_pixel)
                current_pixel=[0,0,0]
        pixels.append(current_pixel)
        
        
        return pixels      

    def encode_watermark(self, text, type):
        #watermark_charcount = str(len(text))
        watermark_charcount = str(len(text))   # ERROR IF BIGGER THAN 16777216
        
        if type == 'DEFAULT':
            watermark=self.WATERMARK_KEY_DEFAULT+watermark_charcount
            return self.encode_text(watermark,True)
            

        elif type == 'ENCODE':
            watermark=self.WATERMARK_KEY_ENCODE+watermark_charcount
            return self.encode_text(watermark,True) # TODO it might fuck up with RSA here, changes are required
        else:
            pass
    
    def create_image(self,pixels):
        size=math.ceil(math.sqrt(len(pixels)))
        self.image = Image.new(mode="RGB", size=(size,size))
        for pixel in pixels:
            self.image.putpixel(self.GLOBAL_INDEX_IMAGE, tuple(pixel))
            self.update_globals()
        
    
    def generate_image(self,text,type):
        
        self.set_size(text)
        
        # encode the watermark
        watermark_pixel_count=self.encode_watermark(text, type)
        
        # encode the text and save the pixel count
        text_pixel_count=self.encode_text(text,False)
        
        pixels=watermark_pixel_count+text_pixel_count
        
        self.create_image(pixels)
        
        print(text_pixel_count+watermark_pixel_count-2) #PROBLEME DE 0
        
        

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
            
            
        char_count=int(watermark[1:])

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
        #print(encoded_bits)
        return image_text


if __name__ == '__main__':
    IM = ImageGenerator()
    text=r'''zinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinczinc'''
    IM.generate_image(text,'DEFAULT')
    IM.image.show()
    IM.GLOBAL_INDEX_IMAGE = (0, 0)   # (width, height)
    IM.GLOBAL_INDEX_RGB = 0
    
    IM.decode()
    #print('decoded: '+IM.decode())
