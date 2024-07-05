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

import json
import os
import socket
import sys
import time
import psutil
# import win32api
# import geckodriver_autoinstaller
# import chromedriver_autoinstaller

from random import randint
from urllib import request
from getmac import get_mac_address
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.chrome.options import Options as OptionsChrome

from src.Default.Models.OpenXls import OpenXls

from src.Default.Views.FormResultado import FormResultado

from src.Default.Controllers.Logger import Logger

# PJE
from src.Default.Controllers.TaskTransitarJulgado_PJE_022 import TaskTransitarJulgado_PJE_022
from src.Default.Controllers.TaskIncluirProcessosJulgamento_PJE_025 import TaskIncluirProcessosJulgamento_PJE_025
from src.Default.Controllers.TaskAssinaturaLancamento_PJE import TaskAssinaturaLancamento_PJE
from src.Default.Controllers.TaskDespachoInicial_PJE_009 import TaskDespachoInicial_PJE_009
from src.Default.Controllers.TaskDeterminarMedidasConstricao_PJE_012 import TaskDeterminarMedidasConstricao_PJE_012
from src.Default.Controllers.TaskMovimentarProcessos_PJE_007 import TaskMovimentarProcessos_PJE_007
from src.Default.Controllers.TaskCartaCitacao_PJE_008 import TaskCartaCitacao_PJE_008
from src.Default.Controllers.TaskMovimentarCertificacaoPrazo_PJE_030 import TaskMovimentarCertificacaoPrazo_PJE_030
from src.Default.Controllers.TaskMandadoCitacao_PJE_019 import TaskMandadoCitacao_PJE_019
from src.Default.Controllers.TaskCitacaoIntimacaoDespachoDecisao_PJE_023 import TaskCitacaoIntimacaoDespachoDecisao_PJE_023
from src.Default.Controllers.TaskEmbargoDeclaracao_PJE_018 import TaskEmbargoDeclaracao_PJE_018
from src.Default.Controllers.TaskCitacaoIntimacaoSentenca_PJE_027 import TaskCitacaoIntimacaoSentenca_PJE_027
from src.Default.Controllers.TaskConsultaRENAJUD_PJE_014 import TaskConsultaRENAJUD_PJE_014

# SEEU
from src.Default.Controllers.TaskIncidentesIntimacao_SEEU_013 import TaskIncidentesIntimacao_SEEU_013
from src.Default.Controllers.TaskIncidentesCitacao_SEEU_020 import TaskIncidentesCitacao_SEEU_020
from src.Default.Controllers.TaskPreAnalise_SEEU_021 import TaskPreAnalise_SEEU_021
from src.Default.Controllers.TaskIntimarPessoalmente_SEEU_011 import TaskIntimarPessoalmente_SEEU_011
from src.Default.Controllers.TaskIntimacaoMpAdvogado_SEEU_017 import TaskIntimacaoMpAdvogado_SEEU_017

# SISBAJUD
from src.Default.Controllers.TaskConsulta_SISBAJUD_010 import TaskConsulta_SISBAJUD_010
from src.Default.Controllers.TaskResultado_SISBAJUD_016 import TaskResultado_SISBAJUD_016

