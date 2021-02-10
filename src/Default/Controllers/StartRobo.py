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

import sys
import time
import json
from urllib import request
import socket
from getmac import get_mac_address
import win32api

from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.OpenWebDriver import OpenWebDriver
from src.Default.Models.OpenXls import OpenXls
from src.Default.Controllers.Perfil import Perfil
from src.Default.Controllers.TaskAguardandoSessaoJulgamento import TaskAguardandoSessaoJulgamento
from src.Default.Controllers.TaskAssinaturaProcessos import TaskAssinaturaProcessos
from src.Default.Controllers.TaskInclusaoProcessos import TaskInclusaoProcessos
from src.Default.Controllers.TaskTransitarJulgado import TaskTransitarJulgado
from src.Default.Views.FormResultado import FormResultado


class StartRobo:

    caminhoWebDrive = ""
    caminhoImages = ""
    url = ""
    versao = 0.0
    webDriveName = ""

    def startRobo(self, log, xml, dataForm):

        # Especifica diretorio dos prints
        self.caminhoImages = [i.text for i in xml.iter('directoryImages')][0] + "\\"
        self.url = [i.text for i in xml.iter('url')][0]

        # Especifica drive ser ultilizado
        self.caminhoWebDrive = [i.text for i in xml.iter('directoryDriver')][0] + "\\"

        self.versao = self.get_installed_version()

        # Geckodrive Name
        # Selecionar a versao de acordo com mozilla instalado na maquina
        if self.versao < 55.0:
            self.webDriveName = 'Driver 0.18.0 para Mozilla Superior ou Igual a Versão 27'
        elif self.versao >= 55.0 and self.versao < 57.0:
            self.webDriveName = 'Driver 0.19.0 para Mozilla Superior ou Igual a Versão 55'
        elif self.versao >= 57.0 and self.versao < 60.0:
            self.webDriveName = 'Driver 0.21.0 para Mozilla Superior ou Igual a Versão 57'
        elif self.versao >= 60.0 and self.versao < 79.0:
            self.webDriveName = 'Driver 0.26.0 para Mozilla Superior ou Igual a Versão 60'
        elif self.versao >= 79.0:
            self.webDriveName = 'Driver 0.27.0 para Mozilla Superior ou Igual a Versão 79'

        # Abrir WebDriver
        # webdriver = OpenWebDriver(self.caminhoWebDrive, dataForm['drive'], self.versao, self.url)
        webdriver = OpenWebDriver(self.caminhoWebDrive, self.webDriveName, self.versao, self.url)

        # Inicia os Objetos

        firefox = webdriver.Open(log)

        if dataForm['atividade'] != 'Assinaturas de Processos para Juiz Titular':
            openXls = OpenXls(dataForm['caminhoArquivo'])  # Instancia o objeto passando o caminho do arquivo
            # Abre o arquivo XLS
            xlsData = openXls.OpenFileXls(firefox, log)

        # Captura informacoes da maquina
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)

        log.info('---------------------------')
        log.info('O robo iniciou com os seguintes dados: ')
        log.info('O caminho do arquivo informado foi: ' + dataForm['caminhoArquivo'])
        #log.info('O usuario utilizado foi: ' + dataForm['login'])
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
            log.info('IP Internet: ')


        log.info('IP Local: ' + str(IP))
        log.info('Nome da maquina: ' + str(hostname))
        log.info('Endereco MAC da maquina: ' + str(get_mac_address()))
        log.info('Versao do Navegador: ' + str(self.versao))
        log.info('---------------------------')

        # Inicia Autenticacao
        auth = Auth(firefox, log, self.caminhoImages)

        # Codigo fica especificado de acordo com codigo atribuido no sistema
        if dataForm['perfil'] == '1ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral' or dataForm['perfil'] == '4ª Turma Recursal / Gab. 2 - 4ª Turma Recursal / Juiz Substituto':
            codPerfil = 0
        elif dataForm['perfil'] == '2ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral' or dataForm['perfil'] == '5ª Turma Recursal Provisória / Gab. 3 - 5ª Turma Recursal Provisória / Juiz Subitituto':
            codPerfil = 1
        elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria' or dataForm['perfil'] == '6ª Turma Recursal Provisória / Gab. 1 - 6ª Turma Recursal Provisória / Juiz Titular':
            codPerfil = 2
        elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão' or dataForm['perfil'] == '6ª Turma Recursal Provisória / Gab. da Presidência da 6ª Turma Recursal / Juiz Titular':
            codPerfil = 3
        elif dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria':
            codPerfil = 4
        elif dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão':
            codPerfil = 5

        # Seleciona o perfil
        selecionarPerfil = Perfil(firefox, log, codPerfil, dataForm['perfil'])

        time.sleep(3)

        if dataForm['atividade'] == 'Encaminhar processos julgados em sessão para assinar inteiro teor de acórdão':

            # Executa a tarefa Aguardando Sessão Julgamento
            executaAguardandoSessaoJulgamento = TaskAguardandoSessaoJulgamento(firefox, self.caminhoImages, log,
                                                                               openXls, xlsData,
                                                                               '(TR) Aguardando sessão de julgamento', xml)

            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaAguardandoSessaoJulgamento.listProcessos, 0, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                sys.exit(0)

        elif dataForm['atividade'] == 'Inclusão de processos na relação de julgamento':

            # Inclusão de processos na relação de julgamento
            executaInclusaoProcessos = TaskInclusaoProcessos(firefox, self.caminhoImages, log,
                                                                               openXls, xlsData,
                                                                               'Inclusão de processos na relação de julgamento',
                                                                               xml)
            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaInclusaoProcessos.listProcessos, 1, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                sys.exit(0)

        elif dataForm['atividade'] == 'Assinaturas de Processos para Juiz Titular':

            # Assinaturas de Processos para Juiz Titular
            executaAssinaturaProcessos = TaskAssinaturaProcessos(firefox, self.caminhoImages, log,
                                                                               'Assinaturas de Processos para Juiz Titular')
            # try:
            # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
            form = FormResultado(executaAssinaturaProcessos.listProcessos, 1, log)
            # except:
            #     log.exception('Falha ao gerar o formulario final.')
            #     log.info('Finalizando o robo.')
            #     log.shutdown()
            #     sys.exit(0)

        elif dataForm['atividade'] == 'Transitar em Julgado':

            # Transitar em Julgado
            executaTransitarJulgado = TaskTransitarJulgado(firefox, self.caminhoImages, log,
                                                                               openXls, xlsData,
                                                                               '(TR) Julgados em sessão',
                                                                               xml)
            try:
                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaTransitarJulgado.listProcessos, 0, log)
            except:
                log.exception('Falha ao gerar o formulario final.')
                log.info('Finalizando o robo.')
                log.shutdown()
                sys.exit(0)


        # elif dataForm['atividade'] == '(TR) Concluso para decisã':
        #     codPerfil = 2

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