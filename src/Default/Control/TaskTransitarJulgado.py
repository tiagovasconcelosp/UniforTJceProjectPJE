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

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Control.Print import Print


class TaskTransitarJulgado:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[],[],[],]
    countEncaminhados = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[],[],[],]
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def localizarProcesso(self, firefox, numProcesso, dateProcesso, logging, caminhoImages):

        registroErroPortal = 0

        try:
            element = WebDriverWait(firefox, 120).until(
                EC.presence_of_element_located(
                    (By.ID, 'inputPesquisaTarefas')))
            element.clear()

            firefox.find_element(By.ID, "inputPesquisaTarefas").send_keys(numProcesso)

            element = firefox.find_element(By.CSS_SELECTOR, '#divActions button[title="Pesquisar"]')
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(1)

            # Valida se houve mais de um resultado
            # caminho no ambiente da unifor
            # element = firefox.find_element(By.CSS_SELECTOR, 'span[title="Quantidade de processos na tarefa"]').text
            element = firefox.find_element(By.CSS_SELECTOR, 'div#divProcessosTarefa div.painel-listagem div.row span.badge').text

            # Verifica se retornou mais de um processo
            if int(element) > 1:
                logging.info('---------------------------')
                logging.info('Foi encontrado mais de um resultado. Total: ' + str(element))
                logging.info('Evidenciando com o print da tela.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

            time.sleep(2)

            # Clica no primeiro processo retornado
            element = WebDriverWait(firefox, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))
            firefox.execute_script("arguments[0].click();", element)

            logging.info('Processo ' + str(numProcesso) + ' foi localizado.')
            logging.info('---------------------------')
            self.listProcessos[0].append(str(numProcesso))

            time.sleep(4)

            # Clica no botao para abrir o processo - Autos
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.header-wrapper div.toolbar-processo button[tooltip="Autos"i]')))
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(3)

            logging.info('Aguardando a nova janela ser aberta.')
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

            try:
                # Clica no botao para Juntar documentos
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'ul.menu-icones-topo a[name="navbar:linkAbaIncluirPeticoes1"i]')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(2)

                # Usado para carregamento da pagina
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]')))

            except:
                logging.info('---------------------------')
                logging.info('Houve um problema na etapa de incluir peticoes. Por ter ocorrido algum problema de conexao.')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Seleciona o Tipo de Documento
                select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]'))
                select.select_by_visible_text('Certidão')

                time.sleep(2)
            except:
                logging.info('---------------------------')
                logging.info('Houve um problema na etapa de selecionar o Tipo Documento')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Seleciona o Modelo
                select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="modTDDecoration:modTD"i]'))
                select.select_by_visible_text('Certidão de Trânsito')

                time.sleep(2)
            except:

                try:
                    # Seleciona o Modelo
                    select = Select(
                        firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="modTDDecoration:modTD"i]'))
                    select.select_by_visible_text('Certidão de Trânsito*')

                    time.sleep(2)
                except:
                    logging.info('---------------------------')
                    logging.info('Houve um problema na etapa de selecionar o Modelo')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)

            try:
                # Seleciona o Tipo de Documento
                select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]'))
                select.select_by_visible_text('Certidão trânsito em julgado')

                time.sleep(2)
            except:
                logging.info('---------------------------')
                logging.info('Houve um problema na etapa de selecionar o Tipo de Documento')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Clica no botao Preencher Documentos
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'table#selectedEventsTable td a[name="selectedEventsTable:0:linkComplementos"i]')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(3)
            except:
                logging.info('---------------------------')
                logging.info('Houve um problema na etapa de selecionar o botao Preencher Documentos')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Inclui a Data
                firefox.find_element(By.CSS_SELECTOR, "div.clearfix div.col-sm-4 div.col-sm-12 input").send_keys(dateProcesso)
                time.sleep(1)

                # Clica no botao Ok
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div#complementosInner input#botaoGravarMovimento')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(3)
            except:
                logging.info('---------------------------')
                logging.info('Houve um problema na etapa de informar a data')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Clica no botao Salvar
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input[value="Salvar"i]')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(3)
            except:
                logging.info('---------------------------')
                logging.info('Houve um problema ao salvar o processo.')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                # Clica no botao Assinar Documento
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'input#btn-assinador')))
                firefox.execute_script("arguments[0].click();", element)

                # Aguarda a Assinatura, demora em torno de 8s. Pois uso a leitura do certificado
                time.sleep(8)

            except:
                logging.info('---------------------------')
                logging.info('Houve um problema realizar a assinatura.')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            try:
                firefox.close()
            except:
                firefox.quit()

            # Para sair do objeto popup
            firefox.switch_to.window(main_window_handle)

            # Localiza frame
            iframe = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            time.sleep(1)

            ##################################################################################
            try:
                # Clica no botao Encaminhar para (ABRE AS OPCOES)
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                firefox.execute_script("arguments[0].click();", element)
            except:

                time.sleep(10)

                try:
                    # Clica no botao Encaminhar para
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                    firefox.execute_script("arguments[0].click();", element)

                except:

                    logging.info('Houve um problema na etapa encaminhar para...')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)

            ##################################################################################
            try:
                # Clica no botao Cumprir acordao
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'ul.dropdown-transicoes li a[title="Encaminhar para Cumprir acórdão"i]')))
                firefox.execute_script("arguments[0].click();", element)
            except:

                time.sleep(10)

                try:
                    # Clica no botao Cumprir acordao
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'ul.dropdown-transicoes li a[title="Encaminhar para Cumprir acórdão"i]')))
                    firefox.execute_script("arguments[0].click();", element)
                except:
                    logging.info('Houve um problema na etapa Encaminhar para Cumprir acórdão...')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)

                    registroErroPortal = 1

            ##################################################################################

            time.sleep(3)

            ##################################################################################

            if registroErroPortal == 0:
                try:
                    # Clica no botao Encaminhar para (ABRE AS OPCOES NOVAMENTE)
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                    firefox.execute_script("arguments[0].click();", element)
                except:

                    time.sleep(10)

                    try:
                        # Clica no botao Encaminhar para (ABRE AS OPCOES NOVAMENTE)
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                        firefox.execute_script("arguments[0].click();", element)

                    except:
                        logging.info('Houve um problema na etapa Encaminhar para... segunda etapa')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(firefox, caminhoImages)
                ##################################################################################

                time.sleep(1)

                ##################################################################################
                try:
                    # Clica no botao Encaminhar para 02 - Devolver para instância de origem
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'ul.dropdown-transicoes li a[title="Encaminhar para 02 - Devolver para instância de origem"i]')))
                    firefox.execute_script("arguments[0].click();", element)

                    time.sleep(6)

                except:

                    time.sleep(10)

                    try:
                        # Clica no botao Encaminhar para 02 - Devolver para instância de origem
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'ul.dropdown-transicoes li a[title="Encaminhar para 02 - Devolver para instância de origem"i]')))
                        firefox.execute_script("arguments[0].click();", element)

                        time.sleep(10)

                    except:
                        logging.info('Houve um problema na etapa devolver para instancia de origem.')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(firefox, caminhoImages)
                ##################################################################################
                try:
                    # Localiza frame
                    iframe = WebDriverWait(firefox, 10).until(
                        EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                    firefox.switch_to.frame(iframe)

                    # Aguarda elemento carregar em tela
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.propertyView div.value select')))

                    # Seleciona o Motivo da Remessa
                    select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.propertyView div.value select'))
                    select.select_by_visible_text('outros motivos')

                    time.sleep(3)
                except:

                    time.sleep(10)

                    try:
                        # Localiza frame
                        iframe = WebDriverWait(firefox, 10).until(
                            EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                        firefox.switch_to.frame(iframe)

                        # Aguarda elemento carregar em tela
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'div.propertyView div.value select')))

                        # Seleciona o Motivo da Remessa
                        select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.propertyView div.value select'))
                        select.select_by_visible_text('outros motivos')

                        time.sleep(3)

                    except:

                        logging.info('Houve um problema na etapa de selecionar o motivo da remessa.')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(firefox, caminhoImages)
                ##################################################################################
                time.sleep(1)
                ##################################################################################
                try:
                    # Clica no botao Retornar para Instancia de Origem
                    element = WebDriverWait(firefox, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'input.btn-primary[value="Retornar para instância de origem"i]')))
                    firefox.execute_script("arguments[0].click();", element)

                    time.sleep(2)

                    ##################################################################################
                    try:
                        # Localiza frame alerta de documento nao assinados
                        iframe = WebDriverWait(firefox, 10).until(
                            EC.presence_of_element_located((By.ID, 'editorFrame')))

                        firefox.switch_to.frame(iframe)

                        # Clica no botao Confirmar
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'input.btn-primary[value="Confirmar"i]')))
                        firefox.execute_script("arguments[0].click();", element)

                        # Para sair do objeto popup
                        firefox.switch_to.window(main_window_handle)

                        # Localiza frame
                        iframe = WebDriverWait(firefox, 10).until(
                            EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                        firefox.switch_to.frame(iframe)

                        logging.info('Alerta de documentos não assinados.')
                        logging.info('Clicando em confirmar.')

                    except:
                        logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                    ##################################################################################

                    time.sleep(20)

                    self.listProcessos[1].append(0)
                    self.countEncaminhados += 1

                    # Para sair do objeto popup
                    firefox.switch_to.window(main_window_handle)

                    # Localiza frame
                    iframe = WebDriverWait(firefox, 10).until(
                        EC.presence_of_element_located((By.ID, 'ngFrame')))

                    firefox.switch_to.frame(iframe)

                # Caso haja falha tentar mais uma vez o processo de envio
                except:

                    time.sleep(20)

                    try:

                        # Clica no botao Retornar para Instancia de Origem
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'input.btn-primary[value="Retornar para instância de origem"i]')))
                        firefox.execute_script("arguments[0].click();", element)

                        time.sleep(2)

                        ##################################################################################
                        try:
                            # Localiza frame alerta de documento nao assinados
                            iframe = WebDriverWait(firefox, 10).until(
                                EC.presence_of_element_located((By.ID, 'editorFrame')))

                            firefox.switch_to.frame(iframe)

                            # Clica no botao Confirmar
                            element = WebDriverWait(firefox, 20).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR,
                                     'input.btn-primary[value="Confirmar"i]')))
                            firefox.execute_script("arguments[0].click();", element)

                            # Para sair do objeto popup
                            firefox.switch_to.window(main_window_handle)

                            # Localiza frame
                            iframe = WebDriverWait(firefox, 10).until(
                                EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                            firefox.switch_to.frame(iframe)

                            logging.info('Alerta de documentos não assinados.')
                            logging.info('Clicando em confirmar.')

                        except:
                            logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                        ##################################################################################

                        time.sleep(20)

                        self.listProcessos[1].append(0)
                        self.countEncaminhados += 1

                        # Para sair do objeto popup
                        firefox.switch_to.window(main_window_handle)

                        # Localiza frame
                        iframe = WebDriverWait(firefox, 10).until(
                            EC.presence_of_element_located((By.ID, 'ngFrame')))

                        firefox.switch_to.frame(iframe)

                    except:

                        logging.info('Houve um problema ao retornar para instancia de origem.')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(firefox, caminhoImages)

                        self.listProcessos[1].append(1)

            else:
                logging.info('Houve um travamento do processo no sistema ao clica em Encaminhar para Cumprir acardao')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            return self.listProcessos
        except:

            logging.info('Houve algum problema ao realizar a atividade do atual processo.')
            self.listProcessos[2].append(str(numProcesso))

            return self.listProcessos

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

        try:

            time.sleep(3)

            element = WebDriverWait(firefox, 200).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            time.sleep(1)

            firefox.find_element(By.CSS_SELECTOR, "#menu div.nivel-aberto ul li:first-child a").click()

            time.sleep(1)
            
            firefox.find_element(By.CSS_SELECTOR, "#menu .nivel-overlay div.nivel-aberto ul li:first-child a").click()

            iframe = WebDriverWait(firefox, 60).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            element = WebDriverWait(firefox, 120).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
            firefox.execute_script("arguments[0].click();", element)

            # Registra horario que iniciou a tarefa
            inicio = time.time()

            logging.info('---------------------------')
            logging.info('Tarefa localizada: ' + str(atividade))
            logging.info('---------------------------')

            time.sleep(2)

            logging.info('Iniciando a busca pelo os processos...')

            listDataProcessos = openXls.getDataProcessTrasidarJulgadoXLS(xlsData, firefox, logging, xml)

            for i in range(len(listDataProcessos)):
                logging.info('Buscando o processo: ' + str(listDataProcessos[i][0]))
                self.localizarProcesso(firefox, listDataProcessos[i][0], listDataProcessos[i][1], logging, caminhoImages)

            logging.info('---------------------------')

            ###################################
            # Verificacao dos processos localizado e encaminhados
            ###################################

            if len(self.listProcessos[0]) > 0:
                logging.info('Lista de processos encontrados:')
                for i in range(len(self.listProcessos[0])):
                    logging.info('Processo: ' + str(self.listProcessos[0][i]))

                logging.info("Total de processos encontrados: " + str(len(self.listProcessos[0])))
                logging.info("Total de processos encaminhados: " + str(self.countEncaminhados))
            else:
                logging.info('Nenhum processo foi encontrado.')

            self.listProcessos.append(len(self.listProcessos[0]))
            self.listProcessos.append(self.countEncaminhados)

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

            firefox.switch_to.default_content()

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