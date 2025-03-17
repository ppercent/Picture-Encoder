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
        print(f'[+] Encoded at: {self.GLOBAL_INDEX_IMAGE} RGB values: {current_pixel} | INDEX_RGB: ', self.GLOBAL_INDEX_RGB, ' INDEX_IMAGE: ', self.GLOBAL_INDEX_IMAGE)

        # update GLOBAL_INDEX_RGB & GLOBAL_INDEX_IMAGE
        if self.GLOBAL_INDEX_RGB == 2:
            new_width = (self.GLOBAL_INDEX_IMAGE[0] + 1) % self.WIDTH
            new_heigth = self.GLOBAL_INDEX_IMAGE[1]
            if new_width == 0:
                new_heigth += 1
            
            # update global variable
            self.GLOBAL_INDEX_IMAGE = (new_width, new_heigth)
        self.GLOBAL_INDEX_RGB = (self.GLOBAL_INDEX_RGB + 1) % 3

    def encode_bits(self, bits):
        print(f'\n[+] Started encoding {len(bits)} bits -> {bits}')
        for bit in bits:
            self.encode_bit(bit)

    def encode_watermark(self, type):
        if type == 'DEFAULT':
            self.encode_bits(self.WATERMARK_KEY_DEFAULT)
        elif type == 'ENCODE':
            self.encode_bits(self.WATERMARK_KEY_ENCODE)
        elif type == 'ENCODE_AND_HIDE':
            self.encode_bits(self.WATERMARK_KEY_ENCODE_AND_HIDE)
        else:
            print('... dont be stupid')

    def encode_text(self, text):
        for char in text:
            bytes, byte_len_indicator = self.get_binary_form(char)
            self.encode_bits(byte_len_indicator)
            self.encode_bits(bytes)

    def encode_image(self, text, type):
        # encode the watermark
        self.encode_watermark(type)

        # encode the text
        self.encode_text(text)

if __name__ == '__main__':
    IM = ImageManager('test.jpg', 0)
    text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur blandit, risus nec gravida tempor, tellus ipsum imperdiet quam, in facilisis justo enim vitae diam. In nec augue erat. Curabitur lorem ante, imperdiet id eros in, consequat mollis leo. Phasellus molestie quam at quam laoreet, et iaculis dui tristique. Fusce ultricies bibendum ante, eleifend aliquet leo pellentesque vitae. Etiam ut pretium velit. Integer id nisi convallis, ornare libero quis, tincidunt magna. Phasellus a diam fermentum, vehicula nulla vitae, tincidunt est. Proin bibendum auctor malesuada. Vivamus sagittis auctor felis ut posuere. Cras vulputate at mauris in vehicula. Pellentesque dignissim, arcu eu egestas consequat, tortor urna bibendum massa, at gravida est lorem sed nibh. Ut fringilla ligula vel odio molestie bibendum. Aliquam ullamcorper velit nec urna congue, eu imperdiet tortor aliquet. Ut eu risus risus.

Donec pretium tellus in mattis ullamcorper. Vivamus id urna et lectus mattis viverra eu in ipsum. Nam malesuada ligula pretium leo feugiat, eu fermentum orci faucibus. In facilisis tempus finibus. Donec malesuada, ligula a ultrices ultrices, odio erat vulputate arcu, a mattis mauris ante feugiat diam. Nulla sed tincidunt sem. Proin ultricies ligula at velit tincidunt, vitae porttitor tortor egestas. Fusce eu scelerisque lorem. In at est quis nulla tempus rhoncus. Vestibulum nec sollicitudin mi.

Praesent posuere dapibus eros in varius. Curabitur pharetra mauris auctor libero egestas, in vestibulum metus accumsan. Fusce fringilla aliquam erat, sit amet tempor lacus viverra sed. Proin cursus congue elit et ultricies. Cras eget massa nec urna aliquet fringilla. Aenean hendrerit est ut pharetra iaculis. Sed et velit sed metus feugiat aliquet. Nullam sed egestas libero. Donec tempor efficitur nulla sit amet congue. Duis ut nibh euismod elit gravida venenatis eget et ante. Mauris eget porttitor elit. Pellentesque sollicitudin diam pellentesque neque congue, ac viverra libero cursus.

