# ###################################################
# ###################################################
# ## Projeto MPCE - Unifor - Universidade de Fortaleza
# ## Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
# ## Laboratório M02
# ## Cientista-Chefe: Prof. Carlos Caminha
# ## Bolsista Desenvolvedor do Projeto:
# ## Tiago Vasconcelos
# ## Email: tiagovasconcelosp@gmail.com
# ###################################################
# ###################################################

from PIL import Image
from io import BytesIO
from datetime import datetime

import time

class Print:

    def __init__(self, driver, caminhoImages, pdf=False, descricao=''):
        self.caminhoPDF = self.Print(driver, caminhoImages, pdf, descricao)

    def Print(self, driver, caminhoImages, pdf=False, descricao=''):

        # Codigo antigo, posteriormente sera apagado
        #
        # image = driver.get_screenshot_as_png()
        # im = Image.open(BytesIO(image))
        # im.save(caminhoImages + datetime.now().strftime("%d_%m_%Y__%H_%M_%S") + '.png')

        try:
            # Definido o nome do arquivo
            file_name = datetime.now().strftime("%d_%m_%Y__%H_%M_%S")

            output_image_path = caminhoImages + file_name + '.png'
            self.Capture_full_page_screenshot(driver, output_image_path)

            if pdf:
                if descricao != '':
                    output_pdf_path = caminhoImages + 'pdf\\' + file_name + '_print_full_page_' + descricao + '.pdf'
                else:
                    output_pdf_path = caminhoImages + 'pdf\\' + file_name + '_print_full_page.pdf'

                self.Convert_image_to_pdf(output_image_path, output_pdf_path)

                # Retorna nome do arquivo pdf
                return output_pdf_path

            # Retorna o nome do arquivo
            return file_name

        except Exception as e:
            print(repr(e))

    # Captura a dimensao da página
    def Capture_full_page_screenshot(self, driver, output_image_path):

        try:
            # Obtenha a altura total da página
            total_height = int(driver.execute_script(
                "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );"))

            # Configure a altura da janela do navegador para a altura total da página
            # Desativado - pode ser util em algum problema futuro
            # driver.set_window_size(driver.get_window_size()['width'], total_height)

            # Inicialize uma imagem para armazenar a captura de tela completa
            full_page_screenshot = Image.new('RGB', (driver.get_window_size()['width'], total_height))

            # Percorra a página capturando as partes visíveis
            current_height = 0
            while current_height < total_height:
                # Capture a parte visível atual da página
                screenshot = Image.open(BytesIO(driver.get_screenshot_as_png()))

                # Cole a parte capturada na imagem completa
                full_page_screenshot.paste(screenshot, (0, current_height))

                # Role para baixo
                current_height += screenshot.size[1]
                driver.execute_script("window.scrollTo(0, {});".format(current_height))

                # Aguarde um curto período para carregar o conteúdo
                time.sleep(0.5)

            # Salve a imagem completa
            full_page_screenshot.save(output_image_path)

        except Exception as e:
            print(repr(e))

    # Realiza a conversão para PDF
    def Convert_image_to_pdf(self, image_path, output_pdf_path):

        try:
            img = Image.open(image_path)
            img.save(output_pdf_path, "PDF", resolution=100.0)
        except Exception as e:
            print(repr(e))