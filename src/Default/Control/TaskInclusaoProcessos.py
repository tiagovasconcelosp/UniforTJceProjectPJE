import time
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Control.Print import Print


class TaskInclusaoProcessos:
    listProcessos = [[], [], [], ]
    countIncluidos = 0
    countEnviaProcesso = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def pecorreProcesso(self, firefox, process, element, logging, caminhoImages):

        # Localiza os processos do dia e marca
        ##########################################################

        for i in range(len(process)):
            # Usado para verificar se o processo nao foi localizado
            count = 0

            for x in range(len(element)):

                try:  # Para verificar se o processo existe na listagem

                    firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
                        x + 1) + "]/td[2]/div/div/h6/a[contains(text(), '" + process[i][0] + "')]")

                    try:
                        firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
                            x + 1) + "]/td[1]/form/center/input").click()

                        # Inclui lista de processos localizados
                        self.listProcessos[0].append(str(process[i][0]))
                        logging.info('Processo selecionado: ' + str(process[i][0]))

                        # Processo incluido
                        self.listProcessos[1].append(0)

                        self.countIncluidos += 1

                        # Processo localizado
                        count += 1

                    except:

                        # Caso acontece de nao existir o botao marcar
                        logging.info('Processo nao pode ser selecionado: ' + str(process[i][0]))
                        # Inclui lista de processos localizados
                        self.listProcessos[0].append(str(process[i][0]))
                        print('nao clicou')
                        # Processo incluido
                        self.listProcessos[1].append(1)

                    # Aguarda loading do click
                    # Verifica time de click
                    time.sleep(1)

                    # break

                except:
                    continue

            # Caso o processo nao seja localizado, incluir na lista de nao localizados
            if count == 0:
                # Inclui lista de processos nao localizados
                self.listProcessos[2].append(str(process[i][0]))

                image = Print(firefox, caminhoImages)
                logging.info('---------------------------')
                logging.info('Ocorreu um processo de nao ser localizado na sessao.')
                logging.info('Processo nao localizado: ' + str(process[i][0]))
                logging.info('---------------------------')

        ##########################################################

    def processoIncluir(self, firefox, process, dayProcess, logging, caminhoImages, countDef):

        try:
            # Mapeamento dos dados da planilha
            # Numero do processo, dia, mes, ano e sessao
            dayProce = int(dayProcess[0:2])
            monthProcess = dayProcess[3:5]
            yearProcess = dayProcess[6:10]

            processVirtual = []
            processPresencial = []

            for x in range(len(process)):
                if (str(process[x][2]).upper()).strip() == (str('Virtual').upper()).strip():
                    processVirtual.append([process[x][0]])
                elif (str(process[x][2]).upper()).strip() == (str('Presencial').upper()).strip():
                    processPresencial.append([process[x][0]])
                else:
                    logging.info('---------------------------')
                    logging.info('A coluna da sessao por um dado incorreto. O valor deve ser Virtual ou Presencial')
                    logging.info('O valor da coluna atual: ' + str(process[x][2]))
                    logging.info('Numero do processo: ' + str(process[x][0]))
                    logging.info('---------------------------')

            # Procura dia no calendario atual
            # A Aberta
            # R Realizada
            # F Finalizada
            logging.info('Buscando o dia da sessao.')
            logging.info('---------------------------')

            element = firefox.find_element_by_xpath("//span[@class='text-center' and ./text()='" + str(
                dayProce) + "']//following-sibling::span[@class='ml-10' and contains(text(),'- EASP')]")

            # Verifica se achou o respectivo dia no calendario
            if element:

                logging.info('Dia da sessao encontrato.')
                logging.info('---------------------------')

                element.click()

                time.sleep(1)

                # Identifica se tem mais de uma sessao e qual deve entrar
                ##########################################################
                try:
                    element = firefox.find_elements_by_css_selector("table#sessaoRelacaoJulgamentoDt tr.rich-table-row")

                    for x in range(len(element)):

                        try:

                            if len(processPresencial) > 0 and countDef == 0:
                                # firefox.find_element(By.XPATH, "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[" + str(
                                #     x + 1) + "]/td[contains(text(), 'Presencial')]//ancestor::tr[" + str(
                                #     x + 1) + "]/td[1]/a").click()

                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a").click()

                                sessao = 'Presencial'

                            elif len(processVirtual) > 0 and countDef == 1:
                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a").click()

                                sessao = 'Virtual'

                            elif  len(processPresencial) > 0:
                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a").click()

                                sessao = 'Presencial'

                            elif len(processVirtual) > 0:
                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a").click()

                                sessao = 'Virtual'

                        except:

                            logging.info('Houver uma divergencia nos dados. Por favor verificar a planilha')
                            logging.info('---------------------------')
                            logging.info('Presencial:')
                            logging.info(str(processPresencial))
                            logging.info('Virtual:')
                            logging.info(str(processVirtual))
                            logging.info('---------------------------')
                            continue

                    firefox.find_element(By.CSS_SELECTOR, "span#fecharModal").click()

                except:

                    logging.info('Entrando na sessao...')
                ##########################################################

                time.sleep(2)

                logging.info('Localizando a nova janela aberta.')
                logging.info('---------------------------')

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

                logging.info('Nova janela encontrada.')
                logging.info('---------------------------')

                # Seleciona "Aptos para inclusão em pauta"
                ##########################################################
                element = WebDriverWait(firefox, 300).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'td#form_lbl')))
                element.click()
                ##########################################################

                logging.info('Seleciona menu: Aptos para inclusão em pauta.')
                logging.info('---------------------------')

                # Verificar time para processos longos
                # time.sleep(3)

                logging.info('Buscando processos para serem incluidos...')
                logging.info('---------------------------')

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

                # Para verificar se caso entrou em uma sessao especifica
                try:
                    if sessao == 'Presencial':
                        processList = processPresencial
                        countDef += 1
                    elif sessao == 'Virtual':
                        processList = processVirtual
                        countDef += 1

                    self.pecorreProcesso(firefox, processList, element, logging, caminhoImages)

                except:

                    self.pecorreProcesso(firefox, process, element, logging, caminhoImages)

                logging.info('Processos selecionados...')
                logging.info('---------------------------')

                # Clica em incluir processos
                # Finaliza atividade
                ##########################################################
                # element = WebDriverWait(firefox, 200).until(
                #     EC.presence_of_element_located(
                #         (By.CSS_SELECTOR,
                #          'form#j_id1620 input')))
                # element.click()
                ##########################################################

                logging.info('Incluindo os processos...')
                logging.info('---------------------------')

                # Verificar quanto tempo demora a inclusao
                time.sleep(1)

                # Fecha popup
                try:
                    firefox.close()
                except:
                    firefox.quit()

                # Para sair do objeto popup
                firefox.switch_to.window(main_window_handle)  # or driver.switch_to_default_content()

                time.sleep(1)

                if len(processPresencial) > 0 and len(processVirtual) > 0 and countDef == 1:
                    self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages, countDef)

                logging.info('Processos incluidos com sucesso.')
                logging.info('---------------------------')

                logging.info('Fechando a janela da sessao.')
                logging.info('---------------------------')

                return self.listProcessos
        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.exception('Dia da sessao nao encontrado.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

    def localizarDataCalendarioIncluir(self, firefox, process, dayProcess, logging, caminhoImages):

        try:
            # Mapeamento dos dados da planilha
            monthProcess = dayProcess[3:5]

            data = date.today()

            # Salva a data atual
            dataAtual = data.strftime('%d-%m-%Y')

            # Usado para capturar a descricao no mes atual
            valMes = int(monthProcess) - 1

            Meses = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')

            logging.info('---------------------------')
            logging.info('Iniciando a busca pela sessao dos processos.')
            logging.info('---------------------------')

            if dataAtual[3:5] != monthProcess:

                logging.info('Selecionado o proximo mes para buscar a sessao.')
                logging.info('---------------------------')

                logging.info('A busca atual não encontrou os processos no mes selecionado no calendario.')
                logging.info('Buscando a sessao no proximo mes: ' + str(Meses[valMes]))
                logging.info('---------------------------')

                # Contador usado para parar o loop somente quando o mes for encontrado
                count = 0
                while count == 0:
                    try:
                        element = firefox.find_element(By.XPATH,
                                                       "//div[@class='rich-calendar-tool-btn' and contains(text(), '" + str(
                                                           Meses[valMes]) + "')]")
                        count + 1

                        logging.info('Encontrado o mes correto para o processo.')
                        logging.info('---------------------------')
                        break

                    except:

                        # Avança o calendário mes
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//div[./text()='>']")))
                        element.click()

                        logging.info('Avancando para o proximo mes.')
                        logging.info('---------------------------')

                        # Aguarda mudar o mês
                        time.sleep(2)

            logging.info('---------------------------')
            logging.info('Iniciando a inclusao dos processos')
            logging.info('---------------------------')

            # Usado para chamada recursiva do metodo
            countDef = 0
            self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages, countDef)

        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

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

            # Registra horario que iniciou a tarefa
            inicio = time.time()

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
                logging.info('---------------------------')
                logging.info('Buscando a sessao...')
                logging.info('---------------------------')
                self.localizarDataCalendarioIncluir(firefox, listDataProcessos[i], str(i), logging, caminhoImages)

            logging.info('---------------------------')

            ###################################
            # Verificacao dos processos localizado e incluidos
            ###################################

            if len(self.listProcessos[0]) > 0:
                logging.info('Lista de processos encontrados:')
                for i in range(len(self.listProcessos[0])):
                    logging.info('Processo: ' + str(self.listProcessos[0][i]))

                logging.info("Total de processos encontrados: " + str(len(self.listProcessos[0])))
                logging.info("Total de processos incluidos: " + str(self.countIncluidos))
            else:
                logging.info('Nenhum processo foi encontrado.')

            self.listProcessos.append(len(self.listProcessos[0]))
            self.listProcessos.append(self.countIncluidos)

            logging.info('---------------------------')

            ###################################
            # Calculo do tempo de execucao
            ###################################

            # Registra horario que finalizou a tarefa
            fim = time.time()

            timeTotal = fim - inicio

            timeTotal = float('{:.2f}'.format(timeTotal))

            if timeTotal <= 60:
                logging.info('Tempo de execucao da atividade: ' + str(timeTotal) + ' segundos')
                self.listProcessos.append(str(timeTotal) + ' segundos')
            else:
                logging.info('Tempo de execucao da atividade: ' + str(timeTotal // 60) + ' minutos')
                self.listProcessos.append(str(timeTotal // 60) + ' minutos')

            logging.info('---------------------------')

            ###################################
            # Vericacao dos processos nao localizados
            ###################################

            if len(self.listProcessos[2]) > 0:
                logging.info('Lista de processos nao foram encontrados:')
                for i in range(len(self.listProcessos[2])):
                    logging.info('Processo: ' + str(self.listProcessos[2][i]))
                logging.info("Total de processos que nao foram encontrados: " + str(len(self.listProcessos[2])))
            else:
                logging.info('Todos os processos foram encontrados corretamente.')

            self.listProcessos.append(len(self.listProcessos[2]))

            logging.info('---------------------------')

            try:
                firefox.close()
            except:
                firefox.quit()

            return self.listProcessos

        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos