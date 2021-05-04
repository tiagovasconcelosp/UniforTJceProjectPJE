####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
### Laboratório M02
### Cientista-Chefe: Prof. Carlos Caminha
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

from PIL import Image
from io import BytesIO
from datetime import datetime


class Print:

    def __init__(self, firefox, caminhoImages):
        self.Print(firefox, caminhoImages)

    def Print(self, firefox, caminhoImages):

        image = firefox.get_screenshot_as_png()
        im = Image.open(BytesIO(image))
        im.save(caminhoImages + datetime.now().strftime("%d_%m_%Y__%H_%M_%S") + '.png')