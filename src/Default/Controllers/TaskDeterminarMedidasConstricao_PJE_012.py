# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Lucas Pacheco de Araújo Jucá 
# ## Email: lucas.juca@tjce.jus.br 
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
import traceback
import pandas as pd
import os
import src.Default.Controllers.helpers as helper
from selenium.webdriver.support.wait import WebDriverWait
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options as OptionsChrome

from .Auth import Auth
from .Metodos import Metodos


import pyautogui

class TaskDeterminarMedidasConstricao_PJE_012():
    
    def __init__(self, driver:webdriver, caminhoImages, logging, atividade, dataBaseModel, 
                 inicioTime, url, dataform, acaoEmErro,xml, log_bi):
        self.config_dict = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='determinarMedidasConstrição')
        helper.driver = driver 
        helper.logging = logging
        self.log_bi = log_bi
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
    def etapa_3(self, driver:webdriver, metodos: Metodos):
        metodos.controlar_tempo_espera(True)

        botao_salvar = (By.XPATH,"//input[@value='Salvar']")
        while True:
            time.sleep(0.2)    
            try:
                metodos.identificacao_erros(driver)
                
                elemento = driver.find_element(*botao_salvar)
                elemento.click()
                print('click Salvar')
       
                #lista_processos.to_excel(nome_arquivo)
               
            except Exception as e:
                print("Erro: ", repr(e))
                traceback.print_exc()
                print("A tentar clickar em salvar")
                time.sleep(1)
                metodos.identificacao_erros(driver)
                metodos.controlar_tempo_espera(max=60)


    def inserir_codigo_movimentacao(self, driver, metodos: Metodos):
        movimento = (By.XPATH,"//*[text()='Determinado o bloqueio/penhora on line (11382)']")
        caixa_pesquisar = (By.XPATH,"//fieldset/input[@type='text']")
        while True:
            try:
                input_text = driver.find_element(*caixa_pesquisar)
                
                current_text = input_text.get_attribute("value")
                if len(driver.find_elements(*movimento)) == 1:
                    return True
                elif current_text != "11382":
                    input_text.send_keys("11382")
                input_pesquisar = (By.XPATH,"//fieldset/input[@value='Pesquisar']")
                helper.efetuar_click(input_pesquisar,'Botao pesquisar')
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, movimento)))
                    # input_pesquisar = metodos.get_element(driver,xpath=)
                    # input_pesquisar.click()
            except NoSuchElementException as e:
                botao_salvar = (By.XPATH,"//input[@value='Salvar']")
                helper.efetuar_click(botao_salvar,rotulo_elemento = 'Botao salvar')
                WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(caixa_pesquisar))
            except Exception as e:
                print("Erro: ", repr(e))
                traceback.print_exc()                          
                time.sleep(0.3)
                print("Aguardando selecao de movimentacao")
                metodos.controlar_tempo_espera(max=60)
    def etapa_5(self, driver, metodos: Metodos):
        time.sleep(0.3)
        driver.switch_to.parent_frame()
        while True:
            try:   
                # Encaminha para assinatura
                print("Encaminhando")
                cabecalho = (By.XPATH , '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                element_cabecalho = driver.find_element(*cabecalho)

                el = metodos.get_element(driver, '//*[@id="btnTransicoesTarefa"]')
                if not 'true' in el.get_attribute('aria-expanded').split():
                    el.click()
                # metodos.get_element(driver, '//*[@id="frameTarefas"]/div/div[2]/div[2]/ul/li[2]/a').click()
                
                element = metodos.get_element(driver,'//*[@id="frameTarefas"]/div/div[2]/div[2]/ul')
                # WebDriverWait.until(EC.element_to_be_clickable())
                element_a = element.find_element(by=By.XPATH, value="//a[contains(text(), 'Encaminhar para assinatura')]")
                element_a.click()
                try:
                    WebDriverWait(driver, 3).until(EC.text_to_be_present_in_element(cabecalho,'[EF] Assinar Decisão - Gabinete'))
                    return True
                except TimeoutError as e:
                    print("Testando se processo foi de fato encaminhado")
                    texto_carregado = driver.find_element(*cabecalho).text
                    botao_salvar = (By.XPATH,"//input[@value='Salvar']")
                    element_msg_nao_salva = (By.XPATH, "//span[contains(text(), 'Há informações não salvas no documento')]")
                    # WebDriverWait(driver, 10).until(lambda d : driver.find_element(*botao_salvar).is_enabled())
                    if '[EF] Minutar Decisão - Gabinete' in texto_carregado:
                        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
                        driver.switch_to.frame(iframe)
                        if driver.find_elements(*element_msg_nao_salva).size() != 0:
                            
                            helper.efetuar_click(botao_salvar,rotulo_elemento = 'Botao salvar')
                        driver.switch_to.parent_frame()
                        continue
            except Exception as e:
                print("Erro: ", repr(e))
                traceback.print_exc()
                time.sleep(0.3)
                metodos.controlar_tempo_espera(max=60)
                print("Aguardando para encaminhar")
                pass


    def Execute(self, driver, caminhoImages, logging, atividade, dataBaseModel, inicioTime, url, dataform, acaoEmErro,xml):
        repete = True
        autenticacao = Auth()
        metodos = Metodos(url)


        # ################## antigo #########################

        # desktop = [i.text for i in xml.iter('caminhoExecutados')][0]
        # if desktop is None:
        #     desktop = Path.home() / "Desktop"
        #     if not Path.exists(desktop):
        #         desktop = Path.home() / "OneDrive" / "Área de Trabalho"
        #     if not Path.exists(desktop):
        #         desktop = Path.home() / "OneDrive" / "Desktop"
        # path_executados = os.path.join(desktop, "executados")
        
        
        # if not os.path.isdir(path_executados):
        #     os.mkdir(path_executados)
        # data_arq = time.localtime() 
        # nome_arquivo = os.path.join(path_executados, "processos_executados_"
        #                 +str(data_arq.tm_mday) +"-"+str(data_arq.tm_mon)+"-"+str(data_arq.tm_year)
        #                 +"_" +str(data_arq.tm_hour)+"-"+str(data_arq.tm_min)+".xlsx")
        
        # lista_processos = pd.DataFrame(columns=['Processo', 'Data', 'Selecionar Modelo', 
        #                                         'movimentacao', 'Salvar','Encaminhar',
        #                                         'Assinatura'])
        # lista_processos.to_excel(nome_arquivo)
        ################### fim antigo ######################

         # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(['Selecionar Modelo', 'movimentacao', 'Salvar','Encaminhar', 'Assinatura'])



        primeira = True
        while repete:
            repete = False
            total_processos = 1            
            try:
                logging.info('##############################')
                logging.info('Robô iniciado')
                driver.get(url)
                logging.info('Acesso da Url: '+ url)
                time.sleep(1)
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
                                metodos.controlar_tempo_espera(max=1200)
                            break
                logging.info('Identificação do Perfil')
                #https://pje2robos.tjce.jus.br/pje1grau/ng2/dev.seam#/painel-usuario-interno
                url2 = url.replace('login.seam', 'ng2/dev.seam#/painel-usuario-interno')
                driver.get(url2)
                logging.info('Acesso da Url: '+ url2)

                iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
                driver.switch_to.frame(iframe)
                logging.info('Alteração para Frame interno')
                print("Switched frames")

                logging.info('Aguardando lista de Tarefas carregar')
                metodos.controlar_tempo_espera(True)
                while not metodos.check_exists_by_xpath(driver, '//*[@id="divTarefasPendentes"]/div[3]/div[1]/div/a/div/span[1]'):
                    time.sleep(0.5)
                    print("Aguarda lista de Tarefas")
                    metodos.identificacao_erros(driver)
                    metodos.controlar_tempo_espera(max=1200)
                
                time.sleep(1)
                fila = '[EF] Minutar Decisão - Gabinete'
                processos_ativos = metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                    '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
                if processos_ativos is None:
                    mensagem = 'Não foi encontrada a fila: '+fila
                    logging.info(mensagem)
                    print(mensagem)                      
                    pyautogui.alert(mensagem)
                    return 
                aux = str(processos_ativos.text).replace('[EF] Minutar Decisão - Gabinete\n', '')
                processos_ativos.click()
                print('Clicou na Tarefa')
                
                logging.info('Aguardando Página de Processos Ativos')
            
                metodos.controlar_tempo_espera(True)
                while aux != metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'):
                    time.sleep(0.5)
                    print("Aguarda Carregar Página de Processos Ativos")
                    metodos.identificacao_erros(driver)
                    metodos.controlar_tempo_espera(max=1200)
               
                total_processos = '1'
                #problema aqui

                ordem_li = 1
                total_li = 1
                texto_anterior = ''
                while int(total_processos) - (total_li-1) > 0 :
                    # Clica no primeiro processo da lista
                    
                    time.sleep(0.5)
                    while metodos.check_exists_by_xpath(driver=driver,xpath='//*[@id="modalStatusContentDiv"]'):
                        time.sleep(0.5)

                    tab_etiqueta = (By.XPATH,"//a[text()='ETIQUETAS']")   
                    outra_tentativa  = True
                    while outra_tentativa:
                        try:
                            elemento_etiqueta = driver.find_element(*tab_etiqueta)
                            
                            if not 'active' in elemento_etiqueta.get_attribute('class').split():
                                helper.efetuar_click(tab_etiqueta, "Tab Etiquetas")

                            outra_tentativa = False
                        except:
                            outra_tentativa = True
                    etiqueta = self.config_dict["etiqueta"]
                    outra_tentativa  = True
                    etiqueta = (By.XPATH,f"//a[contains(., '{etiqueta}')]")
                    while outra_tentativa:
                        try:
                            # etiqueta_mandado = metodos.elemento_por_texto_em_lista_by_tag(driver, 'a', etiqueta)

                            helper.efetuar_click(etiqueta,f'Etiqueta')
                            etiqueta_mandado = driver.find_element(*etiqueta)
                            span_elements_text = etiqueta_mandado.find_element(by=By.XPATH, value=".//span[2]").text
                            total_processos = span_elements_text
                            outra_tentativa = False
                        except:
                            outra_tentativa = True



                            time.sleep(1) 
                            
                    print('Indetificou total de processos', total_processos)
                    logging.info('Total de Processos no início da execução: '+ total_processos)
                    time.sleep(1)

                    processo = '//*[@id="agrupador-etiqueta-aberta"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, processo)))
                    texto_processo = metodos.get_element(driver, processo)  

                    metodos.subir_etiqueta(driver, texto_processo)

                    continua =  False
                    # Clica no processo
                    tentar = True
                    while tentar:
                        try:
                            texto_processo.click()
                            tentar = False
                        except:
                            print('erro ao clicar no processo')
                            time.sleep(1)               
                    texto_clicado = texto_processo.text
                    texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    print(texto_anterior, texto_carregado, texto_carregado == texto_anterior)
                    while texto_carregado.split(' - ')[0] == texto_anterior: 
                        time.sleep(0.1)
                        self.mensagem(logging, "Aguardando recarregar o texto")
                        texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                    texto_anterior = texto_carregado.split(' - ')[0]
                    
                    
                    # Identifica o texto do processo clicado
                    texto_clicado = texto_processo.text
                    if "ExFis" in texto_clicado:
                        # Identifica o processo carregado
                        texto_carregado = metodos.texto_by_xpath(driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
                        if texto_clicado in texto_carregado:
                            continua = True

                    if continua:

                        # Troca o frame 
                        iframe = metodos.get_element(driver, '//*[@id="frame-tarefa"]')
                        driver.switch_to.frame(iframe)
                        # Aguarda o carregamento
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div[4]/form/div/div/span[1]/div/a')))
                        time.sleep(0.5)
                        # Adicionando linha a planilha

                        self.log_bi.adicionar_processo(processo=texto_clicado)

                        # dados = [texto_clicado, datetime.now(), 'Não', 'Não', 'Não', 'Não', 'Não']
                        # lista_processos = self.adicionar_linha_pandas(lista_processos, dados)    
                        # lista_processos.to_excel(nome_arquivo)
                        # metodos.controlar_tempo_espera(True)
                        
                        while True:
                            # Identificar e Selecionar Tipo de Documento

                            try:                               
                                selects = driver.find_elements(By.TAG_NAME, 'select')                             
                                dropdown_element = Select(selects[0])
                                dropdown_element.select_by_visible_text("Decisão")                              
                                break
                            except:
                                time.sleep(0.3)
                                metodos.controlar_tempo_espera(max=120)
                                print("Aguardando para selecionar documento")
                                pass
                        metodos.controlar_tempo_espera(True)
                        time.sleep(0.2)
                        while True:
                            # Identificar e Selecionar Modelo
                            try:
                                # PARAMETRIZAR
                                            # WebDriverWait(driver, 10).until(lambda d : driver.find_element(*botao_salvar).is_enabled())

                                selects = driver.find_elements(By.TAG_NAME, 'select')                             
                                dropdown_element = Select(selects[1])
                                dropdown_element.select_by_visible_text(self.config_dict['modelo'])                              
                                break
                            except:
                                time.sleep(0.3)
                                metodos.controlar_tempo_espera(max=120)
                                print("Aguardando para selecionar modelo")
                                pass

                        self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Selecionar Modelo', 
                                                             atualizacao='Realizado')

                        # lista_processos = self.atualizar_status_processo(lista_processos, 
                        #                                             texto_clicado, 
                        #                                             'Selecionar Modelo',
                        #                                             'Realizado')  
                        # Clica no botão Salvar

                        metodos.controlar_tempo_espera(True)
                        metodos.identificacao_erros(driver)
                        # self.etapa_3(driver, metodos)   
                        botao_salvar = (By.XPATH,"//input[@value='Salvar']")
                        # elemento_botao_salvar = driver.find_element(*botao_salvar)
                        tentativas = 2 
                        for _ in range(tentativas):
                            try:
                                WebDriverWait(driver, 10).until(lambda d : driver.find_element(*botao_salvar).is_enabled())
                                helper.efetuar_click(botao_salvar,rotulo_elemento = 'Botao salvar')
                                break;
                            except StaleElementReferenceException as e:
                                print("Elemento Stale")
                                pass
                            except TimeoutException as e:
                                print('Timeout no botao de salvar')
                            except Exception as e:
                                print('execao nao prevista')
                                pass
                        
                            

                        metodos.controlar_tempo_espera(True)
                        self.inserir_codigo_movimentacao(driver, metodos)

                        self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='movimentacao', 
                                                             atualizacao='Realizado')

                        self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Salvar', 
                                                             atualizacao='Realizado')
                        
                        # lista_processos = self.atualizar_status_processo(lista_processos, 
                        #                             texto_clicado, 
                        #                             'Salvar',
                        #                             'Realizado') 
                        self.etapa_5(driver, metodos)

                        self.log_bi.atualizar_etapa_processo(processo=texto_clicado, 
                                                             etapa='Encaminhar', 
                                                             atualizacao='Realizado')


                        driver.switch_to.default_content()
                        iframe = metodos.get_element(driver, '//*[@id="ngFrame"]')
                        driver.switch_to.frame(iframe)
                        while True:#Checa quando o numero de precessos da etiqueta descer pra ter certeza q o processo foi processado.
                            try:
                                etiqueta = self.config_dict["etiqueta"]
                                etiqueta = (By.XPATH,f"//a[contains(., '{etiqueta}')]")
                                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(*etiqueta)))
                                span_elements_text = element.find_element(by=By.XPATH, value=".//span[2]").text
                                total_processos_atualizado = span_elements_text
                                print('Aguardando')
                                time.sleep(1)
                                if total_processos != total_processos_atualizado:
                                    total_processos = total_processos_atualizado
                                    break
                            except Exception as e:
                                time.sleep(0.3)
                                metodos.controlar_tempo_espera(max=60)
                                print("Aguardando")
                                pass           
                    else:
                        ordem_li+=1
                        total_li+=1
                        # DESCE PARA QUE OS DEMAIS PROCESSOS FIQUEM VISÍVEIS 
                        html = metodos.get_element(driver, 'html')
                        for i in range(4):
                            html.send_keys(Keys.DOWN)
                        if ordem_li > 30:
                            proximo = '/html/body/app-root/selector/div/div/div[2]/right-panel/div/processos-tarefa/div[1]/div[2]/div/div[1]/p-datalist/div/p-paginator/div/a[3]'
                            if metodos.check_exists_by_xpath(driver, proximo):
                                ele_proximo = metodos.get_element(driver, proximo)
                                ele_proximo.click()
                                ordem_li = 1
                                time.sleep(2)
                                for i in range(15):
                                    html.send_keys(Keys.PAGE_UP)
                        

                    print('Total de Processos neste momento da execuação:', total_processos)
                    logging.info('Total de Processos neste momento da execuação: '+ total_processos)   
                    time.sleep(2)

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
        # lista_processos.to_excel(nome_arquivo, index=False)
        # os.system("start " + nome_arquivo)
        # pyautogui.alert(text='A execução terminou. Consulte o arquivo '+nome_arquivo, title='Término de Execução', button='OK')

        os.system("start " + self.log_bi.retorna_nome_arquivo())
        pyautogui.alert(text='A execução terminou. Consulte o arquivo '
                        +self.log_bi.retorna_nome_arquivo(), 
                        title='Término de Execução', button='OK')

    def salvar_etapa(self,processo, etapa='Salvar' ):
        lista_processos = self.atualizar_status_processo(lista_processos, 
                                                    processo, 
                                                    etapa,
                                                    'Realizado')  
        lista_processos.to_excel(self.nome_arquivo)
    
    