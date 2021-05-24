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
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Controllers.Print import Print


class TaskAguardandoSessaoJulgamento:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countEncaminhados = 0
    countEnviaProcesso = 0

    # Geração de dados
    qtd_clicks_all = 0
    qtd_erros_tentativa_processo_all = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml, dataset, dataBaseModel, inicioTime, arrayVarRefDados):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countEnviaProcesso = 0
        self.qtd_clicks_all = 0
        self.qtd_erros_tentativa_processo_all = 0
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml, dataset, dataBaseModel, inicioTime, arrayVarRefDados)

    def localizarProcessoEmcaminhar(self, firefox, numProcesso, logging, caminhoImages):

        try:
            element = WebDriverWait(firefox, 120).until(
                EC.presence_of_element_located(
                    (By.ID, 'inputPesquisaTarefas')))
            element.clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            firefox.find_element(By.ID, "inputPesquisaTarefas").send_keys(numProcesso)

            element = firefox.find_element(By.CSS_SELECTOR, '#divActions button[title="Pesquisar"]')
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(1)

            # Valida se houve mais de um resultado
            # caminho no ambiente da unifor
            # element = firefox.find_element(By.CSS_SELECTOR, 'span[title="Quantidade de processos na tarefa"]').text
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

            # Clica no primeiro processo retornado
            element = WebDriverWait(firefox, 10).until(
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

            time.sleep(4)

            # Clica no botao para encaminhar processo
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#btnTransicoesTarefa')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            time.sleep(1)

            try:

                # Clica em encaminhar tarefa
                element = WebDriverWait(firefox, 5).until(  # 5s
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'ul.dropdown-transicoes li a[title="Encaminhar para Encaminhar manualmente para assinatura do inteiro teor"i]')))
                firefox.execute_script("arguments[0].click();", element)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                # elemento aparece e some
                element = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'div.simple-notification-wrapper div.ng-star-inserted div.sn-content')))

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])

                # Inclui novo registro
                self.listProcessos[1].append(0)
                self.countEncaminhados += 1

                # Contagem de reenvio do processo
                self.countEnviaProcesso = 0

                time.sleep(6)

                # Caso seja concluido com sucesso
                # Mensagem demora 6s para sumir
                # if element.is_displayed():
                #     time.sleep(6)

            # Caso haja falha tentar mais uma vez o processo de envio
            except:
                logging.info('Botao Ecaminhar nao localizado.')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

                if self.countEnviaProcesso == 0:
                    self.countEnviaProcesso += 1

                    # Contabiliza dados
                    self.qtd_erros_tentativa_processo_all += 1

                    # Deleta registro de verificacao de encaminhado para executar novamente
                    del (self.listProcessos[0][(len(self.listProcessos[0]) - 1)])
                    logging.info('---------------------------')
                    logging.info(
                        'Houve falha ao encaminhar o processo. Tentando localizar e encaminhar o processo mais uma vez.')
                    logging.info('---------------------------')
                    self.localizarProcessoEmcaminhar(firefox, numProcesso, logging, caminhoImages)

                else:
                    # Deleta o ultimo registro
                    del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                    # Inclui novo registro
                    # Caso nao tenha o botao emcaminhar
                    # coluna encaminhado com valor 1 para não encaminhado
                    self.listProcessos[1].append(1)

                firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

        except:
            logging.info('Processo nao localizado.')
            logging.info('Evidenciando com o print da tela.')
            image = Print(firefox, caminhoImages)
            self.listProcessos[2].append(str(numProcesso))
            firefox.find_element(By.ID, "inputPesquisaTarefas").clear()

            # Contabiliza dados
            self.qtd_clicks_all += 1

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1


        return self.listProcessos

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml, dataset, dataBaseModel, inicioTime, arrayVarRefDados):

        self.countEncaminhados = 0

        try:

            time.sleep(3)

            element = WebDriverWait(firefox, 200).until(
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

            # Registra horario que iniciou a tarefa
            # inicio = time.time()

            logging.info('---------------------------')
            logging.info('Tarefa localizada: ' + str(atividade))
            logging.info('---------------------------')

            time.sleep(2)

            logging.info('Iniciando a busca pelo os processos...')

            listDataProcessos = openXls.getDataProcessAguardandoSessaoXLS(xlsData, firefox, logging, xml)

            for i in range(len(listDataProcessos)):
                logging.info('Buscando o processo: ' + str(listDataProcessos[i]))
                self.localizarProcessoEmcaminhar(firefox, listDataProcessos[i], logging, caminhoImages)

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
            dataBaseModel['tempo_execucao_min'] = str(timeTotal)

            try:
                firefox.close()
            except:
                firefox.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.shutdown()

        # Retorna valor caso haja algum erro durante a execucao
        return self.listProcessos
