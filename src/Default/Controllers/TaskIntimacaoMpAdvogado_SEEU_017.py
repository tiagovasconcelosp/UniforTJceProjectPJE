# ###################################################
# ###################################################
# ## Desenvolvido por:
# ## Lucas Pacheco
# ## E-mail: lucas.juca@tjce.jus.br
# ## Núcleo de Inovações SETIN
# ###################################################
# ###################################################

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as OptionsChrome
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Print import Print
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
from pathlib import Path
import os
import pandas as pd
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException

class TaskIntimacaoMpAdvogado_SEEU_017:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    
    def __init__(self, driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                 inicioTime, url, dataform, acaoEmErro, xml, log_unificado):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], []]
        desktop = None
        self.xml = xml
        if desktop is None:
            desktop = Path.home() / "Desktop"
            if not Path.exists(desktop):
                desktop = Path.home() / "OneDrive" / "Área de Trabalho"
            if not Path.exists(desktop):
                desktop = Path.home() / "OneDrive" / "Desktop"
        path_executados = os.path.join(desktop, "executados")
        if not os.path.isdir(path_executados):
            os.mkdir(path_executados)
        current_date = datetime.now()
        date_string = current_date.strftime("%Y-%m-%d")

        self.nome_arquivo = os.path.join(path_executados, f"{date_string}_processos_executados.xlsx")
        # if os.path.exists(self.nome_arquivo):
        if False:
            self.lista_processos = pd.read_csv(self.nome_arquivo)
        else:
            self.lista_processos = pd.DataFrame(columns=['Processo', 'Data', 'Notificar_MP', 
                                                    'Notificar_DP','Notificar_IE','Erro'])
            self.lista_processos.to_excel(self.nome_arquivo)


        self.dicionario_elementos = {}
        self.metodos = Metodos(url)
        driver.get(url)
        self.driver = driver
        logging.info('Acesso da Url: ' + url)
        Auth.LoginSeeu(driver, logging, dataform, url)
        logging.info('##############################')
        logging.info('Robô iniciado')
        self.logging = logging 
        try:
            self.executar()
        except Exception as e:
            self.logging.info(repr(e))
            print("Erro: ", repr(e))
        # self.Execute(driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                    #  inicioTime, url, dataform, acaoEmErro)

    def atualizar_status_processo(self, df, processo, coluna, status):         
        indice = df[df["Processo"]==processo] 
        row = indice.iloc[0]
        df.at[row.name, coluna] = status         
        return df
    def adicionar_linha_pandas(self, df, dados):         
        df.loc[0] = dados         
        df.index = df.index + 1         
        return df
    def resolver_recaptcha(self):
        
        #Usado para aguardar validacao do recaptcha
        self.logging.info('Aguardando resolucao de recaptcha - 120s')
        print('Aguardando resolucao de recaptcha - 120s')

        try:
            element = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'li.even')))

        except Exception as e:
            self.logging.info(repr(e))
            self.logging.info('Falha ao resolver recaptcha')
            self.logging.info('Finalizando o robo')
            return self.listProcessos
        
    def selecao_vara(self):
        # Selecao da vara
        # vara = 'TJCE - Fortaleza - 3ª Vara de Execução Penal (Corregedoria)'

        # TESTE
        # perfil = 'TJCE - Fortaleza - 1ª Vara de Execução Penal (Regime Semiaberto e Fechado)'
        vara = self.xml.find('vara').text
        try:
            select = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@title="' + vara + '"]'))).click()

            self.logging.info('Selecionando a vara')
        except Exception as e:
            self.logging.info(repr(e))
            self.logging.info('Nao foi possivel localizar a vara')
            self.logging.info('Finalizando robo')


    def mudar_iframe(self, iframe_xpath: str):
        try:
            iframe = self.metodos.get_element(self.driver, iframe_xpath)
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            self.logging.info(repr(e))
            print("Erro: ", repr(e))
    
    def mudar_frame(self, frame_xpath: str):
        try:
            iframe = self.metodos.get_element(self.driver, frame_xpath)
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            self.logging.info(repr(e))
            print("Erro: ", repr(e))

    def efetuar_click(self, xpath_elemento: str, rotulo_elemento: str ):
        '''
            """efetua um click de um elemento

        Args:
            xpath_elemento (str): Xpath do elemento presente na pagina á ser clicado.
            rotulo_elemento (str): alias para elemento ao ser exbido em log ou para Usuário.

        Returns:
        '''
        time.sleep(1)
        self.logging.info(f'Clicar em {rotulo_elemento}')
        print(f'Clicar em {rotulo_elemento}')
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_elemento))).click()
            self.logging.info(f'Clicando {rotulo_elemento}.')
        except Exception as e:
            self.logging.info(repr(e))
            print("Erro: ", repr(e))
            self.logging.info(f'Nao foi possivel clicar em {rotulo_elemento}.')
            print(f'Nao foi possivel clicar em {rotulo_elemento}.')
            self.info('Continuando . . .')
    def selecionar_opcao_element(self, xpath_elemento: str, texto_opcao):
        self.logging.info(f'Selecionar em {texto_opcao}')
        try:
            select = self.metodos.get_element(self.driver,
                                        xpath_elemento)
            dropdown_element = Select(select)
            dropdown_element.select_by_visible_text(texto_opcao) 
            self.logging.info(f'Selecionado {texto_opcao}.')
            
        except Exception as e:
            self.logging.info(repr(e))
            print(repr(e))
            self.logging.info(f'Não foi possivel selecionar {texto_opcao}')
    def pegar_numero_registros(self):
        WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="navigator"]/div[2]')))
        return int(self.metodos.get_element(self.driver,'//*[@id="navigator"]/div[2]').text.split()[0])
    # //*[@id="quadroPendencias"]
    def advogado_presente(self):
        time.sleep(0.5)
        self.logging.info('Verificando presenca de advogado')
        print('Verificando presenca de advogado')
        max_attempts = 3
        attempts = 0

        while attempts < max_attempts:
            try:
                WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="informacoesProcessuais"]')))
                corpo_tabela = self.metodos.get_element(driver=self.driver,xpath='//*[@id="informacoesProcessuais"]')
                for row in corpo_tabela.find_elements(by=By.TAG_NAME,value = "tr"):
                # Iterate through the cells in each rowd
                    for cell in row.find_elements(By.TAG_NAME,"td"):
                        # Check if the cell contains the desired value
                        if "Advogado" in cell.text:
                            return True
                return False
            except StaleElementReferenceException:
                attempts += 1
            except TimeoutError:
                print('Time Out')
       
    def retornar_lista(self):
        self.logging.info("Retomando para a lista")
        print("Retomando para a lista")
        self.driver.switch_to.default_content()
        self.mudar_frame("//frame[@id='mainFrame']")
        self.efetuar_click('//*[@id="main-menu"]/li[1]/a', 'Retorno ao inicio.')
        self.mudar_iframe("//iframe[@name='userMainFrame']")

        self.efetuar_click("//a[text()='Análise de Juntadas']", 'Analise de Juntadas')
        
        self.efetuar_click("//*[@id='tabprefix4']/table/tbody/tr/td[2]/fieldset/table/tbody/tr[2]/td[2]/a", 'Retorno de Conclusão')

        self.selecionar_opcao_element('//*[@id="tipoConclusao"]',"DECISÃO")
        
        self.efetuar_click('//*[@id="searchButton"]', 'Filtrar')
    def verificar_envio_mp_dp(self):
        self.logging.info("Verificando envio MP, DP")
        print("Verificando envio MP, DP")
        check  = '//*[@id="quadroPendencias"]'
        DP_presente = True
        MP_presente = True
        self.metodos.get_element(driver=self.driver,xpath=check)

        texto_DP = "//*[contains(text(), 'REMETIDOS OS AUTOS PARA DEFENSORIA PÚBLICA')]"
        texto_MP = "//*[contains(text(), 'REMETIDOS OS AUTOS PARA MINISTÉRIO PÚBLICO')]"
        texto_DP_recebido = "//*[contains(text(), 'RECEBIDOS OS AUTOS')]"
        legend_text = "Movimentações Realizadas"
        movimentacoes = self.driver.find_element(By.XPATH, "//fieldset[legend='Movimentações Realizadas']")
        

        try:
            movimentacoes.find_element(by=By.XPATH,value = texto_DP)
            self.logging.info('A movimentacao encontrada')

        except NoSuchElementException:
            self.logging.info('A movimentacao não foi encontrada')
            DP_presente = False
        try:
            movimentacoes.find_element(by=By.XPATH,value = texto_DP_recebido)
            self.logging.info('Achado o retorno da DP')
            DP_presente = True
        except NoSuchElementException:
            # Se o texto RECEBIDO OS AUTOS for encontrado nas movimentacoes a dp ja recebeu e retornou
            pass
        try:
            movimentacoes.find_element(by=By.XPATH,value = texto_MP)
        except NoSuchElementException:
            self.logging.info('A movimentacao não foi encontrada')
            MP_presente = False

        return MP_presente,DP_presente
        
                # self.metodos.get_element(driver=self.driver,xpath="//*[contains(text(), 'REMETIDOS OS AUTOS PARA DEFENSORIA PÚBLICA')]")
                # self.metodos.get_element(driver=self.driver,xpath="//*[contains(text(), 'REMETIDOS OS AUTOS PARA MINISTÉRIO PÚBLICO')]")

    def verificar_envio_mp_ie(self):
        self.logging.info("Verificando envio MP, IE")
        print("Verificando envio MP, IE")
        # quadro = self.metodos.get_element(driver=self.driver,xpath='//*[@id="quadroPendencias"]/table/tbody')
        
        fieldset_element = self.driver.find_element(By.XPATH, "//fieldset[legend='Movimentações Realizadas']")

        IE_presente = False
        MP_presente = False
        if "EXPEDIÇÃO DE INTIMAÇÃO" in fieldset_element.text:
            IE_presente = True
            self.logging.info("Movimentacao encontrado IE")
            print("Movimentacao encontrado IE")
        if 'REMETIDOS OS AUTOS PARA MINISTÉRIO PÚBLICO' in fieldset_element.text:
            self.logging.info("Movimentacao encontrado MP")
            print("Movimentacao encontrado MP")
            MP_presente = True

        self.logging.info('A movimentacao encontrada')
        if (MP_presente and IE_presente):
            return MP_presente, IE_presente
        self.logging.info('A movimentacao não foi encontrada')
        return MP_presente, IE_presente   
    def notificar_mp_dp(self, mp, dp):
        self.logging.info("Notificar MP e DP")
        print("Notificar MP e DP")
        self.efetuar_click("//*[contains(text(), 'Realizar Remessa')]",'Realizar Remessa')
        self.mudar_frame('//*[@frameborder="0"]')
        if not mp:
            self.efetuar_click("//input[@value='ministerioPublico']","Checkbox do miniterio publico")
            self.selecionar_opcao_element('//*[@id="finalidadeRemessa"]','CIÊNCIA')
        if not dp:
            self.efetuar_click("//input[@value='defensoriaPublica']","Checkbox da defensoria publica")
            self.selecionar_opcao_element('//*[@id="finalidadeRemessaDP"]','CIÊNCIA')
        self.efetuar_click('//*[@id="remessaButton"]','Realizar remessa')

    def notificar_mp_ie(self,mp:bool, ie:bool):
        
        time.sleep(0.5)
        
        if mp:
            self.efetuar_click("//*[contains(text(), 'Realizar Remessa')]", "Realizar Remessa")
            self.mudar_frame('//*[@frameborder="0"]')
            self.efetuar_click("//input[@value='ministerioPublico']",'Checkbox Miniterio Publico')
            self.selecionar_opcao_element('//*[@id="finalidadeRemessa"]',"CIÊNCIA")
            self.efetuar_click('//*[@id="remessaButton"]',"Realizar Remessa")

        # //*[@id="errorMessages"]/div[3]/div/ul/li
        # elemento_problema = '//*[@id="errorMessages"]/div[3]/div/ul/li/text()="Your Desired Text"'
        # if self.metodos.check_exists_by_xpath(self.driver, elemento_problema): return False
        
        self.driver.switch_to.default_content()
        if ie:    
            self.mudar_frame("//frame[@id='mainFrame']")
            self.mudar_iframe("//iframe[@name='userMainFrame']")
            self.efetuar_click("//*[contains(text(), 'Intimar Partes')]","Intimar Partes")
            self.mudar_frame('//*[@frameborder="0"]')

            input_xpath = "//td[b='Advogado']/input[@type='checkbox']"
            input_elements = self.driver.find_elements(By.XPATH, input_xpath)
            for e in input_elements:
                e.click()
            input_xpath_parteAtivas = "//input[@name='prazoPartesAtivas']"
            input_xpath_partePassivas = "//input[@name='prazoPartesPassivas']"
            self.metodos.get_element(self.driver, input_xpath_parteAtivas).send_keys('5')
            self.metodos.get_element(self.driver, input_xpath_partePassivas).send_keys('5')
        ### ### ###
            self.efetuar_click('//*[@id="intimarButton"]',"Botão initmar")
    def escrever_planilha_sem_advogado(self,numero_processo,mp,dp):
            texto_mp = 'Já realizado'
            texto_dp = 'Já realizado'
            if not mp:texto_mp = 'Realizado'
            if not dp:texto_dp = 'Realizado' 
            self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                            numero_processo, 
                                                            'Notificar_MP',
                                                            texto_mp)
            self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                            numero_processo, 
                                                            'Notificar_DP',
                                                            texto_dp)
            self.lista_processos.to_excel(self.nome_arquivo)
    def escrever_planilha_com_advogado(self,numero_processo, mp, ie):
        texto_mp = 'Já realizado'
        texto_ie = 'Já realizado'
        if not mp:texto_mp = 'Realizado'
        if not ie:texto_ie = 'Realizado' 
        self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                        numero_processo, 
                                                        'Notificar_MP',
                                                        texto_mp)
        self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                        numero_processo, 
                                                        'Notificar_IE',
                                                        texto_ie)
        self.lista_processos.to_excel(self.nome_arquivo)
    
    def gerenciar_pagina_processos(self,index):
        pagina =((index-1) // 20) + 1 # A pagina 20 ainda ta na pagina 1, e 
        processo = index % 20
        if processo == 0:processo = 20
        pagina_adequada = f"//*[@title='Ir para a página {pagina}']" 
        if self.metodos.check_exists_by_xpath(self.driver,pagina_adequada):
            self.efetuar_click(xpath_elemento = pagina_adequada, rotulo_elemento = f"Navegar para proxima pagina, {pagina}.")
        

        ele_processo = f'//*[@id="processoConclusaoForm"]/table[1]/tbody/tr[{processo}]/td[3]/a'
        numero_processo = f'//*[@id="processoConclusaoForm"]/table[1]/tbody/tr[{processo}]/td[5]/em'
        return ele_processo,numero_processo
    def executar(self):
        # #####################################################
        # Selecao da vara
        # perfil = 'TJCE - Fortaleza - 3ª Vara de Execução Penal (Corregedoria)'

        # TESTE

        # Parametrizar vara.
        seleciona_vara = self.xml.find('vara').text
        
        xpath = f'//*[@title="{seleciona_vara}"]'

        self.efetuar_click(xpath, 'vara')
        
        self.mudar_iframe("//iframe[@name='userMainFrame']")

        self.efetuar_click("//a[text()='Análise de Juntadas']", 'Analise de Juntadas')
        
        self.efetuar_click("//*[@id='tabprefix4']/table/tbody/tr/td[2]/fieldset/table/tbody/tr[2]/td[2]/a", 'Retorno de Conclusão')

        self.selecionar_opcao_element('//*[@id="tipoConclusao"]',"DECISÃO")
        
        self.efetuar_click('//*[@id="searchButton"]', 'Filtrar')

        numero_registros = self.pegar_numero_registros()
        index = 0
        while(index<numero_registros):
            index +=1 ### guardar processo ao final do processo ###
            # ele_processo = f'//*[@id="processoConclusaoForm"]/table[1]/tbody/tr[{index}]/td[3]/a'
            # numero_processo = (f'//*[@id="processoConclusaoForm"]/table[1]/tbody/tr[{index}]/td[5]/em')
            ele_processo,numero_processo = self.gerenciar_pagina_processos(index)
            # if self.lista_processos['Processo'].isin([numero_processo]).any():
            #     continue
            try: 

                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, numero_processo)))
                numero_processo = self.metodos.get_element(self.driver,numero_processo).text
                dados = [numero_processo, datetime.now(), 'Não','Não','Não','Não']
                self.lista_processos = self.adicionar_linha_pandas(self.lista_processos, dados)  
                self.efetuar_click(ele_processo, f"Analisar processo {index}")

                ###metododizar
                element = self.metodos.get_element(self.driver,
                                            '//*[@id="processoConclusaoForm"]/fieldset/table/tbody/tr[1]/td[2]/a[1]')
                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()
                self.driver.switch_to.window(self.driver.window_handles[1])

                advogado_existe = self.advogado_presente()

                if advogado_existe:
                    print("Advogado presente!")
                    print('fechar aba')
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])          
                    print('Mudar aba')
                    self.mudar_frame('//*[@id="mainFrame"]')
                    self.mudar_iframe('//*[@name="userMainFrame"]')
                    self.efetuar_click("//*[@id='editButton']", "Botao de Analise")
                    mp, ie = self.verificar_envio_mp_ie()
                    if  mp and ie:
                        self.logging.info("movimentacao ja realizada")
                        print("movimentacao ja realizada")
                    else:
                        try:
                            self.notificar_mp_ie(not mp,not ie)# ficou esquisito, mas ta certo.
                        except Exception as e:
                            
                            self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                            numero_processo, 
                                                            'Erro',
                                                            'Sim')
                            self.logging.info(repr(e))
                            print("Erro: ", repr(e))
                            print(f"Erro: processo {numero_processo} nao concluiu passo a passo.")
                            self.retornar_lista()
                            continue
                    self.escrever_planilha_com_advogado(numero_processo,mp, ie)
                    self.driver.switch_to.default_content()
                    self.mudar_frame("//frame[@id='mainFrame']")
                    self.mudar_iframe("//iframe[@name='userMainFrame']")

                    self.efetuar_click("//*[contains(text(), 'EXPEDIÇÃO DE INTIMAÇÃO')]", 'EXPEDIÇÃO DE INTIMAÇÃO')
                else:
                    self.logging.info('Advogado não presente')
                    print('Advogado não presente')
                    self.efetuar_click("//*[contains(text(), 'Analisar Conclusão Retornada ')]",'Analisar Conclusão Retomada ')

                    mp,dp =  self.verificar_envio_mp_dp()
                    if not (mp and dp) : 
                        self.notificar_mp_dp(mp,dp)
                    self.escrever_planilha_sem_advogado(numero_processo, mp,dp)
                    self.logging.info("Escrevendo em arquivo")
                    print("Escrevendo em arquivo")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
                self.retornar_lista()
            except Exception as e:
                print(index)
                self.logging.info(repr(e))
                print("Erro: ", repr(e))
                self.lista_processos = self.atualizar_status_processo(self.lista_processos, 
                                                numero_processo, 
                                                'Erro',
                                                'Sim')
                
                self.lista_processos.to_excel(self.nome_arquivo)
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])          
                self.retornar_lista()
                continue
        
            
print("started")
