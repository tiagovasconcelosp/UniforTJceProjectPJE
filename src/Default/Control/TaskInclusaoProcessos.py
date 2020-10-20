import sys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Control.Print import Print


class TaskInclusaoProcessos:

    listProcessos = [[], [], [], ]

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[],[],[],]
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def localizarProcessoEmcaminhar(self, firefox, numProcesso, logging, caminhoImages):

        time.sleep(3)

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

        try:

            #time.sleep(3)

            element = WebDriverWait(firefox, 200).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            time.sleep(1)

            # selecao last-child nao funciona
            # verificar em browser atualizado
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#menu div.nivel-aberto ul li:nth-of-type(2) a')))
            element.click()

            time.sleep(1)

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#menu .nivel-overlay div.nivel-aberto ul li:first-child a')))
            element.click()

            time.sleep(1)

            listDataProcessos = openXls.getDataProcessInclusaoXLS(xlsData, firefox, logging, xml)












            # trazer dia da planilha
            # procura dia no calendario atual
            element = firefox.find_element_by_xpath("//span[@class='text-center' and contains(text(),'20')]")

            if element:
                # verifica se dia está aberto
                element = firefox.find_element_by_xpath("//span[@class='ml-10' and contains(text(),'- A')]")
                if element:
                    element.click()











        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()

            return self.listProcessos