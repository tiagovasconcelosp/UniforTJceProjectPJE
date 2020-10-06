from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Perfil:

    def __init__(self, firefox, logging, perfil, desPerfil):
        self.Perfil(firefox, logging, perfil, desPerfil)

    def Perfil(self, firefox, logging, perfil, desPerfil):

        try:

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '.menu-usuario a')))
            element.click()

            select = Select(firefox.find_element(By.CSS_SELECTOR, "#papeisUsuarioForm select"))

            select.select_by_visible_text(desPerfil)

            logging.info('Perfil selecionado com sucesso! Selecionado: ' + str(desPerfil))
        except:
            logging.exception('Falha selecionar o perfil indicado com codigo ' + str(perfil))
            logging.info('Perfil "' + str(desPerfil) + '" nao identificado.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            firefox.quit()
            exit()