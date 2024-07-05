# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Augusto Lima dos Santos 
# ## Email: augusto.santos@tjce.jus.br 
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################

import time
import os
import re
import pyautogui
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options as OptionsChrome
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from .Auth import Auth
from .Metodos import Metodos
import xml.etree.ElementTree as ET

class TaskCartaCitacao_PJE_008:
    
    def __init__(self, driver, logging, url, dataform, acaoEmErro,xml, log_bi):
        self.modelo = self.get_modelo_by_element(xml,"cartaCitacao")
        self.log_bi = log_bi
        self.Execute(driver, logging, url, dataform, acaoEmErro)
    def get_modelo_by_element(self,xml, element_name):
        try:
            tree = xml
            element = tree.find(element_name)
            modelo_element = element.find("modelo")
            if modelo_element is not None:
                return modelo_element.text
            else:
                return None
            # If the specified element name is not found
            return None
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return None
    def mensagem(self, logging, mensagem):
        logging.info(mensagem)
        print(mensagem)

    def adicionar_linha_pandas(self, df, dados):         
        df.loc[0] = dados         
        df.index = df.index + 1         
        #df.append(pd.Series(dados, index=df.columns[:len(dados)]), ignore_index=True)
        return df

    def atualizar_status_processo(self, df, processo, coluna, status):         
        indice = df[df["Processo"]==processo].index.values.astype(int)         
        df.at[indice[0], coluna] = status         
        return df

    # Clicar no elemento do Polo passivo, preferencialmente CNPJ
    def pegar_tabela_polo_passivo(self, driver, metodos, logging):
        posicao, _, tabelas = metodos.buscar_tabela_por_texto(driver, "Polo passivo", completo=True)
        tabela = tabelas[posicao+1]
        linha_escolhida = False
        for linha in tabela.find_elements(by=By.TAG_NAME, value='span'):
            if "CNPJ" in linha.text:
                linha.click()
                linha_escolhida = True
        if not linha_escolhida:
            tabela.find_elements(by=By.TAG_NAME, value='span')[0].click()
        # Aguarda Destinatários
        self.mensagem(logging, 'Especifica dados da carta')
        metodos.controlar_tempo_espera(True)
        time.sleep(1)
        tabela = metodos.buscar_tabela_por_texto(driver, "Destinatário", repete=True)
        tbody = metodos.get_elements_by_tag(tabela, 'tbody', repete=True)
        #tbody = tabela.find_element(by=By.TAG_NAME, value='tbody')
        while not metodos.check_exists_element_inside(tbody[0], "tr"):
            time.sleep(0.5)
            print("Aguarda Destinatários")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
            tbody = tabela.find_element(by=By.TAG_NAME, value='tbody')
        time.sleep(2)

    def pagina_1(self, driver, logging, metodos):
        self.mensagem(logging, 'Processo apto para procedimento')
        # Encaminha para Participantes do Processo
        metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
        metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[19]/a').click()

    def pagina_2(self, driver, logging, metodos):
        iframe = metodos.get_element(driver, '//*[@id="frame-tarefa"]', max=15)
        # Entra no frame da página
        driver.switch_to.frame(iframe)
        # Aguarda Etapa de Participantes do Processo
        self.mensagem(logging, 'Aguarda Etapa de Participantes do Processo')
        metodos.controlar_tempo_espera(True)
        while not metodos.check_exists_by_xpath(driver, '//*[@id="wizard"]'):
            time.sleep(0.5)
            print("Aguarda Etapa de Participantes do Processo")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
            if metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[3]/div'):
                if 'Há partes no polo passivo que não podem ser intimados via sistema' \
                    in metodos.texto_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[3]/div') \
                    or 'Todos do polo passivo estão aptos a serem intimados via sistema' \
                    in metodos.texto_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[3]/div'):
                    raise Exception("Sem ação")
        time.sleep(1)

        # Exibe os Polos
        clicar_mostrar_todos =  True
        for element in metodos.get_elements_by_tag(driver, "img"):
            if "/pje1grau/a4j/g/3_3_3.Finalimages/spacer.gif" in element.get_attribute("src"):
                clicar_mostrar_todos =  False
        self.mensagem(logging, 'Seleciona Polo Passivo')
        while clicar_mostrar_todos:
            metodos.elemento_por_texto_em_lista_by_tag(driver, "a", "MOSTRAR TODOS", True).click()
            time.sleep(0.2)
            for element in metodos.get_elements_by_tag(driver, "img"):
                if "/pje1grau/a4j/g/3_3_3.Finalimages/spacer.gif" in element.get_attribute("src"):
                    clicar_mostrar_todos =  False
                    break
        time.sleep(1)
        #####################################
        opcao_a_selecionar = "Citação"
        while metodos.buscar_tabela_por_texto(driver, opcao_a_selecionar) is None:
            self.pegar_tabela_polo_passivo( driver, metodos, logging)
        # IDENTIFICA OS SELECTS
        selects = metodos.get_elements_by_tag(driver, "select")
        # Selecionar Comunicação
        metodos.selecionar_option_select(selects, opcao_a_selecionar)
        time.sleep(0.5)
        # Selecionar Meio
        metodos.selecionar_option_select(selects, "Correios")
        time.sleep(1.5)
        # Selecionar Tipo de Prazo
        outra_tentativa  = True
        while outra_tentativa:
            try:
                metodos.selecionar_option_select(selects, "dias")
                time.sleep(0.5)
                outra_tentativa = False
            except:
                outra_tentativa = True
                selects = metodos.get_elements_by_tag(driver, "select")
        
        # Clica em PRÓXIMO
        outra_tentativa  = True
        while outra_tentativa:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                outra_tentativa = False
            except:
                outra_tentativa = True
        

    def pagina_3(self, driver, logging, metodos):
        # Aguarda carregamento da página de Edição de Endereços
        self.mensagem(logging, 'Seleciona Endereço mais recente')
        metodos.controlar_tempo_espera(True)
        while "active" not in metodos.get_element(driver, '//*[@id="wizard"]/li[2]').get_attribute("class"):
            time.sleep(0.5)
            print("Aguarda Edição de Endereços")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        
        # Clica para Editar o endereço
        time.sleep(1)
        if metodos.buscar_tabela_por_texto(driver, "Nome") is None:
            metodos.elemento_por_titulo_em_lista_by_tag(driver, "a", "Editar endereços", True).click()
        # Aguarda Endereços
        metodos.controlar_tempo_espera(True)
        while metodos.buscar_tabela_por_texto(driver, "Nome") is None:
            time.sleep(0.5)
            print("Aguarda Endereços")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
            texto = "Não foram encontrados endereços relacionados à parte ou seus representantes."
            sem_endereco = metodos.elemento_por_texto_em_lista_by_tag(driver, "div", texto)
            if sem_endereco:
                self.processos_percorridos += 1
                raise Exception("Pular processo")
        # Verifica o endereço mais recente
        escolhido = -1
        escolhido_check = -1
        # input_check = None
        tabela = metodos.buscar_tabela_por_texto(driver, "Nome", repete=True)
        tbody = tabela.find_element(by=By.TAG_NAME, value='tbody')
        date_time = datetime.strptime('10/10/1900 00:00', '%d/%m/%Y %H:%M')
        linha_tabela = tbody.find_elements(by=By.TAG_NAME, value='tr')
        for index, linha in enumerate(linha_tabela):
            colunas = linha.find_elements(by=By.TAG_NAME, value='td')
            if metodos.check_by_tag(colunas[0], 'input'):
                escolhido_check = index
            data = colunas[3].text
            if len(data) > 0:
                date_time_new = datetime.strptime(data, '%d/%m/%Y %H:%M')
                print(date_time)
                if date_time_new > date_time:
                    date_time = date_time_new
                    escolhido = index
        if escolhido == -1 and escolhido_check == -1:
            colunas = linha_tabela[0].find_elements(by=By.TAG_NAME, value='td')
            colunas[0].find_element(by=By.TAG_NAME, value='input').click()
        elif escolhido == -1 and escolhido_check != -1:
            print("Já selecionado")
        elif escolhido == escolhido_check and escolhido_check != -1:
            print("Já selecionado")
        else:
            colunas = linha_tabela[escolhido].find_elements(by=By.TAG_NAME, value='td')
            if not metodos.check_by_tag(colunas[0], 'input'):
                colunas[0].find_element(by=By.TAG_NAME, value='input').click()
            if escolhido_check != -1:
                tabela = metodos.buscar_tabela_por_texto(driver, "Nome", repete=True)
                tbody = tabela.find_element(by=By.TAG_NAME, value='tbody')
                linha_tabela = tbody.find_elements(by=By.TAG_NAME, value='tr')
                colunas = linha_tabela[escolhido_check].find_elements(by=By.TAG_NAME, value='td')    
                if metodos.check_by_tag(colunas[0], 'input'):
                    colunas[0].find_element(by=By.TAG_NAME, value='input').click()
                time.sleep(1)

        # Segue para o PRÓXIMO
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                segue_elemento = False
            except:
                segue_elemento = True


    def pagina_4(self, driver, logging, metodos):
        self.mensagem(logging, "Faz o caminho até o frame correto")
        driver.switch_to.default_content()
        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(iframe)
        iframe = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
        driver.switch_to.frame(iframe)
        
        # Aguarda Ato de comunicação
        self.mensagem(logging, 'Escolha do Modelo e Edição do Conteúdo')
        metodos.controlar_tempo_espera(True)
        #while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div/div[2]/div/table/tbody/tr/td[1]/a[1]/i'):
        while not metodos.check_exists_by_xpath(driver, '//*[@id="wizard"]/li[3]'):
            time.sleep(0.5)
            print("Aguarda Ato de Comunicação")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        while "active" not in driver.find_element(by=By.XPATH, value='//*[@id="wizard"]/li[3]').get_attribute("class"):
            time.sleep(0.5)
            print("Aguarda Ato de Comunicação")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        # Clica em EDITAR
        time.sleep(0.5)
        segue_elemento = True
        while segue_elemento:
            try:
                if metodos.elemento_por_texto_em_lista_by_tag(driver, "div", "Edição do ato de comunicação") is None:
                    metodos.elemento_por_titulo_em_lista_by_tag(driver, "a", "Editar", True).click()
                segue_elemento = False
            except:
                segue_elemento = True
        metodos.controlar_tempo_espera(True)
        while metodos.elemento_por_texto_em_lista_by_tag(driver, "div", "Edição do ato de comunicação") is None:
            time.sleep(0.5)
            print("Aguarda Edição do ato de comunicação")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        # Clica em Documento Novo
        if metodos.elemento_por_texto_em_lista_by_tag(driver, "label", "Modelo") is None:
            metodos.elemento_por_texto_em_lista_by_tag(driver, "label", "Documento novo", True).click()
        time.sleep(1)
        metodos.controlar_tempo_espera(True)
        while metodos.elemento_por_texto_em_lista_by_tag(driver, "label", "Modelo") is None:
            time.sleep(0.5)
            print("Aguarda Seleção Modelo")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        # Seleciona o Modelo
        selects = metodos.get_elements_by_tag(driver, "select")
        # metodos.selecionar_option_select(selects, "ECARTAS_CARTA DE CITAÇÃO_NUCLEO 40")
        metodos.selecionar_option_select(selects, self.modelo)
        time.sleep(2)
        # Modifica documento
        frames = metodos.get_elements_by_tag(driver, 'iframe')
        driver.switch_to.frame(frames[0])
        metodos.controlar_tempo_espera(True)
        while not metodos.check_exists_by_xpath(driver, '//*[@id="tinymce"]'):
            time.sleep(0.5)
            self.mensagem(logging, "Aguarda Frame Carregar")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        tabela = metodos.buscar_tabela_por_texto(driver, "Chave de acesso")
        # tabela = driver.find_element(by=By.XPATH, value='//*[@id="tinymce"]/p[9]/table')
        tabela_html = tabela.get_attribute('innerHTML')
        tabela_html_bs = BeautifulSoup(tabela_html, 'html.parser')
        tabela_html_nova = ""
        for index, tr in enumerate(tabela_html_bs.find('tbody').find_all('tr', class_=False)):
            if index < 6:
                tabela_html_nova += str(tr)
        tabela = metodos.buscar_tabela_por_texto(driver, "Chave de acesso")
        tbody = tabela.find_element(by=By.TAG_NAME, value='tbody')
        # tbody = metodos.get_element(driver, '//*[@id="tinymce"]/p[9]/table/tbody')
        driver.execute_script("arguments[0].innerHTML = arguments[1];", tbody, tabela_html_nova)
        driver.switch_to.parent_frame()
        # Clica em Confirmar
        time.sleep(1)
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Confirmar", repete=True).click()
                segue_elemento = False
            except:
                segue_elemento = True
        # Clica em PRÓXIMO
        time.sleep(1)
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo", repete=True).click()
                segue_elemento = False
            except:
                segue_elemento = True

    def pagina_5(self, driver, logging, metodos):
        # Aguarda ASSINAR DIGITALMENTE
        self.mensagem(logging, 'Assinatura da Carta')
        metodos.controlar_tempo_espera(True)
        while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/input'):
            time.sleep(0.5)
            print("Aguarda ASSINAR DIGITALMENTE")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        # Clica em ASSINAR DIGITALMENTE
        metodos.buscar_componente_por_value(driver, "Assinar digitalmente").click()
        
    def pagina_6(self, driver, logging, metodos):
        # ENTRA NO FRAME CERTO
        self.mensagem(logging, "Faz o caminho até o frame correto")
        driver.switch_to.default_content()
        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(iframe)
        self.mensagem(logging, 'Encaminhar para os Correios')
        # driver.switch_to.parent_frame()
        metodos.controlar_tempo_espera(True)
        while "[Sec] - Expedientes - ECarta - DETALHAR ENVIO" not in metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a'):
            time.sleep(0.5)
            print("Aguarda [Sec] - Expedientes - DETALHAR ENVIO")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        time.sleep(2)
        # Encaminha para Participantes do Processo
        metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
        div_opcoes_encaminhar = metodos.get_element(driver, '//*[@id="frameTarefas"]')
        while metodos.elemento_por_texto_em_lista_by_tag(div_opcoes_encaminhar, 'a', 'Enviar ECarta COM AR') is None:
            time.sleep(0.5)
            print("Buscando Enviar ECarta COM AR")
            metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
            div_opcoes_encaminhar = metodos.get_element(driver, '//*[@id="frameTarefas"]')
        metodos.elemento_por_texto_em_lista_by_tag(div_opcoes_encaminhar, 'a', 'Enviar ECarta COM AR').click()
        # metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a').click()
        metodos.controlar_tempo_espera(True)
        while "[Sec] - Expedientes - ECarta - AGUARDAR RESPOSTA DOS CORREIOS" not in metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a'):
            time.sleep(0.5)
            print("Aguarda [Sec] - Expedientes - AGUARDAR RESPOSTA DOS CORREIOS")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=200)
            # if "Analisar erro" not in metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a'):
            #     raise Exception("Erro na página")

    def desce_lista_processos(self, driver, metodos, ordem_li, total_li, location_1):
        div_barra = metodos.get_element(driver, '//*[@id="acoes-processos-selecionados"]/div/div')
        print("Size:", div_barra.size, "Location:", div_barra.location)
        div_processo = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div'          
        div_processo = metodos.get_element(driver, div_processo)
        print(div_processo.size)
        print(div_processo.location)
        if ordem_li == 1:
            location_1 = div_processo.location['y']
        ordem_li+=1
        total_li+=1
        # DESCE PARA QUE OS DEMAIS PROCESSOS FIQUEM VISÍVEIS 
        html = metodos.get_element(driver, 'html')
        passo = 36
        deslocamento = int(div_processo.size['height']/passo)
        print(deslocamento)
        location_anterior = div_processo.location['y']
        for i in range(deslocamento):
            html.send_keys(Keys.DOWN)
        if location_anterior > (location_1 + passo):
            html.send_keys(Keys.DOWN)
        elif location_anterior < (location_1 - passo):
            html.send_keys(Keys.UP)
        return ordem_li, total_li, location_1, html
    
    def sobe_processos_etiqueta(self, driver, metodos, ordem_li, total_li, location_1):
        driver.switch_to.default_content()
        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(iframe)
        ordem_li+=1
        total_li+=1
        div_barra = metodos.get_element(driver, '//*[@id="processosEtiqueta"]')
        print("Size:", div_barra.size, "Location:", div_barra.location)
        div_processo = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div'          
        div_processo = metodos.get_element(driver, div_processo)
        print("Size:", div_processo.size, "Location:", div_processo.location)
        passo = 36
        if ordem_li == 1:
            location_1 = div_processo.location['y']
            deslocamento = int((div_processo.location['y']-div_barra.location['y'])/passo)-3
            if deslocamento < 0:
                deslocamento = 0
        else:
            deslocamento = int(div_processo.size['height']/passo)
        print(deslocamento)
        location_anterior = div_processo.location['y']
        html = metodos.get_element(driver, 'html')
        for i in range(deslocamento):
            html.send_keys(Keys.DOWN)
        if location_anterior > (location_1 + passo):
            html.send_keys(Keys.DOWN)
        elif location_anterior < (location_1 - passo):
            html.send_keys(Keys.UP)
        return ordem_li, total_li, location_1, html

    def mudar_iframe(self, driver, metodos, logging, iframe_xpath: str):
        try:
            iframe = metodos.get_element(driver, iframe_xpath)
            driver.switch_to.frame(iframe)
        except Exception as e:
            self.mensagem(logging, "Erro: "+repr(e))

    def Execute(self, driver, logging, url, dataform, acaoEmErro):

        repete = True
        # autenticacao = Auth()
        primeira = True
        metodos = Metodos(url)
        
        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(['Encaminhar PAC', 'Destinatário', 
                                              'Endereço', 'Conteúdo Carta',
                                              'Assinatura', 'Enviar com AR e Aguardando Correios'])

        # PÁGINAS PERCORRIDAS
        paginas_percorridas = 0
        self.processos_percorridos = 0

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

                # autenticacao.Login(driver, logging, dataform, url)
                if primeira:
                    mensagem = 'Realize o login com o CERTIFICADO DIGITAL e em seguida clique em OK para prosseguir.'
                    self.mensagem(logging, "Aguardando Login com CERTIFICADO DIGITAL")
                    pyautogui.alert(mensagem)
                    primeira = False

                perfil = metodos.get_element(driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
                time.sleep(2)
                if perfil.get_attribute('data-original-title') != dataform['perfil']:
                    self.mensagem(logging, 'Realizando a mudança do Perfil')
                    perfil.click()
                    select = metodos.get_element(driver, '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]')
                    options = select.find_elements(by=By.TAG_NAME, value='option')
                    select.click()
                    for option in options:
                        if option.text == dataform['perfil']:
                            option.click()
                            time.sleep(2)
                            perfil = metodos.get_element(driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
                            metodos.controlar_tempo_espera(True)
                            while perfil.get_attribute('data-original-title') != dataform['perfil']:
                                time.sleep(0.5)
                                metodos.controlar_tempo_espera(max=300)
                            break
                self.mensagem(logging, 'Identificação do Perfil')

                url2 = url.replace('login.seam', 'ng2/dev.seam#/painel-usuario-interno')
                driver.get(url2)
                self.mensagem(logging, 'Acesso da Url: '+ url2)

                iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
                driver.switch_to.frame(iframe)
                self.mensagem(logging, 'Alteração para Frame interno')
                
                self.mensagem(logging, 'Aguardando lista de Tarefas carregar')
                metodos.controlar_tempo_espera(True)
                while not metodos.check_exists_by_xpath(driver, '//*[@id="divTarefasPendentes"]/div[3]/div[1]/div/a/div/span[1]'):
                    time.sleep(0.5)
                    print("Aguarda lista de Tarefas")
                    metodos.identificacao_erros(driver)
                    metodos.controlar_tempo_espera(max=300)
                
                self.mensagem(logging, 'Acessando Lista da Tarefa')
                processos_ativos = None
                for repete in range(2):
                    time.sleep(1.5)
                    fila = '[EF] Preparar comunicações - PAC'
                    processos_ativos = metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                        '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
                    if processos_ativos is not None:
                        break
                if processos_ativos is None:
                    mensagem = 'Não foi encontrada a fila: '+fila
                    self.mensagem(logging, mensagem)
                    pyautogui.alert(mensagem)
                    return 
                total_inicial = str(processos_ativos.text).replace('[EF] Preparar comunicações - PAC\n', '')
                processos_ativos.click()
                
                self.mensagem(logging, 'Aguardando Página de Processos Ativos')
                metodos.controlar_tempo_espera(True)
                while total_inicial != metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'):
                    time.sleep(0.5)
                    print("Aguarda Carregar Página de Processos Ativos")
                    metodos.identificacao_erros(driver)
                    metodos.controlar_tempo_espera(max=300)

                outra_tentativa  = True
                while outra_tentativa:
                    try:
                        etiquetas = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', 'ETIQUETAS')
                        etiquetas.click()
                        outra_tentativa = False
                    except:
                        outra_tentativa = True

                outra_tentativa  = True
                while outra_tentativa:
                    try:
                        etiqueta_carta = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', '1. Ag. Emissão de Cartas de Citação')
                        # etiqueta_carta = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', '1.0 - CITAÇÃO')
                        etiqueta_carta.click()
                        outra_tentativa = False
                    except:
                        outra_tentativa = True

                total_processos = str(etiqueta_carta.text).replace('1. Ag. Emissão de Cartas de Citação\n', '').strip()
                # total_processos = str(etiqueta_carta.text).replace('1.0 - CITAÇÃO\n', '').strip()
                self.mensagem(logging, 'Total de Processos no início da execução: '+ total_processos)
                ordem_li = 1
                total_li = 1
                location_1 = 0

                if self.processos_percorridos > 0:
                    for processos_ in range(self.processos_percorridos):
                        ordem_li, total_li, location_1, html = self.desce_lista_processos(driver, metodos, ordem_li, total_li, location_1)
                        # ordem_li, total_li, location_1, html = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)
                else:
                    ordem_li = 0
                    total_li = 0
                    location_1 = 0
                    ordem_li, total_li, location_1, html = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)


                texto_anterior = ""

                while int(total_processos) - (total_li-1) > 0 :
                    self.mensagem(logging, 'Seleciona novo processo')
                    # Clica no primeiro processo da lista
                    time.sleep(1)
                    processo = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
                    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, processo)))
                    texto_processo = metodos.get_element(driver, processo, max=300)  
                    continua =  False
                    # Clica no processo
                    texto_processo.click()
                    # Identifica o texto do processo clicado
                    texto_clicado = texto_processo.text
                    texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    while texto_carregado == texto_anterior: 
                        time.sleep(0.1)
                        self.mensagem(logging, "Aguardando recarregar o texto")
                        texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    texto_anterior = texto_carregado
                    if "ExFis" in texto_clicado:
                        # Identifica o processo carregado
                        # wait = WebDriverWait(driver,10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')))    
                        if texto_clicado in texto_carregado:
                            continua = True
                        
                    if continua:
                        sem_acao = False
                        # PÁGINA 1
                        self.log_bi.adicionar_processo(processo=texto_clicado)
                        # self.pagina_1(driver, logging, metodos)
                        self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Encaminhar PAC', 
                                                             atualizacao='Realizado')
                        # PÁGINA 2 
                        outra_tentativa  = True
                        while outra_tentativa:
                            try:
                                self.pagina_2(driver, logging, metodos)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                        etapa='Destinatário', 
                                                                        atualizacao='Realizado')
                            except Exception as e:
                                driver.switch_to.parent_frame()
                                outra_tentativa = True
                                print(repr(e))
                                if str(e) == 'Sem ação':
                                    outra_tentativa = False
                                    sem_acao = True
                                if str(e) == 'Excedeu o tempo':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Destinatário",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial devido a Tempo")
                                
                                if str(e) == 'Retornando ao ponto inicial devido a erros':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Destinatário",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial devido a erros")
                        if not sem_acao:
                            # PÁGINA 3
                            outra_tentativa  = True
                            while outra_tentativa:
                                try:
                                    self.pagina_3(driver, logging, metodos)
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                            etapa='Endereço', 
                                                                            atualizacao='Realizado')
                                except Exception as e:
                                    time.sleep(1)
                                    outra_tentativa = True
                                    if str(e) == 'Excedeu o tempo':
                                        outra_tentativa = False
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Endereço",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial devido a Tempo")
                                    if str(e) == 'Pular processo':
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Endereço",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial por precisar pular processo")
                            # PÁGINA 4
                            outra_tentativa  = True
                            while outra_tentativa:
                                try:
                                    self.pagina_4(driver, logging, metodos)
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                            etapa='Conteúdo Carta', 
                                                                            atualizacao='Realizado')
                                except Exception as e:
                                    frames = metodos.get_elements_by_tag(driver, 'iframe') 
                                    if len(frames) == 0:
                                        driver.switch_to.parent_frame()
                                        frames = metodos.get_elements_by_tag(driver, 'iframe')
                                        print(len(frames))
                                    outra_tentativa = True
                                    if str(e) == "Retornando ao ponto inicial devido a erros" \
                                        or str(e) == "Excedeu o tempo":
                                        outra_tentativa = False
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Conteúdo Carta",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial devido a erros ou Tempo")
                            # PÁGINA 5
                            self.pagina_5(driver, logging, metodos)
                            self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                    etapa='Assinatura', 
                                                                    atualizacao='Realizado')
                            # PÁGINA 6
                            outra_tentativa  = True
                            while outra_tentativa:
                                try:
                                    self.pagina_6(driver, logging, metodos)
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                            etapa='Enviar com AR e Aguardando Correios', 
                                                                            atualizacao='Realizado')
                                except Exception as e:
                                    outra_tentativa = True
                                    if str(e) == "Retornando ao ponto inicial devido a erros" \
                                        or str(e) == "Excedeu o tempo" or str(e) == "Erro na página":
                                        outra_tentativa = False
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Enviar com AR e Aguardando Correios",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial devido a erros ou Tempo")
                            
                            #RETIRAR ETIQUETA
                            self.remover_etiqueta(driver, logging, metodos, ordem_li)
                        outra_tentativa  = True
                        while outra_tentativa:
                            try:
                                if int(total_processos) - (total_li-1) > 1 :      
                                    etiqueta_carta = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', '1. Ag. Emissão de Cartas de Citação')
                                    # etiqueta_carta = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', '1.0 - CITAÇÃO')
                                    etiqueta_carta.click()
                                outra_tentativa = False
                            except:
                                outra_tentativa = True
                        try:
                            total_processos = str(etiqueta_carta.text).replace('1. Ag. Emissão de Cartas de Citação\n', '').strip()
                            # total_processos = str(etiqueta_carta.text).replace('1.0 - CITAÇÃO\n', '').strip()
                            # total_processos = metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span')
                        except:
                            total_processos = "0"
            
                    else:
                        ordem_li, total_li, location_1, html = self.desce_lista_processos(driver, metodos, ordem_li, total_li, location_1)
                        self.processos_percorridos += 1
                        if ordem_li > 300:
                            proximo = '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/p-datalist/div/p-paginator/div/a[3]'
                            if metodos.check_exists_by_xpath(driver, proximo):
                                ele_proximo = metodos.get_element(driver, proximo)
                                ele_proximo.click()
                                ordem_li = 1
                                time.sleep(2)
                                for i in range(150):
                                    html.send_keys(Keys.PAGE_UP)
                                paginas_percorridas += 1
                                self.processos_percorridos = 0
                        
                    self.mensagem(logging, 'Total de Processos neste momento da execuação: '+ total_processos)

                self.mensagem(logging, 'Total de Processos no término da execução: '+ total_processos)

                print("Terminou")  
            except Exception as e:
                logging.info(repr(e))
                print("Erro: ", repr(e))
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
        
        # lista_processos.to_excel(nome_arquivo, index=False)
        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                        +self.log_bi.retorna_nome_arquivo(), 
                        title='Término de Execução', button='OK')

    def remover_etiqueta(self, driver, logging, metodos, ordem_li):
        self.mensagem(logging, 'Remover etiqueta')
        etiqueta = '1. Ag. Emissão de Cartas de Citação'
        driver.switch_to.default_content()
        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(iframe)
        div_processo = metodos.get_element(driver, '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div')
        excluir_etiqueta = metodos.elemento_por_titulo_em_lista_by_tag(div_processo, 'span', 'Excluir etiqueta '+etiqueta)
        excluir_etiqueta.click()
        self.mensagem(logging, 'Etiqueta removida')