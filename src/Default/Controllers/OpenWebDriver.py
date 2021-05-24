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

import os
import re
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browsermobproxy import Server
from random import randint
from datetime import datetime

from src.Default.Models.CSV import CSV

class OpenWebDriver():

    pathDriver = ""
    pathUrl = ""
    driveName = ""
    proxy = ""
    traffic = ""
    versao = 0.0
    fileName = ""
    server = ""
    entries = ""
    proxy = ""

    def __init__(self, pathDriver, driveName, versao, pathUrl, proxy, traffic, fileName):
        self._pathUrl = pathUrl
        self._pathDriver = pathDriver
        self._driveName = driveName
        self._versao = versao
        self._proxy = proxy
        self._traffic = traffic
        self._fileName = fileName

    def Open(self, logging):

        # #######################################

        try:

            self.server = Server(self._proxy + "bin\\browsermob-proxy.bat")
            self.server.start()
            self.proxy = self.server.create_proxy()

        except:
            logging.exception('Falha ao iniciar o proxy.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            os._exit(0)
            sys.exit(0)

        # #######################################

        firefoxProfile = webdriver.FirefoxProfile()
        firefoxProfile.set_preference("http.response.timeout", 60)
        firefoxProfile.set_preference("dom.max_script_run_time", 30)
        firefoxProfile.set_preference("browser.cache.disk.enable", False)
        firefoxProfile.set_preference("browser.cache.memory.enable", False)
        firefoxProfile.set_preference("browser.cache.offline.enable", False)
        firefoxProfile.set_preference("network.http.use-cache", False)

        firefoxProfile.set_preference("plugin.state.java", 0)

        firefoxProfile.set_proxy(self.proxy.selenium_proxy())

        # #######################################
        # Vericar em ambiente de produção
        # Nao realiza conexao via SSL
        # firefoxProfile.set_preference("network.proxy.ssl", "")
        # firefoxProfile.set_preference("network.proxy.ssl_port", "")
        # firefoxProfile.set_preference("network.proxy.type", 1)
        # #######################################

        options = FirefoxOptions()

        if self._versao >= 80.0:
            options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            logging.info('Entrou no option de > 80.0.')

        if self._versao <= 78.0:
            options.add_argument("--headless")
            logging.info('Entrou no option de <= 78.0.')

        options.add_argument("--no-sandbox")
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        # capabilities = webdriver.DesiredCapabilities().FIREFOX
        # capabilities['marionette'] = True
        # capabilities['proxy'] = {
        #     "proxyType": "MANUAL",
        #     "sslProxy": "",
        # }

        try:
            firefox = webdriver.Firefox(executable_path=self._pathDriver + self._driveName + '.exe', # capabilities=capabilities,
                                        firefox_profile=firefoxProfile,
                                        options=options,
                                        )


            waitButtonLogin = WebDriverWait(firefox, 5)

            self.proxy.new_har("Robo_" + datetime.now().strftime("%d_%m_%Y__%H_%M_%S") + "_" + str(randint(10, 99)) + str(randint(10, 99)) + str(randint(10, 99)), options={'captureHeaders': True, 'captureContent': True})

            logging.info("Navegador iniciado com sucesso.")

        except:
            logging.exception('Falha ao iniciar o  navegador.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            self.server.stop()
            os._exit(0)
            sys.exit(0)

        # ###################################################################
        # Verificação na abertura do driver
        if self._versao < 78.0:
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

                # Interrompe o carregamento da página após error de time out, se passar de 5s
                waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnEntrar')))
                firefox.execute_script("window.stop();")

                logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
                logging.info('Executar parada de carregamento da pagina.')

        return firefox

    def registre_traffic(self, trafficData):

        csvOb = CSV(self._traffic)

        csvOb.registraCsvTraffic(self, self._fileName, trafficData)

    def stop_proxy(self):
        self.server.stop()

    def monitor_traffic(self):

        countRequest = 0
        countKb = 0
        list_request = []
        list_request_all = []

        self.entries = self.proxy.har['log']['entries']

        for ent in self.entries:

            gaCollect = (ent['request']['url'])

            if not re.search('mozilla.com', gaCollect, re.IGNORECASE):
                if not re.search('mozilla.net', gaCollect, re.IGNORECASE):

                    list_request_all.append(ent)

                    list_request.append(
                                            {
                                                'url' : str(ent['request']['url'] ),
                                                'milissegundos' : str(ent['time']),
                                                'kbytes' : str(round((ent['response']['bodySize'] + ent['response']['headersSize']) / 1024, 2))
                                          }
                    )

                    countRequest += 1
                    countKb += round((ent['response']['bodySize'] + ent['response']['headersSize']) / 1024, 2)

        # [lista individual request, cabecalho total, total de requisicoes, total de kb]
        return [list_request, countRequest, countKb, list_request_all]