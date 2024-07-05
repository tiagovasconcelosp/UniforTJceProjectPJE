# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Augusto Lima dos Santos e Lucas Pacheco de Araújo Jucá 
# ## Email: augusto.santos@tjce.jus.br 
# ##        lucas.juca@tjce.jus.br
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################
from datetime import datetime
import time
import pyautogui

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException,TimeoutException
import src.Default.Controllers.helpers as helpers
import xml.etree.ElementTree as ET

import traceback
import pandas as pd
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options as OptionsChrome

from .Auth import Auth
from .Metodos import Metodos
class Etapas:
        selecao_documento = 'Selecionar Documento'
        selecao_modelo = 'Selecionar Modelo'
        codigo_movimentacao = 'Inserção de codigo de movimentação'
        salvar = 'Salvar'
        encaminhar ='Encaminhar'
        assinatura = 'Assinatura'
        etapas=[selecao_documento, selecao_modelo,codigo_movimentacao, salvar,encaminhar,assinatura]
class TaskDespachoInicial_PJE_009:
    
    def __init__(self, driver, caminhoImages, logging, atividade, dataBaseModel, 
                 inicioTime, url, dataform, acaoEmErro,xml, log_unificado):
        dicionario = Metodos.load_child_tags_as_dict(xml,"despachoInicial")
        self.metodos = Metodos(url)
        self.modelo = dicionario.get('modelo')
        self.processo_atual = None
        self.logging = logging
        
        helpers.logging = logging
        helpers.driver = driver 
        self.driver = driver
        # driver.implicitly_wait(10)
        self.log_bi = log_unificado
        self.log_bi.criar_arquivo_executados(Etapas.etapas)
        self.Execute(driver, caminhoImages, logging, atividade, dataBaseModel, 
                     inicioTime, url, dataform, acaoEmErro,xml)

    def adicionar_linha_pandas(self, df, dados):         
        df.loc[0] = dados         
        df.index = df.index + 1         
        #df.append(pd.Series(dados, index=df.columns[:len(dados)]), ignore_index=True)
        return df

    def atualizar_status_processo(self, df, processo, coluna, status):         
        indice = df[df["Processo"]==processo].index.values.astype(int)         
        df.at[indice[0], coluna] = status         
        return df
    def mensagem(self, logging, mensagem):
        logging.info(mensagem)
        print(mensagem)
    def mudar_frame(self, frame_xpath: str):
        try:
            iframe = self.metodos.get_element(self.driver, frame_xpath)
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            self.logging.info(repr(e))
            print("Erro: ", repr(e))

    def botao_salvar(self):
    
        botao_salvar = (By.XPATH,"//input[@value='Salvar']")
        # elemento_botao_salvar = driver.find_element(*botao_salvar)
        print('Salvando')
        tentativas = 2 
        for _ in range(tentativas):
            try:
                WebDriverWait(self.driver, 10).until(lambda d : self.driver.find_element(*botao_salvar).is_enabled())
                helpers.efetuar_click(botao_salvar,rotulo_elemento = 'Botao salvar')
                self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.salvar,
                atualizacao='Realizado')
                break;
            except StaleElementReferenceException as e:
                print("Elemento Stale")
                pass
            except TimeoutException as e:
                print('Timeout no botao de salvar')
            except Exception as e:
                print('execao nao prevista')
                self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                        passo_executado=Etapas.salvar,
                                        mensagem=repr(e))
                pass
            
    def selecionar_tipo_documento(self):
        elemento = None
        print("Selecionando documento")
        while True:
            try:
                # PARAMETRIZAR    
                elements = self.driver.find_elements(by=By.TAG_NAME, value='select')
                      
                dropdown_element = Select(elements[0])
                dropdown_element.select_by_visible_text("Despacho")                              
                self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.selecao_documento,
                atualizacao='Realizado')
                return None
            except Exception as e:
                self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                        passo_executado="Selecionar Documento",
                                        mensagem=repr(e))
    def selecionar_tipo_modelo(self):
        elemento = None
        print("Selecionando modelo")
        while True:
            try:
                # PARAMETRIZAR    
                elements = self.driver.find_elements(by=By.TAG_NAME, value='select')
                
                dropdown_element =elements[1]
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(dropdown_element))
                dropdown_element =  Select(dropdown_element)
                dropdown_element.select_by_visible_text(self.modelo)                              
                
                self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.selecao_modelo,
                atualizacao='Realizado')
                return None
            except Exception as e:
                self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                        passo_executado=Etapas.selecao_modelo,
                                        mensagem=repr(e))
    def inserir_codigo_movimentao(self):
        elemento_t = (By.XPATH, "//fieldset/input[@type='text']")
        elemento_b = (By.XPATH, "//fieldset/input[@value='Pesquisar']")
        elemento_m = (By.XPATH, "//*[text()='Proferido despacho de mero expediente (11010)']")
        print("Inserindo codigo de movimentacao.")
       
        try:
            if not self.driver.find_elements(*elemento_m):   
                WebDriverWait(self.driver, 10).until(lambda d : self.driver.find_element(*elemento_t).is_enabled())
                self.driver.find_element(*elemento_t)
                input_text = self.driver.find_element(*elemento_t)
                input_text.send_keys("11010")
                WebDriverWait(self.driver, 10).until(lambda d : self.driver.find_element(*elemento_b).is_enabled())
                input_pesquisar = self.driver.find_element(*elemento_b)
                input_pesquisar.click()
            self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.codigo_movimentacao,
                atualizacao='Realizado')
        except Exception as e:
            self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                    passo_executado=Etapas.codigo_movimentacao,
                                    mensagem=repr(e))
            time.sleep(0.3)
            print("Aguardando selecao de movimentacao")
            self.metodos.controlar_tempo_espera(max=60)

    def encaminhar(self):
        botao_transicoes = (By.XPATH,'//*[@id="btnTransicoesTarefa"]')
        botao_encaminhar_assinatura = (By.XPATH,"//a[contains(text(), 'Encaminhar para assinatura')]")

        try:   
            # Encaminha para assinatura
            print("Encaminhando")

            elemento_transicoes = self.driver.find_element(*botao_transicoes)
            
            if not 'true' in elemento_transicoes.get_attribute('aria-expanded').split():
                elemento_transicoes.click()
            time.sleep(1.5)
            self.driver.find_element(*botao_encaminhar_assinatura).click()

            self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.encaminhar,
                atualizacao='Realizado')
        except Exception as e:
            self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                    passo_executado=Etapas.encaminhar,
                                    mensagem=repr(e))

    def assinar(self):
        botao_assinar = (By.XPATH,"//input[@value='Assinar documento(s)']")
        print('Assinando')
        try:
            self.driver.switch_to.default_content()
            self.mudar_frame(frame_xpath='//*[@id="ngFrame"]')
            # element =  self.driver.find_element(By.XPATH,'//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
            # time.sleep(0.5)
            self.mudar_frame(frame_xpath='//*[@id="frame-tarefa"]')
            helpers.efetuar_click(botao_assinar,'Botao assinar')
            print("Click efetuado")

            self.log_bi.atualizar_etapa_processo(processo=self.processo_atual,
                etapa=Etapas.assinatura,
                atualizacao='Realizado')


        except Exception as e:
            print('Erro ao assinar')
            print(e)
            traceback.print_exc()
            self.log_bi.enviar_erro(num_processo=self.processo_atual,
                                    passo_executado=Etapas.assinatura,
                                    mensagem=repr(e))
    def atualizar_fila_processos(self):
        self.driver.switch_to.default_content()
        self.mudar_frame(frame_xpath='//*[@id="ngFrame"]')
        
        return self.metodos.texto_by_xpath(self.driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span')
    def esperar_conclusao_assinatura(self):
        self.driver.switch_to.default_content()
        self.mudar_frame(frame_xpath='//*[@id="ngFrame"]')
        mov ='[EF] Avaliar ato judicial proferido'
        texto_carregado = self.driver.find_element(By.XPATH,'//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
        wait = WebDriverWait(self.driver, 20)
        wait.until(lambda d :mov in texto_carregado.text)
        return None
        

    def Execute(self, driver, caminhoImages, logging, atividade, dataBaseModel, inicioTime, url, dataform, acaoEmErro,xml):
        repete = True
        autenticacao = Auth()
        # metodos = Metodos(url)
        desktop = [i.text for i in xml.iter('caminhoExecutados')][0]
        if desktop is None:

            desktop = Path.home() / "Desktop"
            if not Path.exists(desktop):
                desktop = Path.home() / "OneDrive" / "Área de Trabalho"
            if not Path.exists(desktop):
                desktop = Path.home() / "OneDrive" / "Desktop"
        path_executados = os.path.join(desktop, "executados")

        
        if not os.path.isdir(path_executados):
            os.mkdir(path_executados)
        data_arq = time.localtime() 
        # nome_arquivo = os.path.join(path_executados, "processos_executados_"
        #                 +str(data_arq.tm_mday) +"-"+str(data_arq.tm_mon)+"-"+str(data_arq.tm_year)
        #                 +"_" +str(data_arq.tm_hour)+"-"+str(data_arq.tm_min)+".xlsx")

        primeira = True
        while repete:
            repete = False
            total_processos = 1            
            try:
                logging.info('##############################')
                logging.info('Robô iniciado')
                driver.get(url)
                logging.info('Acesso da Url: '+ url)
                time.sleep(2)
                print("started")
                
                if primeira:
                    mensagem = 'Realize o login com o CERTIFICADO DIGITAL e em seguida clique em OK para prosseguir.'
                    self.mensagem(logging, "Aguardando Login com CERTIFICADO DIGITAL")
                    pyautogui.alert(mensagem)
                    primeira = False
                perfil = self.metodos.get_element(driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
                time.sleep(2)
                if perfil.get_attribute('data-original-title') != dataform['perfil']:
                    perfil.click()
                    select = self.metodos.get_element(driver, '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]')
                    options = select.find_elements(by=By.TAG_NAME, value='option')
                    select.click()
                    for option in options:
                        if option.text == dataform['perfil']:
                            option.click()
                            time.sleep(2)
                            perfil = self.metodos.get_element(driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
                            self.metodos.controlar_tempo_espera(True)
                            while perfil.get_attribute('data-original-title') != dataform['perfil']:
                                time.sleep(0.5)
                                self.metodos.controlar_tempo_espera(max=1200)
                            break
                logging.info('Identificação do Perfil')

                url2 = url.replace('login.seam', 'ng2/dev.seam#/painel-usuario-interno')
                driver.get(url2)
                logging.info('Acesso da Url: '+ url2)

                iframe = self.metodos.get_element(driver, '//*[@id="ngFrame"]')
                driver.switch_to.frame(iframe)
                logging.info('Alteração para Frame interno')
                print("Switched frames")

                logging.info('Aguardando lista de Tarefas carregar')
                self.metodos.controlar_tempo_espera(True)
                while not self.metodos.check_exists_by_xpath(driver, '//*[@id="divTarefasPendentes"]/div[3]/div[1]/div/a/div/span[1]'):
                    time.sleep(0.5)
                    print("Aguarda lista de Tarefas")
                    self.metodos.identificacao_erros(driver)
                    self.metodos.controlar_tempo_espera(max=1200)
                
                time.sleep(1)
                fila = '[EF] Minutar ato inicial'
                processos_ativos = self.metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                    '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
                if processos_ativos is None:
                    mensagem = 'Não foi encontrada a fila: '+fila
                    logging.info(mensagem)
                    print(mensagem)                      
                    pyautogui.alert(mensagem)
                    return 
                total_inicial = str(processos_ativos.text).replace('[EF] Minutar ato inicial\n', '')
                processos_ativos.click()
                print('Clicou na Tarefa')
                
                logging.info('Aguardando Página de Processos Ativos')
                self.metodos.controlar_tempo_espera(True)
                while total_inicial != self.metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'):
                    time.sleep(0.5)
                    print("Aguarda Carregar Página de Processos Ativos")
                    self.metodos.identificacao_erros(driver)
                    self.metodos.controlar_tempo_espera(max=1200)
                checkbox = '//*[@id="acoes-processos-selecionados"]/div/div/button/i'
               
                total_processos = self.metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span')
                print('Indetificou total de processos', total_processos)
                logging.info('Total de Processos no início da execução: '+ total_processos)
                ordem_li = 1
                total_li = 1 
                
                texto_anterior = ""
                             
                while int(total_processos) - (total_li-1) > 0 :
                    # Clica no primeiro processo da lista
                    time.sleep(1)
                    processo = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, processo)))
                    texto_processo = self.metodos.get_element(driver, processo)  
                    continua =  False
                    # Clica no processo
                    
                    
                    texto_clicado = texto_processo.text
                    texto_processo.click()
                    

                    texto_carregado = self.metodos.texto_by_xpath(self.driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    print(texto_anterior, texto_carregado, texto_carregado == texto_anterior)
                    while texto_carregado.split(' - ')[0] == texto_anterior: 
                        time.sleep(0.1)
                        self.mensagem(logging, "Aguardando recarregar o texto")
                        texto_carregado = self.metodos.texto_by_xpath(self.driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    texto_anterior = texto_carregado.split(' - ')[0]
                    if "ExFis" in texto_clicado:
                        # Identifica o processo carregado
                        texto_carregado = self.metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                        if texto_clicado in texto_carregado:
                            continua = True

                    if continua:
                        numProcesso = texto_clicado
                        self.processo_atual = numProcesso
                        self.log_bi.adicionar_processo(processo=numProcesso)
                        # Troca o frame 
                        iframe = self.metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                        driver.switch_to.frame(iframe)
                        # Aguarda o carregamento
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/a')))
                        time.sleep(0.5)

                        self.selecionar_tipo_documento()
                        time.sleep(1.2)
                        self.selecionar_tipo_modelo()
                        time.sleep(0.5)
                        self.inserir_codigo_movimentao()
                        time.sleep(0.5)
                        self.botao_salvar()

                        self.driver.switch_to.default_content()

                        iframe = '//*[@id="ngFrame"]'
                        self.driver.switch_to.frame(self.driver.find_element(By.XPATH,iframe))
                        time.sleep(0.5)
                        self.encaminhar()

                        # [EF] Assinar ato inicial. O processo deve ir para essa fila apos encaminhar.
                        self.driver.switch_to.parent_frame()

                        self.assinar()

                        self.esperar_conclusao_assinatura()
                        total_processos = self.atualizar_fila_processos()

                    else:
                        ordem_li+=1
                        total_li+=1
                        # DESCE PARA QUE OS DEMAIS PROCESSOS FIQUEM VISÍVEIS 
                        html = self.metodos.get_element(driver, 'html')
                        for i in range(4):
                            html.send_keys(Keys.DOWN)
                        if ordem_li > 30:
                            proximo = '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/p-datalist/div/p-paginator/div/a[3]'
                            if self.metodos.check_exists_by_xpath(driver, proximo):
                                ele_proximo = self.metodos.get_element(driver, proximo)
                                ele_proximo.click()
                                ordem_li = 1
                                time.sleep(2)
                                for i in range(15):
                                    html.send_keys(Keys.PAGE_UP)
                        

                    print('Total de Processos neste momento da execuação:', total_processos)
                    logging.info('Total de Processos neste momento da execuação: '+ total_processos)

                logging.info('Total de Processos no término da execução: '+ total_processos)

                print("Terminou")   
            except Exception as e:
                logging.info(repr(e))
                print("Erro: ", repr(e))
                traceback.print_exc()
                print(total_processos, repete)
                if int(total_processos)>0:
                    repete = True
                    if int(acaoEmErro) == 1:
                        driver.close()
                        # options = OptionsChrome()
                        service = Service()
                        options = webdriver.ChromeOptions()
                        options.add_argument("--start-maximized")
                        driver = webdriver.Chrome(service=service, options=options)
                        # driver = webdriver.Chrome(chrome_options=options)
  