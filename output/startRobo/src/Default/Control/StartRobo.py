import sys
import time
import json
from urllib import request
import socket
from getmac import get_mac_address

from src.Default.Control.Auth import Auth
from src.Default.Control.OpenWebDriver import OpenWebDriver
from src.Default.Control.OpenXls import OpenXls
from src.Default.Control.Perfil import Perfil
from src.Default.Control.TaskAguardandoSessaoJulgamento import TaskAguardandoSessaoJulgamento
from src.Default.Forms.FormResultado import FormResultado


class StartRobo:

    caminhoWebDrive = ""
    caminhoImages = ""
    url = ""

    def startRobo(self, log, xml, dataForm):

        self.caminhoWebDrive = [i.text for i in xml.iter('directoryDriver')][0] + "\\" + \
                                [i.text for i in xml.iter('driverName')][0]
        self.caminhoImages = [i.text for i in xml.iter('directoryImages')][0] + "\\"
        self.url = [i.text for i in xml.iter('url')][0]

        # Abrir WebDriver
        webdriver = OpenWebDriver(self.caminhoWebDrive, self.url)

        # Inicia os Objetos
        xls = OpenXls(dataForm['caminhoArquivo']) # Instancia o objeto passando o caminho do arquivo
        firefox = webdriver.Open(log)

        # Abre o arquivo XLS
        xlsData = xls.OpenFileXls(firefox, log)

        # Captura o IP externo
        url = request.urlopen('http://ip-api.com/json').read()
        jsn = json.loads(url.decode('UTF-8'))

        # Captura informacoes da maquina
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)

        log.info('---------------------------')
        log.info('O robo iniciou com os seguintes dados: ')
        log.info('O caminho do arquivo informado foi: ' + dataForm['caminhoArquivo'])
        log.info('O usuario utilizado foi: ' + dataForm['login'])
        log.info('A atividade selecionada foi: ' + dataForm['atividade'])
        log.info('O perfil selecionado foi: ' + dataForm['perfil'])
        log.info('---------------------------')
        log.info('Dados da maquina que executou: ')
        log.info('IP Internet: ' + str(jsn['query']))
        log.info('IP Local: ' + str(IP))
        log.info('Nome da maquina: ' + str(hostname))
        log.info('Endereco MAC da maquina: ' + str(get_mac_address()))
        log.info('---------------------------')

        # Inicia Autenticacao
        auth = Auth(firefox, log, self.caminhoImages, dataForm['login'], dataForm['senha'])

        try:
            if dataForm['perfil'] == '1ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral':
                codPerfil = 0
            elif dataForm['perfil'] == '2ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral':
                codPerfil = 1
            elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria':
                codPerfil = 2
            elif dataForm['perfil'] == '5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão':
                codPerfil = 3
            elif dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria':
                codPerfil = 4
            elif dataForm['perfil'] == '6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão':
                codPerfil = 5
        except:
            log.exception('Falha identificar o perfil')
            log.info('Finalizando o robo.')
            log.shutdown()
            firefox.quit()
            sys.exit(0)

        # Seleciona o perfil com codigo 0
        selecionarPerfil = Perfil(firefox, log, codPerfil, dataForm['perfil'])

        time.sleep(3)

        try:
            if dataForm['atividade'] == 'Encaminhar processos julgados em sessão para assinar inteiro teor de acórdão':
                # Executa a tarefa Aguardando Sessão Julgamento
                executaAguardandoSessaoJulgamento = TaskAguardandoSessaoJulgamento(firefox, self.caminhoImages, log,
                                                                                   xls, xlsData,
                                                                                   '(TR) Aguardando sessão de julgamento', xml)

                # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]
                form = FormResultado(executaAguardandoSessaoJulgamento.listProcessos, log)

            elif dataForm['atividade'] == '(TR) Aguardando decurso de prazo':
                codPerfil = 1
            elif dataForm['atividade'] == '(TR) Concluso para decisã':
                codPerfil = 2


        except:
            log.exception('Falha identificar a atividade')
            log.info('Finalizando o robo.')
            log.shutdown()
            firefox.quit()
            sys.exit(0)