####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
### Laboratório M02
### Cientista-Chefe: Prof. Carlos Caminha
### Co-coordenador: Daniel Sullivan
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

import sys

from selenium.webdriver.common.by import By
from src.Default.Control.Print import Print


class Auth:

    # Autenticacao por login
    # #########################################################
    # def __init__(self, firefox, logging, caminhoImages, login, senha):
    #     self.Login(firefox, logging, caminhoImages, login, senha)

    def __init__(self, firefox, logging, caminhoImages):
        self.Login(firefox, logging, caminhoImages)

    # Autenticacao por login
    # #########################################################
    # def Login(self, firefox, logging, caminhoImages, login, senha):
    def Login(self, firefox, logging, caminhoImages):

        try:
            # Aumenta o tempo de time out para 120s
            # Linhas comentadas para interroper preenchimento do login e senha

            firefox.set_page_load_timeout(120)

            # Autenticacao por login
            # #########################################################
            # login = firefox.find_element(By.ID, "username").send_keys(login)
            # firefox.find_element(By.ID, "password").send_keys(senha)
            # firefox.find_element(By.ID, "btnEntrar").click()
            # #########################################################

            firefox.find_element(By.ID, "username").send_keys('60013884310')
            firefox.find_element(By.ID, "password").send_keys('12345')

            #time.sleep(4)

            logging.info("Realizando autenticacao.")
        except:

            image = Print(firefox, caminhoImages)

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            # firefox.quit()
            sys.exit(0)