Mauris at ullamcorper leo. Vivamus at hendrerit lectus, facilisis venenatis ligula. Suspendisse ac congue tortor, consequat pharetra orci. Proin a nisi ut turpis hendrerit sagittis imperdiet vulputate lectus. Morbi et massa eget massa sollicitudin posuere ac non arcu. Aenean rutrum dui in neque ultricies eleifend. Mauris ultricies rhoncus lacus in commodo. Donec scelerisque felis ex, ac varius mi pretium ut. Duis blandit ultricies volutpat. Quisque aliquet sagittis turpis.

Nullam ut nisl interdum, facilisis turpis at, eleifend sapien. Integer sed auctor odio. Phasellus semper leo et bibendum auctor. Morbi eu mauris non neque cursus commodo. Aliquam erat volutpat. In nulla tellus, vestibulum nec magna sed, luctus hendrerit lectus. Aliquam vitae metus lectus. Quisque id est vel purus molestie pharetra. Sed consectetur lobortis justo, blandit bibendum libero vehicula eu. Duis pulvinar posuere quam, ac accumsan quam tincidunt in. Cras a tortor sed ipsum tempus scelerisque eget in nisi. Curabitur sodales sem id pharetra malesuada. Aenean aliquam massa tortor, et gravida massa aliquet a. Aliquam eleifend ullamcorper vehicula. Nunc rhoncus et lectus et congue.

Aliquam posuere tincidunt blandit. Donec tempor mattis arcu, eu vehicula libero mollis id. Morbi vel neque at arcu pellentesque mollis quis et lorem. Fusce purus est, vulputate at nulla in, posuere interdum massa. Sed eu sem vitae tortor egestas egestas. Aenean nec dui vel orci commodo aliquet nec vel quam. Vestibulum ultrices, nisi eget tincidunt commodo, diam tellus tristique mi, laoreet vestibulum sem turpis non enim. Sed scelerisque elit lacus, in aliquet nisi ultricies in. Phasellus ut semper ex. Mauris eleifend, dui vitae lacinia scelerisque, nulla massa egestas sapien, eu euismod metus nisi nec urna. Vivamus eget justo a tortor elementum placerat. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Phasellus varius, tellus at sollicitudin porta, nunc magna convallis orci, vel semper nibh arcu quis est. Fusce iaculis pellentesque fringilla.

Mauris dignissim risus metus, ac feugiat quam finibus vel. Phasellus quis imperdiet arcu, in consequat purus. In accumsan interdum quam sit amet lobortis. Cras purus dolor, ornare non accumsan id, sodales non lectus. Integer egestas quam tincidunt mauris ornare, sed varius velit sagittis. Pellentesque lacinia ante eget lorem eleifend gravida. Nam orci nunc, pretium sed tristique non, porttitor quis lorem. Integer ut massa fermentum, hendrerit ante at, porttitor erat. Fusce porta lacinia elit vitae consectetur. Mauris metus lorem, convallis vitae arcu nec, rhoncus placerat velit. Vestibulum in interdum nunc.

Nullam auctor sit amet quam eu efficitur. Quisque non felis eget mauris tincidunt eleifend eu quis diam. Vestibulum dapibus est eget nisl fermentum, quis placerat lorem sodales. Phasellus efficitur lorem quis purus auctor cursus. Etiam vitae risus id sem ultrices posuere eu sit amet magna. Vivamus condimentum, mauris ut ullamcorper elementum, nisl massa interdum nisi, non gravida metus purus eu est. Donec condimentum vestibulum leo, nec vulputate ligula sodales vel. Nulla bibendum quam vel nisl faucibus, vel maximus lacus consequat. Curabitur ornare nisl aliquet orci iaculis condimentum. Curabitur fringilla ornare sodales.

Donec in tristique enim, sit amet malesuada metus. Phasellus vestibulum imperdiet justo, at semper dui interdum at. Nam volutpat tellus et mauris facilisis, dictum vestibulum orci sodales. Vivamus consequat non erat eu tempus. Curabitur luctus lorem sed ultricies pharetra. Mauris rhoncus turpis a risus ultricies, eu rhoncus est convallis. Pellentesque eleifend magna ut rhoncus eleifend. Quisque hendrerit ipsum non euismod bibendum. Integer ullamcorper aliquet diam, et lobortis justo consequat eget.

