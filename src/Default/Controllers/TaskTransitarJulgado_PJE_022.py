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

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Controllers.Print import Print
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Perfil import Perfil


class TaskTransitarJulgado_PJE_022:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countEncaminhados = 0

    def __init__(self, driver, caminhoImagesPrint, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, 
                 url, dataForm, xml, log_unificado):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0

        self.Execute(driver, caminhoImagesPrint, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, 
                 url, dataForm, xml, log_unificado)

    def localizarProcesso(self, driver, numProcesso, dateProcesso, logging, caminhoImages, log_unificado):

        # registroProcessoEncontrado = 0
        registroErroPortal = 0
        countErro = 0

        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located(
                (By.ID, 'inputPesquisaTarefas')))
        element.clear()

        driver.find_element(By.ID, "inputPesquisaTarefas").send_keys(numProcesso)

        element = driver.find_element(By.CSS_SELECTOR, '#divActions button[title="Pesquisar"]')
        driver.execute_script("arguments[0].click();", element)

        time.sleep(1)

        # Valida se houve mais de um resultado
        # caminho no ambiente da unifor
        # element = driver.find_element(By.CSS_SELECTOR, 'span[title="Quantidade de processos na tarefa"]').text
        element = driver.find_element(By.CSS_SELECTOR,
                                       'div#divProcessosTarefa div.painel-listagem div.row span.badge').text

        # Verifica se retornou mais de um processo
        if int(element) > 1:

            logging.info('---------------------------')
            logging.info('Foi encontrado mais de um resultado. Total: ' + str(element))
            logging.info('Evidenciando com o print da tela.')
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)

        time.sleep(2)

        try:
            # Clica no primeiro processo retornado
            element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))
            driver.execute_script("arguments[0].click();", element)

            logging.info('Processo ' + str(numProcesso) + ' foi localizado.')
            self.listProcessos[0].append(str(numProcesso))

            # Adicao previa de nao concluido
            self.listProcessos[1].append(1)
            log_unificado.adicionar_processo(str(numProcesso))

            time.sleep(2)

        except Exception as e:
            self.listProcessos[2].append(str(numProcesso))
            logging.info('Processo ' + str(numProcesso) + ' nao foi localizado.')
            # logging.info(repr(e))
            # registroProcessoEncontrado += 1

            return self.listProcessos

        # if registroProcessoEncontrado == 0:

        # Clica no botao para abrir o processo - Autos
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.header-wrapper div.toolbar-processo button[tooltip="Autos"i]')))
        driver.execute_script("arguments[0].click();", element)

        time.sleep(3)

        logging.info('Aguardando a nova janela ser aberta.')

        try:
            # Localiza a nova janela aberta
            ##########################################################
            main_window_handle = None
            while not main_window_handle:
                main_window_handle = driver.current_window_handle

            signin_window_handle = None
            while not signin_window_handle:
                for handle in driver.window_handles:
                    if handle != main_window_handle:
                        signin_window_handle = handle
                        break
            driver.switch_to.window(signin_window_handle)
            ##########################################################

            logging.info('Nova janela encontrada.')
            logging.info('---------------------------')

        except Exception as e:
            logging.info('Houve um problema ao encontrar a nova tela.')
            logging.info(repr(e))
            logging.info('---------------------------')

            countErro += 1

        try:
            # Clica no botao para Juntar documentos
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.menu-icones-topo a[name="navbar:linkAbaIncluirPeticoes1"i]')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(2)

            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="cbTDDecoration:cbTD"]')))

            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="modTDDecoration:modTD"]')))
            
            

        except Exception as e:            
            logging.info('Houve um problema na etapa de incluir peticoes. Por ter ocorrido algum problema de conexao.')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)
            countErro += 1

        time.sleep(2)

        try:

            # Seleciona o Tipo de Documento
            # select = Select(driver.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="cbTDDecoration:cbTD"i]'))
            select = Select(driver.find_element(By.XPATH, '//*[@id="cbTDDecoration:cbTD"]'))

            select.select_by_visible_text('Certidão trânsito em julgado')
            # select.select_by_value('14')

        except Exception as e:
            logging.info('Houve um problema na etapa de selecionar o Tipo Documento')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)
            countErro += 1

        time.sleep(2)

        try:
            # Seleciona o Modelo
            # select = Select(driver.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="modTDDecoration:modTD"i]'))
            select = Select(driver.find_element(By.XPATH, '//*[@id="modTDDecoration:modTD"]'))

            select.select_by_visible_text('Certificação Trânsito em Julgado')
            # select.select_by_value('51')

        except Exception as e:
            logging.info(repr(e))
            time.sleep(1)
            try:
                # Seleciona o Modelo
                # select = Select(driver.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="modTDDecoration:modTD"i]'))
                select = Select(driver.find_element(By.XPATH, '//*[@id="modTDDecoration:modTD"]'))

                select.select_by_visible_text('Certificação Trânsito em Julgado')
                # select.select_by_value('51')

                time.sleep(1)


            except Exception as e:
                logging.info(repr(e))
                # Mudança de nome que vem aconter
                try:
                    # Seleciona o Modelo
                    # select = Select(driver.find_element(By.CSS_SELECTOR, 'div.col-sm-12 select[name="modTDDecoration:modTD"i]'))
                    select = Select(driver.find_element(By.XPATH, '//*[@id="modTDDecoration:modTD"]'))

                    select.select_by_visible_text('Certificação de Trânsito em Julgado')

                except Exception as e:
                    logging.info('Houve um problema na etapa de selecionar o Modelo')
                    logging.info('Evidenciando com o print da tela.')
                    logging.info(repr(e))
                    logging.info('---------------------------')
                    image = Print(driver, caminhoImages)
                    countErro += 1

                    # ##############################

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro
                    # Caso nao tenha o botao emcaminhar
                    # coluna encaminhado com valor 1 para não encaminhado
                    self.listProcessos[1].append(1)

                    try:
                        driver.close()
                    except:
                        driver.quit()

                    time.sleep(3)

                    # Para sair do objeto popup
                    driver.switch_to.window(main_window_handle)

                    driver.switch_to.default_content()

                    # Localiza frame alerta de documento nao assinados
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'ngFrame')))

                    driver.switch_to.frame(iframe)

                    driver.find_element(By.ID, "inputPesquisaTarefas").clear()

                    return self.listProcessos
                    # ##############################

        time.sleep(2)

        try:
            # Clica no botao Preencher Documentos
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                    By.CSS_SELECTOR, 'table#selectedEventsTable td a[name="selectedEventsTable:0:linkComplementos"i]')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(4)

        except Exception as e:
            logging.info('Houve um problema na etapa de selecionar o botao Preencher Documentos')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)
            countErro += 1

        try:
            # Inclui a Data
            driver.find_element(By.CSS_SELECTOR, "div.clearfix div.col-sm-4 div.col-sm-12 input").send_keys(
                dateProcesso)
            time.sleep(1)

            # Clica no botao Ok
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#complementosInner input#botaoGravarMovimento')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(4)

            # Clica em editar texto
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'table#raTipoDocPrincipal input[value="HTML"i]')))
            driver.execute_script("arguments[0].click();", element)

        except Exception as e:
            logging.info('Houve um problema na etapa de informar a data')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)
            countErro += 1

        try:
            # Clica no botao Salvar
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input[value="Salvar"i]')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(3)
            log_unificado.atualizar_etapa_processo(
                processo= str(numProcesso),
                etapa="JUNTAR DOCUMENTOS",
                atualizacao ="Realizado"
            )

        except Exception as e:
            log_unificado.enviar_erro(
                num_processo = str(numProcesso),
                passo_Executado = "JUNTAR DOCUMENTOS",
                mensagem=repr(e)
            )
            logging.info('Houve um problema ao salvar o processo.')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)
            countErro += 1


        try:
            # Clica no botao Assinar Documento
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'input#btn-assinador')))
            driver.execute_script("arguments[0].click();", element)

            # Aguarda a Assinatura, demora em torno de 8s. Pois uso a leitura do certificado
            time.sleep(8)
            log_unificado.atualizar_etapa_processo(
                processo= str(numProcesso),
                etapa="ASSINAR DOCUMENTO",
                atualizacao ="Realizado"
            )

        except Exception as e:
            log_unificado.enviar_erro(
                num_processo = str(numProcesso),
                passo_Executado = "ASSINAR DOCUMENTO",
                mensagem=repr(e)
            )
            logging.info('Houve um problema realizar a assinatura.')
            logging.info('Evidenciando com o print da tela.')
            logging.info(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImages)


        try:
            driver.close()
        except:
            driver.quit()

        time.sleep(3)

        # Para sair do objeto popup
        driver.switch_to.window(main_window_handle)

        driver.switch_to.default_content()

        # Localiza frame alerta de documento nao assinados
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        driver.switch_to.frame(iframe)

        ##################################################################################
        try:
            # Clica no botao Encaminhar para (ABRE AS OPCOES)
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.dropdown button#btnTransicoesTarefa')))
            driver.execute_script("arguments[0].click();", element)

        except Exception as e:
            logging.info(repr(e))
            time.sleep(30)

            try:
                # Clica no botao Encaminhar para
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.dropdown button#btnTransicoesTarefa')))
                driver.execute_script("arguments[0].click();", element)

                log_unificado.atualizar_etapa_processo(
                    processo= str(numProcesso),
                    etapa="ENCAMINHAR PARA OUTRAS DILIGENCIAS",
                    atualizacao ="Realizado"
                )
            except Exception as e:
                log_unificado.enviar_erro(
                    num_processo = str(numProcesso),
                    passo_Executado = "ENCAMINHAR PARA OUTRAS DILIGENCIAS",
                    mensagem=repr(e)
                )
                logging.info(repr(e))

                logging.info('Houve um problema na etapa encaminhar para...')
                logging.info('Evidenciando com o print da tela.')
                image = Print(driver, caminhoImages)
                countErro += 1

        ##################################################################################

        time.sleep(3)

        ##################################################################################
        try:
            # Clica no botao Cumprir acordao
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'ul.dropdown-transicoes li a[title="Encaminhar para Concluir"i]')))
            driver.execute_script("arguments[0].click();", element)

        except Exception as e:

            logging.info('Tentando novamente "Encaminhar para Cumprir acórdão" . . .')
            logging.info(repr(e))


            time.sleep(30)

            try:
                # Clica no botao Cumprir acordao
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'ul.dropdown-transicoes li a[title="Encaminhar para Concluir"i]')))
                driver.execute_script("arguments[0].click();", element)

            except Exception as e:
                logging.info('Houve um problema na etapa Encaminhar para Cumprir acórdão...')
                logging.info('Evidenciando com o print da tela.')
                logging.info(repr(e))
                image = Print(driver, caminhoImages)

                registroErroPortal += 1
                countErro += 1

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(1)

        if registroErroPortal > 0 or countErro > 0:
            return self.listProcessos

        ##################################################################################

        time.sleep(3)

        ##################################################################################

        if registroErroPortal == 0:
            try:
                # Clica no botao Encaminhar para (ABRE AS OPCOES NOVAMENTE)
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                driver.execute_script("arguments[0].click();", element)

            except Exception as e:
                logging.info(repr(e))
                time.sleep(30)

                try:
                    # Clica no botao Encaminhar para (ABRE AS OPCOES NOVAMENTE)
                    element = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'button#btnTransicoesTarefa')))
                    driver.execute_script("arguments[0].click();", element)

                except Exception as e:
                    logging.info(repr(e))

                    logging.info('Houve um problema na etapa Encaminhar para... segunda etapa')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(driver, caminhoImages)
            ##################################################################################

            time.sleep(2)

            ##################################################################################
            try:
                # Clica no botao Encaminhar para 10 - Devolver para a origem
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'ul li a[title="Encaminhar para 10 - Devolver para a origem"i]')))
                driver.execute_script("arguments[0].click();", element)

                time.sleep(30)

            except Exception as e:

                logging.info('Tentando novamente "Encaminhar para 10 - Devolver para a origem" . . .')
                logging.info(repr(e))

                time.sleep(30)

                try:
                    # Clica no botao Encaminhar para 02 - Devolver para instância de origem
                    element = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'ul li a[title="Encaminhar para 10 - Devolver para a origem"i]')))
                    driver.execute_script("arguments[0].click();", element)

                    #############
                    time.sleep(20)

                except Exception as e:


                    logging.info('Houve um problema na etapa devolver para a origem.')
                    logging.info('Evidenciando com o print da tela.')
                    logging.info(repr(e))
                    image = Print(driver, caminhoImages)
            ##################################################################################
            try:
                # Localiza frame
                iframe = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                driver.switch_to.frame(iframe)

                # Aguarda elemento carregar em tela
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.propertyView div.value select')))

                # Seleciona o Motivo da Remessa
                select = Select(driver.find_element(By.CSS_SELECTOR, 'div.propertyView div.value select'))
                # select.select_by_visible_text('outros motivos')
                select.select_by_visible_text('por julgamento definitivo do recurso')

                time.sleep(3)

            except Exception as e:

                logging.info('Tentando novamente selecionar "Motivo Remessa" . . .')
                logging.info(repr(e))
                #############
                time.sleep(20)

                try:
                    # Localiza frame
                    iframe = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.ID, 'frame-tarefa')))

                    driver.switch_to.frame(iframe)

                    # Aguarda elemento carregar em tela
                    element = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.propertyView div.value select')))

                    # Seleciona o Motivo da Remessa
                    select = Select(driver.find_element(By.CSS_SELECTOR, 'div.propertyView div.value select'))
                    # select.select_by_visible_text('outros motivos')
                    select.select_by_visible_text('por julgamento definitivo do recurso')

                    time.sleep(3)

                except Exception as e:
                    logging.info(repr(e))

                    logging.info('Houve um problema na etapa de selecionar o motivo da remessa.')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(driver, caminhoImages)
            ##################################################################################
            time.sleep(1)
            ##################################################################################
            try:
                # Clica no botao Retornar para Instancia de Origem
                element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'input.btn-primary[value="Retornar para instância de origem"i]')))
                driver.execute_script("arguments[0].click();", element)

                time.sleep(25)

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(0)
                self.countEncaminhados += 1

                log_unificado.atualizar_etapa_processo(
                    processo= str(numProcesso),
                    etapa="RETORNAR PARA INSTANCIA DE ORIGEM",
                    atualizacao ="Realizado"
                )

                ##################################################################################
                try:
                    element = driver.find_element(By.CSS_SELECTOR, 'input.btn-primary[value="Confirmar"i]')

                    time.sleep(15)

                    ###############
                    # Altercao Karyna - Nao clica no confirmar
                    # driver.execute_script("arguments[0].click();", element)
                    ###############

                    logging.info('Esse processo não será assinado. Mensagem apareceu.')
                    logging.info('Evidenciando com o print da tela.')
                    image = Print(driver, caminhoImages)
                    logging.info('---------------------------')

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro como nao assinado
                    self.listProcessos[1].append(1)
                    self.countEncaminhados += 1

                    # logging.info('Clicando em confirmar.')

                except Exception as e:
                    logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                    logging.info(repr(e))

                ##################################################################################

                time.sleep(2)

            # Caso haja falha tentar mais uma vez o processo de envio
            except Exception as e:
                logging.info(repr(e))

                logging.info('Houver falha, tentando novamente . . .')

                logging.info('Tentando novamente "Retornar para instância de origem" . . .')

                time.sleep(10)

                try:

                    # Clica no botao Retornar para Instancia de Origem
                    element = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'input.btn-primary[value="Retornar para instância de origem"i]')))
                    driver.execute_script("arguments[0].click();", element)

                    time.sleep(25)

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro
                    self.listProcessos[1].append(0)
                    self.countEncaminhados += 1

                    ##################################################################################
                    try:
                        element = driver.find_element(By.CSS_SELECTOR, 'input.btn-primary[value="Confirmar"i]')

                        time.sleep(15)

                        ###############
                        # Altercao Karyna - Nao clica no confirmar
                        # driver.execute_script("arguments[0].click();", element)
                        ###############

                        logging.info('Esse processo não será assinado. Mensagem apareceu.')
                        logging.info('Evidenciando com o print da tela.')
                        image = Print(driver, caminhoImages)
                        logging.info('---------------------------')

                        # Deleta o ultimo registro
                        del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                        # Inclui novo registro como nao assinado
                        self.listProcessos[1].append(1)
                        self.countEncaminhados += 1

                        # logging.info('Clicando em confirmar.')

                    except Exception as e:
                        logging.info(repr(e))

                        logging.info('Nao houver alerta de documentos nao assinados nesse processo. Continuando . . .')
                    ##################################################################################

                    time.sleep(2)

                except Exception as e:

                    logging.info('Houve um problema ao retornar para instancia de origem.')
                    logging.info('Evidenciando com o print da tela.')
                    logging.info(repr(e))
                    image = Print(driver, caminhoImages)

                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro

                    self.listProcessos[1].append(1)

                    # Localiza frame alerta de documento nao assinados
                    iframe = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.ID, 'ngFrame')))

                    driver.switch_to.frame(iframe)

                    # raise e from None

                    log_unificado.enviar_erro(
                        num_processo = str(numProcesso),
                        passo_Executado = "RETORNAR PARA INSTANCIA DE ORIGEM",
                        mensagem=repr(e)
                    )

            driver.switch_to.default_content()

            # Localiza frame alerta de documento nao assinados
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            driver.switch_to.frame(iframe)

            return self.listProcessos

        else:


            logging.info('Houve um travamento do processo no sistema ao clica em Encaminhar para Cumprir acardao.')

            return self.listProcessos

    def Execute(self, driver, caminhoImages, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, 
         url, dataForm, xml, log_unificado):
        
        log_unificado.criar_arquivo_executados(
            ["VERIFICADO CERTIDAO DE TRANSITO EM JULGADO", "ASSINAR DOCUMENTO", "ENCAMINHAR PARA OUTRAS DILIGENCIAS", "RETORNAR PARA INSTANCIA DE ORIGEM"]
        )

        self.countEncaminhados = 0

        metodos = Metodos(url)
        driver.get(url)
        logging.info('##############################')
        logging.info('Robô iniciado')
        logging.info('Acesso da Url: ' + url)
        time.sleep(5)
        autenticacao = Auth()
        autenticacao.LoginPje2g(driver, logging, dataForm, url)

        # Seleciona o perfil
        selecionarPerfil = Perfil(driver, logging, dataForm['perfil'])

        try:

            time.sleep(3)

            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            time.sleep(1)

            driver.find_element(By.CSS_SELECTOR, "#menu div.nivel-aberto ul li:first-child a").click()

            time.sleep(1)

            driver.find_element(By.CSS_SELECTOR, "#menu .nivel-overlay div.nivel-aberto ul li:first-child a").click()

            iframe = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            driver.switch_to.frame(iframe)

            element = WebDriverWait(driver, 40).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
            driver.execute_script("arguments[0].click();", element)

            logging.info('---------------------------')
            logging.info('Tarefa localizada: ' + str(atividade))
            logging.info('---------------------------')

            time.sleep(2)

            logging.info('Iniciando a busca pelo os processos...')

            listDataProcessos = openXls.getDataProcessTrasitarJulgadoXLS(xlsData, driver, logging, xml)

            for i in range(len(listDataProcessos)):

                # Registra horario que iniciou o processo
                inicioTimeProc = time.time()

                logging.info('Buscando o processo: ' + str(listDataProcessos[i][0]))
                self.localizarProcesso(driver, listDataProcessos[i][0], listDataProcessos[i][1], logging,
                                       caminhoImages)

                fimProc = time.time()
                timeTotal = fimProc - inicioTimeProc
                timeTotal = float('{:.2f}'.format(timeTotal))

                try:
                    # Inclui processo na lista dataset
                    dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[0][i]))
                    dataBaseModel['individual']['processo_realizado'].append(str(self.listProcessos[1][i]))
                    dataBaseModel['individual']['tempo_execucao_individual_sec'].append(str(timeTotal))

                except:
                    logging.info('Falha ao registrar os dados individual na lista.')

                logging.info('---------------------------')
                logging.info('---------------------------')
                logging.info('---------------------------')

            # for i in range(len(self.listProcessos[0])):
            #     dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[0][i]))
            #     dataBaseModel['individual']['processo_realizado'].append(str(self.listProcessos[1][i]))
            #     dataBaseModel['individual']['processo_nao_encontrado'].append(0)

            try:
                if self.listProcessos[2]:
                    for i in range(len(self.listProcessos[2])):
                        dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[2][i]))
                        dataBaseModel['individual']['processo_realizado'].append(1)
                        dataBaseModel['individual']['processo_nao_encontrado'].append(1)
                        dataBaseModel['individual']['tempo_execucao_individual_sec'].append(0)

            except:
                logging.info('Falha ao registrar os dados individual.')

            logging.info('---------------------------')
            logging.info('Dados gerados apos conclusao da super classe - individual')
            logging.info(dataBaseModel)
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

            timeTotal = fim - inicioTime

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

            driver.switch_to.default_content()

            # Registra base
            dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
            dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
            dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

            try:
                driver.close()
            except:
                driver.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

            return self.listProcessos


        except Exception as e:


            logging.info('---------------------------')
            logging.info('Atividade Erro:')
            logging.info(dataBaseModel)

            image = Print(driver, caminhoImages)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            # logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos