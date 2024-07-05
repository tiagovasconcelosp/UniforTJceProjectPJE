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

class TaskCitacaoIntimacaoDespachoDecisao_PJE_023:
    
    def __init__(self, driver, logging, url, dataform, acaoEmErro, xml, log_bi):
        #self.modelo = self.get_modelo_by_element(xml,"mandadoCitacao")
        #self.modelo = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='mandadoCitacao')
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

        # Clicar nos Advogados

        #participantes_el = metodos.elemento_por_texto_em_lista_by_tag(driver, 'div', 'Participantes do Processo')
        #participantes_el_pai = participantes_el.find_element(by=By.XPATH,value='..').find_element(by=By.XPATH,value='..')

        #advogados = metodos.elementos_por_texto_em_lista_by_tag(participantes_el_pai, "span", "ADVOGADO", True)
        advogados = driver.find_elements(by=By.XPATH, value='//span[@title="ADVOGADO"]')


        for adv in advogados:
            nome_adv = adv.text.replace('ADVOGADO - ','')
            adv.click()
            time.sleep(2)
            tabela = metodos.buscar_tabela_por_texto(driver, "Destinatário", repete=True)
            tbody = metodos.get_elements_by_tag(tabela, 'tbody', repete=True)
            nome_na_tabela = metodos.elemento_por_texto_em_lista_by_tag(tbody[0], 'tr', nome_adv)
            while nome_adv not in nome_na_tabela.text:
                nome_na_tabela = metodos.elemento_por_texto_em_lista_by_tag(tbody[0], 'tr', nome_adv)
                time.spleep(0.5)    

        tabela = metodos.buscar_tabela_por_texto(driver, "Destinatário", repete=True)
        tbody = metodos.get_elements_by_tag(tabela, 'tbody', repete=True)
        linhas = tbody[0].find_elements(by=By.TAG_NAME,value='tr')

        for linha in linhas:
            #selects = linha.find_elements(by=By.TAG_NAME,value='select')
            selects = metodos.get_elements_by_tag(linha, "select")
            # Selecionar Comunicação
            metodos.selecionar_option_select(selects, "Intimação", identico=True)
            time.sleep(2)
            # Selecionar Meio
            metodos.selecionar_option_select(selects, "Diário Eletrônico")
            time.sleep(3)
            # Mudar prazo para 15 dias
            #dias = linha.find_element(by=By.XPATH,value='//input[contains(@name, "quantidadePrazoAto")]')
            #dias = metodos.get_element(linha, '//input[contains(@name, "quantidadePrazoAto")]')
            dias = metodos.elemento_por_type_em_lista_by_tag(linha, 'input', 'text')
            dias.clear()
            dias.send_keys('15')
            time.sleep(3)      
        
        # Clicar no botão Proximo
        segue_elemento = True
        while segue_elemento:
            try:
                metodos.buscar_componente_por_value(driver, "Próximo").click()
                segue_elemento = False
            except:
                segue_elemento = True
        time.sleep(3)

    def prepAto(self,driver,logging,metodos):
        self.mensagem(logging, 'Preparando Ato de Comunicação')
        tabela = metodos.buscar_tabela_por_texto(driver, "Destinatário", repete=True)
        tbody = metodos.get_elements_by_tag(tabela, 'tbody', repete=True)
        linhas = tbody[0].find_elements(by=By.TAG_NAME,value='tr')
        primeiro_advogado =  metodos.get_element(driver, '/html/body/div[5]/div/div[4]/form/div/div/span[2]/div/div/div/div/div/div/div/div[2]/div/table/tbody/tr[1]/td[3]')
        primeiro_advogado_texto = primeiro_advogado.text
        for li in linhas[1:]:
            selects = metodos.get_elements_by_tag(li, "select")
            # Selecionar Agrupar
            metodos.selecionar_option_select(selects, primeiro_advogado_texto)
            time.sleep(3)
        
        lapis= metodos.get_element(driver, '//i[@class="fa fa-pencil"]')
        lapis.click()
        time.sleep(2)

        #Clicar no Documento do processo
        while not metodos.check_exists_by_xpath(driver, '//label[contains(text(),"Documento do processo")]'):
            time.sleep(0.5)
        metodos.get_element(driver, '//label[contains(text(),"Documento do processo")]').click()

        # Procurar por Despacho ou decisão

        try:
            totalpaginas = metodos.get_elements_by_classe(driver, 'rich-datascr-inact')
            totalpaginas = int(totalpaginas[-1].text)
        except:
            totalpaginas = 1
                        
        driver.switch_to.default_content()
        frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
        driver.switch_to.frame(frame1)
        frame1 = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
        driver.switch_to.frame(frame1)

        npagina_incrementada = 1
        decisao = "Decisão"
        despacho = 'Despacho'
        while npagina_incrementada <= totalpaginas:

            tabela2 = metodos.buscar_tabela_por_texto(driver, "Juntado por", repete=True)
            tbody2 = metodos.get_elements_by_tag(tabela2, 'tbody', repete=True)
            linhas2 = tbody2[1].find_elements(by=By.TAG_NAME,value='tr')
            
            for linha in linhas2:
                colunas = linha.find_elements(by=By.TAG_NAME,value='td')
                colunas_elemento = colunas[2].text
                if decisao in colunas_elemento or despacho in colunas_elemento:
                    #botao_check = coluna_tipo.find_element(by=By.XPATH,value='//a[@title="Usar como ato de comunicação"]')
                    #linha_el = metodos.get_element(driver, linha)
                    botao_check = metodos.elemento_por_titulo_em_lista_by_tag(linha, 'a', 'Usar como ato de comunicação')
                    botao_check.click()
                    botao_check_clicado = True
                    break
            time.sleep(2)
            if botao_check_clicado:
                break
            avancar = metodos.elemento_por_texto_em_lista_by_classe(driver, 'rich-datascr-button','»')
            avancar.click()
            npagina_incrementada += 1    

            
            time.sleep(2)  



        # Clicar no botão confirmar
        segue = True
        while segue:
            try:
                metodos.get_element(driver, '//input[@value="Confirmar"]').click()
                segue = False
            except:
                segue = True
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
      


    def escDocAssinatura(self,driver,logging,metodos):               
        # Clicar em assinar
        self.mensagem(logging, 'Assinatura')
        metodos.get_element(driver, '//input[@value="Assinar digitalmente"]').click()
        while metodos.check_exists_by_xpath(driver, '//input[@value="Assinar digitalmente"]'):
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

       
        ############## antigo ###################
        # # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        # desktop = Path.home() / "Desktop"
        # path_executados = os.path.join(desktop, "executados")
        # if not os.path.isdir(path_executados):
        #         os.mkdir(path_executados)
        # data_arq = time.localtime() 
        # nome_arquivo = os.path.join(path_executados, "processos_executados_"
        #                 +str(data_arq.tm_mday) +"-"+str(data_arq.tm_mon)+"-"+str(data_arq.tm_year)
        #                 +"_" +str(data_arq.tm_hour)+"-"+str(data_arq.tm_min)+".xlsx")
        
        # lista_processos = pd.DataFrame(columns=['Processo', 'Data', 
        #                                         'Destinatário', 'Ato de Comunicação',
        #                                         'Assinatura'])
        # lista_processos.to_excel(nome_arquivo)
        ################# fim antigo ######################


        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(['Destinatário', 'Ato de Comunicação', 'Assinatura'])



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
                    fila = '[Sec] - Expediente - PREPARAR CITAÇÃO E(OU) INTIMAÇÃO'
                    processos_ativos = metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                        '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
                    if processos_ativos is not None:
                        break
                if processos_ativos is None:
                    mensagem = 'Não foi encontrada a fila: '+fila
                    self.mensagem(logging, mensagem)
                    pyautogui.alert(mensagem)
                    return 
                total_inicial = str(processos_ativos.text).replace('[Sec] - Expediente - PREPARAR CITAÇÃO E(OU) INTIMAÇÃO\n', '')
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


                etiqueta = [i.text for i in xml.iter('etiquetaCitacaoIntimacao')][0]    
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

                #texto_anterior = ''
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
                                #         'Realizado', 'Não','Não']
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
                                
                                if str(e) == 'Retornando ao ponto inicial devido a erros':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Destinatário",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial por precisar pular processo")    
                        time.sleep(2)

                        outra_tentativa = True
                        while outra_tentativa:
                            try:
                                self.prepAto(driver,logging,metodos)
                                outra_tentativa = False
                                self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Ato de Comunicação', 
                                                             atualizacao='Realizado')
                                # lista_processos = self.atualizar_status_processo(lista_processos, 
                                #                                         texto_clicado, 
                                #                                         'Ato de Comunicação',
                                #                                         'Realizado')
                                # lista_processos.to_excel(nome_arquivo)
                            except Exception as e:
                                self.mensagem(logging, repr(e))
                                time.sleep(1)
                                outra_tentativa = True
                                if str(e) == 'Excedeu o tempo':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Ato de Comunicação",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial devido a Tempo")
                                if str(e) == 'Retornando ao ponto inicial devido a erros':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Ato de Comunicação",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial por precisar pular processo")    
                        time.sleep(3)

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
                                if str(e) == 'Retornando ao ponto inicial devido a erros':
                                    outra_tentativa = False
                                    self.log_bi.enviar_erro(num_processo=texto_clicado,
                                                            passo_executado="Assinatura",
                                                            mensagem=repr(e))
                                    raise Exception("Retornando ao ponto inicial por precisar pular processo")    
                        time.sleep(2)

                        

                        outra_tentativa  = True
                        while outra_tentativa:
                            try:
                                if int(total_processos) - (total_li-1) > 1 :
                                    driver.switch_to.default_content()
                                    frame1 = metodos.get_element(driver, '//*[@id="ngFrame"]')
                                    driver.switch_to.frame(frame1)         
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
        
        #lista_processos.to_excel(nome_arquivo, index=False)
        #os.system("start " + nome_arquivo)
        #pyautogui.alert(text='A execução terminou. Consulte o arquivo '+nome_arquivo, title='Término de Execução', button='OK')
        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                        +self.log_bi.retorna_nome_arquivo(), 
                        title='Término de Execução', button='OK')