Aenean rutrum, augue ut hendrerit condimentum, ex magna placerat est, nec finibus leo purus a lectus. Nullam laoreet lorem arcu, sed finibus mauris gravida quis. Vestibulum porta nisl a leo pretium sodales. In fringilla auctor risus eu ornare. In a condimentum magna, at volutpat nunc. In sed dapibus eros. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Sed nec massa nunc. Fusce ultricies condimentum fringilla. Nam non diam urna. Nulla imperdiet augue non justo sagittis mollis. Vivamus vulputate est at varius malesuada.

Maecenas iaculis sollicitudin lectus ut aliquam. Aliquam sit amet convallis ante. Pellentesque et dolor pretium, condimentum leo nec, placerat erat. Curabitur placerat congue risus in auctor. Sed aliquam dui eget eros porttitor, ac ultrices risus egestas. Morbi mi purus, tristique commodo mattis non, egestas vel nulla. Donec ullamcorper dolor augue, ut convallis leo mollis vel. Aliquam erat volutpat.

Ut auctor vitae odio nec sollicitudin. Aliquam in laoreet tellus. Morbi et elementum turpis. Nunc tincidunt maximus ultrices. Nulla placerat massa non finibus ultrices. Aliquam nec diam ut est auctor egestas. Praesent tellus mauris, varius at lorem sed, sollicitudin cursus lectus. Etiam non sapien auctor, tristique magna vitae, mollis odio. In maximus posuere urna, vel blandit elit consequat ac. Nullam pretium facilisis nulla, ut blandit turpis iaculis non. Ut ac massa ante. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Quisque sed sollicitudin lorem, rhoncus interdum elit. Cras eget arcu in est consectetur tincidunt ut non velit. In tellus nulla, varius quis interdum non, fringilla sed leo. Etiam porttitor eget nulla et tincidunt.

Fusce pharetra, nulla nec interdum congue, lorem dui iaculis turpis, nec facilisis nibh massa in lorem. Praesent ultrices faucibus quam eget facilisis. Donec neque magna, aliquet non eros nec, consequat varius enim. Vivamus sagittis urna at magna pharetra vulputate. Praesent sed dolor et ligula varius ultricies. In nisi metus, sagittis sed felis ac, scelerisque vehicula ipsum. Nullam tincidunt facilisis augue ac blandit. Cras vitae condimentum velit. Donec bibendum, sapien quis bibendum vulputate, arcu leo suscipit mauris, non tincidunt est eros id nibh.

Maecenas posuere lectus nunc, in gravida tortor rutrum sit amet. Proin tellus nisl, porta vestibulum consequat ut, placerat a odio. Nulla sit amet sem ut est malesuada vestibulum. Phasellus bibendum imperdiet blandit. Nulla varius efficitur faucibus. Nam vitae consectetur mauris. Suspendisse fermentum, lacus nec fermentum dictum, mi lorem faucibus lacus, eu congue dolor felis non erat. Sed erat ex, tempor at nulla nec, condimentum aliquam libero. Morbi quis sem pellentesque nisl hendrerit ultricies. Pellentesque est dolor, laoreet vel venenatis eu, venenatis et metus. Proin dapibus dui et fringilla condimentum. Vivamus efficitur fringilla velit et consectetur.

Integer commodo fermentum neque, sit amet efficitur nulla scelerisque porta. Phasellus condimentum quis eros in faucibus. Vivamus ut enim sit amet sapien volutpat posuere. Nullam sollicitudin, urna sagittis tristique rhoncus, sem neque eleifend eros, sit amet luctus metus libero quis sem. Aliquam nec elit dapibus, finibus enim tempus, blandit arcu. Nullam varius facilisis dolor, sit amet imperdiet nunc dignissim et. Proin mollis sem at imperdiet finibus. Donec rutrum lacinia dolor ut dictum. Phasellus nec malesuada nisi. Phasellus ac venenatis dui. Ut vel placerat orci, et tempus urna. Morbi sit amet posuere diam, vel faucibus libero. Curabitur venenatis eros sollicitudin ligula vestibulum, vel pretium sem vestibulum. Quisque id venenatis velit, nec dignissim lectus. Sed lacus ligula, fermentum eu nisi at, eleifend suscipit nisl.

