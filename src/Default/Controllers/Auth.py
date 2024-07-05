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
import os
import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from .Metodos import Metodos
from src.Default.Controllers.Print import Print

class Auth:

    def __init__(self):
        # self.Login(firefox, logging, caminhoImages)
        pass

    def Login(self, driver, logging, dataform, url):
        metodos = Metodos(url)

        try:
            titulo_pagina = 'Bem vindo ao PJe · Processo Judicial Eletrônico'

            if 'pje2' in url:
                # titulo_pagina = 'Bem vindo ao PJe · [CÃPIA DE PRODUÃÃO - 1G] Processo Judicial EletrÃ´nico'
                titulo_pagina = driver.title

            if driver.title == titulo_pagina:
                frames = metodos.identifica_frames(driver)
                frame = metodos.verifica_presenca_no_frame(driver, frames, '//*[@id="username"]')
                if frame is not None:
                    driver.switch_to.frame(frame)
                username = metodos.get_element_check_page(driver, '//*[@id="username"]', titulo_pagina)
                if username is not None:
                    password = metodos.get_element(driver, '//*[@id="password"]')
                    login = metodos.buscar_componente_por_value(driver, 'Entrar')

                    username.send_keys(dataform["login"])
                    password.send_keys(dataform["pass"])
                    
                    login.click()
                    logging.info('Procedimento de Autenticação')

                driver.switch_to.default_content()
            logging.info("Realizando autenticacao.")

        except Exception as e:

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()
            os._exit(0)
            sys.exit(0)

    def LoginPje2g(self, driver, logging, dataform, url):

        try:
            # Linhas comentadas para interroper preenchimento do login e senha
            driver.implicitly_wait(15)
            driver.set_page_load_timeout(420)

            # firefox.find_element(By.ID, "username").send_keys('60013884310')
            # firefox.find_element(By.ID, "password").send_keys('12345')
            logging.info("Realizando autenticacao.")
            print("Realizando autenticacao.")


        except Exception as e:

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()
            os._exit(0)
            sys.exit(0)

    def LoginSeeu(self, driver, logging, dataform, url):
        metodos = Metodos(url)
        try:
            titulo_pagina = 'SEEU - Sistema Eletrônico de Execução Unificado'

            # iframe = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, 'mainFrame')))

            # driver.switch_to.frame(iframe)

            username = metodos.get_element_check_page(driver, '//*[@id="login"]', titulo_pagina)
            if username is not None:
                password = metodos.get_element(driver, '//*[@id="senha"]')
                login = metodos.get_element(driver, '//*[@id="btEntrar"]')

                username.send_keys(dataform["login"])
                password.send_keys(dataform["pass"])

                login.click()
                logging.info('Procedimento de Autenticação')

        except Exception as e:

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()
            os._exit(0)
            sys.exit(0)

class AuthV2:

    def __init__(self):
        # self.Login(driver, logging, caminhoImages)
        pass

    def Login(self, driver, logging, dataform, url):
        metodos = Metodos(url)
        try:
            titulo_pagina = 'Entrar em PDPJ - Plataforma Digital do Poder Judiciário'
            if "sisbajudh.cnj" in url:
                titulo_pagina = 'Login Sisbajud'
            if driver.title == titulo_pagina:
                username = metodos.get_element_check_page(driver, '//*[@id="username"]', titulo_pagina)
                if username is not None:
                    password = metodos.get_element(driver, '//*[@id="password"]')
                    login = metodos.buscar_componente_por_value(driver, 'Entrar')

                    username.send_keys(dataform["login"])
                    password.send_keys(dataform["pass"]) 
                    login.click()
                    # logging.info('Procedimento de Autenticação')


            # logging.info("Realizando autenticacao.")

        except Exception as e:

            # logging.exception('Falha realizar autenticacao.')
            # logging.info('Finalizando o robo.')
            # logging.info(repr(e))
            # logging.shutdown()
            os._exit(0)
            sys.exit(0)

