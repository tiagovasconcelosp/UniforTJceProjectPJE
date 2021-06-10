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


class TaskAssinaturaProcessos:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countTask = 0
    countEncaminhados = 0

    listAtividades = [
        '(TR) Confirmar relatório - voto - ementa',
        '(TR) Assinar inteiro teor',
    ]

    # Etiqueta a ser buscada
    etiqueta = "ASSINAR"


    # Geração de dados
    qtd_clicks_all = 0
    qtd_erros_tentativa_processo_all = 0

    def __init__(self, firefox, caminhoImages, logging, atividade, dataset, dataBaseModel, inicioTime, arrayVarRefDados):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countEnviaProcesso = 0
        self.Execute(firefox, caminhoImages, logging, atividade, dataset, dataBaseModel, inicioTime, arrayVarRefDados)

    def checkQtdProcessosAtividade(self, firefox, logging, caminhoImages):

        for i in range(len(self.listAtividades)):

            try:

                # Realizando a busca pela a atividade
                element = WebDriverWait(firefox, 60).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a span')))

                # Usado so para aguardar o loading
                # element = WebDriverWait(firefox, 10).until(
                    # EC.presence_of_element_located((By.XPATH, "/html/body/app-root/selector/div/div/div/right-panel/div/div/div/tarefas/div/div/div/div/a[@title='" + self.listAtividades[i] + "']/div/span[2]")))


                # element = firefox.find_element(By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + self.listAtividades[i] + '"i] span.quantidadeTarefa').text
                element = firefox.find_element(By.XPATH,
                       "/html/body/app-root/selector/div/div/div/right-panel/div/div/div/tarefas/div/div/div/div/a[@title='" + self.listAtividades[i] + "']/div/span[2]").text

                logging.info('---------------------------')
                logging.info('Verificando lista de atividades...')
                logging.info('---------------------------')

                # Verifica se foi encontrado e se ha processos dentro do mesmo
                if int(element) > 0:

                    # (TR) Elaborar relatório - voto - ementa
                    if (self.listAtividades[i] == '(TR) Confirmar relatório - voto - ementa' and self.countTask == 0):

                        logging.info('---------------------------')
                        logging.info('Tarefa localizada: ' + self.listAtividades[i])
                        logging.info('Total de processos encontrados na atividade: ' + str(element))
                        logging.info('---------------------------')

                        # Carrega atividade
                        element = WebDriverWait(firefox, 40).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + self.listAtividades[i] + '"i]')))
                        firefox.execute_script("arguments[0].click();", element)

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

                        logging.info('Iniciando tarefa: ' + str(self.listAtividades[i]))

                        self.assinaAtividadeEmbDeclaracao(firefox, logging, caminhoImages, i)

                        return True

                    # (TR) Assinar inteiro teor
                    elif (self.listAtividades[i] == '(TR) Assinar inteiro teor'): # Remover count

                        logging.info('---------------------------')
                        logging.info('Tarefa localizada: ' + self.listAtividades[i])
                        logging.info('Total de processos encontrados na atividade: ' + str(element))
                        logging.info('---------------------------')

                        # Carrega atividade
                        element = WebDriverWait(firefox, 40).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 '#divTarefasPendentes .menuItem a[title="' + self.listAtividades[i] + '"i]')))
                        firefox.execute_script("arguments[0].click();", element)

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

                        logging.info('Iniciando tarefa: ' + str(self.listAtividades[i]))

                        self.assinaAtividadeInteiroTeor(firefox, logging, caminhoImages, i)

                        return True

            except:
                logging.info('---------------------------')
                logging.info('Nao foi encontrado pendencias na atividade: ' + str(self.listAtividades[i]))

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                try:

                    veryficProcess = firefox.find_element(By.CSS_SELECTOR,
                                                          'div#divProcessosTarefa div.ui-widget-content div.ui-datalist-emptymessage').text

                    logging.info('Nenhum processo foi encontrado.')
                    logging.info('---------------------------')

                    if str(veryficProcess) == 'Nenhum processo encontrado':
                        # Volta para a lista de tarefas
                        element = firefox.find_element(By.CSS_SELECTOR, 'ul#menu li#liHome a')
                        firefox.execute_script("arguments[0].click();", element)

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

                        time.sleep(3)

                        # Para nao entrar mais nessa atividade
                        self.countTask += 1

                        # Realizando a aguardar o loading
                        element = WebDriverWait(firefox, 120).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a span')))

                        # Repete o processo de busca por processos - Não faz sentido implementar a mesma tarefa
                        self.checkQtdProcessosAtividade(firefox, logging, caminhoImages)
                except:

                    # Contabiliza dados
                    self.qtd_erros_tentativa_processo_all += 1

                    logging.info('Houve um erro ao retornar a atividade.')
                    logging.info('---------------------------')

        return False

    def assinaAtividadeEmbDeclaracao(self, firefox, logging, caminhoImages, i):

        #############################################################################################################

        # Limpa o campo de busca
        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located(
                (By.ID, 'inputPesquisaTarefas')))
        element.clear()

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1)

        # Abre filtro da pesquisa para etiquetas
        element = firefox.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1)

        logging.info('---------------------------')
        logging.info('Filtrando os processos pela etiqueta: ' + str(self.etiqueta))

        firefox.find_element(By.ID, "porEtiqueta").send_keys(self.etiqueta)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        # Clica em pesquisar processos
        element = firefox.find_element(By.CSS_SELECTOR, '.col-sm-12 button.btn-pesquisar-filtro')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1) # Verificar time em lista grande de processos

        # Fecha filtro da pesquisa
        element = firefox.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        #############################################################################################################

        time.sleep(1)

        # Aguarda carregamento dos processos
        element = WebDriverWait(firefox, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))

        # Total de processos encontrados
        listCountProcess = firefox.find_element(By.CSS_SELECTOR,
                                       'div#divProcessosTarefa div.painel-listagem div.row span.badge').text

        logging.info('Total de processos encontrados: ' + str(listCountProcess))

        ##########################################
        ##########################################

        # Realiza a assnatura de cada um deles
        for x in range(int(listCountProcess)):

            e = firefox.find_element(By.CSS_SELECTOR,
                                     'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) div.datalist-content span.tarefa-numero-processo').text

            e = e.split()

            self.listProcessos[0].append(str(e[1]))
            # Adicao previa de nao concluido
            self.listProcessos[1].append(1)

            # Clica no processo
            element = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) a.selecionarProcesso')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            logging.info('---------------------------')
            logging.info('Abrindo o processo: ' + e[1])

            time.sleep(4)

            # Usado para garantir carregamento completo do processo
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#btnTransicoesTarefa')))

            try:
                # Verifique se botao "Libera para demais gabinetes" esta disponivel
                ass = WebDriverWait(firefox, 20).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'ul.dropdown-transicoes li a[title="Encaminhar para Liberar para demais gabinetes"i]')))

                firefox.execute_script("arguments[0].click();", ass)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                logging.info('Processo assinado.')
                logging.info('---------------------------')

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(0)

            except:

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                logging.info('---------------------------')
                logging.info('Nao foi possivel assinar o processo.')
                logging.info('Nao foi localizado o botao: Libera para demais gabinetes')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            time.sleep(8)

        # Registra todos os processos encontrados
        logging.info('Lista de processos que foram encontrados e liberados:')

        for x in range(len(self.listProcessos[0])):
            # Listagem de processos encontrados
            logging.info(self.listProcessos[0][x])
        logging.info('---------------------------')

        # Remover filtro no final da assinatura

        logging.info('---------------------------')
        logging.info('Limpando filtro da etiqueta')

        #############################################################################################################

        time.sleep(2)

        # Abre filtro da pesquisa para etiquetas
        element = firefox.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1)

        # Clica em limpar
        element = firefox.find_element(By.CSS_SELECTOR, '.col-sm-12 button.ml-5')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1)

        # Fecha filtro da pesquisa
        element = firefox.find_element(By.CSS_SELECTOR, '#divActions button[title="Pesquisar"]')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(2)

        #############################################################################################################

        # Volta para a lista de tarefas
        element = firefox.find_element(By.CSS_SELECTOR, 'ul#menu li#liHome a')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(3)

        # Para nao entrar mais nessa atividade
        self.countTask += 1

        # Realizando a aguardar o loading
        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a span')))

        # Repete o processo de busca por processos - Não faz sentido implementar a mesma tarefa
        self.checkQtdProcessosAtividade(firefox, logging, caminhoImages)

    def assinaAtividadeInteiroTeor(self, firefox, logging, caminhoImages, i):

        #############################################################################################################

        # Limpa o campo de busca
        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located(
                (By.ID, 'inputPesquisaTarefas')))
        element.clear()

        # Contabiliza dados
        self.qtd_clicks_all += 1

        time.sleep(1)

        #############################################################################################################

        # Aguarda carregamento dos processos
        element = WebDriverWait(firefox, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li:first-child a.selecionarProcesso')))

        # Total de processos encontrados
        listCountProcess = firefox.find_element(By.CSS_SELECTOR,
                                                'div#divProcessosTarefa div.painel-listagem div.row span.badge').text

        logging.info('Total de processos encontrados: ' + str(listCountProcess))

        ##########################################

        # Realiza a assnatura de cada um deles
        for x in range(int(listCountProcess)):

            e = firefox.find_element(By.CSS_SELECTOR,
                                     'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) div.datalist-content span.tarefa-numero-processo').text

            e = e.split()

            self.listProcessos[0].append(str(e[1]))
            # Adicao previa de nao concluido
            self.listProcessos[1].append(1)

            # Clica no processo
            element = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) a.selecionarProcesso')))
            firefox.execute_script("arguments[0].click();", element)

            # Contabiliza dados
            self.qtd_clicks_all += 1

            logging.info('---------------------------')
            logging.info('Abrindo o processo: ' + e[1])

            time.sleep(4)

            # Usado para garantir carregamento completo do processo
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#btnTransicoesTarefa')))

            # Localiza frame
            iframe2 = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located((By.ID, 'frame-tarefa')))
            firefox.switch_to.frame(iframe2)

            # Usado para garantir carregamento completo do processo
            element = WebDriverWait(firefox, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.col-sm-12 input')))

            try:
                # Clica no botao para assinar
                # Assinar digitalmente e finalizar
                ass = WebDriverWait(firefox, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'form div.col-sm-12 input[value="Assinar digitalmente e finalizar"i]')))

                firefox.execute_script("arguments[0].click();", ass)

                # Contabiliza dados
                self.qtd_clicks_all += 1

                logging.info('Processo assinado.')
                logging.info('---------------------------')

                # Deleta o ultimo registro
                del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
                # Inclui novo registro
                self.listProcessos[1].append(0)

            except:

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                logging.info('---------------------------')
                logging.info('Nao foi possivel assinar o processo.')
                logging.info('Evidenciando com o print da tela.')
                image = Print(firefox, caminhoImages)

            # Seleciona Frame
            ##########################
            firefox.switch_to.default_content()
            iframe = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))
            firefox.switch_to.frame(iframe)
            ##########################

            time.sleep(10)

        # Registra todos os processos encontrados
        logging.info('Lista de processos que foram encontrados em todas as atividades:')

        for x in range(len(self.listProcessos[0])):
            # Listagem de processos encontrados
            logging.info(self.listProcessos[0][x])
        logging.info('---------------------------')

        # Volta para a lista de tarefas
        element = firefox.find_element(By.CSS_SELECTOR, 'ul#menu li#liHome a')
        firefox.execute_script("arguments[0].click();", element)

        # Contabiliza dados
        self.qtd_clicks_all += 1

        # time.sleep(3)

        # Para nao entrar mais nessa atividade
        self.countTask += 1

        # Realizando a aguardar o loading
        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a span')))

        # Repete o processo de busca por processos
        self.checkQtdProcessosAtividade(firefox, logging, caminhoImages)

    def Execute(self, firefox, caminhoImages, logging, atividade, dataset, dataBaseModel, inicioTime, arrayVarRefDados):

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

            # Registra horario que iniciou a tarefa
            # inicio = time.time()

            self.checkQtdProcessosAtividade(firefox, logging, caminhoImages)

            logging.info(dataBaseModel)

            for i in range(len(self.listProcessos[0])):
                dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[0][i]))
                dataBaseModel['individual']['processo_realizado'].append(str(self.listProcessos[1][i]))
                dataBaseModel['individual']['processo_nao_encontrado'].append(0)

            if self.listProcessos[2]:
                for i in range(len(self.listProcessos[2])):
                    dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[2][i]))
                    dataBaseModel['individual']['processo_realizado'].append(1)
                    dataBaseModel['individual']['processo_nao_encontrado'].append(1)

            # for i in range(len(self.listProcessos[2])):
            #     try:
            #         dataBaseModel['individual']['processo_nao_encontrado'].append(str(self.listProcessos[2][i]))
            #     except:
            #         continue

            ###################################
            # Verificacao dos processos localizado e encaminhados
            ###################################

            if len(self.listProcessos[0]) > 0:
                logging.info('Lista de processos encontrados:')
                for i in range(len(self.listProcessos[0])):
                    logging.info('Processo: ' + str(self.listProcessos[0][i]))

                logging.info("Total de processos encontrados para assinatura: " + str(len(self.listProcessos[0])))
                logging.info("Total de processos assinados: " + str(self.countEncaminhados))
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
                logging.info('Lista de processos nao foram assinados:')
                for i in range(len(self.listProcessos[2])):
                    logging.info('Processo: ' + str(self.listProcessos[2][i]))
                logging.info("Total de processos que nao foram assinados: " + str(len(self.listProcessos[2])))

            self.listProcessos.append(len(self.listProcessos[2]))

            logging.info('---------------------------')

            firefox.switch_to.default_content()

            # Registra base
            dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
            dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
            dataBaseModel['qtd_clicks'] = arrayVarRefDados['qtd_clicks'] + self.qtd_clicks_all
            dataBaseModel['qtd_erros_tentativa_processo'] = self.qtd_erros_tentativa_processo_all
            dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

            logging.info(dataBaseModel)

            try:
                firefox.close()
            except:
                firefox.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

            return self.listProcessos

        except Exception as e:

            image = Print(firefox, caminhoImages)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos