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
from urllib import request

import win32api
from getmac import get_mac_address

from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.OpenWebDriver import OpenWebDriver
from src.Default.Controllers.Perfil import Perfil
from src.Default.Controllers.TaskAguardandoSessaoJulgamento import TaskAguardandoSessaoJulgamento
from src.Default.Controllers.TaskAssinaturaProcessos import TaskAssinaturaProcessos
from src.Default.Controllers.TaskInclusaoProcessos import TaskInclusaoProcessos
from src.Default.Controllers.TaskLancamento import TaskLancamento
from src.Default.Controllers.TaskTransitarJulgado import TaskTransitarJulgado
from src.Default.Models.OpenXls import OpenXls
from src.Default.Models.CSV import CSV
from src.Default.Views.FormResultado import FormResultado


class StartRobo:
    caminhoWebDrive = ""
    caminhoImages = ""
    url = ""
    proxy = ""
    traffic = ""
    versao = 0.0
    webDriveName = ""

    pathDatabaseGeral = "database\database-geral.csv"
    pathDatabaseIndividual = "database\database-individual.csv"

    # var
    arrayVarRefDados = {
        'qtd_clicks': 0,
        'qtd_trafeco_baixado_kb': 0,
        'qtd_erros_robo': 0,
    }

    def startRobo(self, log, xml, dataForm, dataset, dataBaseModel, fileName):

        # Contabiliza dados
        self.qtd_clicks = 0

        # Especifica diretorio dos prints
        self.caminhoImages = [i.text for i in xml.iter('directoryImages')][0] + "\\"
        self.url = [i.text for i in xml.iter('url')][0]

        # Especifica drive ser ultilizado
        self.caminhoWebDrive = [i.text for i in xml.iter('directoryDriver')][0] + "\\"

        # Proxy
        self.proxy = [i.text for i in xml.iter('directoryProxy')][0] + "\\"
        self.traffic = [i.text for i in xml.iter('directoryLogTraffic')][0] + "\\"

        self.versao = self.get_installed_version()

        # Geckodrive Name
        # Selecionar a versao de acordo com mozilla instalado na maquina
        if self.versao < 53.0:
            self.webDriveName = 'Driver 0.17.0 para Mozilla Superior ou Igual a Versão 52'
        elif self.versao >= 53.0 and self.versao < 55.0:
            self.webDriveName = 'Driver 0.18.0 para Mozilla Superior ou Igual a Versão 53'
        elif self.versao >= 55.0 and self.versao < 63.0:
            self.webDriveName = 'Driver 0.20.1 para Mozilla Superior ou Igual a Versão 55'
        elif self.versao >= 78.0 and self.versao < 79.0:
            self.webDriveName = 'Driver 0.26.0 para Mozilla Superior ou Igual a Versão 78'
        elif self.versao >= 63.0 and self.versao < 80.0:
            self.webDriveName = 'Driver 0.24.0 para Mozilla Superior ou Igual a Versão 57'
        elif self.versao >= 80.0:
            self.webDriveName = 'Driver 0.29.1 para Mozilla Superior ou Igual a Versão 60'

        # Codigo fica especificado de acordo com codigo atribuido no sistema
        if dataForm['perfil'] == '5ª Turma Recursal / Presidência da 5ª Turma Recursal / Juiz de Direito' \
                or dataForm['perfil'] == 'Gab. 3 - 5ª Juizado Especial Cível e Criminal de Iguatu / Juiz de Direito' \
                or dataForm[
            'perfil'] == '5ª Turma Recursal Provisória / Gab. 2 - 5ª Turma Recursal Provisória / Juiz Titular':
            codPerfil = 0
        elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Gab. 1 - 5ª Turma Recursal Provisória / Juiz Titular' \
                or dataForm[
            'perfil'] == '6ª Turma Recursal Provisória / Gab. 2 - 6ª Turma Recursal Provisória / Juiz Titular' \
                or dataForm['perfil'] == 'Gab. 3 - 5ª Juizado Especial Cível e Criminal do Crato / Juiz Substituto':
            codPerfil = 1
        elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria' \
                or dataForm[
            'perfil'] == '6ª Turma Recursal Provisória / Gab. 1 - 6ª Turma Recursal Provisória / Juiz Titular':
            codPerfil = 2
        elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão' \
                or dataForm[
            'perfil'] == '6ª Turma Recursal Provisória / Gab. da Presidência da 6ª Turma Recursal / Juiz Titular' \
                or dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Servidor Geral':
            codPerfil = 3
        elif dataForm[
            'perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria':
            codPerfil = 4
        elif dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão' \
                or dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Servidor Geral':
            codPerfil = 5

        # Registra horario que iniciou a tarefa
        inicioTime = time.time()

        # Captura informacoes da maquina
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)

        log.info('---------------------------')
        log.info('O robo iniciou com os seguintes dados: ')
        log.info('O caminho do arquivo informado foi: ' + dataForm['caminhoArquivo'])
        log.info('A atividade selecionada foi: ' + dataForm['atividade'])
        log.info('O perfil selecionado foi: ' + dataForm['perfil'])
        log.info('---------------------------')
        log.info('Dados da maquina que executou: ')

        try:
            # Captura o IP externo
            url = request.urlopen('http://ip-api.com/json').read()
            jsn = json.loads(url.decode('UTF-8'))
            log.info('IP Internet: ' + str(jsn['query']))
        except:
            log.info('Nao foi possivel identificar endereco de IP. Falha na conexao.')

        log.info('IP Local: ' + str(IP))
        log.info('Nome da maquina: ' + str(hostname))
        log.info('Endereco MAC da maquina: ' + str(get_mac_address()))
        log.info('Versao do Navegador: ' + str(self.versao))
        log.info('Driver: ' + str(self.webDriveName))
        log.info('---------------------------')

        # Registra base
        dataBaseModel['endereco_mac'] = str(get_mac_address())

        # Abrir WebDriver
        webdriver = OpenWebDriver(self.caminhoWebDrive, self.webDriveName, self.versao, self.url, self.proxy,
                                  self.traffic, fileName)

        # Inicia os Objetos
        firefox = webdriver.Open(log)

        # Inicia Autenticacao
        auth = Auth(firefox, log, self.caminhoImages)

        # Atividade de assinatura nao usa planilha
        if dataForm['atividade'] != 'Assinaturas de Processos para Juiz Titular':
            openXls = OpenXls(dataForm['caminhoArquivo'])  # Instancia o objeto passando o caminho do arquivo
            # Abre o arquivo XLS
            xlsData = openXls.OpenFileXls(firefox, log)

        # Seleciona o perfil
        selecionarPerfil = Perfil(firefox, log, codPerfil, dataForm['perfil'])

        # Contabiliza dados
        # Começa com dois, pois para selecionar o perfil sao 2 clicks
        self.arrayVarRefDados['qtd_clicks'] = 2

        time.sleep(1)

        if dataForm['atividade'] == 'Encaminhar processos julgados em sessão para assinar inteiro teor de acórdão':

            # Registra Base
            dataBaseModel['cod_atividade'] = '1'

            # Executa a tarefa Aguardando Sessão Julgamento
            executaAguardandoSessaoJulgamento = TaskAguardandoSessaoJulgamento(firefox, self.caminhoImages, log,
                                                                               openXls, xlsData,
                                                                               '(TR) Aguardando sessão de julgamento',
                                                                               xml, dataset, dataBaseModel, inicioTime,
                                                                               self.arrayVarRefDados)

            # Request
            trafficData = self.registre_request(self, webdriver, log)

            # Dataset
            self.dataset_csv(self, dataBaseModel, trafficData, log)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaAguardandoSessaoJulgamento.listProcessos, 0, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Inclusão de processos na relação de julgamento':

            # Registra Base
            dataBaseModel['cod_atividade'] = '2'

            # Inclusão de processos na relação de julgamento
            executaInclusaoProcessos = TaskInclusaoProcessos(firefox, self.caminhoImages, log,
                                                             openXls, xlsData,
                                                             'Inclusão de processos na relação de julgamento',
                                                             xml, dataset, dataBaseModel, inicioTime,
                                                             self.arrayVarRefDados)

            # Request
            trafficData = self.registre_request(self, webdriver, log)

            # Dataset
            self.dataset_csv(self, dataBaseModel, trafficData, log)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInclusaoProcessos.listProcessos, 1, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Assinaturas de Processos para Juiz Titular':

            # Registra Base
            dataBaseModel['cod_atividade'] = '3'

            # Assinaturas de Processos para Juiz Titular
            executaAssinaturaProcessos = TaskAssinaturaProcessos(firefox, self.caminhoImages, log,
                                                                 'Assinaturas de Processos para Juiz Titular', dataset,
                                                                 dataBaseModel, inicioTime, self.arrayVarRefDados)

            # Request
            trafficData = self.registre_request(self, webdriver, log)

            # Dataset
            self.dataset_csv(self, dataBaseModel, trafficData, log)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaAssinaturaProcessos.listProcessos, 2, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Transitar em Julgado':

            # Registra Base
            dataBaseModel['cod_atividade'] = '4'

            # Transitar em Julgado
            executaTransitarJulgado = TaskTransitarJulgado(firefox, self.caminhoImages, log,
                                                           openXls, xlsData,
                                                           '(TR) Julgados em sessão',
                                                           xml, dataset, dataBaseModel, inicioTime,
                                                           self.arrayVarRefDados)

            # Request
            trafficData = self.registre_request(self, webdriver, log)

            # Dataset
            self.dataset_csv(self, dataBaseModel, trafficData, log)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaTransitarJulgado.listProcessos, 0, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                os._exit(0)
                sys.exit(0)

        elif dataForm['atividade'] == 'Lançamento de movimentação TPU':

            # Registra Base
            dataBaseModel['cod_atividade'] = '5'

            # Caso haja dados incorretos na planilha, já será verificado e validado
            # Chamada feita somente para validacao e nao perder tempo na execucao
            # Nao usa mais
            # listDataProcessos = openXls.getDataProcessLancamentoXLS(xlsData, firefox, log, xml)

            # Lançamento de movimentação TPU
            executaLancamento = TaskLancamento(firefox, self.caminhoImages, log,
                                               openXls, xlsData,
                                               '(TR) Lançar movimentações de julgamento',
                                               xml, dataset, dataBaseModel, inicioTime, self.arrayVarRefDados)

            # Adiciona a lista de processos nao aptos
            # A partir dos dados da planilha
            listDataProcessosInaptos = openXls.listProcessosInaptos

            if len(listDataProcessosInaptos) > 0:
                for x in range(len(listDataProcessosInaptos)):
                    executaLancamento.listProcessos[0].append(listDataProcessosInaptos[x][0])
                    executaLancamento.listProcessos[1].append(4)

            # Request
            trafficData = self.registre_request(self, webdriver, log)

            # Dataset
            self.dataset_csv(self, dataBaseModel, trafficData, log)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaLancamento.listProcessos, 3, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                os._exit(0)
                sys.exit(0)

    def dataset_csv(self, dataBaseModel, trafficData, log):

        # Registra trafico
        dataBaseModel['qtd_requisicao'] = trafficData[1]
        dataBaseModel['qtd_trafeco_baixado_kb'] = trafficData[2]

        try:
            # Registra dados de execução geral
            csv = CSV(self.pathDatabaseGeral)
            csv.registraCsvDatabase(dataBaseModel)
        except:
            log.info('Houve uma falha ao registrar os dados de execucao.')

    def registre_request(self, firefox, log):

        try:
            # Captura os dados de trafeco
            trafficData = firefox.monitor_traffic()
            # Registra trafico em CSV
            firefox.registre_traffic(trafficData[0])
        except:
            log.info('Houve uma falha ao registrar os dados de trafico.')

        firefox.stop_proxy()

        return trafficData

    def get_installed_version(self):
        try:
            firefox_filepath = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            version_info = win32api.GetFileVersionInfo(firefox_filepath, "\\")
        except:
            firefox_filepath = r"C:\Program Files\Mozilla Firefox\firefox.exe"
            version_info = win32api.GetFileVersionInfo(firefox_filepath, "\\")
        product_version = version_info["ProductVersionMS"]
        product_version = float(f"{product_version >> 16}.{product_version & 0xFFFF}")

        return product_version
