import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class OpenWebDriver():

    pathDriver = ""
    pathUrl = ""

    def __init__(self, pathDriver, pathUrl):
        self._pathUrl = pathUrl
        self._pathDriver = pathDriver

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

        firefoxProfile.set_preference("http.response.timeout", 20)
        firefoxProfile.set_preference("dom.max_script_run_time", 10)
        firefoxProfile.set_preference("browser.cache.disk.enable", False)
        firefoxProfile.set_preference("browser.cache.memory.enable", False)
        firefoxProfile.set_preference("browser.cache.offline.enable", False)
        firefoxProfile.set_preference("network.http.use-cache", False)

        # options = FirefoxOptions()
        # options.add_argument("--headless")

        try:
            firefox = webdriver.Firefox(executable_path=self._pathDriver, firefox_profile=firefoxProfile)
            logging.info("Navegador iniciado com sucesso.")
        except:
            logging.exception('Falha ao iniciar o  navegador.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            sys.exit(0)

        firefox.maximize_window()
        firefox.delete_all_cookies()

        try:
            firefox.set_page_load_timeout(10)
            firefox.get(self._pathUrl)
        except:
            firefox.find_element(By.ID, "btnEntrar").send_keys(Keys.CONTROL + 'Escape')
            logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
            logging.info('Executar parada de carregamento da pagina.')

        return firefox