Quisque consectetur efficitur sapien, eu pellentesque metus ultricies quis. Pellentesque tempus metus id sem interdum venenatis. Morbi lacus leo, sodales non metus ac, scelerisque suscipit lorem. Suspendisse suscipit risus in libero feugiat aliquet sit amet nec massa. Proin lectus magna, sollicitudin in massa in, aliquet imperdiet nunc. Proin vel nunc sed eros mattis laoreet at a erat. Sed pharetra purus ullamcorper, rutrum tellus et, pulvinar purus. Phasellus eu tempor dui, non rutrum dolor.

Mauris id augue vel mi consectetur placerat id ut felis. Duis sed finibus augue, nec viverra mauris. Vivamus aliquet justo ut rutrum placerat. Curabitur ac orci porta, malesuada nulla eget, laoreet mi. Donec dignissim nisi ligula, et tempor turpis aliquet in. Vivamus non commodo turpis. Curabitur tincidunt, elit at ultricies aliquet, mauris diam vestibulum orci, eget blandit augue turpis nec velit. Donec suscipit id turpis at varius. Vivamus ex mauris, pellentesque id erat sit amet, tempus euismod nunc. Praesent ut dolor a enim interdum convallis. Sed a pulvinar mauris. Ut blandit justo quam, vitae feugiat nulla pretium id.

Donec faucibus molestie mattis. Maecenas quis dui nisi. Nullam auctor orci sed lorem iaculis sagittis. Sed mollis commodo mauris consectetur tempor. Vestibulum facilisis feugiat consectetur. Quisque accumsan dolor elit. Nam commodo, purus porttitor elementum tristique, massa sem gravida quam, eu elementum orci lectus tincidunt elit. Sed commodo ullamcorper dui, et aliquam libero interdum id. Curabitur quis quam bibendum, tincidunt libero vel, placerat arcu. Morbi commodo in risus eget accumsan. Interdum et malesuada fames ac ante ipsum primis in faucibus. Quisque facilisis vulputate pharetra. Quisque vitae nibh purus. Vestibulum non erat magna. Duis commodo quis augue nec elementum.

In lacinia sapien cursus consectetur tempus. Nulla efficitur purus vel pellentesque tristique. Curabitur faucibus volutpat tincidunt. Fusce ultrices purus eget volutpat pretium. Suspendisse quis odio fringilla, interdum dui sed, vestibulum est. Nulla lobortis turpis facilisis risus aliquet placerat. Pellentesque gravida ex vitae neque bibendum, vel egestas mi porttitor. Maecenas risus tortor, cursus non massa in, suscipit ornare ligula. Quisque id ultrices ligula, eu semper neque. In luctus tristique auctor. Phasellus sit amet ipsum ut ligula eleifend lacinia non sed augue. Vivamus nisi ante, feugiat ultricies semper eu, commodo posuere eros. Etiam rutrum odio a eros vulputate posuere. Suspendisse a sodales erat. Sed vehicula, mi a ultrices consectetur, magna ipsum elementum velit, a tempor neque mi ut dolor. Ut tempus ultrices enim, ac bibendum tellus imperdiet non.

Donec convallis libero velit. Integer auctor vel neque at lacinia. Sed efficitur lacus eu nisi volutpat pellentesque. Aenean sit amet neque condimentum, ornare justo et, mattis sem. Sed commodo ante turpis, eget tempor massa dignissim nec. Integer quis elit in magna eleifend faucibus. Nunc a lectus et ante euismod pretium. Sed ullamcorper dui tortor, sit amet hendrerit ante venenatis et. Maecenas eu consectetur justo. Curabitur non suscipit eros. Nulla quam lacus, cursus id nisi id, iaculis porta mi. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec bibendum augue sit amet nulla feugiat venenatis. Nam ornare elit eu sapien fringilla, quis porttitor mauris fringilla.

