# ###################################################
# ###################################################
# ## Desenvolvido por:
# ## Augusto Lima dos Santos 
# ## Rian Radeck Santos Costa
# ## E-mails: augusto.santos@tjce.jus.br 
# ##          rian.costa@tjce.jus.br
# ###################################################
# ###################################################

import time
import pyautogui

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as OptionsChrome
from selenium.common.exceptions import WebDriverException

from .Auth import Auth
from .Metodos import Metodos

class TaskMovimentarProcessos_PJE_007:
    
    def __init__(self, driver, caminhoImages, logging, url, dataform, acaoEmErro, log_bi):
        self.log_bi = log_bi
        self.Execute(driver, caminhoImages, logging, url, dataform, acaoEmErro)


    def Execute(self, driver, caminhoImages, logging, url, dataform, acaoEmErro):
        repete = True
        autenticacao = Auth()
        metodos = Metodos(url)

        self.log_bi.criar_arquivo_executados(['Selecionar Lote', 'Clicar Transições', 
                                              'Movimentar'])

        while repete:
            repete = False
            total_processos = 1            
            try:
                logging.info('##############################')
                logging.info('Robô iniciado')
                #url = 'https://pje2cp.tjce.jus.br/pje1grau/login.seam'
                driver.get(url)
                logging.info('Acesso da Url: '+ url)
                time.sleep(2)
                print("started")

                autenticacao.Login(driver, logging, dataform, url)

                perfil = metodos.get_element(driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
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
                
                fila = '[SAJ] Processos ativos'
                processos_ativos = metodos.elemento_por_texto_em_lista_by_xpath_e_tag(driver, \
                    '//*[@id="rightPanel"]/div/div[3]', 'a', fila)
                if processos_ativos is None:
                    mensagem = 'Não foi encontrada a fila: '+fila
                    logging.info(mensagem)
                    print(mensagem)                      
                    pyautogui.alert(mensagem)
                    return 
                total_inicial = str(processos_ativos.text).replace('[SAJ] Processos ativos\n', '')
                processos_ativos.click()
                print('Clicou na Tarefa')
                
                logging.info('Aguardando Página de Processos Ativos')
                metodos.controlar_tempo_espera(True)
                while total_inicial != metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'):
                    time.sleep(0.5)
                    print("Aguarda Carregar Página de Processos Ativos")
                    metodos.identificacao_erros(driver)
                    metodos.controlar_tempo_espera(max=1200)

                total_processos = metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span')
                print('Indetificou total de processos', total_processos)
                logging.info('Total de Processos no início da execução: '+ total_processos)
                total_atual = str(total_processos)
                while int(total_processos) > 0 :

                    self.log_bi.adicionar_processo(processo=total_atual)

                    time.sleep(1)
                    checkbox = metodos.get_element(driver, '//*[@id="acoes-processos-selecionados"]/div/div/button')
                    checkbox.click()
                    
                    time.sleep(1)
                    movimentar_lotes = metodos.get_element(driver, '//*[@id="acoes-processos-selecionados"]/div/div/button[2]')
                    movimentar_lotes.click()
                    
                    self.log_bi.atualizar_etapa_processo(processo=total_atual,
                                                         etapa='Selecionar Lote',
                                                         atualizacao='Realizado')

                    metodos.controlar_tempo_espera(True)
                    while not metodos.check_exists_by_xpath(driver, '//*[@id="myModalLabel"]'):
                        time.sleep(0.5)
                        print("Aguarda Carregar Processos no Modal")
                        metodos.identificacao_erros(driver)
                        metodos.controlar_tempo_espera(max=1200)

                    metodos.controlar_tempo_espera(True)
                    while len(driver.find_elements(by=By.CLASS_NAME, value='processos-list-row')[0].text)<=0:
                        time.sleep(0.5)
                        print("Aguarda Carregar Processos no Modal 2")
                        metodos.identificacao_erros(driver)
                        metodos.controlar_tempo_espera(max=1200)

                    logging.info('Clique nas transições')
                    time.sleep(0.5)
                    # Tenta clicar na Transição
                    segue_elemento = True
                    metodos.controlar_tempo_espera(True)
                    while segue_elemento:
                        try:
                            print("Tenta clicar nas transições")
                            transicoes = metodos.get_element(driver, '//*[@id="transicoes"]')
                            transicoes.click()
                            segue_elemento = False
                        except:
                            time.sleep(0.5)
                            print("Aguarda Carregar Transição")
                            metodos.identificacao_erros(driver)
                            metodos.controlar_tempo_espera(max=240)
                            segue_elemento = True

                    time.sleep(1)
                    logging.info('Clique na Opção')
                    transicoes_option = metodos.get_element(driver, '//*[@id="transicoes"]/option[2]')
                    transicoes_option.click()   
                    
                    self.log_bi.atualizar_etapa_processo(processo=total_atual,
                                                         etapa='Clicar Transições',
                                                         atualizacao='Realizado')

                    movimentar = metodos.get_element(driver, '//*[@id="modalMovimentarEmLote"]/div/div/div[3]/div/button[1]')
                    movimentar.click()
                    
                    metodos.controlar_tempo_espera(True)
                    while total_processos == metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span'):
                        time.sleep(0.5)
                        print("Aguarda atualizar lista de processos")
                        metodos.identificacao_erros(driver)
                        metodos.controlar_tempo_espera(max=1200)

                    self.log_bi.atualizar_etapa_processo(processo=total_atual,
                                                         etapa='Movimentar',
                                                         atualizacao='Realizado')

                    time.sleep(0.5)   
                    fechar = metodos.get_element(driver, '//*[@id="modalMovimentarEmLote"]/div/div/div[3]/div/button[2]')
                    fechar.click() 
                    
                    total_processos = metodos.texto_by_xpath(driver, '//*[@id="divActions"]/filtro-tarefas/div/div[1]/div[2]/span')
                    print('Indetificou total de processos', total_processos)
                    total_atual = str(total_processos)
                    logging.info('Total de Processos neste momento da execuação: '+ total_processos)

                logging.info('Total de Processos no término da execução: '+ total_processos)

                print("Terminou")   
            except Exception as e:
                logging.info(repr(e))
                print("Erro: ", repr(e))
                print(total_processos, repete)
                self.log_bi.enviar_erro(num_processo=total_atual,
                                    passo_executado="Geral",
                                    mensagem=repr(e))
                if int(total_processos)>0:
                    repete = True
                    if int(acaoEmErro) == 1:
                        driver.close()
                        options = OptionsChrome()
                        options.add_argument("--start-maximized")
                        driver = webdriver.Chrome(chrome_options=options)
                    
            

