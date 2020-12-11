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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class OpenWebDriver():

    pathDriver = ""
    pathUrl = ""
    driveName = ""
    versao = 0.0

    def __init__(self, pathDriver, driveName, versao, pathUrl):
        self._pathUrl = pathUrl
        self._pathDriver = pathDriver
        self._driveName = driveName
        self._versao = versao

    def getPathDriver(self):
        return self._pathDriver

    def setPathDriver(self, pathDriver):
        self._pathDriver = pathDriver

    def getPathUrl(self):
        return self._pathUrl

    def setPathUrl(self, pathUrl):
        self._pathUrl = pathUrl

    def Open(self, logging):

        firefoxProfile = webdriver.FirefoxProfile()

        firefoxProfile.set_preference("http.response.timeout", 60)
        firefoxProfile.set_preference("dom.max_script_run_time", 30)
        firefoxProfile.set_preference("browser.cache.disk.enable", False)
        firefoxProfile.set_preference("browser.cache.memory.enable", False)
        firefoxProfile.set_preference("browser.cache.offline.enable", False)
        firefoxProfile.set_preference("network.http.use-cache", False)

        # usado na configuracao pelo formulario
        # if self._versao == 18:
        #     firefoxProfile.set_preference("plugin.state.java", 0)

        if self._versao < 55.0:
            firefoxProfile.set_preference("plugin.state.java", 0)
        elif self._versao >= 55.0 and self._versao < 57.0:
            firefoxProfile.set_preference("plugin.state.java", 0)
        elif self._versao >= 57.0 and self._versao < 60.0:
            firefoxProfile.set_preference("plugin.state.java", 0)
        elif self._versao >= 60.0 and self._versao < 79.0:
            firefoxProfile.set_preference("plugin.state.java", 0)
        # elif self._versao >= 79.0:


        options = FirefoxOptions()
        options.add_argument("--headless")

        try:
            firefox = webdriver.Firefox(executable_path=self._pathDriver + self._driveName + '.exe',
                                        firefox_profile=firefoxProfile,
                                        #options=options
                                        )
            logging.info("Navegador iniciado com sucesso.")
        except:
            logging.exception('Falha ao iniciar o  navegador.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            sys.exit(0)

        waitButtonLogin = WebDriverWait(firefox, 5)

        if self._versao < 79.0:

            try:
                firefox.get(self._pathUrl)

                firefox.maximize_window()
                firefox.delete_all_cookies()
                firefox.set_page_load_timeout(5)

            except:

                waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnEntrar')))
                firefox.execute_script("window.stop();")

                logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
                logging.info('Executar parada de carregamento da pagina.')

        else:

            firefox.maximize_window()
            firefox.delete_all_cookies()
            firefox.set_page_load_timeout(5)

            try:
                firefox.get(self._pathUrl)

            except:
                # firefox.find_element(By.ID, "btnEntrar").send_keys(Keys.CONTROL + 'Escape')

                # Interrompe o carregamento da página após error de time out, se passar de 5s
                waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnEntrar')))
                firefox.execute_script("window.stop();")

                logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
                logging.info('Executar parada de carregamento da pagina.')

        return firefox