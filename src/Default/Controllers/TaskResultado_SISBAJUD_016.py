# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Augusto Lima dos Santos 
# ## Email: augusto.santos@tjce.jus.br 
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

from .Auth import AuthV2
from .Metodos import Metodos

import os
import re
import glob
import pyautogui
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

class TaskResultado_SISBAJUD_016:
    
    def __init__(self, driver, logging, url, urlSISBAJUD, dataform, acaoEmErro, xml, log_bi):
        self.log_bi = log_bi
        self.modelo = self.get_modelo_by_element(xml,"resultadoSISBAJUD")
        self.Execute(driver, logging, url, urlSISBAJUD, dataform, acaoEmErro, xml)
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

    def pje_1(self, driver, metodos, aba, logging):
        # TROCA ABA
        driver.switch_to.window(aba)
        while not metodos.check_exists_by_xpath(driver, '//*[@id="navbar"]'):
            time.sleep(0.5)
            self.mensagem(logging, "Aguarda Carregar Página Autos do Processo")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        span_bloqueio = metodos.elemento_por_texto_em_lista_by_tag(driver, 'span', 'JUNTADA DE ORDEM DE BLOQUEIO')
        elemento_pai = span_bloqueio.find_element(by=By.XPATH, value='../..')
        # spans = elemento_pai.find_elements(by=By.TAG_NAME, value='span')
        # span_protocolo = spans[len(spans)-1]
        span_protocolo = metodos.elemento_por_texto_em_lista_by_tag(elemento_pai, 'span', '(Sisbajud')
        if span_protocolo is not None:
            protocolo = span_protocolo.text.split("(")[1]
            protocolo_regex = re.search(r'[A-Z|a-z| ]* ', protocolo)
            protocolo = protocolo.replace(protocolo_regex.group(), "").replace(")", "")
            # dados_coletados = {'protocolo': '20230000001542'} # ALTERAR PARA A VARIÁVEL protocolo
            dados_coletados = {'protocolo': protocolo}
            self.mensagem(logging, "Coletou dados")
        else:
            self.mensagem(logging, "Juntada da Ordem de Bloqueio fora do Padrão - Passar para Próximo")
            return None
        return dados_coletados
    

    def get_download_path(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        return os.path.join(os.path.expanduser('~'), 'downloads')

    def identifica_ultimo_pdf(self, folder_path, timestamp, logging):
        file_type = '\*pdf'
        repete = True
        while repete:
            files = glob.glob(folder_path + file_type)
            max_file = max(files, key=os.path.getctime)
            ti_c = os.path.getctime(max_file)
            if ti_c > timestamp: 
                return max_file
            else:
                self.mensagem(logging, "Aguardando o download do recibo")
                time.sleep(1)

    def renomear_arquivo(self, pdfdownload, protocolo):
        pdfdownload_2 = pdfdownload.split("\\")[-1]
        path_pdf = pdfdownload.replace(pdfdownload_2, "")
        pdf = "RESPOSTA SISBAJUD - "+protocolo+".pdf"
        path_pdf = f"{path_pdf}"+pdf
        os.rename(f"{pdfdownload}", path_pdf)
        return path_pdf


    def sisbajud_1(self, driver, metodos, logging, aba, url, dados):
        # TROCA ABA
        driver.switch_to.window(aba)
        # ACESSA CADASTRO DE MINUTA
        if metodos.elemento_por_texto_em_lista_by_tag(driver, 'span', 'Limpar') is None:
            url2 = url+'/ordem-judicial'
            driver.get(url2)
        self.mensagem(logging, "Acessou página de CADASTRO DE MINUTA")
        while metodos.elemento_por_texto_em_lista_by_tag(driver, 'span', 'Ordens Judiciais') is None:
            time.sleep(0.5)
            print("Aguarda Carregar Página Consultar Ordens Judiciais")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        self.mensagem(logging, "Carregou página de Consultar Ordens Judiciais")
        # VAI AO TOPO
        body = driver.find_element(by=By.TAG_NAME, value='sisbajud-pesquisa-ordem-judicial')
        for i in range(5):
            body.click()
        # Clica na aba Consulta pelo número de protocolo
        aba_consulta_protocolo = metodos.elemento_por_texto_em_lista_by_tag(driver, 'div', 'Consulta pelo número de protocolo')
        aba_consulta_protocolo.click()
        self.mensagem(logging, "Clica na aba Consulta pelo número de protocolo")
        # INFORMA O PROTOCOLO
        input_protocolo = metodos.elemento_por_placeholder_em_lista_by_tag(driver, 'input', 'Protocolo')
        if input_protocolo is not None:
            input_protocolo.clear()
            input_protocolo.click()
            input_protocolo.send_keys(dados['protocolo'])
        time.sleep(0.3)
        self.mensagem(logging, "INFORMOU O PROTOCOLO")
        # CLICA NO SALVAR
        button_consultar = metodos.elemento_por_texto_em_lista_by_tag(driver, 'span', 'Consultar')                
        button_consultar.click()
        self.mensagem(logging, "CLICOU NO SALVAR")
        return True


    def sisbajud_2(self, driver, metodos, logging, processo):
        # AGUARDA PÁGINA DE DADOS DA ORDEM JUDICIAL DE BLOQUEIO DE VALORES
        while metodos.elemento_por_texto_em_lista_by_tag(driver, 'mat-card-title', 'Dados da Ordem Judicial de Bloqueio de Valores') is None:
            time.sleep(0.5)
            print("Aguarda Carregar Página de Gerar Recibo")
            metodos.identificacao_erros(driver)
            metodos.controlar_tempo_espera(max=300)
        time.sleep(2)
        self.mensagem(logging, "Carregou Página de DADOS DA ORDEM JUDICIAL DE BLOQUEIO DE VALORES")
        # REMOVER PDF ANTERIOR
        folder_path = self.get_download_path()
        pdf_anterior = os.path.join(folder_path, "RESPOSTA SISBAJUD - "+processo+".pdf")
        if os.path.isfile(pdf_anterior):
            os.remove(pdf_anterior)
        self.mensagem(logging, "Removeu PDF anterior")
        # EXPORTAR PDF
        timestamp = time.time()
        button_exportar_pdf = metodos.elemento_por_titulo_em_lista_by_tag(driver, 'button', 'Exportar PDF') 
        button_exportar_pdf.click()
        time.sleep(2)
        self.mensagem(logging, "Exportou PDF")
        # ALTERA NOME DO PDF
        pdfdownload = self.identifica_ultimo_pdf(folder_path, timestamp, logging)
        path_pdf = self.renomear_arquivo(pdfdownload, processo)
        self.mensagem(logging, "Renomeou PDF")
        return path_pdf


    def pje_2(self, driver, metodos, pdf, ultima_juntada, logging):
        nome_pdf = pdf.split("\\")[-1]
        doc = nome_pdf.replace(" - ", " ").replace(".pdf", "")
        # ÚLTIMA JUNTADA
        if metodos.check_exists_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[3]/div[2]'):
            ultima_juntada = metodos.texto_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[3]/div[2]')
        elif metodos.check_exists_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[4]/div[2]'):
            ultima_juntada = metodos.texto_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[4]/div[2]')
        if doc not in ultima_juntada:
            # AGUARDA Página de Juntar Documentos
            while metodos.elemento_por_texto_em_lista_by_tag(driver, 'h5', 'Juntar documentos') is None:
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda Carregar Página de Juntar Documentos")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=300)
            # SELECIONA TIPO DE DOCUMENTO
            if metodos.get_element(driver, '//*[@id="ipDescDecoration:ipDesc"]').get_attribute("value") \
                != 'Resposta da ordem de Bloqueio':
                label_tipo_documento = metodos.elemento_por_texto_em_lista_by_tag(driver, 'label', 'Tipo de documento')
                label_tipo_documento.click()
                select_tipo_documento = metodos.get_element(driver, '//*[@id="'+label_tipo_documento.get_attribute("for")+'"]')
                select_tipo_documento.send_keys("Resposta da ordem de Bloqueio")
            # AGUARDA CARREGAMENTO DA ORDEM DE BLOQUEIO
            while metodos.get_element(driver, '//*[@id="ipDescDecoration:ipDesc"]').get_attribute("value") \
                != 'Resposta da ordem de Bloqueio':
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda CARREGAMENTO DA RESPOSTA DA ORDEM DE BLOQUEIO")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=300)
            # SELECIONA MODELO
            time.sleep(1)
            input_radio = metodos.elemento_por_type_em_lista_by_tag(driver, 'input', 'radio')
            if not input_radio.get_attribute('checked'):
                label_modelo = metodos.elemento_por_texto_em_lista_by_tag(driver, 'label', 'Modelo', repete=True)
                label_modelo.click()
                select_modelo = metodos.get_element(driver, '//*[@id="'+label_modelo.get_attribute("for")+'"]')
                # select_modelo.send_keys("NÚCLEO 4.0 - RESPOSTA DA ORDEM DE BLOQUEIO")
                select_modelo.send_keys(self.modelo)
                self.mensagem(logging, "Selecionou Modelo")
                time.sleep(1)
                # CLICA EM Editor de Texto
                label_editor = metodos.elemento_por_texto_em_lista_by_tag(driver, 'label', 'Editor de texto')
                label_editor.click()
            # Aguarda carregamento de documento
            while not metodos.check_exists_by_xpath(driver, '//*[@id="docPrincipalEditorTextArea_ifr"]'):
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda Carregar Documento")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=300)
            # VERIFICA SE PRECISA ADICIONAR O ARQUIVO       
            # if not metodos.check_exists_by_xpath(driver, '//*[@id="marcarDesmarcarTodosCB"]'):
            #if metodos.elemento_por_atributo_em_lista_by_tag(driver, 'span', 'data-dz-name', nome_pdf) is None:
            if len(metodos.get_elements_by_classe(driver, "dz-file-preview"))<1:
                if not self.salvo:
                    # CLICA EM SALVAR
                    input_salvar = metodos.buscar_componente_por_value(driver, 'Salvar')
                    input_salvar.click()
                    self.salvo = True
                # Espera se o elemento Adicionar esta clicável
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="commandLinkAdicionar"]')))
                # ADICIONAR ANEXO
                time.sleep(1)
                input_file = metodos.elemento_por_type_em_lista_by_tag(driver, 'input', 'file', repete=True)
                input_file.send_keys(pdf)
            # Aguarda Carregamento de Arquivo
            #while not metodos.check_exists_by_xpath(driver, '//*[@id="marcarDesmarcarTodosCB"]'):
            while metodos.elemento_por_atributo_em_lista_by_tag(driver, 'span', 'data-dz-name', nome_pdf) is None:
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda Carregamento de Arquivo")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=100)
            while len(metodos.get_elements_by_classe(driver, "dz-file-preview"))>1:
                uploads = metodos.get_elements_by_classe(driver, "dz-file-preview")
                button_excluir = metodos.elemento_por_titulo_em_lista_by_tag(uploads[1], "a", "Excluir anexo")
                button_excluir.click()
                time.sleep(1) 
                driver.switch_to.alert.accept() 
                self.mensagem(logging, "Excluiu segundo upload")
            # SELECIONA ORDEM DE BLOQUEIO NO ANEXO
            painel_anexo = metodos.get_element(driver, '//*[@id="dz-tabela-upload"]')
            painel_anexo_select = painel_anexo.find_elements(by=By.TAG_NAME, value='select')
            painel_anexo_select = painel_anexo_select[0]
            if metodos.buscar_componente_por_value(driver, 'Assinar documento(s)') is None:
                painel_anexo_select.send_keys("Resposta da ordem de Bloqueio")
            op = ""
            while "Resposta da ordem de Bloqueio" not in op:
                options = painel_anexo_select.find_elements(by=By.TAG_NAME, value="option")
                for option in options:
                    if option.get_attribute('selected'):
                        op = option.text
                        break
            # AGUARDA BOTÃO DE ASSINATURA
            while metodos.buscar_componente_por_value(driver, 'Assinar documento(s)') is None:
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda Botão de Assinatura")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=300)
            time.sleep(1)
            input_assinar = metodos.buscar_componente_por_value(driver, 'Assinar documento(s)')
            input_assinar.click()
            self.mensagem(logging, "Clicou para Assinar")
            # Aguarda Carregamento de Página Ordem de Bloqueio
            while metodos.elemento_por_texto_em_lista_by_tag(driver, 'span', 'JUNTADA DE RESPOSTA DA ORDEM DE BLOQUEIO') is None:
                time.sleep(0.5)
                self.mensagem(logging, "Aguarda Carregamento de Página Resposta da Ordem de Bloqueio")
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=300)


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


    def Execute(self, driver, logging, url, urlSISBAJUD, dataform, acaoEmErro, xml):
        repete = True
        autenticacao = AuthV2()
        primeira = True
        metodos = Metodos(url)

        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(['Coleta Informações PJe', 'Consultar Protocolo', 
                                              'Download Resultado', 'Juntar Documentação e Assinar'])

        # PÁGINAS PERCORRIDAS
        paginas_percorridas = 0
        self.processos_percorridos = 0

        # CONTROLE DE ABAS
        abas ={}

        # while repete:
        repete = False
        total_processos = 1            
        try:
            logging.info('##############################')
            logging.info('Robô iniciado')
            logging.info('Acesso URL 1')
            driver.get(url)
            logging.info('Acesso da Url: '+ url)
            abas['PJe'] = driver.window_handles[0]
            
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

            # ABRE NOVA ABA
            logging.info('Acesso URL 2')
            driver.execute_script("window.open('');")
            abas['SISBAJUD'] = driver.window_handles[1]
            driver.switch_to.window(abas['SISBAJUD'])
            driver.get(urlSISBAJUD)
            logging.info('Acesso da Url: '+ urlSISBAJUD)
            # REALIZA LOGIN NO SISBAJUD
            # autenticacao.Login(driver, logging, dataform, urlSISBAJUD)
            # if primeira:
            #     mensagem = 'Realize o login com o CERTIFICADO DIGITAL e em seguida clique em OK para prosseguir.'
            #     self.mensagem(logging, "Aguardando Login com CERTIFICADO DIGITAL SISBAJUD")
            #     pyautogui.alert(mensagem)
            #     primeira = False
            time.sleep(1.5)
            # APENAS NO CASO DE HOMOLOGAÇÃO REALIZA O PASSO SEGUINTE
            if "sisbajudh.cnj" in urlSISBAJUD:
                autenticacao.Login(driver, logging, dataform, urlSISBAJUD)
                # AGUARDA CARREGAMENTO DE ESCOLHA DO PERFIL
                perfil = None
                while perfil is None:
                    time.sleep(0.5)
                    print("Aguarda CARREGAMENTO DE ESCOLHA DO PERFIL")
                    # perfil = metodos.elemento_por_texto_em_lista_by_tag(driver, 'td', '1ª UNIDADE DO JUIZADO ESPECIAL CIVEL E CRIMINAL DA COMARCA DE JUAZEIRO DO NORTE')
                    perfil = metodos.elemento_por_texto_em_lista_by_tag(driver, 'tr', '1ª UNIDADE DO JUIZADO ESPECIAL CIVEL E CRIMINAL DA COMARCA DE JUAZEIRO DO NORTE Assessor')
                    # perfil = metodos.elemento_por_texto_em_lista_by_tag(driver, 'tr', '1ª UNIDADE DO JUIZADO ESPECIAL CIVEL E CRIMINAL DA COMARCA DE JUAZEIRO DO NORTE Juiz')
                perfil.click()
            # RETORNA PARA ABA DO PJe
            driver.switch_to.window(abas['PJe']) 


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
            time.sleep(1)
            # fila = '[EF] Recebidos da consulta aos convênios'
            fila = [i.text for i in xml.iter('filaRespostaSISBAJUD')][0]
            processos_ativos = metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
            if processos_ativos is None:
                mensagem = 'Não foi encontrada a fila: '+fila
                self.mensagem(logging, mensagem)
                pyautogui.alert(mensagem)
                return 
            total_inicial = str(processos_ativos.text).replace(fila+'\n', '')
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
            etiqueta = [i.text for i in xml.iter('etiquetaRespostaSISBAJUD')][0]
            outra_tentativa  = True
            while outra_tentativa:
                try:
                    etiqueta_carta = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', etiqueta)
                    etiqueta_carta.click()
                    outra_tentativa = False
                except:
                    outra_tentativa = True

            total_processos = str(etiqueta_carta.text).replace(etiqueta+'\n', '').strip()
            self.mensagem(logging, 'Total de Processos no início da execução: '+ total_processos)
            ordem_li = 0
            total_li = 0
            location_1 = 0

            ordem_li, total_li, location_1, html = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)

            while int(total_processos) - (total_li-1) > 0 :
                self.mensagem(logging, 'Seleciona novo processo')
                # Clica no primeiro processo da lista
                time.sleep(1)
                processo = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
                # processo = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, processo)))
                texto_processo = metodos.get_element(driver, processo)  
                continua =  False
                # Clica no processo
                texto_processo.click()
                # Identifica o texto do processo clicado
                texto_clicado = texto_processo.text
                if "ExFis" in texto_clicado:
                    # Identifica o processo carregado
                    texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    if texto_clicado in texto_carregado:
                        continua = True
                        
                if continua:
                    # PREENCHE PLANILHA
                    self.log_bi.adicionar_processo(processo=texto_clicado)
                    # CLICA EM AUTOS
                    time.sleep(0.5)
                    outra_tentativa  = True
                    while outra_tentativa:
                        try:
                            if metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', etiqueta) is not None:
                                # div_opcoes_encaminhar = metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]')
                                # autos = metodos.elemento_por_atributo_em_lista_by_tag(div_opcoes_encaminhar, 
                                #                                                         'button', 'tooltip', 'Autos')
                                xpath_autos = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[1]/div[2]/pje-link-autos-digitais/button'
                                autos = metodos.get_element(driver, xpath_autos)
                                autos.click()
                            outra_tentativa = False
                        except Exception as e:
                                time.sleep(1)
                                print("Erro: ", repr(e))
                                outra_tentativa = True
                    time.sleep(1)
                    # TROCA ABA
                    abas['PJe - Autos'] = driver.window_handles[2]
                    # PÁGINA 1 DO PJE
                    outra_tentativa  = True
                    while outra_tentativa:
                        try:
                            dados = self.pje_1(driver, metodos, abas['PJe - Autos'], logging)
                            self.log_bi.atualizar_etapa_processo(processo=texto_clicado,
                                                                 etapa='Coleta Informações PJe',
                                                                 atualizacao='Realizado')
                            outra_tentativa = False
                            if dados:
                                dados['processo'] = texto_clicado.split(" ")[1].replace("-", "").replace(".", "")
                        except Exception as e:
                            time.sleep(1)
                            print("Erro: ", repr(e))
                            outra_tentativa = True
                    
                    if dados:
                        status = True
                        pdf = None
                        # PÁGINA 1 DO SISBAJUD    
                        outra_tentativa  = True
                        while outra_tentativa:
                            try:
                                status = self.sisbajud_1(driver, metodos, logging, abas['SISBAJUD'], 
                                                    urlSISBAJUD, dados)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado,
                                                                     etapa='Consultar Protocolo',
                                                                     atualizacao='Realizado')
                            except Exception as e:
                                time.sleep(1)
                                print("Erro: ", repr(e))
                                outra_tentativa = True
                        
                        if status:
                            # PÁGINA 2 DO SISBAJUD    
                            outra_tentativa  = True
                            while outra_tentativa:
                                try:
                                    pdf = self.sisbajud_2(driver, metodos, logging, dados['processo'])
                                    outra_tentativa = False
                                    self.log_bi.atualizar_etapa_processo(processo=texto_clicado,
                                                                         etapa='Download Resultado',
                                                                         atualizacao='Realizado')
                                except Exception as e:
                                    time.sleep(1)
                                    print("Erro: ", repr(e))
                                    outra_tentativa = True
                        
                        # TROCA ABA
                        print("Página 2 PJE")
                        driver.switch_to.window(abas['PJe - Autos'])
                        while not metodos.check_exists_by_xpath(driver, '//*[@id="navbar"]'):
                            time.sleep(0.5)
                            print("Aguarda Carregar Página Autos do Processo")
                            metodos.identificacao_erros(driver)
                            metodos.controlar_tempo_espera(max=300)
                        # ÚLTIMA JUNTADA
                        if metodos.check_exists_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[3]/div[2]'):
                            ultima_juntada = metodos.texto_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[3]/div[2]')
                        elif metodos.check_exists_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[4]/div[2]'):
                            ultima_juntada = metodos.texto_by_xpath(driver, '//*[@id="divTimeLine:eventosTimeLineElement"]/div[4]/div[2]')
                        else:
                            ultima_juntada = ""
                        # CLICA EM JUNTAR DOCUMENTOS
                        button_juntar_documentos = metodos.elemento_por_titulo_em_lista_by_tag(driver, 'a', 'Juntar documentos')
                        button_juntar_documentos.click()
                        # PÁGINA 2 DO PJE
                        self.salvo = False
                        outra_tentativa  = True
                        while outra_tentativa:
                            try:
                                self.pje_2(driver, metodos, pdf, ultima_juntada, logging)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado,
                                                                     etapa='Juntar Documentação e Assinar',
                                                                     atualizacao='Realizado')
                            except Exception as e:
                                time.sleep(1)
                                print("Erro: ", repr(e))
                                outra_tentativa = True
                        # Fecha Aba de Autos
                        driver.switch_to.window(abas['PJe - Autos'])
                        driver.close()
                        # APAGA PDF
                        if os.path.isfile(pdf):
                            os.remove(pdf)
                        # Muda para a aba do PJe
                        driver.switch_to.window(abas['PJe']) 
                        # RETIRA ETIQUETA
                        driver.switch_to.default_content()
                        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
                        driver.switch_to.frame(iframe)
                        div_processo = metodos.get_element(driver, '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div')
                        # div_etiqueta_juiz = metodos.elemento_por_texto_em_lista_by_tag(div_processo, 'div', etiqueta)
                        excluir_etiqueta = metodos.elemento_por_titulo_em_lista_by_tag(div_processo, 'span', 'Excluir etiqueta '+etiqueta)
                        excluir_etiqueta.click()
                    else:
                        # Fecha Aba de Autos
                        driver.switch_to.window(abas['PJe - Autos'])
                        driver.close()
                        # Muda para a aba do PJe
                        driver.switch_to.window(abas['PJe'])
                    # Avança para o próximo processo
                    ordem_li, total_li, location_1, html = self.sobe_processos_etiqueta(driver, metodos, ordem_li, total_li, location_1)
                        


                self.mensagem(logging, 'Total de Processos neste momento da execuação: '+ total_processos)

            self.mensagem(logging, 'Total de Processos no término da execução: '+ total_processos)

            print("Terminou")  
        except Exception as e:
            logging.info(repr(e))
            print("Erro: ", repr(e))
            print(total_processos, repete)
            self.log_bi.enviar_erro(num_processo=texto_clicado,
                                    passo_executado="Geral",
                                    mensagem=repr(e))
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
        
        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                        +self.log_bi.retorna_nome_arquivo(), 
                        title='Término de Execução', button='OK')