Praesent nisl est, maximus sit amet augue ut, gravida gravida nibh. Sed risus neque, finibus non lacus iaculis, sodales imperdiet dolor. Proin aliquam mi velit, blandit pellentesque est dictum sit amet. Nam faucibus sem at nisi sagittis, in pretium justo porttitor. Aenean ultrices elementum tortor sed varius. Quisque accumsan, enim id gravida commodo, tellus felis sagittis est, non scelerisque tellus dui nec felis. Quisque lacinia mi pellentesque pretium tempor. Donec auctor quam sed nisl pretium malesuada.

Vivamus posuere accumsan nibh vel finibus. Vestibulum in turpis molestie, consectetur dui ut, mattis nisi. Sed in fermentum mauris. Donec aliquam sapien vehicula, cursus arcu mattis, dignissim dolor. Quisque pulvinar lacus quis mi suscipit, sit amet tincidunt eros pharetra. Morbi odio sapien, elementum sed ipsum ac, vestibulum aliquam ipsum. Pellentesque nibh lectus, consectetur vel felis ac, ultricies pellentesque enim. Nulla ac viverra ante, id cursus libero. Proin fermentum odio a quam malesuada, vitae posuere augue dignissim. Vestibulum id malesuada massa. Donec pulvinar ultrices tortor eu laoreet. Suspendisse potenti.

Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Pellentesque tincidunt tincidunt velit. Phasellus a odio et magna aliquet volutpat sed sit amet dui. Etiam congue accumsan elit, sed congue quam interdum eget. Maecenas commodo massa non tincidunt ullamcorper. Sed id tempus mauris. Donec elementum dolor et arcu fermentum, sit amet volutpat est molestie. Nunc condimentum ultricies quam, eget condimentum sem sodales venenatis. Aenean interdum mauris sed ligula blandit iaculis. Etiam pulvinar, diam et sagittis maximus, odio est pharetra ante, in pharetra libero metus non metus.

Nulla facilisi. Duis eget blandit augue, ac scelerisque nibh. Nunc eget est nec orci varius ultricies. Integer molestie ac ligula vitae pharetra. Nulla finibus sodales commodo. Nulla fringilla laoreet neque, venenatis consequat massa eleifend ac. Proin vitae mi eget enim lacinia tincidunt ut et ex. Proin auctor metus metus, nec convallis felis aliquam id. Pellentesque purus libero, efficitur sit amet rutrum et, eleifend id diam. Aenean varius nisl vel placerat rhoncus.

Ut laoreet vitae diam sed feugiat. In accumsan convallis orci id auctor. Integer vitae mi rutrum, aliquet urna eget, porta justo. Mauris eleifend tempus ex. Donec vulputate ac diam vel porta. Nulla et commodo lacus. Cras varius ultricies mi gravida tristique. Maecenas et fermentum turpis. In consectetur fermentum semper. Ut justo orci, venenatis nec est non, dapibus cursus diam. Pellentesque aliquam, tortor eu sodales dignissim, eros nunc tempus ipsum, in dictum quam libero sit amet magna. Vestibulum vel sapien dolor.

Quisque ullamcorper urna id lorem fermentum volutpat. Pellentesque congue, purus sit amet malesuada viverra, nunc libero lacinia purus, sed faucibus sapien magna quis purus. Maecenas non egestas magna, ut tincidunt nisl. Fusce vestibulum tellus ullamcorper tortor commodo bibendum ac eget leo. Aliquam a sollicitudin orci. Morbi viverra posuere pulvinar. Donec commodo dolor at felis pulvinar lacinia vitae quis tellus. Suspendisse lacinia ante vel augue pulvinar sollicitudin. Nam eu lacus semper turpis lobortis mollis. Nullam id risus tempus, ullamcorper nisl non, bibendum lacus. Aenean nec est mauris. Aenean tempor tincidunt nunc, eu fermentum tellus fermentum at. Praesent eget turpis odio. Fusce sed consectetur massa, eu vestibulum justo. Nulla faucibus venenatis leo, ut consequat odio facilisis sit amet. Donec ullamcorper egestas est, pretium tempor arcu pretium in.

