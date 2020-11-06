import sys
import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Control.Print import Print


class TaskInclusaoProcessos:

    # listProcessos = [[], [], [], ]

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        # self.listProcessos = [[],[],[],]
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def processoIncluir(self, firefox, process, dayProcess, logging, caminhoImages):

        # Mapeamento dos dados da planilha
        # Numero do processo, dia, mes, ano e sessao

        dayProce = int(dayProcess[0:2])
        monthProcess = dayProcess[3:5]
        yearProcess = dayProcess[6:10]

        print('dia processo abrir: ' + str(dayProce))

        # Procura dia no calendario atual
        # A Aberta
        # R Realizada
        # F Finalizada
        element = firefox.find_element_by_xpath("//span[@class='text-center' and ./text()='" + str(dayProce) + "']//following-sibling::span[@class='ml-10' and contains(text(),'- EASP')]")

        # Verifica se achou o respectivo dia no calendario
        if element:

            element.click()

            time.sleep(1)

            # Localiza a nova janela aberta
            ##########################################################
            main_window_handle = None
            while not main_window_handle:
                main_window_handle = firefox.current_window_handle

            signin_window_handle = None
            while not signin_window_handle:
                for handle in firefox.window_handles:
                    if handle != main_window_handle:
                        signin_window_handle = handle
                        break
            firefox.switch_to.window(signin_window_handle)
            ##########################################################

            # Seleciona "Aptos para inclusão em pauta"
            ##########################################################
            element = WebDriverWait(firefox, 300).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'td#form_lbl')))
            element.click()
            ##########################################################

            # Verificar time para processos longos
            # time.sleep(3)

            # Localiza processos a serem selecionados e seleciona cada um deles
            # WebDrive usado somente para o aguardo do carregamento da pagina
            ##########################################################
            element = WebDriverWait(firefox, 300).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'table#pautaJulgamentoList tbody tr')))

            # Localiza tabela com listagem dos processos
            element = firefox.find_elements_by_css_selector("table#pautaJulgamentoList tbody tr.rich-table-row")
            ##########################################################

            # Localiza os processos do dia e marca
            ##########################################################
            for i in range(len(process)):
                for x in range(len(element)):
                    try:
                        firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
                            x + 1) + "]/td[2]/div/div/h6/a[contains(text(), '" + process[i][0] + "')]")
                        firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
                            x + 1) + "]/td[1]/form/center/input").click()

                        # Aguarda loading do click
                        time.sleep(2)

                        break
                    except:
                        continue
            ##########################################################

            # Clica em incluir processos
            # Finaliza atividade
            ##########################################################
            # element = WebDriverWait(firefox, 200).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR,
            #          'form#j_id1620 input')))
            # element.click()
            ##########################################################

            time.sleep(2)

            # Fecha popup
            firefox.close()

            # Para sair do objeto popup
            firefox.switch_to.window(main_window_handle)  # or driver.switch_to_default_content()

    def localizarProcessoIncluir(self, firefox, process, dayProcess,  logging, caminhoImages):

        # Mapeamento dos dados da planilha
        # Numero do processo, dia, mes, ano e sessao

        dayProce = dayProcess[0:2]
        monthProcess = dayProcess[3:5]
        yearProcess = dayProcess[6:10]

        data = date.today()

        # Salva a data atual
        dataAtual = data.strftime('%d-%m-%Y')

        # Usado para capturar a descricao no mes atual
        valMes = int(monthProcess) - 1

        Meses = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')



        print(process)
        print('data atual' +  str(dataAtual))
        print(dataAtual[3:5])
        print(monthProcess)

        print('texto calendario')
        print(str(firefox.find_element(By.CSS_SELECTOR, '.calendario .rich-calendar-month .rich-calendar-tool-btn').text))


        if dataAtual[3:5] != monthProcess:

            count = 0
            while count == 0:
                try:
                    element = firefox.find_element(By.XPATH, "//div[@class='rich-calendar-tool-btn' and contains(text(), '" + str(
                        Meses[valMes]) + "')]")
                    count+1
                    break
                except:

                    # Avança o calendário mes
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "//div[./text()='>']")))
                    element.click()

                    # Aguarda mudar o mês
                    time.sleep(2)

        self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages)







    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

        try:

            time.sleep(3)

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

            # {'29-10-2020': [['3000746-69.2019.8.06.0012', '29-10-2020', '5'],
            #                 ['3000074-61.2017.8.06.9964', '29-10-2020', '5'],
            #                 ['3000323-07.2017.8.06.0008', '29-10-2020', '5']],
            #  '30-10-2020': [['3000323-07.2017.8.06.0007', '30-10-2020', '8']],
            #  '15-11-2020': [['3000323-07.2017.8.06.0006', '15-11-2020', '5']],
            #  '20-11-2020': [['3000323-07.2017.8.06.0004', '20-11-2020', '8'],
            #                 ['3000323-07.2017.8.06.0005', '20-11-2020', '8']]
            #                 }
            listDataProcessos = openXls.getDataProcessInclusaoXLS(xlsData, firefox, logging, xml)

            # Chama metodo que localiza os processos
            for i in listDataProcessos:
                logging.info('Incluindo processos ne sessao do dia: ' + str(i))
                self.localizarProcessoIncluir(firefox, listDataProcessos[i], str(i),  logging, caminhoImages)

            logging.info('---------------------------')



















        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()


            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos