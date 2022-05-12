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

from selenium.webdriver.common.action_chains import ActionChains
from src.Default.Controllers.Print import Print


class TaskAssinaturaLancamento:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countEncaminhados = 0

    # Geração de dados
    qtd_clicks_all = 0
    qtd_erros_tentativa_processo_all = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml, dataBaseModel, inicioTime,
                 arrayVarRefDados):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countEnviaProcesso = 0
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml, dataBaseModel, inicioTime,
                     arrayVarRefDados)

    def localizarProcesso(self, firefox, numProcesso, codRecorrente, logging, caminhoImages):

        try:
            element = WebDriverWait(firefox, 120).until(
                EC.presence_of_element_located(
                    (By.ID, 'inputPesquisaTarefas')))
            element.clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            firefox.find_element(By.ID, "inputPesquisaTarefas").send_keys(numProcesso)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            element = firefox.find_element(By.CSS_SELECTOR, '#divActions button[title="Pesquisar"]')
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(2)

            # Valida se houve mais de um resultado
            element = firefox.find_element(By.CSS_SELECTOR,
                                           'div#divProcessosTarefa div.painel-listagem div.row span.badge').text

            # Verifica se retornou mais de um processo
            if int(element) > 1:
                logging.info('---------------------------')
                logging.info('Foi encontrado mais de um resultado. Total: ' + str(element))
                logging.info('Evidenciando com o print da tela.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

            time.sleep(3)

            # Clica no primeiro processo retornado
            element = WebDriverWait(firefox, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            logging.info('Processo ' + str(numProcesso) + ' foi localizado.')
            self.listProcessos[0].append(str(numProcesso))

            # Adicao previa de nao concluido
            self.listProcessos[1].append(1)

            time.sleep(5)

        except:
            logging.info('Processo nao localizado: ' + str(numProcesso))
            logging.info('Evidenciando com o print da tela.')
            image = Print(firefox, caminhoImages)
            self.listProcessos[2].append(str(numProcesso))
            firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1

            return self.listProcessos

        try:

            try:
                # Clica no botao para abrir o processo
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.header-wrapper div.toolbar-processo button[tooltip="Autos"i]')))
                firefox.execute_script("arguments[0].click();", element)
            except:
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div#conteudoTarefa div.col-md-12 div.btn-toolbar button[tooltip="Autos"i]')))
                firefox.execute_script("arguments[0].click();", element)
                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(4)

            logging.info('Aguardando a nova janela ser aberta.')

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

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1

            firefox.switch_to.default_content()

            # Localiza frame para o proximo processo
            iframe = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            try:
                firefox.close()
            except:
                firefox.quit()

            return self.listProcessos

        try:
            # Clica no botao para Juntar documentos
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'form#navbar ul li.mais-detalhes a')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(2)

            # Paga as informacoes da quantidade de Recorrente e Recorrido para saber se sera executado
            qtdRecorrente = firefox.find_elements_by_css_selector('div#poloAtivo table tbody tr')
            qtdRecorrido = firefox.find_elements_by_css_selector('div#poloPassivo table tbody tr')

            # if len(qtdRecorrente) > 1 or len(qtdRecorrido) > 1:
            if len(qtdRecorrente) > 1:

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                # Caso nao tenha o botao emcaminhar
                # coluna encaminhado com valor 3 para mais de um recorrente
                self.listProcessos[1].append(3)

                logging.info('---------------------------')
                logging.info('O processo ' + str(numProcesso) + ' possui mais de um Recorrente ou Recorrido.')
                logging.info('Evidenciando com o print da tela.')
                logging.info('Interrompedo a execução desse processo.')
                logging.info('Iniciando a busca pelo proximo processo.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                try:
                    firefox.close()
                except:
                    firefox.quit()

                time.sleep(4)

                # Para sair do objeto popup
                firefox.switch_to.window(main_window_handle)

                firefox.switch_to.default_content()

                # Localiza frame para o proximo processo
                iframe = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located((By.ID, 'ngFrame')))

                firefox.switch_to.frame(iframe)

                firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                return self.listProcessos

            nameRecorrente = firefox.find_element(By.CSS_SELECTOR,
                                                  'div#poloAtivo table tbody tr td span').text

            nameRecorrido = firefox.find_element(By.CSS_SELECTOR,
                                                 'div#poloPassivo table tbody tr td span').text

            logging.info('---------------------------')
            logging.info('Encontrado o recorrente: ' + str(nameRecorrente))
            logging.info('Encontrado o recorrido: ' + str(nameRecorrido))
            logging.info('---------------------------')

        except:
            logging.info('---------------------------')
            logging.info('Houve um erro ao procurar pela informacoes do recorrente e recorrido.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1

            # Deleta o ultimo registro
            del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
            # Inclui novo registro
            # Caso nao tenha o botao emcaminhar
            # coluna encaminhado com valor 3 para mais de um recorrente
            self.listProcessos[1].append(1)

            # Fecha janela aberta
            try:
                firefox.close()
            except:
                firefox.quit()

            # Para sair do objeto popup
            firefox.switch_to.window(main_window_handle)

            firefox.switch_to.default_content()

            # Localiza frame para o proximo processo
            iframe = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            return self.listProcessos

        try:
            # Fecha janela aberta
            try:
                firefox.close()
            except:
                firefox.quit()

            time.sleep(1)

            # Para sair do objeto popup
            firefox.switch_to.window(main_window_handle)

            firefox.switch_to.default_content()

            # Localiza frame para o proximo processo
            iframe = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            iframe = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located((By.ID, 'frame-tarefa')))

            firefox.switch_to.frame(iframe)

            firefox.find_element(By.CSS_SELECTOR,
                                 'form#taskInstanceForm input.inputText').send_keys(
                codRecorrente)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Clica no botao pesquisar
            element = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'form#taskInstanceForm div.rich-panel-body span div.col-sm-6 div.col-sm-12 fieldset input.btn-primary')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(3)

            try:

                codRecorrente = str(codRecorrente)

                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         "*//span[contains(text(), '(" + codRecorrente + ")')]")))

                element = firefox.find_element(By.XPATH,
                                               "*//span[contains(text(), '(" + codRecorrente + ")')]").text

                logging.info('---------------------------')
                logging.info('Codigo localizado: ' + str(element))
                logging.info('---------------------------')

            except Exception as e:

                logging.info(repr(e))

                logging.info('---------------------------')
                logging.info('Nao foi possivel encontrar o codigo de lancamento para o processo: ' + str(numProcesso))
                logging.info('Evidenciando com o print da tela.')
                logging.info('Interrompedo a execução desse processo.')
                logging.info('Iniciando a busca pelo proximo processo.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                firefox.switch_to.default_content()

                # Localiza frame para o proximo processo
                iframe = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located((By.ID, 'ngFrame')))

                firefox.switch_to.frame(iframe)

                firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                return self.listProcessos

            # Usado para consultar a quantidade de elementos gerado, para chegar até o elemento principal
            # elementDiv = ""
            # element = firefox.find_elements_by_css_selector('form#taskInstanceForm .value table')

            try:
                # element = firefox.find_element(By.XPATH,
                #                "*//span[contains(., '(" + codRecorrente + ")')]//ancestor::tr/td[last()]")

                element = firefox.find_element_by_xpath(
                            "*//span[contains(text(), '(" + codRecorrente + ")')]//ancestor-or-self::tr[1]/td[last()]")

            except Exception as e:
                logging.info(repr(e))
                logging.info('---------------------------')
                logging.info('Nao foi possivel localizar elemento com xpath.')
                logging.info('---------------------------')

                image = Print(firefox, caminhoImages)

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                firefox.switch_to.default_content()

                # Localiza frame para o proximo processo
                iframe = WebDriverWait(firefox, 30).until(
                    EC.presence_of_element_located((By.ID, 'ngFrame')))

                firefox.switch_to.frame(iframe)

                firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                return self.listProcessos

            script1 = 'var evt = document.createEvent("MouseEvents");'
            script2 = 'evt.initMouseEvent("mousedown", true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);'
            # script3 = '$x("*//span[contains(text(), \'(230)\')]//ancestor-or-self::tr[1]/td[last()]")[0].dispatchEvent(evt);'
            script4 = 'arguments[0].dispatchEvent(evt);'

            # Seleciona codigo
            firefox.execute_script(script1 + script2 + script4, element)

            # for x in range(len(element)):
            #     elementDiv = elementDiv + ' div'

            # Usa funcoes para simular o uso do mouse, nao é possivel executar por script
            # actions = ActionChains(firefox)
            # actions.click(on_element=element)
            # actions.perform()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Verificar se tem botao "preencher complemento"
            try:
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'a[title="Preencher complementos"i]')))
                firefox.execute_script("arguments[0].click();", element)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                time.sleep(1)

                # Seleciona o recorrente
                select = Select(firefox.find_element(By.CSS_SELECTOR, "form#taskInstanceForm select"))
                select.select_by_visible_text(nameRecorrente)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                # Clica em 'Ok'
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'form#taskInstanceForm  input[value="OK"i]')))
                firefox.execute_script("arguments[0].click();", element)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                logging.info('---------------------------')
                logging.info('O codigo lancado possui complemento.')
                logging.info('Recorrente selecionado com sucesso: ' + str(nameRecorrente))
                logging.info('Finalizando atividade com o processo: ' + str(numProcesso))
                logging.info('---------------------------')
            except Exception as e:

                logging.info(repr(e))
                logging.info('---------------------------')
                logging.info('O codigo lancado nao possui complemento.')
                logging.info('Finalizando atividade com o processo: ' + str(numProcesso))
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

            time.sleep(3)

            # Clica no botao salvar
            # element = WebDriverWait(firefox, 20).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR,
            #          'div.actionButtons input[value="Salvar"i]')))
            # firefox.execute_script("arguments[0].click();", element)

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'form#taskInstanceForm input[value="Salvar"i]')))
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(3)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Aguarda o carregamento novamente do botao
            # element = WebDriverWait(firefox, 20).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR,
            #          'form#taskInstanceForm input[value="Salvar"i]')))

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'form#taskInstanceForm input[value="Assinar digitalmente e finalizar"i]')))
            firefox.execute_script("arguments[0].click();", element)

            time.sleep(10)

            logging.info('Processo assinado.')
            logging.info('---------------------------')

            # Contabiliza dados
            self.qtd_clicks_all += 1

            firefox.switch_to.default_content()

            # Localiza frame para o proximo processo
            iframe = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))
            firefox.switch_to.frame(iframe)

            time.sleep(2)

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.ID, 'inputPesquisaTarefas')))
            element.clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Deleta o ultimo registro
            del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
            # Inclui novo registro
            # Caso nao tenha o botao emcaminhar
            # coluna encaminhado com valor 0 para concluido
            self.listProcessos[1].append(0)

            self.countEncaminhados += 1

            return self.listProcessos

        except Exception as e:
            logging.info(repr(e))

            logging.info('---------------------------')
            logging.info('Nao foi possivel finalizar o processo: ' + str(numProcesso))
            logging.info('Evidenciando com o print da tela.')
            logging.info('Interrompedo a execução desse processo.')
            logging.info('Iniciando a busca pelo proximo processo.')
            logging.info('---------------------------')
            image = Print(firefox, caminhoImages)

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1

            firefox.switch_to.default_content()

            # Localiza frame para o proximo processo
            iframe = WebDriverWait(firefox, 30).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            firefox.switch_to.frame(iframe)

            firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Deleta o ultimo registro
            del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
            # Inclui novo registro
            # Caso nao tenha o botao emcaminhar
            # coluna encaminhado com valor 0 para concluido
            self.listProcessos[1].append(1)

            return self.listProcessos

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml, dataBaseModel,
                inicioTime, arrayVarRefDados):

        self.countEncaminhados = 0

        # try:

        time.sleep(3)

        element = WebDriverWait(firefox, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'a[title="Abrir menu"i]')))
        element.click()

        # Contabiliza dados
        arrayVarRefDados['qtd_clicks'] += 1

        time.sleep(1)

        firefox.find_element(By.CSS_SELECTOR, "#menu div.nivel-aberto ul li:first-child a").click()

        # Contabiliza dados
        arrayVarRefDados['qtd_clicks'] += 1

        time.sleep(1)

        firefox.find_element(By.CSS_SELECTOR, "#menu .nivel-overlay div.nivel-aberto ul li:first-child a").click()

        # Contabiliza dados
        arrayVarRefDados['qtd_clicks'] += 1

        iframe = WebDriverWait(firefox, 60).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        firefox.switch_to.frame(iframe)

        element = WebDriverWait(firefox, 40).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        arrayVarRefDados['qtd_clicks'] += 1

        logging.info('---------------------------')
        logging.info('Tarefa localizada: ' + str(atividade))
        logging.info('---------------------------')

        time.sleep(2)

        logging.info('Iniciando a busca pelo os processos...')

        listDataProcessos = openXls.getDataProcessLancamentoXLS(xlsData, firefox, logging, xml)

        for i in range(len(listDataProcessos)):

            # Registra horario que iniciou o processo
            inicioTimeProc = time.time()

            logging.info('Buscando o processo: ' + str(listDataProcessos[i][0]))
            self.localizarProcesso(firefox, listDataProcessos[i][0], listDataProcessos[i][1], logging,
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

        logging.info('---------------------------')
        logging.info('Dados gerados apos conclusao da super classe')
        logging.info(dataBaseModel)
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
            logging.info('Falha ao registrar os dados individual')

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

        firefox.switch_to.default_content()

        # Registra base
        dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
        dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
        dataBaseModel['qtd_clicks'] = arrayVarRefDados['qtd_clicks'] + self.qtd_clicks_all
        dataBaseModel['qtd_erros_tentativa_processo'] = self.qtd_erros_tentativa_processo_all
        dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

        logging.info('---------------------------')
        logging.info('Final Atividade:')
        logging.info(dataBaseModel)
        logging.info('---------------------------')

        try:
            firefox.close()
        except:
            firefox.quit()

        logging.info('Lista completa para formulario:')
        logging.info(str(self.listProcessos))
        logging.info('---------------------------')

        return self.listProcessos


        # except Exception as e:
        #
        #     dataBaseModel['qtd_erros_robo'] = 1
        #
        #     logging.info('---------------------------')
        #     logging.info('Atividade Erro:')
        #     logging.info(dataBaseModel)
        #     logging.info('---------------------------')
        #
        #     image = Print(firefox, caminhoImages)
        #     logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
        #     logging.info('Finalizando o robo.')
        #     logging.info(repr(e))
        #     # logging.shutdown()
        #
        #     # Retorna valor caso haja algum erro durante a execucao
        #     return self.listProcessos