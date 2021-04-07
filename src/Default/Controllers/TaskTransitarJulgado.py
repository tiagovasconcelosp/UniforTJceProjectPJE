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

from src.Default.Controllers.Print import Print


class TaskTransitarJulgado:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[],[],[],]
    countEncaminhados = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countEnviaProcesso = 0
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def localizarProcesso(self, firefox, numProcesso, dateProcesso, logging, caminhoImages):

        registroProcessoEncontrado = 0
        registroErroPortal = 0
        countErro = 0

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

        try:
            # Clica no primeiro processo retornado
            element = WebDriverWait(firefox, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))
            firefox.execute_script("arguments[0].click();", element)

            logging.info('Processo ' + str(numProcesso) + ' foi localizado.')
            self.listProcessos[0].append(str(numProcesso))

            # Adicao previa de nao concluido
            self.listProcessos[1].append(1)

            time.sleep(4)

        except:
            self.listProcessos[2].append(str(numProcesso))
            logging.info('Processo ' + str(numProcesso) + ' nao foi localizado.')
            # registroProcessoEncontrado += 1

            return self.listProcessos

        # if registroProcessoEncontrado == 0:

        # Clica no botao para abrir o processo - Autos
        element = WebDriverWait(firefox, 20).until(
            EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.header-wrapper div.toolbar-processo button[tooltip="Autos"i]')))
        firefox.execute_script("arguments[0].click();", element)

        time.sleep(3)

        logging.info('Aguardando a nova janela ser aberta.')

        try:
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

        except:
            logging.info('Houve um problema ao encontrar a nova tela.')
            logging.info('---------------------------')

            countErro += 1

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
            logging.info('Houve um problema na etapa de incluir peticoes. Por ter ocorrido algum problema de conexao.')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

        try:
            # Seleciona o Tipo de Documento
            select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]'))
            select.select_by_visible_text('Certidão')

            time.sleep(2)
        except:
            logging.info('Houve um problema na etapa de selecionar o Tipo Documento')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

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
                logging.info('Houve um problema na etapa de selecionar o Modelo')
                logging.info('Evidenciando com o print da tela.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)
                countErro += 1

        try:
            # Seleciona o Tipo de Documento
            select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]'))
            select.select_by_visible_text('Certidão trânsito em julgado')

            time.sleep(2)
        except:
            logging.info('Houve um problema na etapa de selecionar o Tipo de Documento')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

        try:
            # Clica no botao Preencher Documentos
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'table#selectedEventsTable td a[name="selectedEventsTable:0:linkComplementos"i]')))
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(3)
        except:
            logging.info('Houve um problema na etapa de selecionar o botao Preencher Documentos')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

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
            logging.info('Houve um problema na etapa de informar a data')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

        try:
            # Clica no botao Salvar
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[value="Salvar"i]')))
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(3)
        except:
            logging.info('Houve um problema ao salvar o processo.')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)
            countErro += 1

        try:
            # Clica no botao Assinar Documento
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input#btn-assinador')))
            firefox.execute_script("arguments[0].click();", element)

            # Aguarda a Assinatura, demora em torno de 8s. Pois uso a leitura do certificado
            time.sleep(8)

        except:
            logging.info('Houve um problema realizar a assinatura.')
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)

        try:
            firefox.close()
        except:
            firefox.quit()

        time.sleep(3)

        # Para sair do objeto popup
        firefox.switch_to.window(main_window_handle)

        firefox.switch_to.default_content()

        # Localiza frame alerta de documento nao assinados
        iframe = WebDriverWait(firefox, 10).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        firefox.switch_to.frame(iframe)


        ##################################################################################
        try:
            # Clica no botao Encaminhar para (ABRE AS OPCOES)
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.dropdown button#btnTransicoesTarefa')))
            firefox.execute_script("arguments[0].click();", element)
        except:

            time.sleep(10)

            try:
                # Clica no botao Encaminhar para
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.dropdown button#btnTransicoesTarefa')))
                firefox.execute_script("arguments[0].click();", element)

            except:

                logging.info('Houve um problema na etapa encaminhar para...')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)
                countErro += 1

        ##################################################################################

        time.sleep(1)

        ##################################################################################
        try:
            # Clica no botao Cumprir acordao
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.dropdown-transicoes li a[title="Encaminhar para Cumprir acórdão"i]')))
            firefox.execute_script("arguments[0].click();", element)
        except:

            logging.info('Tentando novamente "Encaminhar para Cumprir acórdão" . . .')

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

                registroErroPortal += 1
                countErro += 1

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(1)

        if registroErroPortal > 0 or countErro > 0:
            return self.listProcessos

        ##################################################################################

        time.sleep(5)

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
                    element = WebDriverWait(firefox, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                    firefox.execute_script("arguments[0].click();", element)

                except:
                    logging.info('Houve um problema na etapa Encaminhar para... segunda etapa')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)
            ##################################################################################

            time.sleep(4)

            ##################################################################################
            try:
                # Clica no botao Encaminhar para 02 - Devolver para instância de origem
                element = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'ul li a[title="Encaminhar para 02 - Devolver para instância de origem"i]')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(20)

            except:

                logging.info('Tentando novamente "Encaminhar para 02 - Devolver para instância de origem" . . .')

                time.sleep(10)

                try:
                    # Clica no botao Encaminhar para 02 - Devolver para instância de origem
                    element = WebDriverWait(firefox, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'ul li a[title="Encaminhar para 02 - Devolver para instância de origem"i]')))
                    firefox.execute_script("arguments[0].click();", element)
                    #############
                    time.sleep(20)

                except:
                    logging.info('Houve um problema na etapa devolver para instancia de origem.')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)
            ##################################################################################
            try:
                # Localiza frame
                iframe = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                firefox.switch_to.frame(iframe)

                # Aguarda elemento carregar em tela
                element = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.propertyView div.value select')))

                # Seleciona o Motivo da Remessa
                select = Select(firefox.find_element(By.CSS_SELECTOR, 'div.propertyView div.value select'))
                select.select_by_visible_text('outros motivos')

                time.sleep(3)
            except:

                logging.info('Tentando novamente selecionar "Motivo Remessa" . . .')
                #############
                time.sleep(20)

                try:
                    # Localiza frame
                    iframe = WebDriverWait(firefox, 30).until(
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
                element = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'input.btn-primary[value="Retornar para instância de origem"i]')))
                firefox.execute_script("arguments[0].click();", element)

                time.sleep(25)

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(0)
                self.countEncaminhados += 1

                ##################################################################################
                try:
                    # Clica no botao Confirmar
                    # element = WebDriverWait(firefox, 10).until(
                    #     EC.presence_of_element_located(
                    #         (By.CSS_SELECTOR,
                    #          'input.btn-primary[value="Confirmar"i]')))

                    element = firefox.find_element(By.CSS_SELECTOR, 'input.btn-primary[value="Confirmar"i]')

                    time.sleep(15)

                    ###############
                    # Altercao Karyna - Nao clica no confirmar
                    # firefox.execute_script("arguments[0].click();", element)
                    ###############

                    logging.info('Esse processo não será assinado. Mensagem apareceu.')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)
                    logging.info('---------------------------')

                    # Deleta o ultimo registro
                    del(self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro como nao assinado
                    self.listProcessos[1].append(1)
                    self.countEncaminhados += 1

                    # logging.info('Clicando em confirmar.')

                except:
                    logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                ##################################################################################

                time.sleep(2)

            # Caso haja falha tentar mais uma vez o processo de envio
            except:

                logging.info('Houver falha, tentando novamente . . .')

                logging.info('Tentando novamente "Retornar para instância de origem" . . .')

                time.sleep(10)

                try:

                    # Clica no botao Retornar para Instancia de Origem
                    element = WebDriverWait(firefox, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'input.btn-primary[value="Retornar para instância de origem"i]')))
                    firefox.execute_script("arguments[0].click();", element)

                    time.sleep(25)

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro
                    self.listProcessos[1].append(0)
                    self.countEncaminhados += 1

                    ##################################################################################
                    try:
                        # Clica no botao Confirmar
                        # element = WebDriverWait(firefox, 10).until(
                        #     EC.presence_of_element_located(
                        #         (By.CSS_SELECTOR,
                        #          'input.btn-primary[value="Confirmar"i]')))

                        element = firefox.find_element(By.CSS_SELECTOR, 'input.btn-primary[value="Confirmar"i]')

                        time.sleep(15)

                        ###############
                        # Altercao Karyna - Nao clica no confirmar
                        # firefox.execute_script("arguments[0].click();", element)
                        ###############

                        logging.info('Esse processo não será assinado. Mensagem apareceu.')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(firefox, caminhoImages)
                        logging.info('---------------------------')

                        # Deleta o ultimo registro
                        del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                        # Inclui novo registro como nao assinado
                        self.listProcessos[1].append(1)
                        self.countEncaminhados += 1

                        # logging.info('Clicando em confirmar.')

                    except:
                        logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                    ##################################################################################

                    time.sleep(2)

                except Exception as e:

                    logging.info('Houve um problema ao retornar para instancia de origem.')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(firefox, caminhoImages)

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro

                    self.listProcessos[1].append(1)

                    # Localiza frame alerta de documento nao assinados
                    iframe = WebDriverWait(firefox, 30).until(
                        EC.presence_of_element_located((By.ID, 'ngFrame')))

                    firefox.switch_to.frame(iframe)

                    # raise e from None

            firefox.switch_to.default_content()

            # Localiza frame alerta de documento nao assinados
            iframe = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            return self.listProcessos

        else:
            logging.info('Houve um travamento do processo no sistema ao clica em Encaminhar para Cumprir acardao.')

            return self.listProcessos

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

        self.countEncaminhados = 0

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

            # print(self.listProcessos)

            try:
                firefox.close()
            except:
                firefox.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

            return self.listProcessos

        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos