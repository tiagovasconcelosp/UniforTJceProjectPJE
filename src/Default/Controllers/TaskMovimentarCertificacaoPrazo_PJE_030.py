# ###################################################
# ###################################################
# ## Desenvolvido por:
# ## Érico Neto
# ## E-mail: erico.neto@tjce.jus.br
# ## Núcleo de Inovações SETIN
# ###################################################
# ###################################################

import time
import pyautogui
import os

from selenium.webdriver.common.by import By

from .Auth import Auth
from .Metodos import Metodos


class TaskMovimentarCertificacaoPrazo_PJE_030:
    def __init__(self, driver, logging, url, dataForm, log_bi):
        self.log_bi = log_bi
        self.driver = driver
        self.logging = logging
        self.url = url
        self.dataForm = dataForm
        self.metodos = Metodos(url)
        self.processo_em_execucao = ""
        self.total_processos = 0

        self.execute()

    def mensagem(self, mensagem):
        self.logging.info(mensagem)

    def escolher_perfil(self):
        perfil = self.metodos.get_element(
            self.driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]'
        )
        time.sleep(2)
        if perfil.get_attribute("data-original-title") != self.dataForm["perfil"]:
            self.mensagem("Realizando a mudança do Perfil")
            perfil.click()
            select = self.metodos.get_element(
                self.driver,
                '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]',
            )
            options = select.find_elements(by=By.TAG_NAME, value="option")
            select.click()
            for option in options:
                if option.text == self.dataForm["perfil"]:
                    option.click()
                    time.sleep(2)
                    perfil = self.metodos.get_element(
                        self.driver,
                        '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]',
                    )
                    self.metodos.controlar_tempo_espera(True)
                    while (
                        perfil.get_attribute("data-original-title")
                        != self.dataForm["perfil"]
                    ):
                        time.sleep(0.5)
                        self.metodos.controlar_tempo_espera(max=150)
                    break
        self.mensagem("Identificação do Perfil")

    def acessar_tarefas(self):
        self.driver.switch_to.default_content()
        url2 = self.url.replace("login.seam", "ng2/dev.seam#/painel-usuario-interno")
        print(f"url:{url2}")
        self.driver.get(url2)
        self.mensagem("Acesso da Url: " + url2)

        self.acessar_frame('//*[@id="ngFrame"]')
        self.mensagem("Alteração para Frame interno")

        self.mensagem("Aguardando lista de Tarefas carregar")
        self.metodos.controlar_tempo_espera(True)
        while not self.metodos.check_exists_by_xpath(
            self.driver,
            '//*[@id="divTarefasPendentes"]/div[3]/div[1]/div/a/div/span[1]',
        ):
            time.sleep(0.5)
            print("Aguarda lista de Tarefas")
            self.metodos.identificacao_erros(self.driver)
            self.metodos.controlar_tempo_espera(max=150)
        self.driver.switch_to.default_content()

    def selecionar_fila(self):
        self.acessar_frame('//*[@id="ngFrame"]')
        self.mensagem("Acessando Lista da Tarefa")
        processos_ativos = None
        fila = "[Sec] - Prazo - VERIFICAR PRAZO JÁ DECORRIDO"
        processos_ativos = self.metodos.elemento_por_texto_em_lista_by_xpath_e_tag(
            self.driver, '//*[@id="rightPanel"]/div/div[3]', "a", fila
        )

        if processos_ativos is None:
            mensagem = "Não foi encontrada a fila: " + fila
            self.mensagem(mensagem)
            pyautogui.alert(mensagem)
            return

        total_inicial = str(processos_ativos.text).replace(
            "[Sec] - Prazo - VERIFICAR PRAZO JÁ DECORRIDO\n", ""
        )
        processos_ativos.click()
        self.mensagem("Aguardando Página de Processos Ativos")
        self.metodos.controlar_tempo_espera(True)
        while total_inicial != self.metodos.texto_by_xpath(
            self.driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'
        ):
            time.sleep(0.5)
            self.metodos.identificacao_erros(self.driver)
            self.metodos.controlar_tempo_espera(max=150)

        self.driver.switch_to.default_content()

    def selecionar_aba_processos(self):
        self.acessar_frame('//*[@id="ngFrame"]')
        aba_processos_xpath = '//*[@id="myTabs"]/li[1]/a'
        aba_processos = self.metodos.get_element(
            self.driver, aba_processos_xpath, max=20
        )
        aba_processos.click()
        self.driver.switch_to.default_content()

    def seleciona_processo(self):
        processo = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[1]/processo-datalist-card/div/div[3]/a/div/span[2]'
        texto_processo = self.metodos.get_element(self.driver, processo, max=150)
        self.processo_em_execucao = texto_processo.text
        print(self.processo_em_execucao)
        self.log_bi.adicionar_processo(processo=self.processo_em_execucao)
        texto_processo.click()

    def clica_encaminhar_processo(self):
        botao_encaminhar_para = '//*[@id="btnTransicoesTarefa"]'
        botao_encaminhar_para = self.metodos.get_element(
            self.driver, botao_encaminhar_para, max=150
        )
        botao_encaminhar_para.click()

    def seleciona_opcao(self, xpath):
        botao_concluir = self.metodos.get_element(self.driver, xpath, max=20)
        time.sleep(1.5)
        print(botao_concluir.text)
        botao_concluir.click()


    def acessar_frame(self, frame):
        iframe = self.metodos.get_element(self.driver, frame)
        self.driver.switch_to.frame(iframe)

    def movimenta_certificacao_prazo(self):        
        self.mensagem("Seleciona novo processo")
        try:
            self.seleciona_processo()
            time.sleep(2)
            self.clica_encaminhar_processo()
            time.sleep(2)
            self.seleciona_opcao('//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[2]/a')
            
            self.log_bi.atualizar_etapa_processo(
                processo=self.processo_em_execucao,
                etapa="VERIFICADO PRAZO JÁ DECORRIDO",
                atualizacao="Realizado",
            )            
        except Exception as e:
            self.log_bi.enviar_erro(
                num_processo=self.processo_em_execucao,
                passo_executado="VERIFICADO PRAZO JÁ DECORRIDO",
                mensagem=repr(e),
            )
            raise Exception("Erro no fluxo de verificar prazo ja decorrido")

    def execute(self):
        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(
            ["VERIFICADO PRAZO JÁ DECORRIDO"]
        )
        repete = True
        self.logging.info("##############################")
        self.logging.info("Robô iniciado")
        self.logging.info("Acesso da Url: " + self.url)
        self.driver.get(self.url)
        time.sleep(2)
        # autenticacao = Auth()
        # autenticacao.Login(self.driver, self.logging, self.dataForm, self.url)
        primeira = True
        if primeira:
            mensagem = (
                "Realize o login manualmente e em seguida clique em OK para prosseguir."
            )
            self.mensagem("Aguardando Login")
            pyautogui.alert(mensagem)
            primeira = False

        self.escolher_perfil()
        self.mensagem("Identificação do Perfil")
        while repete:
            try:
                repete = False
                self.acessar_tarefas()
                self.selecionar_fila()
                time.sleep(2)
                self.selecionar_aba_processos()
                time.sleep(2)
                while True:
                    self.acessar_frame('//*[@id="ngFrame"]')
                    total_processos = self.metodos.get_element(
                        self.driver,
                        '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span',
                    )
                    self.total_processos = total_processos.text
                    if int(self.total_processos) > 0:
                        try:                            
                            self.movimenta_certificacao_prazo()
                            time.sleep(3)
                        except:
                            self.driver.switch_to.default_content()
                            if "QuadroAviso" in str(self.driver.current_url):
                                raise Exception("Voltou quadro de aviso")
                            continue
                    else:
                        break
                    self.driver.switch_to.default_content()
            except Exception as e:
                self.logging.info(repr(e))
                print("Erro: ", repr(e))
                print(self.total_processos, repete)
                if int(self.total_processos) > 0:
                    repete = True
                    self.driver.refresh()

        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(
            text="A execução terminou. Consulte o arquivo "
            + self.log_bi.retorna_nome_arquivo(),
            title="Término de Execução",
            button="OK",
        )
