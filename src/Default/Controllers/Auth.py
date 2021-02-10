####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Funda��o Cearense de Apoio ao Desenvolvimento Cient�fico e Tecnol�gico (Funcap)
### Laborat�rio M02
### Cientista-Chefe: Prof. Carlos Caminha
### Co-coordenador: Daniel Sullivan
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

import sys

from selenium.webdriver.common.by import By

from src.Default.Controllers.Print import Print


class Auth:

    def __init__(self, firefox, logging, caminhoImages):
        self.Login(firefox, logging, caminhoImages)

    def Login(self, firefox, logging, caminhoImages):

        try:
            # Aumenta o tempo de time out para 120s
            # Linhas comentadas para interroper preenchimento do login e senha

            firefox.set_page_load_timeout(120)

            firefox.find_element(By.ID, "username").send_keys('61446130304')
            firefox.find_element(By.ID, "password").send_keys('12345')

            logging.info("Realizando autenticacao.")
        except:

            image = Print(firefox, caminhoImages)

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            # firefox.quit()
            sys.exit(0)
