import os
import tkinter as Tkinter
from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter.ttk import Combobox
from tkinter import messagebox
from brutils import cpf, cnpj

from src.Default.Control.StartRobo import StartRobo


class Form(StartRobo):

    log = ""
    xml = ""
    inFileTxt = ""

    def __init__(self, log, xml):
        self._log = log
        self._xml = xml
        self.criaForm()

    def criaForm(self):
        form = Tkinter.Tk()

        getFld = Tkinter.IntVar()

        form.iconbitmap(self.resource_path('icon_pje.ico'))

        form.wm_title([i.text for i in self._xml.iter('title')][0])

        frame = Tkinter.Frame(form, relief=RAISED, borderwidth=1)
        frame.pack(fill=BOTH, expand=True)

        stepOne = Tkinter.LabelFrame(frame, text=" 1. Informe a localização da planilha: ")
        stepOne.grid(row=0, columnspan=7, sticky='W', \
                     padx=5, pady=5, ipadx=5, ipady=5,)

        # Autenticacao por login
        # #########################################################
        # stepTwo = Tkinter.LabelFrame(frame, text=" 2. Informe os dados de autenticação: ")
        # stepTwo.grid(row=2, columnspan=7, sticky='W', \
        #              padx=5, pady=5, ipadx=5, ipady=5)
        # #########################################################

        stepThree = Tkinter.LabelFrame(frame, text=" 2. Configure a Atividade: ")
        stepThree.grid(row=1, columnspan=7, sticky='W', \
                       padx=5, pady=5, ipadx=5, ipady=5)

        stepFour = Tkinter.LabelFrame(frame, text=" 3. Configure o Perfil: ")
        stepFour.grid(row=2, columnspan=7, sticky='W', \
                       padx=5, pady=5, ipadx=5, ipady=5)

        # stepFive = Tkinter.LabelFrame(frame, text=" 4. Informe o drive ser ultilizado: ")
        # stepFive.grid(row=3, columnspan=7, sticky='W', \
        #              padx=5, pady=5, ipadx=5, ipady=5)

        inFileLbl = Tkinter.Label(stepOne, text="Selecione o arquivo: ")
        inFileLbl.grid(row=0, column=0, sticky='E', padx=(5, 2), pady=2)

        self._inFileTxt = Tkinter.Entry(stepOne, width=50, state="readonly")
        self._inFileTxt.grid(row=0, column=1, columnspan=7, sticky="WE", pady=6)

        inFileBtn = Tkinter.Button(stepOne, text="Selecionar ...", command=lambda: self.open_file())
        inFileBtn.grid(row=0, column=8, sticky='W', padx=5, pady=2)

        # Autenticacao por login
        # #########################################################
        # outTblLbl = Tkinter.Label(stepTwo, \
        #       text="Login: ")
        # outTblLbl.grid(row=3, column=0, sticky='W', padx=5, pady=2)
        #
        # outTblTxt = Tkinter.Entry(stepTwo)
        # outTblTxt.grid(row=3, column=1, columnspan=3, pady=2, sticky='WE')
        #
        # outTblLblS = Tkinter.Label(stepTwo, \
        #                           text="Senha: ")
        # outTblLblS.grid(row=4, column=0, sticky='W', padx=5, pady=2)
        #
        # outTblTxtS = Tkinter.Entry(stepTwo, show="*")
        # outTblTxtS.grid(row=4, column=1, columnspan=3, pady=2, sticky='WE')
        # #########################################################

        # #########################################################
        selectTask = Combobox(stepThree, width=80, state="readonly")

        selectTask['values'] = (
            "Encaminhar processos julgados em sessão para assinar inteiro teor de acórdão",
            "Inclusão de processos na relação de julgamento",
            "Certidão de trânsito em julgado/devolver para origem ou para o arquivo (depende da classe)",
            "Lançamento de movimentação TPU",
            "Assinatura de decisão sobre recurso",
            "Assinatura de inteiro teor de acórdãos",
        )

        # selectTask.current(0)
        selectTask.grid(row=6, sticky='W', padx=5, pady=2, ipady=2)
        # #########################################################

        # #########################################################
        selectPerfil = Combobox(stepFour, width=80, state="readonly")

        selectPerfil['values'] = (
            "1ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral",
            "2ª Turma Recursal / Secretaria de Turma Recursal / Servidor Geral",
            "5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria",
            "5ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão",
            "6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Diretor de Secretaria",
            "6ª Turma Recursal Provisória / Secretaria de Turma Recursal / Secretário da Sessão",
        )

        # selectPerfil.current(0)
        selectPerfil.grid(row=7, sticky='W', padx=5, pady=2, ipady=2)
        # #########################################################

        # #########################################################

        # selectDrive = Combobox(stepFive, width=80, state="readonly")
        #
        #
        # listDrive = []
        #
        # for elem in self._xml:
        #     if elem.tag == 'driverNameList':
        #         for var in elem:
        #             # if var.attrib.get('name') == '':
        #             listDrive.append(var.text)
        #
        # selectDrive['values'] = listDrive
        #
        #
        # selectDrive.grid(row=7, sticky='W', padx=5, pady=2, ipady=2)
        # #########################################################

        closeButton = Tkinter.Button(form, text="Fechar", command=lambda: self.clickClose())
        closeButton.pack(side=RIGHT, padx=5, pady=5)                                                       # Usado com autenticacao com login
        okButton = Tkinter.Button(form, text="OK", command=lambda: self.clickOk(selectTask, selectPerfil)) # self.clickOk(outTblTxt, outTblTxtS, selectTask, selectPerfil, selectDrive)
        okButton.pack(side=RIGHT)

        form.mainloop()

    def clickClose(self):
        sys.exit(0)

    def clickOk(self, selectTask, selectPerfil):

        dataForm = {'caminhoArquivo' : str(self._inFileTxt.get()),
                   # 'login' : str(outTblTxt.get()),
                   # 'senha' : str(outTblTxtS.get()),
                    'atividade' : str(selectTask.get()),
                    'perfil' : str(selectPerfil.get()),
                    # 'drive' : str(selectDrive.get()),
        }

        for i, v in dataForm.items():
            if v == '' or len(v) == 0:
                if str(i) == 'caminhoArquivo':
                    Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado", message="Por favor, verifique se preencheu o campo Selecionar Arquivo corretamente.")
                    return 0
                # Autenticacao por login
                # #########################################################
                # elif str(i) == 'login':
                #     Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                #                                    message="Por favor, verifique se preencheu o campo Login corretamente.")
                #     outTblTxt.focus()
                #     return 0
                # elif str(i) == 'senha':
                #     Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                #                                    message="Por favor, verifique se preencheu o campo Senha corretamente.")
                #     outTblTxtS.focus()
                #     return 0
                # #########################################################
                elif str(i) == 'atividade':
                    Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                                                   message="Por favor, verifique se selecionou à Atividade corretamente.")
                    selectTask.focus()
                    return 0
                elif str(i) == 'perfil':
                    Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                                                   message="Por favor, verifique se selecionou o Perfil corretamente.")
                    selectTask.focus()
                    return 0
                # else:
                #     Tkinter.messagebox.showwarning(title="Campo Vazio Encontrado",
                #                                    message="Por favor, verifique se selecionou o Drive corretamente.")
                #     selectPerfil.focus()
                #     return 0

        # Autenticacao por login
        # #########################################################
        # if not cpf.validate(dataForm['login']):
        #     if not cnpj.validate(dataForm['login']):
        #         Tkinter.messagebox.showwarning(title="Login Inválido",
        #                                        message="O dado de login CPF/CNPJ não é válido!")
        #         outTblTxt.focus()
        #         return 0
        #
        # if not cnpj.validate(dataForm['login']):
        #     if not cpf.validate(dataForm['login']):
        #         Tkinter.messagebox.showwarning(title="Login Inválido",
        #                                        message="O dado de login CPF/CNPJ não é válido!")
        #         outTblTxt.focus()
        #         return 0
        # #########################################################

        robo = self.startRobo(self._log, self._xml, dataForm)

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