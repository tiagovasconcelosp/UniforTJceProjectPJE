# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Levy Rocha Wnaderley Cavalcante 
# ## Email: levy.cavalcante@tjce.jus.br 
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options as OptionsChrome

from .Auth import Auth
from .Metodos import Metodos

import json
import os
import re
import pyautogui
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

class TaskMandadoCitacao_PJE_019:
    
    def __init__(self, driver, logging, url, dataform, acaoEmErro, xml,  log_bi):
        #self.modelo = self.get_modelo_by_element(xml,"mandadoCitacao")
        self.modelo = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='mandadoCitacao')
        self.log_bi = log_bi
        self.Execute(driver, logging, url, dataform, acaoEmErro,xml)

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
    

    def encaminharPAC(self,driver,logging,metodos):
        # Clicar em encaminhar para
        self.mensagem(logging, 'Encaminhando processo para Pac')
        driver.switch_to.default_content()
        frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(frame1)
        metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
        time.sleep(2)
        # Clicar Preparar comunicações - Rotina Preparar Comunicação - PAC
        #'//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[19]'
        #'//*[@title="Encaminhar para Preparar comunicações - Rotina Preparar Comunicação - PAC"]'
        while not metodos.check_exists_by_xpath(driver, '//*[@title="Encaminhar para Preparar comunicações - Rotina Preparar Comunicação - PAC"]'):
            time.sleep(1)
            print('aguardando opções de encaminhamento aparecerem')
        metodos.get_element(driver, '//*[@title="Encaminhar para Preparar comunicações - Rotina Preparar Comunicação - PAC"]').click()


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


    def prepDestinatario(self,driver,logging,metodos):
        self.mensagem(logging, 'Preparando Destinatários')
        driver.switch_to.default_content()
        frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(frame1)
        frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
        driver.switch_to.frame(frame1)
        # # clicar mostrar todos
        # metodos.get_element(driver,'/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[1]/a[2]').click()
       
        ######################################################################
        ########################SUBSTITUIÇÃO DE CÓDIGO########################
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
        #####################FIM DA SUBSTITUIÇÃO DE CÓDIGO####################
        ######################################################################
        time.sleep(1)

        while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[3]/a'):
            time.sleep(0.5)

        # # Clicar em executados    
        # metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/div[1]/div[1]/div/div/div[2]/div[3]/div[1]/div[2]/table/tbody/tr/td[3]/a').click()

        ######################################################################
        ########################SUBSTITUIÇÃO DE CÓDIGO########################
        opcao_a_selecionar = "Citação"
        while metodos.buscar_tabela_por_texto(driver, opcao_a_selecionar) is None:
            self.pegar_tabela_polo_passivo(driver, metodos, logging)

        #####################FIM DA SUBSTITUIÇÃO DE CÓDIGO####################
        ######################################################################
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
        
        # IDENTIFICA OS SELECTS
        selects = metodos.get_elements_by_tag(driver, "select")
        # Selecionar Comunicação
        metodos.selecionar_option_select(selects, "Citação")
        time.sleep(2)
        # Selecionar Meio
        metodos.selecionar_option_select(selects, "Central de Mandados")
        time.sleep(3)
        # Selecionar contagem do prazo
        selects = metodos.get_elements_by_tag(driver, "select")
        metodos.selecionar_option_select(selects, "Da juntada da certidão da diligência")
        time.sleep(2)
        
        # Clicar no botão Proximo
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                segue_elemento = False
            except:
                segue_elemento = True
        time.sleep(3)

    def prepEndereco(self,driver,logging,metodos):
        self.mensagem(logging, 'Preparando Endereços')
        #SELEÇÃO DE DESTINOS
        # Clica para Editar o endereço
        time.sleep(1)
        if metodos.buscar_tabela_por_texto(driver, "Nome") is None:
            metodos.elemento_por_titulo_em_lista_by_tag(driver, "a", "Editar endereços", True).click()
        time.sleep(1)
       
        
        # Verifica o endereço mais recente
        escolhido = -1
        escolhido_check = -1
        # input_check = None
        tabela = metodos.buscar_tabela_por_texto(driver, "Nome")
        if tabela is None:
            addendereco = metodos.elemento_por_texto_em_lista_by_classe(driver, 'rich-panel-body', 'Não foram encontrados endereços')
            if addendereco is not None:
                return 'Adicionar Endereço'            
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

        # Clicar no botão proximo
        # Segue para o PRÓXIMO
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                segue_elemento = False
            except:
                segue_elemento = True
        time.sleep(1)
        return 'Realizado'

    def prepMandado(self,driver,logging,metodos):
        self.mensagem(logging, 'Preparando Ato')
        #ABA ATO DE COMUNICAÇÃO
        # Clicar no lápis
        metodos.get_element(driver,'/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div/div[2]/div/table/tbody/tr/td[1]/a[1]').click()
        time.sleep(1)
        # Clicar documento novo
        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div[1]/table/tbody/tr/td[2]/input').click()
        time.sleep(3)
        #Selecionar NÚCLEO 4.0 MANDADO DE CITAÇÃO
        selects = metodos.get_elements_by_tag(driver, "select")
        # metodos.selecionar_option_select(selects, "NÚCLEO 4.0 MANDADO DE CITAÇÃO")
        metodos.selecionar_option_select(selects, self.modelo['modelo'])
        time.sleep(3)
        
        #Modifica documento
        self.modificar_documento(driver, logging, metodos)

        checagem = True                            
        while checagem:
            paragrafo = driver.find_element(by=By.XPATH, value='//*[@id="tinymce"]')
            if paragrafo is None:
                time.sleep(1)
            else:
                checagem = False    

        time.sleep(2)
        driver.switch_to.default_content()
        frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(frame1)
        frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
        driver.switch_to.frame(frame1)
        time.sleep(2)

        # Clicar em confirmar
        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div/div[2]/div/div/div[2]/div[3]/input').click()
        time.sleep(3)
        # Clicar em proximo
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                segue_elemento = False
            except:
                segue_elemento = True
        time.sleep(1)

    def modificar_documento(self, driver, logging, metodos):
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
        frames = metodos.get_elements_by_tag(driver, 'iframe')
        driver.switch_to.frame(frames[0])

    def escDocAssinatura(self,driver,logging,metodos):
        driver.switch_to.default_content()
        frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(frame1)
        frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
        driver.switch_to.frame(frame1)
        time.sleep(2)
        self.mensagem(logging, 'Escolher documentos')
        # Marcar os 5 primeiros documentos
        for i in range(1,6):
            quadrado = metodos.get_element(driver,'/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/div[1]/table/tbody/tr['+str(i)+']/td[1]/input' )
            quadrado.click()
            while not quadrado.is_selected():
                time.sleep(1)
        time.sleep(2)

        # Clicar em Vincular documentos
        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/table[1]/tbody/tr/td[2]/div/input').click()     
        doc5 = 'Há 5 documentos vinculados.'
        while  doc5 != metodos.texto_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/table[1]/tbody/tr/td[1]/div'):
            time.sleep(1)
        
        # Clicar em assinar
        self.mensagem(logging, 'Assinatura')
        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/input').click()
        while metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[2]/input'):
            time.sleep(1)

    def desce_lista_processos(self, driver, metodos, ordem_li, total_li, location_1):
        div_barra = metodos.get_element(driver, '//*[@id="acoes-processos-selecionados"]/div/div')
        print(div_barra.size)
        print(div_barra.location)
        # div_processo = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div'
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

    def Execute(self, driver, logging, url, dataform, acaoEmErro, xml):
        repete = True
        # autenticacao = Auth()
        primeira = True
        metodos = Metodos(url)
        
        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        ################ antigo ############
        # desktop = Path.home() / "Desktop"
        # path_executados = os.path.join(desktop, "executados")
        # if not os.path.isdir(path_executados):
        #         os.mkdir(path_executados)
        # data_arq = time.localtime() 
        # nome_arquivo = os.path.join(path_executados, "processos_executados_"
        #                 +str(data_arq.tm_mday) +"-"+str(data_arq.tm_mon)+"-"+str(data_arq.tm_year)
        #                 +"_" +str(data_arq.tm_hour)+"-"+str(data_arq.tm_min)+".xlsx")
        
        # lista_processos = pd.DataFrame(columns=['Processo', 'Data', 
        #                                         'Destinatário', 'Endereço', 'Conteúdo Carta',
        #                                         'Assinatura', 'Constar na nova tarefa'])
        # lista_processos.to_excel(nome_arquivo)
        ###################### fim antigo########################################

        self.log_bi.criar_arquivo_executados(['Destinatário', 'Endereço', 'Conteúdo Carta',
                                              'Assinatura', 'Constar na nova tarefa'])

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


                etiqueta = [i.text for i in xml.iter('etiquetaMandado')][0]
                    
                outra_tentativa  = True
                while outra_tentativa:
                    try:
                        etiqueta_mandado = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', etiqueta)
                        etiqueta_mandado.click()
                        outra_tentativa = False
                    except:
                        outra_tentativa = True

                total_processos = str(etiqueta_mandado.text).replace(etiqueta +'\n', '').strip()
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

                texto_anterior = ''
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
                        time.sleep(3)
                        texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                        # while texto_anterior == texto_carregado:
                        #     time.sleep(0.5)
                        #     texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                        # texto_anterior = texto_carregado
                        if texto_clicado in texto_carregado:
                            # identifica processos de 01-12-22 em diante
                            data_inicial = datetime.strptime('01-12-22', '%d-%m-%y')
                            data_final = texto_processo.find_element(by= By.XPATH, value='../../../..')
                            data_final = data_final.find_elements(by= By.TAG_NAME, value='span')
                            data_str = data_final[5].text
                            data_dt = datetime.strptime(data_str, '%d-%m-%y')
                            
                            if data_dt >= data_inicial:
                                continua = True  

                    if continua:

                        outra_tentativa = True
                        while outra_tentativa:
                            try:
                                self.log_bi.adicionar_processo(processo=texto_clicado)
                                self.prepDestinatario(driver,logging,metodos)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Destinatário', 
                                                             atualizacao='Realizado')
                                # dados = [texto_clicado, datetime.now(), 
                                #         'Realizado', 'Não','Não', 'Não', 'Não']
                                # lista_processos = self.adicionar_linha_pandas(lista_processos, dados) 
                                # lista_processos.to_excel(nome_arquivo)
                            except Exception as e:
                                self.mensagem(logging, repr(e))
                                time.sleep(1)
                                outra_tentativa = True
                                if str(e) == 'Excedeu o tempo':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Destinatário",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial devido a Tempo")
                                if str(e) == 'Pular processo':
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Destinatário",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial por precisar pular processo")    
                        time.sleep(2)

                        outra_tentativa = True
                        while outra_tentativa:
                            try:
                                resultado = self.prepEndereco(driver,logging,metodos)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                            etapa='Endereço', 
                                                                            atualizacao='Realizado')
                                # lista_processos = self.atualizar_status_processo(lista_processos, 
                                #                                         texto_clicado, 
                                #                                         'Endereço',
                                #                                         resultado)
                                # lista_processos.to_excel(nome_arquivo)
                            except Exception as e:
                                self.mensagem(logging, repr(e))
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
                        time.sleep(3)

                        if resultado == 'Realizado':

                            outra_tentativa = True    
                            while outra_tentativa:
                                try:
                                    self.prepMandado(driver,logging,metodos)
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                            etapa='Conteúdo Carta', 
                                                                            atualizacao='Realizado')
                                    # lista_processos = self.atualizar_status_processo(lista_processos, 
                                    #                                         texto_clicado, 
                                    #                                         'Conteúdo Carta',
                                    #                                         'Realizado')
                                    # lista_processos.to_excel(nome_arquivo)
                                except Exception as e:
                                    #self.mensagem(logging, repr(e))
                                    #time.sleep(1)
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
                                        raise Exception("Retornando ao ponto inicial devido a Tempo")    
                            time.sleep(2)
                            self.remover_etiqueta(driver, logging, metodos, ordem_li)
                            outra_tentativa = True    
                            while outra_tentativa:
                                try:
                                    self.escDocAssinatura(driver,logging,metodos)
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                    etapa='Assinatura', 
                                                                    atualizacao='Realizado')
                                    # lista_processos = self.atualizar_status_processo(lista_processos, 
                                    #                                         texto_clicado, 
                                    #                                         'Assinatura',
                                    #                                         'Realizado')
                                    # lista_processos.to_excel(nome_arquivo)
                                except Exception as e:
                                    self.mensagem(logging, repr(e))
                                    time.sleep(1)
                                    outra_tentativa = True
                                    if str(e) == 'Excedeu o tempo':
                                        outra_tentativa = False
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Assinatura",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial devido a Tempo")
                                    if str(e) == 'Pular processo':
                                        self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                                passo_executado="Assinatura",
                                                                mensagem=repr(e))
                                        raise Exception("Retornando ao ponto inicial por precisar pular processo")    
                            time.sleep(2)                            
                            # Verificar se o processo consta na fase da tarefa “[EF] selecionar central de mandados”
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            fila_atual = metodos.texto_by_xpath(driver, '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[2]/conteudo-tarefa/div[1]/div/div/div[1]/div[1]/div/div[1]/a')
                            fila_correta = '[EF] Selecionar Central de Mandados'
                            if fila_correta in fila_atual:
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                                    etapa='Constar na nova tarefa', 
                                                                    atualizacao='Realizado')
                                # lista_processos = self.atualizar_status_processo(lista_processos, 
                                #                                             texto_clicado, 
                                #                                             'Constar na nova tarefa',
                                #                                             'Realizado')
                                # lista_processos.to_excel(nome_arquivo)

                            

                            outra_tentativa  = True
                            while outra_tentativa:
                                try:
                                    if int(total_processos) - (total_li-1) > 1 :         
                                        etiqueta_mandado = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', etiqueta)
                                        etiqueta_mandado.click()
                                        # driver.execute_script('arguments[0].scrollIntoView(true)', etiqueta_mandado)
                                        _, _, _, _ = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)
                                        # print(ordem_li, total_li, location_1)
                                    outra_tentativa = False
                                except:
                                    outra_tentativa = True
                            
                            try:
                                total_processos = str(etiqueta_mandado.text).replace(etiqueta + '\n', '').strip()    
                            except: 
                                total_processos = "0"
                            
                    else:
                        # ordem_li, total_li, location_1, html = self.desce_lista_processos(driver, metodos, ordem_li, total_li, location_1)
                        ordem_li, total_li, location_1, html = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)
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



                # # Reiniciando pesquisa
                # driver.switch_to.default_content()
                # frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                # driver.switch_to.frame(frame1)
                # pesquisa = metodos.get_element(driver,'//*[@id="inputPesquisaTarefas"]')
                # pesquisa.click()
                # time.sleep(1)
                # pesquisa.clear()
                # time.sleep(1)
                # pesquisa.send_keys(' ')
                # metodos.get_element(driver,'//*[@id="divActions"]/filtro-tarefas/div/div[2]/span/button[2]').click()
                # time.sleep(3)    
 
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
        # os.system("start " + nome_arquivo)
        # pyautogui.alert(text='A execução terminou. Consulte o arquivo '+nome_arquivo, title='Término de Execução', button='OK')
        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                        +self.log_bi.retorna_nome_arquivo(), 
                        title='Término de Execução', button='OK')
        
    def remover_etiqueta(self, driver, logging, metodos, ordem_li):
        self.mensagem(logging, 'Remover etiqueta')
        etiqueta_emitir_mandado = 'EMITIR MANDADO CITAÇÃO'
        driver.switch_to.default_content()
        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(iframe)
        div_processo = metodos.get_element(driver, '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div')
        excluir_etiqueta = metodos.elemento_por_titulo_em_lista_by_tag(div_processo, 'span', 'Excluir etiqueta '+etiqueta_emitir_mandado)
        excluir_etiqueta.click()
        self.mensagem(logging, 'Etiqueta removida')