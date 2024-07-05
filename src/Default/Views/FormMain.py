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

import os
import tkinter as Tkinter
import time
import sys
import datetime
import psutil

from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter.ttk import Combobox
from tkinter import messagebox

from src.Default.Controllers.StartRobo import StartRobo
from src.Default.Controllers.Logger import Logger


class Form(StartRobo):

    log = ""
    xml = ""
    time_string = ""
    time_string2 = ""
    inFileTxt = ""
    form = ""

    dataBaseModel = {}
    inicioAppTime = 0

    def __init__(self, log, xml, timeRegistreExe):
        self._log = log
        self._xml = xml
        self._timeRegistreExe = timeRegistreExe

        # Tempo da aplicacao iniciada
        named_tuple = time.localtime()

        self.time_string = time.strftime("%d-%m-%Y %H:%M:%S", named_tuple)

        self.time_string2 = time.strftime("%d%m%Y%H%M", named_tuple)

        # Registra horario que iniciou a tarefa
        self.inicioAppTime = time.time()

        # for direc in os.listdir("."):
        #     # direc = os.path.join(".", direc)
        #     if os.path.isdir(direc):
        #         tempo = os.path.getmtime(direc)
        #         datestamp = datetime.datetime.fromtimestamp(tempo)
        #         tempo_tolerancia = datetime.timedelta(minutes= 20)
        #         if datetime.datetime.now() <= datestamp+tempo_tolerancia:
        #             print(direc, datestamp, tempo_tolerancia)

        # direc = "clovis"
        direc = os.getcwd()
        self.codigo_execucao = str(int(time.time()))

        try:
            usuario_bi = [i.text for i in xml.iter('matricula')][0]
            if usuario_bi is None:
                usuario_bi = os.environ['USERNAME']
        except:
            usuario_bi = os.environ['USERNAME']

        if os.path.isdir(direc):
            tempo = os.path.getmtime(direc)
            datestamp = datetime.datetime.fromtimestamp(tempo)
            tempo_tolerancia = datetime.timedelta(minutes= 20)
            if datetime.datetime.now() <= datestamp+tempo_tolerancia:
                print(direc, datestamp, tempo_tolerancia)

                log_instalacao = Logger()
                log_instalacao.set_macro_dados(nome_rpa="Instalação",
                                               aplicacao=[i.text for i in xml.iter('aplicacao')][0],
                                               versao=[i.text for i in xml.iter('versao')][0],
                                               navegador="Não se aplica",
                                               usuario=usuario_bi,
                                               codigoRpa=self.codigo_execucao)
                log_instalacao.realizar_requisicao(num_processo=self.codigo_execucao,
                                                   passo_executado="Instalação",
                                                   mensagem="Instalação Nova Versão Realizada")

        self.criaForm()

    def kill_chromedriver(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'chromedriver.exe':
                try:
                    process = psutil.Process(proc.info['pid'])
                    process.terminate()  # Pode ser necessário usar process.kill() dependendo da situação
                    print(f"Processo {proc.info['pid']} ({proc.info['name']}) terminado com sucesso.")
                except Exception as e:
                    print(f"Erro ao terminar o processo {proc.info['pid']} ({proc.info['name']}): {e}")

    def setDatabase(self):
        self.dataBaseModel = {
                    'id' : self.time_string2,
                    'data_aplicacao' : self.time_string,
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

    def center_window(self, w=300, h=200):
        # get screen width and height
        ws = self.form.winfo_screenwidth()
        hs = self.form.winfo_screenheight()
        # calculate position x, y
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.form.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def criaForm(self):

        self.form = Tkinter.Tk()

        # Detecta se clicou no X
        self.form.protocol("WM_DELETE_WINDOW", self.clickClose)

        self.form.resizable(False, False)

        self.center_window(538, 312)

        getFld = Tkinter.IntVar()

        self.form.iconbitmap(self.resource_path('icon_pje.ico'))

        self.form.wm_title([i.text for i in self._xml.iter('title')][0])

        frame = Tkinter.Frame(self.form, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=True)

        stepThree = Tkinter.LabelFrame(frame, text=" 1. Selecione a Atividade: ")
        stepThree.grid(row=0, columnspan=7, sticky='W', \
                       padx=5, pady=5, ipadx=5, ipady=5)

        stepFour = Tkinter.LabelFrame(frame, text=" 2. Configure o Perfil: ")
        stepFour.grid(row=1, columnspan=7, sticky='W', \
                       padx=5, pady=5, ipadx=5, ipady=5)

        stepOne = Tkinter.LabelFrame(frame, text=" 3. Informe a localização da planilha: ")
        stepOne.grid(row=2, columnspan=7, sticky='W', \
                     padx=5, pady=5, ipadx=5, ipady=5,)

        stepFive = Tkinter.LabelFrame(frame, text=" 4. Informe seus dados de autenticação (PJE/SEEU): ", width=80)
        stepFive.grid(row=3, columnspan=7, sticky='W', \
                       padx=5, pady=5, ipadx=5, ipady=5)

        inFileLbl = Tkinter.Label(stepOne, text="Selecione o arquivo: ")
        inFileLbl.grid(row=0, column=0, sticky='E', padx=(5, 2), pady=2)

        self._inFileTxt = Tkinter.Entry(stepOne, width=50, state="readonly")
        self._inFileTxt.grid(row=0, column=1, columnspan=7, sticky="WE", pady=6)

        inFileBtn = Tkinter.Button(stepOne, text="Selecionar ...", command=lambda: self.open_file())
        inFileBtn.grid(row=0, column=8, sticky='W', padx=5, pady=2)

        inLoginLbl = Tkinter.Label(stepFive, text="Login: ")
        inLoginLbl.grid(row=0, column=0, sticky='W', padx=(15, 2), pady=2)

        self._inLogin = Tkinter.Entry(stepFive, width=15,)
        self._inLogin.grid(row=0, column=1, columnspan=7, sticky="W", pady=6)

        inPassLbl = Tkinter.Label(stepFive, text="Senha: ")
        inPassLbl.grid(row=0, column=3, sticky='W', padx=(100, 2), pady=2)

        self._inPass = Tkinter.Entry(stepFive, show='*', width=15, )
        self._inPass.grid(row=0, column=4, columnspan=7, sticky="W", pady=6)

        # #########################################################
        selectTask = Combobox(stepThree, width=80, state="readonly")

        automacoes = {"Execuções Fiscais": ["Elaboração de Despacho Inicial Núcleo 4.0",
                                            "Carta de Citação Núcleo 4.0",
                                            "Determinar Medidas de Constrição",
                                            "Elaborar Mandado de Citação",
                                            "Preparar Citação e ou Intimação",
                                            "Preparar Citação e ou Intimação da Sentença"],
                      "SISBAJUD": ["Consulta no SISBAJUD", "Resultado no SISBAJUD"],
                      "RENAJUD": ["Consulta no RENAJUD [PJE2G]"],
                      "SEEU": ["Instauração dos incidentes a vencer e realização de citação [SEEU]", 
                               "Intimação de MP e Advogado/DP de uma decisão/sentença [SEEU]", 
                               "Intimar pessoalmente a partir de despacho pré-determinado [SEEU]",
                               "Instauração dos incidentes a vencer e realização de intimação [SEEU]",
                               "Realizar Pré-análise de Processos [SEEU]",],
                      "Turmas Recursais": ["Inclusão de processos na relação de julgamento [PJE2G]",
                                           "Transitar em Julgado [PJE2G]",
                                            ],
                      "SEJUD":["Realizar Movimentação para Certificação de Prazo"],    
                      "Outros": ["Movimentação de Processos Ativos [SAJ]",
                                 "Intimação de embargos de declaração para contrarrazões"]}
        
        ambiente_selecionado = []
        for ambiente in [i.text for i in self._xml.iter('ambiente')]:
            if ambiente == "Todos":
                for aut in automacoes:
                    ambiente_selecionado += automacoes[aut]
                break
            ambiente_selecionado += automacoes[ambiente]
        selectTask['values'] = tuple(ambiente_selecionado)

        # selectTask.current(0)
        selectTask.grid(row=6, sticky='W', padx=5, pady=2, ipady=2)
        # #########################################################

        # #########################################################
        selectPerfil = Combobox(stepFour, width=80, state="readonly")

        selectPerfil['values'] = [i.text for i in self._xml.iter('value')]

        # selectPerfil.current(0)
        selectPerfil.grid(row=7, sticky='W', padx=5, pady=2, ipady=2)
        # #########################################################

        closeButton = Tkinter.Button(self.form, text="Fechar", command=lambda: self.clickClose())
        closeButton.pack(side=RIGHT, padx=5, pady=5)                                                       # Usado com autenticacao com login
        okButton = Tkinter.Button(self.form, text="OK", command=lambda: self.clickOk(selectTask, selectPerfil)) # self.clickOk(outTblTxt, outTblTxtS, selectTask, selectPerfil, selectDrive)
        okButton.pack(side=RIGHT)

        # #########################################################
        label_versao = Tkinter.Label(self.form, text="Versão "+[i.text for i in self._xml.iter('versao')][0])
        label_versao.pack(side=LEFT) 

        self.form.mainloop()

    def clickClose(self):

        # Registra horario que finalizou a tarefa
        fim = time.time()

        timeTotal = fim - self.inicioAppTime

        timeTotal = float('{:.2f}'.format(timeTotal))

        self.form.destroy()

        self._log.info('Finalizando o robo.')

        self._log.shutdown()

        self.kill_chromedriver()
        os._exit(0)
        sys.exit(0)

    def clickOk(self, selectTask, selectPerfil):

        self.setDatabase()

        dataForm = {'caminhoArquivo' : str(self._inFileTxt.get()),
                    'atividade' : str(selectTask.get()),
                    'perfil' : str(selectPerfil.get()),
                    'login': str(self._inLogin.get()),
                    'pass': str(self._inPass.get()),
        }

        for i, v in dataForm.items():
            if v == '' or len(v) == 0:
                if str(i) == 'perfil':
                    # Filtro de atividades que não utiliza Perfil
                    if dataForm['atividade'] != 'Instauração dos incidentes a vencer e realização de intimação [SEEU]' \
                        and dataForm['atividade'] != 'Instauração dos incidentes a vencer e realização de citação [SEEU]' \
                        and dataForm['atividade'] != 'Realizar Pré-análise de Processos [SEEU]' \
                        and dataForm['atividade'] != 'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]' \
                        and dataForm['atividade'] != 'Intimação de MP e Advogado/DP de uma decisão/sentença [SEEU]' \
                        and dataForm['atividade'] != 'Consulta no RENAJUD [PJE2G]':
                        Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado", message="Por favor, verifique se selecionou o Perfil corretamente.")
                        selectTask.focus()
                        return 0

                elif str(i) == 'caminhoArquivo':
                    # Essa atividade nao utiliza planilha
                    if dataForm['atividade'] == 'Inclusão de processos na relação de julgamento [PJE2G]' \
                        or dataForm['atividade'] == 'Transitar em Julgado [PJE2G]':

                        Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado", message='Por favor, verifique se preencheu o campo "Selecionar Arquivo" corretamente.')
                        return 0
                elif str(i) == 'atividade':
                    Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado", 
                                                   message="Por favor, verifique se selecionou à Atividade corretamente.")
                    selectTask.focus()
                    return 0

                elif str(i) == 'login':
                    # Filtro de atividades que não utilizam login
                    if dataForm['atividade'] != 'Carta de Citação Núcleo 4.0' \
                        and dataForm['atividade'] != 'Elaboração de Despacho Inicial Núcleo 4.0' \
                        and dataForm['atividade'] != 'Determinar Medidas de Constrição'\
                        and dataForm['atividade'] != 'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]'\
                        and dataForm['atividade'] != 'Elaborar Mandado de Citação' \
                        and dataForm['atividade'] != 'Inclusão de processos na relação de julgamento [PJE2G]' \
                        and dataForm['atividade'] != 'Transitar em Julgado [PJE2G]' \
                        and dataForm['atividade'] != 'Consulta no RENAJUD [PJE2G]' \
                        and dataForm['atividade'] != 'Preparar Citação e ou Intimação'\
                        and dataForm['atividade'] != 'Preparar Citação e ou Intimação da Sentença'\
                        and dataForm['atividade'] != 'Intimação de embargos de declaração para contrarrazões'\
                        and dataForm['atividade'] != 'Resultado no SISBAJUD'\
                        and dataForm['atividade'] != 'Realizar Movimentação para Certificação de Prazo':
                        Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                                                    message="Por favor, informe o Login.")
                        selectTask.focus()
                        return 0
                elif str(i) == 'pass':
                    # Filtro de atividades que não utilizam senha
                    if dataForm['atividade'] != 'Carta de Citação Núcleo 4.0' \
                        and dataForm['atividade'] != 'Elaboração de Despacho Inicial Núcleo 4.0' \
                        and dataForm['atividade'] != 'Determinar Medidas de Constrição'\
                        and dataForm['atividade'] != 'Intimar pessoalmente a partir de despacho pré-determinado [SEEU]'\
                        and dataForm['atividade'] != 'Elaborar Mandado de Citação' \
                        and dataForm['atividade'] != 'Inclusão de processos na relação de julgamento [PJE2G]' \
                        and dataForm['atividade'] != 'Transitar em Julgado [PJE2G]' \
                        and dataForm['atividade'] != 'Consulta no RENAJUD [PJE2G]' \
                        and dataForm['atividade'] != 'Preparar Citação e ou Intimação'\
                        and dataForm['atividade'] != 'Preparar Citação e ou Intimação da Sentença'\
                        and dataForm['atividade'] != 'Intimação de embargos de declaração para contrarrazões'\
                        and dataForm['atividade'] != 'Resultado no SISBAJUD'\
                        and dataForm['atividade'] != 'Realizar Movimentação para Certificação de Prazo':
                        Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                                                    message="Por favor, informe a senha do Login.")
                        selectTask.focus()
                        return 0

        robo = self.startRobo(self._log, self._xml, dataForm, self.dataBaseModel, self.codigo_execucao)

    def open_file(self):

        try:
            file = askopenfile(mode='r', title="Selecione o arquivo", initialdir=os.path.expanduser('~\\Downloads'), filetypes=[('Arquivo Excel', '*.xls'), ('Arquivo Excel', '*.xlsx')])

            if file is not None:
                self._inFileTxt.configure(state="normal")
                self._inFileTxt.delete(0, END)
                self._inFileTxt.insert(0, str(file.name))
                self._inFileTxt.configure(state="readonly")
        except:
            file = ''

    def resource_path(self, relative_path):
        """ Obtenha o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
        try:
            # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)