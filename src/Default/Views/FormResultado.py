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

import tkinter as tk
from tkinter import *
from tkinter.ttk import Notebook


class FormResultado:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    # [['3000462-70.2019.8.06.0009', '0046121-55.2016.8.06.0011'], [1, 1], ['3000516-78.2020.8.06.0016'], 2, 0, '40.26 segundos', 1]

    log = ""
    tab1 = ""
    tab2 = ""
    canvas = ""
    scroll = ""
    canvas2 = ""
    scroll2 = ""
    window = ""

    def __init__(self, resultadoTarefa, valorDescricao, log):
        self._log = log
        self.criaForm(resultadoTarefa, valorDescricao)

    def criaForm(self, resultadoTarefa, valorDescricao):

        self.window = Tk()
        self.window.title("Resultado da Atividade Executada")
        self.window.geometry("644x700")

        # Criar Tab
        tablayout = Notebook(self.window, width=326)
        tablayout.pack(fill=BOTH, side="left", expand=FALSE)

        # Frame Listagem Processos + Encaminhados
        frame1 = Frame(tablayout, relief=RAISED, borderwidth=1, width=100)
        frame1.pack(fill=BOTH, side="left", expand=FALSE)

        frame2 = Frame(tablayout, relief=RAISED, borderwidth=1)
        frame2.pack(fill=BOTH, side="left", expand=TRUE)

        # ------------------------------------------------------------------------------------
        # Frame com resultados totais
        frame3 = Frame(self.window, relief=RAISED, borderwidth=1, )
        frame3.pack(fill=BOTH, side="left", expand=True)

        stepOne = LabelFrame(frame3, text=" Resumo do Relatório ")
        stepOne.grid(row=0, columnspan=7, sticky='W', \
                     padx=5, pady=5, ipadx=5, ipady=5, )

        outTblLbl1 = Label(stepOne, \
                                  text="Total de processos localizados: " + str(resultadoTarefa[3]))
        outTblLbl1.grid(row=1, column=0, sticky='W', padx=5, pady=2)

        outTblLbl2 = Label(stepOne, \
                          text="Total de processos encaminhados: " + str(resultadoTarefa[4]))
        outTblLbl2.grid(row=2, column=0, sticky='W', padx=5, pady=2)

        outTblLbl3 = Label(stepOne, \
                          text="Tempo de execucao da atividade: " + str(resultadoTarefa[5]))
        outTblLbl3.grid(row=3, column=0, sticky='W', padx=5, pady=2)

        outTblLbl4 = Label(stepOne, \
                          text="Total de processos que não foram localizados: " + str(resultadoTarefa[6]))
        outTblLbl4.grid(row=4, column=0, sticky='W', padx=5, pady=2)

        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # Tab 1
        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------

        self.canvas = tk.Canvas(frame1, borderwidth=0, width=320)

        # Tab Processos Localizados
        self.tab1 = Frame(self.canvas, relief=RAISED, borderwidth=1, width=100)
        self.tab1.pack(fill=BOTH, side="left", expand=FALSE)

        self.scroll = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)

        self.canvas.pack(side="left", fill="both", expand=FALSE)
        self.canvas.create_window((4, 4), window=self.tab1, anchor="nw")

        if len(resultadoTarefa[0]) >= 24:
            self.canvas.configure(yscrollcommand=self.scroll.set)
            self.scroll.pack(side="right", fill="y")
            self.tab1.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))

        if len(resultadoTarefa[0]) > 0:
            for row in range(len(resultadoTarefa[0])+1):
                for column in range(2):
                    if row == 0:
                        if column == 0:
                            label = Label(self.tab1, text="Número do Processo", bg="#f0f0f0", relief=RAISED, fg="black", padx=3, pady=3)
                            label.config(font=('Arial', 14))
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)
                        else:
                            if valorDescricao == 0:
                                descricao = 'Encaminhado'
                            elif valorDescricao == 1:
                                descricao = 'Incluído'

                            label = Label(self.tab1, text=descricao, bg="#f0f0f0", fg="black", relief=RAISED,
                                              padx=3, pady=3)

                            label.config(font=('Arial', 14))
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)
                    else:

                        if column != 0:

                            Cor = ''
                            Texto = ''

                            if (resultadoTarefa[1][row-1]) == 0:
                                Cor = 'green'

                                if valorDescricao == 0:
                                    Texto = 'Enviado com sucesso'
                                elif valorDescricao == 1:
                                    Texto = 'Incluído com sucesso'
                                elif valorDescricao == 2:
                                    Texto = 'Assinado com sucesso'

                            else:
                                Cor = 'red'

                                if valorDescricao == 0 or valorDescricao == 1:
                                    Texto = 'Houve falha ao conluir'
                                elif valorDescricao == 2:
                                    Texto = 'Houve falha ao assinar'


                            label = Label(self.tab1, text=Texto, bg=Cor, relief=RIDGE, fg="white", padx=3, pady=3)
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)

                        else:
                            label = Label(self.tab1, text=str(resultadoTarefa[0][row-1]), bg="#f0f0f0", relief=RIDGE, fg="black", padx=3, pady=3)
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)
        else:
            for row in range(2):
                for column in range(2):
                    if row == 0:
                        if column == 0:
                            label = Label(self.tab1, text="Número do Processo", bg="#f0f0f0", relief=RAISED, fg="black", padx=3, pady=3)
                            label.config(font=('Arial', 14))
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)
                        else:
                            label = Label(self.tab1, text="Encaminhado", bg="#f0f0f0", fg="black", relief=RAISED, padx=3, pady=3)
                            label.config(font=('Arial', 14))
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)
                    else:

                        if column != 0:

                            label = Label(self.tab1, text="Nenhum Dado", bg="#f0f0f0", relief=RIDGE, fg="black", padx=3, pady=3)
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)

                        else:
                            label = Label(self.tab1, text="Nenhum Dado", bg="#f0f0f0",relief=RIDGE, fg="black", padx=3, pady=3)
                            label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                            self.tab1.grid_columnconfigure(column, weight=1)


        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------
        # Tab 2
        # ------------------------------------------------------------------------------------
        # ------------------------------------------------------------------------------------

        self.canvas2 = tk.Canvas(frame2, borderwidth=0)

        # Tab Processos Localizados
        self.tab2 = Frame(self.canvas2, relief=RAISED, borderwidth=1)
        self.tab2.pack(fill=BOTH, side="left", expand=TRUE)

        self.scroll2 = tk.Scrollbar(self.window, orient="vertical", command=self.canvas2.yview)

        self.canvas2.pack(side="left", fill="both", expand=FALSE)
        self.canvas2.create_window((4, 4), window=self.tab2, anchor="nw")

        if len(resultadoTarefa[0]) < 24:
            self.canvas2.configure(yscrollcommand=self.scroll2.set)
            self.scroll2.pack(side="right", fill="y")
            self.tab2.bind("<Configure>", lambda event, canvas=self.canvas2: self.onFrameConfigure(self.canvas2))

        # ------------------------------------------------------------------------------------

        if len(resultadoTarefa[2]) > 0:
            for row in range(len(resultadoTarefa[2])+1):
                for column in range(1):
                    if row == 0:

                        label = Label(self.tab2, text="Número do Processo", bg="#efefef", relief=RAISED, fg="black", padx=3, pady=3)
                        label.config(font=('Arial', 14))
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        self.tab2.grid_columnconfigure(column, weight=1)

                    else:
                        label = Label(self.tab2, text=str(resultadoTarefa[2][row-1]), bg="#efefef", relief=RIDGE, fg="black", padx=87, pady=3)
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        self.tab2.grid_columnconfigure(column, weight=1)
        else:
            for row in range(2):
                for column in range(1):
                    if row == 0:

                        label = Label(self.tab2, text="Número do Processo", bg="#efefef", relief=RAISED, fg="black",
                                      padx=3, pady=3)
                        label.config(font=('Arial', 14))
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        self.tab2.grid_columnconfigure(column, weight=1)

                    else:

                        label = Label(self.tab2, text="Nenhum Dado", bg="#efefef", relief=RIDGE,
                                      fg="black", padx=87, pady=3)
                        label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                        self.tab2.grid_columnconfigure(column, weight=1)

        tablayout.add(frame1, text="Processos Localizados")
        tablayout.add(frame2, text="Processos Não Localizados")
        tablayout.pack(fill="both")

        tablayout.bind('<ButtonRelease-1>', lambda e: self.ScrollTab(tablayout, resultadoTarefa))

        self.window.mainloop()

    def onFrameConfigure(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def ScrollTab(self, tablayout, resultadoTarefa):

        self.scroll.destroy()
        if len(resultadoTarefa[0]) >= 24:
            self.scroll2.destroy()

        if int(tablayout.index("current")) == 1:

            self.scroll2 = tk.Scrollbar(self.window, orient="vertical", command=self.canvas2.yview)
            self.canvas.configure(yscrollcommand=self.scroll2.set)

            self.scroll2.pack(side="right", fill="y")
            self.canvas2.pack(side="left", fill="both", expand=FALSE)
            self.canvas2.create_window((4, 4), window=self.tab2, anchor="nw")

            self.tab2.bind("<Configure>", lambda event, canvas=self.canvas2: self.onFrameConfigure(self.canvas2))

        else:

            self.scroll = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.scroll.set)

            self.scroll.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=FALSE)
            self.canvas.create_window((4, 4), window=self.tab1, anchor="nw")

            self.tab1.bind("<Configure>", lambda event, canvas=self.canvas: self.onFrameConfigure(self.canvas))