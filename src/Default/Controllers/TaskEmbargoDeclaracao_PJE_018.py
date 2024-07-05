# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Levy Rocha Wanderley Cavalcante 
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
from selenium.webdriver.chrome.options import Options as OptionsChrome

from .Auth import Auth
from .Metodos import Metodos

import os
import re
import pyautogui
import pandas as pd
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime



class TaskEmbargoDeclaracao_PJE_018:

    def __init__(self, driver, logging, url, dataform, xml, log_bi):
        self.log_bi = log_bi
        self.Execute(driver, logging, url,dataform,xml)
        

    def mensagem(self, logging, mensagem):
        logging.info(mensagem)
        print(mensagem)    

    def atualizar_status_processo(self, df, processo, coluna, status):         
        indice = df[df["Processo"]==processo].index.values.astype(int)         
        df.at[indice[0], coluna] = status         
        return df
    
    def adicionar_linha_pandas(self, df, dados):         
        df.loc[0] = dados         
        df.index = df.index + 1         
        #df.append(pd.Series(dados, index=df.columns[:len(dados)]), ignore_index=True)
        return df
    
    def maximo_paginas(self, qtprocessos):
        quociente = qtprocessos//10
        resto = qtprocessos % 10
        if resto > 0:
            return quociente + 1
        else:
            return quociente

    def substituir_ativo(self, texto):
        soup = BeautifulSoup(texto, 'html.parser')
        
        for tag in soup.find_all(text=True):
            if 'EXEQUENTE:' in tag:
                novo_texto = re.sub(r'EXEQUENTE:.*(?=EXECUTADO)', '', tag)
                tag.replace_with(novo_texto)
            elif 'AUTOR:' in tag:
                novo_texto = re.sub(r'AUTOR:.*(?=REU)', '', tag)
                tag.replace_with(novo_texto)
            elif 'REQUERENTE:' in tag:
                novo_texto = re.sub(r'REQUERENTE:.*(?=REQUERIDO)', '', tag)
                tag.replace_with(novo_texto)        
        
        texto_modificado = str(soup)
        return texto_modificado

    def substituir_passivo(self, texto):
        soup = BeautifulSoup(texto, 'html.parser')
        
        for tag in soup.find_all(text=True):
            if 'EXECUTADO:' in tag:
                novo_texto = re.sub(r'EXECUTADO:.*(?=para)', '', tag)
                tag.replace_with(novo_texto)
            elif 'REU:' in tag:
                novo_texto = re.sub(r'REU:.*(?=para)', '', tag)
                tag.replace_with(novo_texto)
            elif 'REQUERIDO:' in tag:
                novo_texto = re.sub(r'REQUERIDO:.*(?=para)', '', tag)
                tag.replace_with(novo_texto)        
        
        texto_modificado = str(soup)
        return texto_modificado

    def Execute(self, driver, logging, url, dataform, xml):
        repete = True
        autenticacao = Auth()
        primeira = True
        metodos = Metodos(url)
        
        #GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS

        self.log_bi.criar_arquivo_executados(['Juntado por', 'Encaminhar Expedir Ato', 
                                              'Texto Editado', 'Dados Gravados', 'Encaminhar Assinatura', 'Assinatura',
                                                'Excluir Doc Nao Lidos'])


        # PÁGINAS PERCORRIDAS
        # paginas_percorridas = 0
        # self.processos_percorridos = 0

        # Controle de ABAS
        abas = {}


        while repete:
            repete = False
            #total_processos = 1            
            try:
                logging.info('##############################')
                logging.info('Robô iniciado')
                #driver.get(url)
                #logging.info('Acesso da Url: '+ url)
                abas['DocNLidos'] = driver.window_handles[0]
                if len(driver.window_handles)>1:
                    for i in driver.window_handles[1:]:
                        driver.switch_to.window(i)
                        driver.close()
                driver.switch_to.window(abas['DocNLidos'])
                driver.get(url)
                logging.info('Acesso da Url: '+ url)
                time.sleep(2)
                print("started")

                #autenticacao.Login(driver, logging, dataform, url)
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
                time.sleep(2)


                # Clicar no icone de agrupadores
                frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                driver.switch_to.frame(frame1)
                metodos.get_element(driver,'//*[@id="liAgrupadores"]').click()
                time.sleep(3)

                # Entrar no frame agrupadores
                driver.switch_to.default_content()
                frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                driver.switch_to.frame(frame1)
                frame1 = metodos.get_element(driver, '//*[@id="frameAgrupadores"]')
                driver.switch_to.frame(frame1)
                metodos.get_element(driver, '/html/body/div[2]/div[2]/div[1]/div/form/div').click() # id com número, checar se fullXpath melhor alternativa
                time.sleep(2)

                   
                npagina = metodos.get_elements_by_classe(driver, 'rich-datascr-act')
                npagina = npagina[0].text
                totalpaginas = metodos.get_elements_by_classe(driver, 'rich-datascr-inact')
                totalpaginas = int(totalpaginas[-1].text)                
                npagina_incrementada = 1
                repete = True
                #embargo = 'Petição'
                embargo = [i.text for i in xml.iter('tarefaEmbargo')][0]
                ativo = 'POLO ATIVO'
                passivo = 'POLO PASSIVO'
                while npagina_incrementada <= totalpaginas:
                    
                    primeiroprocesso = metodos.texto_by_xpath(driver,'//*[@id="processoDocumentoNaoLidoForm:processoDocumentoNaoLidoDataTable:tb"]/tr[1]/td[3]')
                    qtprocessos = metodos.get_element(driver, '/html/body/div[2]/div[2]/div[1]/div/form/div').text
                    qtprocessos = int(re.sub('[^0-9]','',qtprocessos))
                    totalpaginas = self.maximo_paginas(qtprocessos)
                    linha = '//*[@id="processoDocumentoNaoLidoForm:processoDocumentoNaoLidoDataTable:tb"]/tr[1]'
                    linha_incrementada = 1
                    # Looping nas linhas da parte de documentos não lidos
                    while metodos.check_exists_by_xpath(driver, linha):
                        coluna_nprocesso = linha+'/td[3]'
                        col_nprocesso_el = metodos.texto_by_xpath(driver, coluna_nprocesso)
                        coluna_polo = linha+'/td[5]'
                        col_polo_el = metodos.texto_by_xpath(driver, coluna_polo)
                        documento = linha+'/td[4]'
                        doc_el = metodos.texto_by_xpath(driver, documento)
                        if embargo in doc_el:
                            # Abrir nova aba
                            logging.info('Acesso URL 2')
                            driver.execute_script("window.open('');")
                            abas['Procedimento'] = driver.window_handles[1]
                            driver.switch_to.window(abas['Procedimento'])
                            driver.get(url2)
                            logging.info('Acesso da Url: '+ url2)

                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            time.sleep(2)
                            #Abrir filtros
                            filtro = driver.find_elements(By.XPATH, value='//*[@id="divTarefasPendentes"]/div[1]/div/span')
                            filtro[3].click()
                            time.sleep(1)

                            # Colar o numero do processo no filtro
                            nprocesso = re.sub('[^0-9]','',col_nprocesso_el)
                            espaco_digitar = driver.find_elements(By.XPATH,value='//*[@id="itNrProcesso"]')
                            espaco_digitar[3].send_keys(nprocesso)

                            tarefa = driver.find_elements(By.XPATH,value='//*[@id="divTarefasPendentes"]')
                            spans = len(tarefa[3].find_elements(By.TAG_NAME,value='span'))

                            # Clicar no botão de pesquisa                  
                            pesquisar = driver.find_elements(By.XPATH,value='//*[@id="divTarefasPendentes"]/div[2]/filtro-tarefas-pendentes/div/form/fieldset/div[4]/button[1]')
                            pesquisar[3].click()                                       

                            # Clicar na tarefa
                            i = spans
                            while spans == i:
                                time.sleep(1)
                                tarefa = driver.find_elements(By.XPATH,value='//*[@id="divTarefasPendentes"]')
                                i = len(tarefa[3].find_elements(By.TAG_NAME,value='span'))
                                print('Aguardando pesquisa')
                            metodos.get_element(tarefa[3],'div[3]/div/div/a/div/span[1]').click()
                            time.sleep(2)
                        
                            # Clicar no número do processo
                            metodos.get_element(driver, '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li/processo-datalist-card/div/div[3]/a/div/span[2]').click()
                            time.sleep(3)
                            
                            self.log_bi.adicionar_processo(processo=nprocesso)
                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Juntado por', 
                                                             atualizacao=doc_el)

                            
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                            driver.switch_to.frame(frame1)
                            # Verificar se já está na parte de seleção de providencia
                            if metodos.check_exists_by_xpath(driver, '//input[contains(@name, "expedir_ato_ordinatorio")]'):
                                # Clicar no checkbox de ato ordinatorio
                                metodos.get_element(driver, '//input[contains(@name, "expedir_ato_ordinatorio")]').click()
                                # '/html/body/div[5]/div/div[4]/form/div/div/span[17]/div/div[2]/input'
                                time.sleep(2)
                                # Clicar em encaminhar para
                                driver.switch_to.default_content()
                                frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                                driver.switch_to.frame(frame1)
                                metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
                                time.sleep(2)
                                # Clicar 01 - Prosseguir com nas opções selecionadas
                                while not metodos.check_exists_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a'):
                                    time.sleep(1)
                                    print('aguardando opções de encaminhamento aparecerem')
                                metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a').click()
                            else:
                                # Clicar em encaminhar para    
                                driver.switch_to.default_content()
                                frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                                driver.switch_to.frame(frame1)               
                                metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
                                time.sleep(2)
                                # Clicar em verificar providencias
                                while not metodos.check_exists_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a'):
                                    time.sleep(1)
                                    print('aguardando opções de encaminhamento aparecerem')
                                metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a').click()
                                frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                                driver.switch_to.frame(frame1)
                                # Clicar na checkbox de ato ordinatorio
                                while not metodos.check_exists_by_xpath(driver, '//input[contains(@name, "expedir_ato_ordinatorio")]'):
                                    time.sleep(1)
                                    print('aguardando opções de checkbox')                                    
                                metodos.get_element(driver, '//input[contains(@name, "expedir_ato_ordinatorio")]').click()
                                time.sleep(2)                        
                                # Clicar em encaminhar para
                                driver.switch_to.default_content()
                                frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                                driver.switch_to.frame(frame1) 
                                metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
                                time.sleep(2)                    
                                # Clicar 01 - Prosseguir com nas opções selecionadas
                                while not metodos.check_exists_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a'):
                                    time.sleep(1)
                                    print('aguardando opções de encaminhamento aparecerem')
                                metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[1]/a').click()

                            time.sleep(4)

                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Encaminhar Expedir Ato', 
                                                             atualizacao='Realizado')

                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                            driver.switch_to.frame(frame1)
                            time.sleep(3)
                            while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/div[1]/div[1]/div[1]'):
                                time.sleep(1)
                                print('esperando select')
                            # Selecionar ATO Embargos de Declaração Tempestivo no menu de seleção
                            selects = metodos.get_elements_by_tag(driver, "select")
                            outra_tentativa  = True
                            time.sleep(2)
                            while outra_tentativa:
                                try:
                                    metodos.selecionar_option_select(selects, "ATO Embargos de Declaração Tempestivo")
                                    time.sleep(0.5)
                                    outra_tentativa = False
                                except:
                                    outra_tentativa = True
                            #metodos.selecionar_option_select(selects, "ATO Embargos de Declaração Tempestivo")
                            time.sleep(3)

                            # Retirar polo ativo ou passivo do texto
                            frames = metodos.get_elements_by_tag(driver, 'iframe')
                            driver.switch_to.frame(frames[0])
                            paragrafo = driver.find_element(by=By.XPATH, value='//*[@id="tinymce"]')                            
                            paragrafo_correto = metodos.elemento_por_texto_em_lista_by_tag(paragrafo,'span','Certifico para os devidos fins')
                            paragrafo_correto_texto = paragrafo_correto.get_attribute('innerHTML')
                            if ativo in col_polo_el:
                                paragrafo_correto_texto = self.substituir_ativo(paragrafo_correto_texto)
                                driver.execute_script("arguments[0].innerHTML = arguments[1];", paragrafo_correto, paragrafo_correto_texto)
                            elif passivo in col_polo_el:
                                paragrafo_correto_texto = self.substituir_passivo(paragrafo_correto_texto)
                                driver.execute_script("arguments[0].innerHTML = arguments[1];", paragrafo_correto, paragrafo_correto_texto)

                            # Clicar em salvar
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                            driver.switch_to.frame(frame1)
                            metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/div[2]/div/div[2]/input[1]').click()
                            time.sleep(2)
 
                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Texto Editado', 
                                                             atualizacao='Realizado')          

                            # Trabalhar na parte de preparar ato
                            metodos.get_element(driver,'/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[1]').click()
                            while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[1]/input[2]'):
                                time.sleep(0.5)
                            time.sleep(3)
                            if ativo in col_polo_el: # se ativo clica no passivo
                                tentativa1 = True
                                while tentativa1:
                                    try:
                                        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[1]/input[2]').click()
                                        time.sleep(0.5)
                                        tentativa1 = False
                                    except:
                                        tentativa1 = True
                                        
                            elif passivo in col_polo_el: # se passivo clica no ativo
                                tentativa1 = True
                                while tentativa1:
                                    try:
                                        metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[1]/input[1]').click()
                                        time.sleep(0.5)
                                        tentativa1 = False
                                    except:
                                        tentativa1 = True
                            
                            time.sleep(2)
                            dias = metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[2]/table/thead/tr[1]/th[4]/input')
                            dias.clear()
                            dias.send_keys('5')
                            metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[2]/table/thead/tr[2]/th[2]').click() # clicar 2x
                            time.sleep(2)
                            metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[2]/table/thead/tr[2]/th[2]').click()
                            time.sleep(2)
                            metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div[3]/div[4]/input').click()
                            time.sleep(2)
                            while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div[1]/div[2]/div/div[2]/dl/dt/span'):
                                time.sleep(1)
                                print('aguardando comunicação de gravação de dados com sucesso')


                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Dados Gravados', 
                                                             atualizacao='Realizado')

                            # Encaminhar para assinatura
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]').click()
                            ### resolver problema para aparecer lista ###
                            while not metodos.check_exists_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[2]/a'):
                                time.sleep(1.5)
                                print('aguardando opções de encaminhamento')
                            metodos.get_element(driver,'//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[2]/a').click()
                            time.sleep(3)

                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Encaminhar Assinatura', 
                                                             atualizacao='Realizado')

                            #Clicar para Assinar
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                            driver.switch_to.frame(frame1)
                            time.sleep(2)
                            while not metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/input'):
                                time.sleep(1)
                                print('aguardando botão de assinatura')
                            outra_tentativa2 = True                            
                            while outra_tentativa2:
                                try:
                                    metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/input').click()
                                    time.sleep(0.5)
                                    outra_tentativa2 = False
                                except:
                                    outra_tentativa2 = True
                            
                            while metodos.check_exists_by_xpath(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/div/div/div/div/div/div[1]/div[2]/div/div[2]/div[3]/div/div[2]/div/div[2]/div/div[2]/input'):
                                time.sleep(1)

                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Assinatura', 
                                                             atualizacao='Realizado')

                            # Após assinatura, voltar para ABA DE DOCUMENTO NAO LIDOS
                            driver.close()
                            driver.switch_to.window(abas['DocNLidos'])
                            driver.switch_to.default_content()
                            frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                            driver.switch_to.frame(frame1)
                            frame1 = metodos.get_element(driver, '//*[@id="frameAgrupadores"]')
                            driver.switch_to.frame(frame1)
                            # clicar no marcador
                            marcador = linha+'/td[1]/input'
                            metodos.get_element(driver, marcador).click()
                            # clicar no retirar destaque
                            metodos.get_element(driver, '/html/body/div[2]/div[2]/div[1]/div/div/form/div/input').click()
                            #clicar em confirmar
                            while not metodos.check_exists_by_xpath(driver, '/html/body/div[3]/div[2]/div/div[2]/table/tbody/tr[2]/td/center/form/input[1]'):
                                time.sleep(1)
                                print('aguardando pedido de confirmação')
                            metodos.get_element(driver, '/html/body/div[3]/div[2]/div/div[2]/table/tbody/tr[2]/td/center/form/input[1]').click()
                            time.sleep(3)
                            linha_incrementada -=1
                            doc_el=''

                            self.log_bi.atualizar_etapa_processo(processo=nprocesso, 
                                                             etapa='Excluir Doc Nao Lidos', 
                                                             atualizacao='Realizado')
                                                                                
                            

                        linha_incrementada += 1
                        linha = '//*[@id="processoDocumentoNaoLidoForm:processoDocumentoNaoLidoDataTable:tb"]/tr['+str(linha_incrementada)+']'
                    time.sleep(2)    
                    avancar = metodos.elemento_por_texto_em_lista_by_classe(driver, 'rich-datascr-button','»')
                    avancar.click()
                    npagina_incrementada += 1
                    checagem = True
                    contador = 1
                    while checagem:
                        if contador % 30==0:
                            avancar = metodos.elemento_por_texto_em_lista_by_classe(driver, 'rich-datascr-button','»')
                            avancar.click()
                        priproximapg = metodos.texto_by_xpath(driver,'//*[@id="processoDocumentoNaoLidoForm:processoDocumentoNaoLidoDataTable:tb"]/tr[1]/td[3]')
                        if npagina_incrementada <= totalpaginas:
                            if primeiroprocesso == priproximapg:
                                time.sleep(1)
                                contador +=1
                                print('aguardando proxima pagina')
                            else:
                                checagem = False
                        else:
                            checagem = False         
                
                    
                repete = False

                os.system("start " + self.log_bi.retorna_nome_arquivo())
                pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                                +self.log_bi.retorna_nome_arquivo(), 
                                title='Término de Execução', button='OK')

            except Exception as e:
                print(repr(e))
                repete = True

