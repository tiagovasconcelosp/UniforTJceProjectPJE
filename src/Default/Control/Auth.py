import sys

from selenium.webdriver.common.by import By
from src.Default.Control.Print import Print


class Auth:

    def __init__(self, firefox, logging, caminhoImages, login, senha):
        self.Login(firefox, logging, caminhoImages, login, senha)

    def Login(self, firefox, logging, caminhoImages, login, senha):

        try:
            # Aumenta o tempo de time out para 120s
            # Linhas comentadas para interroper preenchimento do login e senha

            firefox.set_page_load_timeout(120)

            # login = firefox.find_element(By.ID, "username").send_keys(login)

            # firefox.find_element(By.ID, "password").send_keys(senha)

            logging.info("Tentando realizar autenticacao.")

            # firefox.find_element(By.ID, "btnEntrar").click()
        except:

            image = Print(firefox, caminhoImages)

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            firefox.quit()
            sys.exit(0)
