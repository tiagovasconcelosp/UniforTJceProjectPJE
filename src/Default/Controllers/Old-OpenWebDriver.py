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
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from browsermobproxy import Server
from random import randint
from datetime import datetime
import psutil

import functools


class OpenWebDriver():
    pathDriver = ""
    pathUrl = ""
    driveName = ""
    proxy = ""
    traffic = ""
    versao = 0.0
    firefox_filepath = 0
    server = ""
    entries = ""
    proxy = ""

    def __init__(self, pathDriver, driveName, versao, pathUrl, proxy, firefox_filepath):
        self._pathUrl = pathUrl
        self._pathDriver = pathDriver
        self._driveName = driveName
        self._versao = versao
        self._proxy = proxy
        self._firefox_filepath = firefox_filepath

    def Open(self, logging):

        # #######################################
        # Hide Console

        flag = 0x08000000  # No-Window flag
        webdriver.common.service.subprocess.Popen = functools.partial(
            webdriver.common.service.subprocess.Popen, creationflags=flag)

        # #######################################

        # for proc in psutil.process_iter():
        #     # check whether the process name matches
        #     if proc.name() == "browsermob-proxy":
        #         proc.kill()
        #
        # if self.server != "":
        #     try:
        #         self.server.stop()
        #     except:
        #         self.server = ""
        #
        # try:
        #     dict = {'port': 8090}
        #     self.server = Server(self._proxy + "bin\\browsermob-proxy.bat")#, options=dict)
        #     self.server.start()
        #     time.sleep(1)
        #     self.proxy = self.server.create_proxy()
        #     time.sleep(1)
        #
        # except Exception as e:
        #     logging.exception('Falha ao iniciar o proxy.')
        #     logging.info('Finalizando o robo.')
        #     logging.info(repr(e))
        #     logging.shutdown()
        #     os._exit(0)
        #     sys.exit(0)

        # #######################################

        firefoxProfile = webdriver.FirefoxProfile()
        firefoxProfile.set_preference("http.response.timeout", 420)
        firefoxProfile.set_preference("dom.max_script_run_time", 30)
        firefoxProfile.set_preference("browser.cache.disk.enable", False)
        firefoxProfile.set_preference("browser.cache.memory.enable", False)
        firefoxProfile.set_preference("browser.cache.offline.enable", False)
        firefoxProfile.set_preference("network.http.use-cache", False)
        firefoxProfile.set_preference("devtools.chrome.enabled", True)
        firefoxProfile.set_preference("plugin.state.java", 0)

        #firefoxProfile.set_proxy(self.proxy.selenium_proxy())

        # #######################################
        # Vericar em ambiente de produção
        # Nao realiza conexao via SSL
        # firefoxProfile.set_preference("network.proxy.ssl", "")
        # firefoxProfile.set_preference("network.proxy.ssl_port", "")
        # firefoxProfile.set_preference("network.proxy.type", 1)
        # #######################################

        options = FirefoxOptions()

        if self._versao >= 80.0:
            options.binary_location = self._firefox_filepath

        if self._versao <= 78.0:
            options.add_argument("--headless")

        options.add_argument("--marionette")

        # options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems

        # Já estava comentado
        # capabilities = webdriver.DesiredCapabilities().FIREFOX
        # capabilities['marionette'] = True
        # capabilities['proxy'] = {
        #     "proxyType": "MANUAL",
        #     "sslProxy": "",
        # }

        try:
            firefox = webdriver.Firefox(executable_path=self._pathDriver + self._driveName + '.exe',
                                        # capabilities=capabilities,
                                        firefox_profile=firefoxProfile,
                                        options=options,
                                        )

            waitButtonLogin = WebDriverWait(firefox, 10)

            # self.proxy.new_har(
            #     "Robo_" + datetime.now().strftime("%d_%m_%Y__%H_%M_%S") + "_" + str(randint(10, 99)) + str(
            #         randint(10, 99)) + str(randint(10, 99)), options={'captureHeaders': True, 'captureContent': True})

            logging.info("Navegador iniciado com sucesso.")

        except Exception as e:
            logging.exception('Falha ao iniciar o  navegador.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()
            #self.server.stop()

            os._exit(0)
            sys.exit(0)

        # ###################################################################
        # Verificação na abertura do driver
        if self._versao < 78.0:
            try:
                firefox.get(self._pathUrl)

                firefox.maximize_window()
                firefox.delete_all_cookies()
                firefox.set_page_load_timeout(120)

            except:

                waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnEntrar')))
                firefox.execute_script("window.stop();")

                logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
                logging.info('Executar parada de carregamento da pagina.')
        else:
            firefox.maximize_window()
            firefox.delete_all_cookies()
            firefox.set_page_load_timeout(120)

            try:
                firefox.get(self._pathUrl)
            except:

                # Interrompe o carregamento da página após error de time out, se passar de 5s
                waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnEntrar')))
                firefox.execute_script("window.stop();")

                logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
                logging.info('Executar parada de carregamento da pagina.')

        return firefox

    def stop_proxy(self):
        self.server.stop()

    def monitor_traffic(self, logging):

        countRequest = 0
        countKb = 0
        list_request = []
        list_request_all = []

        self.entries = self.proxy.har['log']['entries']

        try:
            with open("harfile.har", "w") as harfile:
                harfile.write(json.dumps(self.proxy.har))
        except Exception as e:
            logging.info('Falha ao registrar arquivo harfile.')
            logging.info(repr(e))

        for ent in self.entries:

            gaCollect = (ent['request']['url'])

            if not re.search('mozilla.com', gaCollect, re.IGNORECASE):
                if not re.search('mozilla.net', gaCollect, re.IGNORECASE):
                    list_request_all.append(ent)

                    list_request.append(
                        {
                            'url': str(ent['request']['url']),
                            'milissegundos': str(ent['time']),
                            'kbytes': str(
                                round((ent['response']['bodySize'] + ent['response']['headersSize']) / 1024, 2))
                        }
                    )

                    countRequest += 1
                    countKb += round((ent['response']['bodySize'] + ent['response']['headersSize']) / 1024, 2)

        # [lista individual request, cabecalho total, total de kb, total de requisicoes]
        return [list_request, countRequest, countKb, list_request_all]
        # return [{'url': -1, 'milissegundos':-1, 'kbytes':-1}, -1, -1, -1]