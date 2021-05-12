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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class Perfil:

    def __init__(self, firefox, logging, perfil, desPerfil):
        self.Perfil(firefox, logging, perfil, desPerfil)

    def Perfil(self, firefox, logging, perfil, desPerfil):

        try:

            # foi alterado para 300s, antes estava 20s
            # aguarda para que seja feita a autenticacao manual
            element = WebDriverWait(firefox, 300).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '.menu-usuario a')))
            element.click()

            select = Select(firefox.find_element(By.CSS_SELECTOR, "form#papeisUsuarioForm select"))

            select.select_by_visible_text(desPerfil)

            logging.info('Perfil selecionado com sucesso! Selecionado: ' + str(desPerfil))

        except:
            logging.exception('Falha ao autenticar ou selecionar perfil')
            logging.exception('Falha em selecionar o perfil indicado com codigo ' + str(perfil))
            logging.info('Perfil "' + str(desPerfil) + '" nao identificado.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

            try:
                firefox.close()
            except:
                firefox.quit()