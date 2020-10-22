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

    def localizarProcessoIncluir(self, firefox, numProcess, dayProcess, hourProcess, logging, caminhoImages):

        # Mapeamento dos dados da planilha
        # Numero do processo, dia, mes, ano, hora e minuto
        # Usados para localizar os respectivos dias e horarios no calendario
        dayProce = dayProcess[0:2]
        monthProcess = dayProcess[3:5]
        yearProcess = dayProcess[6:10]
        hourProce = hourProcess[0:2]
        minProcess = hourProcess[3:5]

        # trazer dia da planilha
        # procura dia no calendario atual
        element = firefox.find_element_by_xpath("//span[@class='text-center' and contains(text(),'20')]")

        # Verifica se achou o respectivo dia no calendario
        if element:
            # Verifica se dia está aberto
            # A Aberta
            # R Realizada
            # F Finalizada
            element = firefox.find_element_by_xpath("//span[@class='ml-10' and contains(text(),'- A')]")
            if element:
                element.click()

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

            # ['3000323-07.2017.8.06.0004', '3000746-69.2019.8.06.0012']
            # ['13-11-2020', '14-11-2020']
            # ['13:30:00', '17:30:00']
            listDataProcessos = openXls.getDataProcessInclusaoXLS(xlsData, firefox, logging, xml)



            for i in range(len(listDataProcessos[0])):
                logging.info('Incluindo o processo: ' + str(listDataProcessos[0][i]))
                self.localizarProcessoIncluir(firefox, listDataProcessos[0][i], listDataProcessos[1][i], listDataProcessos[2][i], logging, caminhoImages)

            logging.info('---------------------------')



















        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()

            return self.listProcessos