class StartRobo:

    caminhoImagesPrint = ""
    caminhoImagesGui = ""
    url = ""
    versao = 0.0
    webDriveName = ""

    def startRobo(self, log, xml, dataForm, dataBaseModel, codigo_execucao):

        # Especifica diretorio dos prints
        self.caminhoImagesPrint = [i.text for i in xml.iter('directoryImagesPrints')][0] + "\\"
        self.caminhoImagesGui = [i.text for i in xml.iter('directoryImagesGui')][0] + "\\"
        self.url = [i.text for i in xml.iter('url')][0]

        if dataForm['atividade'] == 'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]' \
                or dataForm['atividade'] == 'Instauração dos incidentes a vencer e realização de intimação [SEEU]' \
                or dataForm['atividade'] == 'Instauração dos incidentes a vencer e realização de citação [SEEU]' \
                or dataForm['atividade'] == 'Realizar Pré-análise de Processos [SEEU]' \
                or dataForm['atividade'] == 'Intimação de MP e Advogado/DP de uma decisão/sentença [SEEU]':
            self.url = [i.text for i in xml.iter('urlSeeu')][0]
            # self.url = "https://seeutreino.pje.jus.br/seeu/"

        self.urlSISBAJUD = [i.text for i in xml.iter('urlSisbajud')][0]

        self.acaoEmErro = [i.text for i in xml.iter('acaoEmErro')][0]

        try:
            f = open("harfile.har", "w")
            f.close()
        except Exception as e:
            log.info('Falha ao limpar arquivo harfile.')
            log.info(repr(e))

        log.info('---------------------------')
        log.info('Robô utilizará Navegador Chrome')
        log.info('---------------------------')

        try:
            if dataForm['atividade'] != 'Inclusão de processos na relação de julgamento [PJE2G]':
                # AutoInstaller do ChromeDriver
                # chromedriver_autoinstaller.install()
                service = Service()
                # options = OptionsChrome()
                options = webdriver.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--start-maximized')
                # Validar necessidade - ocorre erro na execuçãp
                # Importante comentar definiçao de cada parametro
                # options.add_argument('--single-process')
                # options.add_argument('--disable-dev-shm-usage')
                # options.add_argument("--incognito")
                # options.add_argument('--disable-blink-features=AutomationControlled')
                # options.add_argument('--disable-blink-features=AutomationControlled')
                # options.add_experimental_option('useAutomationExtension', False)
                # options.add_experimental_option("excludeSwitches", ["enable-automation"])
                # options.add_argument("disable-infobars")
                # MODIFICAR A PASTA DE DOWNLOADS
                if dataForm['atividade'] == 'Consulta no SISBAJUD' \
                        or dataForm['atividade'] == 'Resultado no SISBAJUD':
                    options.add_experimental_option('prefs', {
                        # "download.default_directory": "C:\\Users\\augusto.santos\\Desktop\\download_pdfs_teste", #Change default directory for downloads
                        "download.prompt_for_download": False,  # To auto download the file
                        "download.directory_upgrade": True,
                        "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
                    })
                # driver = webdriver.Chrome(chrome_options=options)
                driver = webdriver.Chrome(service=service, options=options)
                self.versao = driver.capabilities['browserVersion']
                self.webDriveName = 'Google Chrome'

            else:

                service = Service()

                options = webdriver.FirefoxOptions()
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument('--disable-web-security')
                options.add_argument("--ignore-certificate-errors")
                options.add_argument("--disable-dev-shm-usage")

                driver = webdriver.Firefox(service=service, options=options)
                self.versao = driver.capabilities['browserVersion']
                self.webDriveName = 'Mozilla Firefox'

        except Exception as e:
            log.info('Falha na abertura do driver')
            log.info(repr(e))
            print(repr(e))
            print('Falha na abertura do driver')
            log.shutdown()
            os._exit(0)
            sys.exit(0)

        # Usado para testar tela de resultado
        # a =  [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 0], [], 2, 0, '40.26 segundos', 1]
        # form = FormResultado(a, 0, log)
        # time.sleep(9999)

        # Tarefas das Turmas Recursais
        if (dataForm['atividade'] == 'Transitar em Julgado [PJE2G]' \
                or dataForm['atividade'] == 'Inclusão de processos na relação de julgamento [PJE2G]'):

            self.url = [i.text for i in xml.iter('urlPje2g')][0]
            openXls = OpenXls(dataForm['caminhoArquivo'])  # Instancia o objeto passando o caminho do arquivo
            # Abre o arquivo XLS
            xlsData = openXls.OpenFileXls(driver, log)


        # Registra horario que iniciou a tarefa
        inicioTime = time.time()

        # Captura informacoes da maquina
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)

        log.info('---------------------------')
        log.info('O robo iniciou com os seguintes dados: ')
        log.info('O caminho do arquivo informado foi: ' + dataForm['caminhoArquivo'])
        log.info('A atividade selecionada foi: ' + dataForm['atividade'])

        if dataForm['atividade'] != 'Instauração dos incidentes a vencer e realização de intimação [SEEU]' \
                and dataForm['atividade'] != 'Instauração dos incidentes a vencer e realização de citação [SEEU]' \
                and dataForm['atividade'] != 'Realizar Pré-análise de Processos [SEEU]' \
                and dataForm['atividade'] != 'Resultado no SISBAJUD':

            log.info('O perfil selecionado foi: ' + dataForm['perfil'])
        log.info('---------------------------')
        log.info('Dados da maquina que executou: ')

        try:
            # Captura o IP externo
            url = request.urlopen('http://ip-api.com/json').read()
            jsn = json.loads(url.decode('UTF-8'))
            log.info('IP Internet: ' + str(jsn['query']))
        except Exception as e:
            log.info('Nao foi possivel identificar endereco de IP. Falha na conexao.')
            log.info(repr(e))

        log.info('IP Local: ' + str(IP))
        log.info('Nome da maquina: ' + str(hostname))
        log.info('Endereco MAC da maquina: ' + str(get_mac_address()))
        log.info('Versao do Navegador: ' + str(self.versao))
        log.info('Driver: ' + str(self.webDriveName))
        log.info('---------------------------')

        # Reset List dataBaseModel
        self.resetDataBaseModel(dataBaseModel)

        dataBaseModel['endereco_mac'] = str(get_mac_address())
        dataBaseModel['id'] = dataBaseModel['id'] + str(randint(10, 99)) + str(randint(10, 99)) + str(randint(10, 99)) + str(randint(10, 99))

        try:
            usuario_bi = [i.text for i in xml.iter('matricula')][0]
            if usuario_bi is None:
                usuario_bi = os.environ['USERNAME']
        except:
            usuario_bi = os.environ['USERNAME']

        log_bi = Logger()
        log_bi.set_macro_dados(nome_rpa=dataForm['atividade'],
                               aplicacao=[i.text for i in xml.iter('aplicacao')][0],
                               versao=[i.text for i in xml.iter('versao')][0],
                               navegador=self.webDriveName,
                               usuario=usuario_bi,
                               codigoRpa=codigo_execucao)
        log_bi.realizar_requisicao(num_processo=self.codigo_execucao,
                                   passo_executado="Início Geral",
                                   mensagem="Início em StartRobo")
        ###################################################################################

        time.sleep(1)

        if dataForm['atividade'] == 'Inclusão de processos na relação de julgamento [PJE2G]':

            log.info('---------------------------')
            log.info('Atividade: Inclusão de processos na relação de julgamento')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '2'
            dataBaseModel['atividade_concluida'] = '1'

            # Inclusão de processos na relação de julgamento
            executaInclusaoProcessos = TaskIncluirProcessosJulgamento_PJE_025(driver, self.caminhoImagesPrint, log,
                                                             openXls, xlsData,
                                                             '[EF] Consultar convênios',
                                                             dataBaseModel, inicioTime,
                                                             self.url, dataForm, xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInclusaoProcessos.listProcessos, 1, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaInclusaoProcessos.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Transitar em Julgado [PJE2G]':

            log.info('---------------------------')
            log.info('Atividade: Transitar em Julgado')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '6'
            dataBaseModel['atividade_concluida'] = '1'

            # Transitar em Julgado
            executaTransitarJulgado = TaskTransitarJulgado_PJE_022(driver, self.caminhoImagesPrint, log,
                                                           openXls, xlsData,
                                                           '[Sec] - Prazo - VERIFICAR PRAZO JÁ DECORRIDO',
                                                           dataBaseModel, inicioTime,
                                                           self.url, dataForm, xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaTransitarJulgado.listProcessos, 0, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaTransitarJulgado.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Lançamento de movimentação TPU e Assinatura de Acórdão':

            log.info('---------------------------')
            log.info('Atividade: Lançamento de movimentacao TPU e Assinatura de Acordao')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '7'
            dataBaseModel['atividade_concluida'] = '1'


            # Caso haja dados incorretos na planilha, já será verificado e validado
            # Chamada feita somente para validacao e nao perder tempo na execucao
            # Nao usa mais
            listDataProcessos = openXls.getDataProcessLancamentoXLS(xlsData, driver, log, xml)


            # Lançamento de movimentacao TPU e Assinatura de Acordao
            executaLancamento = TaskAssinaturaLancamento_PJE(driver, self.caminhoImagesPrint, log,
                                               openXls, xlsData,
                                               '[Gab] -Julgamento Colegiado - ASSINAR INTEIRO TEOR',
                                               xml, dataBaseModel, inicioTime, 
                                               log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            # ###########################################################################################
            # Adiciona a lista de processos nao aptos
            # Particularidade da Atividade
            try:
                # Adiciona a lista de processos nao aptos
                # A partir dos dados da planilha
                listDataProcessosInaptos = openXls.listProcessosInaptos

                if len(listDataProcessosInaptos) > 0:
                    for x in range(len(listDataProcessosInaptos)):
                        executaLancamento.listProcessos[0].append(listDataProcessosInaptos[x][0])
                        executaLancamento.listProcessos[1].append(4)

                log.info('Adicionando a lista de processos nao aptos.')

            except Exception as e:
                log.info('Falha ao adicionar os dados ingnorados da planilha.')
                log.info(repr(e))

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaLancamento.listProcessos, 3, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaLancamento.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Movimentação de Processos Ativos [SAJ]':

            log.info('---------------------------')
            log.info('Atividade: Movimentação de Processos Ativos [SAJ]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '8'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskMovimentarProcessos_PJE_007(driver, self.caminhoImagesPrint, log,
                                                            self.url, dataForm, self.acaoEmErro, log_bi)
                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
        
        elif dataForm['atividade'] == 'Elaboração de Despacho Inicial Núcleo 4.0':

            log.info('---------------------------')
            log.info('Atividade: Elaboração de Despacho Inicial Núcleo 4.0')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '9'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskDespachoInicial_PJE_009(driver, self.caminhoImagesPrint, log, 
                                                               'Elaboração de Despacho Inicial Núcleo 4.0',
                                                               dataBaseModel, inicioTime, 
                                                               self.url, dataForm, self.acaoEmErro,xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))

        elif dataForm['atividade'] == 'Carta de Citação Núcleo 4.0':

            log.info('---------------------------')
            log.info('Atividade: Carta de Citação Núcleo 4.0')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '10'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskCartaCitacao_PJE_008(driver, log, self.url, dataForm, self.acaoEmErro,xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))

        elif dataForm['atividade'] == 'Intimação de MP e Advogado/DP de uma decisão/sentença [SEEU]':
    
            log.info('---------------------------')
            log.info('Atividade: Intimação de MP e Advogado/DP de uma decisão/sentença [SEEU]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '12'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskIntimacaoMpAdvogado_SEEU_017(driver, self.caminhoImagesPrint, self.caminhoImagesGui, log,
                                                            dataForm['atividade'],
                                                            dataBaseModel, inicioTime, 
                                                            self.url, dataForm, self.acaoEmErro, xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))

        elif dataForm['atividade'] == 'Instauração dos incidentes a vencer e realização de intimação [SEEU]':
    
            log.info('---------------------------')
            log.info('Atividade: Instauração dos incidentes a vencer e realização de intimação [SEEU]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '11'
            dataBaseModel['atividade_concluida'] = '1'

            executaInstauracao = TaskIncidentesIntimacao_SEEU_013(driver, self.caminhoImagesPrint, self.caminhoImagesGui, log,
                                                dataForm['atividade'],
                                                dataBaseModel, inicioTime, 
                                                self.url, dataForm, xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                driver.close()
            except:
                driver.quit()

            if len(executaInstauracao.listProcessos) < 7:
                if len(executaInstauracao.listProcessos) <= 4:
                    # executaInstauracao.listProcessos.append(0) # total de processos
                    executaInstauracao.listProcessos.append(0) # total encaminha/assinado
                    executaInstauracao.listProcessos.append('0 segundo') # tempo execucao
                    executaInstauracao.listProcessos.append(0)  # total nao encontrado
                elif len(executaInstauracao.listProcessos) == 5:
                    executaInstauracao.listProcessos.append('0 segundo')
                    executaInstauracao.listProcessos.append(0)
                elif len(executaInstauracao.listProcessos) >= 6:
                    executaInstauracao.listProcessos.append(0)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInstauracao.listProcessos, 4, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaInstauracao.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Determinar Medidas de Constrição':

            log.info('---------------------------')
            log.info('Atividade: Determinar Medidas de Constrição')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '12'
            dataBaseModel['atividade_concluida'] = '1'


            executaInstauracao = TaskDeterminarMedidasConstricao_PJE_012(driver, self.caminhoImagesGui, log,
                                                               'Determinar Medidas de Constrição',
                                                               dataBaseModel, inicioTime, 
                                                               self.url, dataForm, self.acaoEmErro,xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInstauracao.listProcessos, 4, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaInstauracao.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Intimar pessoalmente a partir de despacho pré-determinado [SEEU]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '13'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskIntimarPessoalmente_SEEU_011(driver, self.caminhoImagesGui, log,
                                                            'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]',
                                                            dataBaseModel, inicioTime, 
                                                            self.url, dataForm, self.acaoEmErro, xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Consulta no SISBAJUD':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Consulta no SISBAJUD')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '12'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskConsulta_SISBAJUD_010(driver, log, self.url, self.urlSISBAJUD,
                                                         dataForm, self.acaoEmErro, xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Elaborar Mandado de Citação':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Elaborar Mandado de Citação')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '13'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskMandadoCitacao_PJE_019(driver, log, self.url, dataForm, self.acaoEmErro,xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Resultado no SISBAJUD':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Resultado no SISBAJUD')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '14'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskResultado_SISBAJUD_016(driver, log, self.url, self.urlSISBAJUD,
                                                         dataForm, self.acaoEmErro, xml, log_bi)
                
                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Intimação de embargos de declaração para contrarrazões':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Intimação de embargos de declaração para contrarrazões')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '15'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskEmbargoDeclaracao_PJE_018(driver, log, self.url, dataForm, xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Instauração dos incidentes a vencer e realização de citação [SEEU]':

            log.info('---------------------------')
            log.info('Atividade: Instauração dos incidentes a vencer e realização de citação [SEEU]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '16'
            dataBaseModel['atividade_concluida'] = '1'

            executaInstauracao = TaskIncidentesCitacao_SEEU_020(driver, self.caminhoImagesPrint, self.caminhoImagesGui, log,
                                                dataForm['atividade'],
                                                dataBaseModel, inicioTime, 
                                                self.url, dataForm, xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                driver.close()
            except:
                driver.quit()

            if len(executaInstauracao.listProcessos) < 7:
                if len(executaInstauracao.listProcessos) <= 4:
                    executaInstauracao.listProcessos.append(0)  # total encaminha/assinado
                    executaInstauracao.listProcessos.append('0 segundo')  # tempo execucao
                    executaInstauracao.listProcessos.append(0)  # total nao encontrado
                elif len(executaInstauracao.listProcessos) == 5:
                    executaInstauracao.listProcessos.append('0 segundo')
                    executaInstauracao.listProcessos.append(0)
                elif len(executaInstauracao.listProcessos) >= 6:
                    executaInstauracao.listProcessos.append(0)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInstauracao.listProcessos, 4, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaInstauracao.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Realizar Pré-análise de Processos [SEEU]':

            log.info('---------------------------')
            log.info('Atividade: Realizar Pré-análise de Processos [SEEU]')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '17'
            dataBaseModel['atividade_concluida'] = '1'

            executaPreAnalise = TaskPreAnalise_SEEU_021(driver, self.caminhoImagesPrint, self.caminhoImagesGui, log,
                                                dataForm['atividade'],
                                                dataBaseModel, inicioTime, 
                                                self.url, dataForm, xml, log_bi)

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                driver.close()
            except:
                driver.quit()

            if len(executaPreAnalise.listProcessos) < 7:
                if len(executaPreAnalise.listProcessos) <= 4:
                    executaPreAnalise.listProcessos.append(0)  # total encaminha/assinado
                    executaPreAnalise.listProcessos.append('0 segundo')  # tempo execucao
                    executaPreAnalise.listProcessos.append(0)  # total nao encontrado
                elif len(executaPreAnalise.listProcessos) == 5:
                    executaPreAnalise.listProcessos.append('0 segundo')
                    executaPreAnalise.listProcessos.append(0)
                elif len(executaPreAnalise.listProcessos) >= 6:
                    executaPreAnalise.listProcessos.append(0)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaPreAnalise.listProcessos, 4, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaPreAnalise.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Realizar Movimentação para Certificação de Prazo':
            
            log.info('---------------------------')
            log.info('Atividade: Realizar Movimentação para Certificação de Prazo')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '18'
            dataBaseModel['atividade_concluida'] = '1'

            executaInstauracao = TaskMovimentarCertificacaoPrazo_PJE_030(
                driver, log, self.url, dataForm, log_bi
            )

            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

        elif dataForm['atividade'] == 'Preparar Citação e ou Intimação':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Preparar Citação e ou Intimação')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '19'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskCitacaoIntimacaoDespachoDecisao_PJE_023(driver, log, self.url, dataForm, self.acaoEmErro,xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Preparar Citação e ou Intimação da Sentença':
            print(dataForm)
            log.info('---------------------------')
            log.info('Atividade: Preparar Citação e ou Intimação da Sentença')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '19'
            dataBaseModel['atividade_concluida'] = '1'

            try:
                executaLancamento = TaskCitacaoIntimacaoSentenca_PJE_027(driver, log, self.url, dataForm, self.acaoEmErro,xml, log_bi)

                individual = dataBaseModel['individual']

                del dataBaseModel['individual']

            except Exception as e:
                log.info(repr(e))
                print(repr(e))

        elif dataForm['atividade'] == 'Consulta no RENAJUD [PJE2G]':

            log.info('---------------------------')
            log.info('Atividade: Consulta no RENAJUD')
            log.info('---------------------------')

            # Registra Base
            dataBaseModel['cod_atividade'] = '20'
            dataBaseModel['atividade_concluida'] = '1'

            # Transitar em Julgado
            executaTransitarJulgado = TaskConsultaRENAJUD_PJE_014(driver, self.caminhoImagesPrint, log,
                                                           '[EF] Consultar convênios', # ATUALIZAR AQUI
                                                           dataBaseModel, inicioTime,
                                                           self.url, dataForm, xml, log_bi)


            dataBaseModel['atividade_concluida'] = '0'

            individual = dataBaseModel['individual']

            del dataBaseModel['individual']

            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')
            log.info('Dados para registro.')
            log.info('Modelo principal:')
            log.info(dataBaseModel)
            log.info('Modelo individual:')
            log.info(individual)
            log.info('-------------------------------------------------')
            log.info('-------------------------------------------------')

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaTransitarJulgado.listProcessos, 0, log)
                log.info('Formulario gerado com sucesso.')
                log.info('Atividade realizada com sucesso.')

            except Exception as e:
                log.info('Falha ao gerar o formulario final.')
                log.info(executaTransitarJulgado.listProcessos)
                log.info('Finalizando o robo.')
                log.info(repr(e))
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        log_bi.realizar_requisicao(num_processo=self.codigo_execucao,
                                   passo_executado="Término Geral",
                                   mensagem="Término em StartRobo")

        try:
            driver.close()
        except:
            driver.quit()

        # Necessario o encerramento do processo devido a ocultacao do console
        self.kill_chromedriver()

    def kill_chromedriver(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'chromedriver.exe':
                try:
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()  # Pode ser necessário usar process.kill() dependendo da situação
                    print(f"Processo {proc.info['pid']} ({proc.info['name']}) terminado com sucesso.")
                except Exception as e:
                    print(f"Erro ao terminar o processo {proc.info['pid']} ({proc.info['name']}): {e}")

    def resetDataBaseModel(self, dataBaseModel):

        # Tempo da aplicacao iniciada
        named_tuple = time.localtime()

        time_string = time.strftime("%d-%m-%Y %H:%M:%S", named_tuple)

        time_string2 = time.strftime("%d%m%Y%H%M", named_tuple)

        dataBaseModel = {
                    'id' : time_string2,
                    'data_aplicacao' : time_string,
                    'qtd_processos' : 0,
                    'qtd_processos_nao_localizados' : 0,
                    'tempo_execucao_sec' : 0,
                    'endereco_mac' : 0,
                    'cod_atividade' : 0,
                    'atividade_concluida' : 1,
        'individual' : {
                'cod_processo': [],
                'processo_realizado': [],
                'processo_nao_encontrado': [],
                'tempo_execucao_individual_sec': [],
            },
        }

    # Captura versao do firefox
    # Pode ser util algum momento
    # def get_installed_version(self):
    #     try:
    #         self.firefox_filepath = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
    #         version_info = win32api.GetFileVersionInfo(self.firefox_filepath, "\\")
    #     except:
    #         self.firefox_filepath = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    #         version_info = win32api.GetFileVersionInfo(self.firefox_filepath, "\\")
    #
    #     product_version = version_info["ProductVersionMS"]
    #     product_version = float(f"{product_version >> 16}.{product_version & 0xFFFF}")
    #
    #     return product_version