Nullam sodales ultricies dui, eget mollis purus pulvinar nec. Cras vitae est et felis euismod pretium. Integer et dolor id metus euismod auctor. Vivamus sed nibh purus. Nulla facilisi. Integer maximus sem sem, porta congue sem bibendum at. In ac quam non tellus blandit tincidunt. Sed vitae tempor nunc. Sed gravida mollis ligula sed mollis. Curabitur sed libero id erat pulvinar cursus at vitae eros. Pellentesque porttitor augue egestas, aliquet orci ac, commodo tortor. Vivamus id malesuada mi.

In iaculis velit nunc, id blandit risus lobortis eu. Mauris at tempor erat, vitae dapibus mi. Praesent ut vulputate sem, ac luctus erat. Sed malesuada porta ornare. Suspendisse potenti. Phasellus at mauris posuere, finibus ante eu, tincidunt magna. Ut vulputate porta eleifend. Curabitur condimentum dolor ac quam vestibulum lacinia. Nullam rhoncus tincidunt vestibulum. Pellentesque non sapien in sapien faucibus sollicitudin quis a felis. In facilisis dignissim porta. Donec fringilla commodo augue, a suscipit eros mollis at. Quisque sapien nulla, aliquam et est vitae, imperdiet ullamcorper nisl. Duis sed facilisis ligula, et mollis lacus. Donec rutrum odio eu elit rhoncus vestibulum.

Mauris consequat erat et urna commodo auctor. Donec tempor auctor ipsum non congue. Praesent dapibus faucibus laoreet. Morbi sem ipsum, blandit id interdum ac, iaculis nec tortor. Nullam quis purus ut erat sollicitudin varius. Nullam tortor velit, tincidunt eu ultricies sed, sodales id odio. Ut ut hendrerit velit, ut blandit mauris. Cras volutpat semper tortor, sed sollicitudin tellus iaculis quis. Cras venenatis sed diam quis lobortis. Sed commodo velit vitae felis faucibus cursus. Donec bibendum in magna sit amet porta. Integer et laoreet nisl. Maecenas pharetra vel mi at fermentum. Aliquam aliquet, massa nec convallis bibendum, nisi purus feugiat odio, sit amet eleifend velit nibh sed urna. Nullam rhoncus porttitor nisi, blandit feugiat enim congue eu.

Suspendisse rhoncus convallis arcu, ut hendrerit urna vehicula sed. Suspendisse dui nisi, condimentum eu porta quis, consectetur sit amet eros. Donec pretium, ligula ac congue aliquam, felis lacus sodales arcu, eget viverra nulla odio id nisl. Maecenas non elit quis libero consectetur ullamcorper vitae ac est. Maecenas ullamcorper magna eu ligula tempus, quis semper magna rutrum. Nulla eleifend tincidunt massa, et iaculis mi auctor vitae. Ut vehicula semper libero, suscipit volutpat nibh molestie a. Sed dui sem, posuere eu posuere id, consectetur quis quam.

Cras lobortis at ipsum sit amet iaculis. Proin tincidunt fermentum laoreet. Nam feugiat, nunc ut malesuada vehicula, orci dui blandit diam, a venenatis ante ex vitae erat. Nunc at sapien eget arcu consectetur ornare. Suspendisse potenti. Donec bibendum enim lacus, at gravida tellus laoreet eget. Nam at maximus ex, et molestie ligula. Suspendisse euismod, tellus sed tempus pulvinar, nunc arcu faucibus felis, id mattis nulla sapien vitae lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; In turpis justo, faucibus in velit ut, convallis gravida mi. Vivamus rhoncus pellentesque magna, non tristique nunc tempus sit amet. Aenean ut dictum dolor, id varius enim. Proin blandit quam et convallis ornare. Phasellus viverra luctus nisl nec congue. Mauris condimentum eget sem et fermentum. Phasellus ut tortor quis eros posuere sagittis.

Ut lorem nibh, sollicitudin eget nibh ac, ullamcorper hendrerit enim. Nulla at nulla non ipsum hendrerit faucibus non sed neque. Integer auctor libero ut est lacinia, bibendum facilisis turpis sagittis. In dui libero, malesuada in accumsan et, sodales ut metus. Sed ultricies consequat enim, ut gravida ipsum."""
    IM.encode_image(text, 'DEFAULT')
    IM.image.show()
    IM.image.save('edited.png', format='PNG')
