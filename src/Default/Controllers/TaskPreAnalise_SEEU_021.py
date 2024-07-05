# ###################################################
# ###################################################
# ## Desenvolvido por:
# ## Tiago Vasconcelos
# ## E-mail: tiago.ponte@tjce.jus.br
# ## Núcleo de Inovações SETIN
# ###################################################
# ###################################################
import glob
import time
import pyautogui
import os
import winreg
import xml.etree.ElementTree as ET

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Print import Print


class TaskPreAnalise_SEEU_021:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], 0, ] # Adicionado uma nova posicao de lista para somar total de processos
    countEncaminhados = 0
    processoExecutado = ""
    
    def __init__(self, driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                 inicioTime, url, dataForm, xml, log_bi):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], 0, ] # Adicionado uma nova posicao de lista para somar total de processos
        self.countEncaminhados = 0
        self.processoExecutado = ""
        self.modelo = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='preAnalise')
        self.Execute(driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                     inicioTime, url, dataForm, log_bi)

    def ExecuteProcesso(self, driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui, log_bi):

        try:
            selectResult = driver.find_elements(By.XPATH, '//td[contains(text(), "Nenhum registro encontrado")]')
            if selectResult:
                logging.info('Nenhum registro encontrado em Pre-analise')
                logging.info('Interropendo execucao de Pre-analise')
                print('Nenhum registro encontrado em Pre-analise')
                print('Interropendo execucao de Pre-analise')
                return self.listProcessos
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu um erro na tela de Pre-analise - Registros')
            print(repr(e))
            return self.listProcessos

        try:
            # Verifica se é a primeira vez que está executando
            if self.countEncaminhados == 0:
                # time.sleep(5)
                try:
                    selectResult = driver.find_elements(By.XPATH, '//*[@id="navigator"]/div[2]')[0].text
                    # 67 registro(s) encontrado(s), exibindo de 1 até 40
                    selectResult = selectResult.split()
                    logging.info('Quantidade de registro(s) encontrado(s): ' + str(selectResult[0]))
                    print('Quantidade de registro(s) encontrado(s): ' + str(selectResult[0]))
                    # Total encontrado
                    self.listProcessos[3] = self.listProcessos[3] + int(selectResult[0])
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu um erro ao capturar os processos')
                    self.listProcessos[3] = 0

            # Captura todos os elementos da lista
            selectResult = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr")

            for x in range(len(selectResult)):

                # Captura numero do processo
                # Invertando execucao, do ultimo para o mais recente
                try:
                    numeroProcesso = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(
                        len(selectResult) - x) + "]/td[2]/a[1]/em")[0].text
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Falha ao localizar o numero do processo')
                    print('Falha ao localizar o numero do processo')
                    numeroProcesso = "Falha Numero Processo"
                    continue

                logging.info('Abrindo processo: ' + numeroProcesso)
                print('Abrindo processo: ' + numeroProcesso)
                self.processoExecutado = str(numeroProcesso)
                log_bi.adicionar_processo(self.processoExecutado)
                
                # Alimentando resultando
                self.listProcessos[0].append(str(numeroProcesso))
                self.listProcessos[1].append(1) # Valor 1 para nao concluido

                # Clica em Minuta Expressa
                # Captura numero do processo
                try:
                    select = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(
                        len(selectResult) - x) + "]/td[9]/table/tbody/tr/td[2]/span[2]/a")[0].click()

                    time.sleep(1)
                except Exception as e:
                    logging.info(repr(e))
                    print(repr(e))
                    logging.info('Falha ao clicar em minuta expressa do processo')
                    print('Falha ao clicar em minuta expressa do processo')
                    return self.listProcessos

                # #####################################################
                # Localiza iframe
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarrega elementos')
                print('Recarrega elementos')
                # Localiza frame para o proximo processo
                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'mainFrame')))
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe mainFrame')
                    print('Ocorreu uma falha ao localizar iframe mainFrame')
                    return self.listProcessos
                # alternar para o iframe selecionado
                driver.switch_to.frame(iframe)
                logging.info('Recarregando elementos mainFrame')
                print('Recarregando elementos mainFrame')

                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'userMainFrame')))
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe userMainFrame')
                    print('Ocorreu uma falha ao localizar iframe userMainFrame')
                    return self.listProcessos
                # alternar para o iframe selecionado
                driver.switch_to.frame(iframe)
                logging.info('Recarregando elementos userMainFrame')
                print('Recarregando elementos userMainFrame')

                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe window_16955555555_content')
                    print('Ocorreu uma falha ao localizar iframe window_16955555555_content')
                    return self.listProcessos
                # alternar para o iframe selecionado
                driver.switch_to.frame(iframe)
                logging.info('Recarregando elementos iframe window_16955555555_content')
                print('Recarregando elementos iframe window_16955555555_content')

                # #####################################################
                # #####################################################

                # Realiza a busca
                try:
                    # metodos.get_element(driver,
                    #                     '//*[@id="textoPesq"]').send_keys('ROBO MP')
                    metodos.get_element(driver,
                                        '//*[@id="textoPesq"]').send_keys(self.modelo['modeloPesquisa'])
                    time.sleep(2)
                    pyautogui.press('enter')
                    time.sleep(2)

                    logging.info('Incluindo: ' + str(self.modelo['modeloPesquisa']))

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel buscar por ROBO MP')
                    print('Nao foi possivel buscar por ROBO MP')
                    return self.listProcessos

                # #####################################################
                # Localiza iframe
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarrega elementos default_content')
                print('Recarrega elementos default_content')

                # Localiza frame para o proximo processo
                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'mainFrame')))

                    # alternar para o iframe selecionado
                    driver.switch_to.frame(iframe)
                    logging.info('Recarregando elementos mainFrame')
                    print('Recarregando elementos mainFrame')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe mainFrame')
                    print('Ocorreu uma falha ao localizar iframe mainFrame')
                    return self.listProcessos

                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'userMainFrame')))

                    # alternar para o iframe selecionado
                    driver.switch_to.frame(iframe)
                    logging.info('Recarregando elementos userMainFrame')
                    print('Recarregando elementos userMainFrame')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe userMainFrame')
                    print('Ocorreu uma falha ao localizar iframe userMainFrame')
                    return self.listProcessos

                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))

                    # alternar para o iframe selecionado
                    driver.switch_to.frame(iframe)
                    logging.info('Recarregando elementos iframe window_1695076499555_content')
                    print('Recarregando elementos iframe window_1695076499555_content')
                except Exception as e:
                    
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe window_1695076499555_content')
                    print('Ocorreu uma falha ao localizar iframe window_1695076499555_content')
                    return self.listProcessos

                # #####################################################
                # #####################################################

                # #####################################################
                # Clica em salvar
                try:
                    # element = WebDriverWait(driver, 10).until(
                    #     EC.presence_of_element_located(
                    #         (By.CSS_SELECTOR, 'input#saveButton'))).click()

                    element = driver.find_element(By.CSS_SELECTOR, 'input#saveButton')
                    driver.execute_script("javascript:salvarPreAnaliseExpressa();", element)

                    logging.info('Clica em Salvar e Concluir')
                    print('Clica em Salvar e Concluir')


                except Exception as e:                    
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em Salvar e Concluir')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    return self.listProcessos
                # #####################################################

                time.sleep(6)

                # #####################################################
                try:
                    # Total finalizado
                    self.countEncaminhados += 1
                    # Altera o status para finalizado
                    # Deleta o ultimo registro
                    del (self.listProcessos[1][-1])
                    # Finaliza com status de sucesso
                    self.listProcessos[1].append(0)
                    log_bi.atualizar_etapa_processo(
                        processo=str(numeroProcesso),
                        etapa="EXECUTA MINUTA EXPRESSA",
                        atualizacao="Realizado",
                    )
                except Exception as e:
                    
                    logging.info(repr(e))
                    logging.info('Falha em atualizar os registros')

                logging.info('Finalizando processo: ' + str(numeroProcesso))

                # #####################################################
                # Localiza iframe
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarrega elementos - 01')
                print('Recarrega elementos - 01')

                # Localiza frame para o proximo processo
                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'mainFrame')))
                    # alternar para o iframe selecionado
                    driver.switch_to.frame(iframe)
                    logging.info('Recarregando elementos mainFrame - 01')
                    print('Recarregando elementos mainFrame - 01')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe mainFrame - 01')
                    print('Ocorreu uma falha ao localizar iframe mainFrame - 01')
                    return self.listProcessos

                try:
                    iframe = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.NAME, 'userMainFrame')))
                    # alternar para o iframe selecionado
                    driver.switch_to.frame(iframe)
                    logging.info('Recarregando elementos userMainFrame - 01')
                    print('Recarregando elementos userMainFrame - 01')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu uma falha ao localizar iframe userMainFrame - 01')
                    print('Ocorreu uma falha ao localizar iframe userMainFrame - 01')
                    return self.listProcessos

            # #####################################################
            # Clica em filtrar - para carregar novos processos
            try:
                select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '#searchButton'))).click()

                logging.info('Clica em Pesquisar')


                time.sleep(4)
            except Exception as e:
                logging.info(repr(e))
                logging.info('Ocorreu um erro ao clicar em filtrar')
                return self.listProcessos
            #####################################################
            #####################################################

            #####################################################
            #####################################################
            logging.info('Checando se existe mais processos . . .')
            try:
                selectResult = driver.find_elements(By.XPATH, '//td[contains(text(), "Nenhum registro encontrado")]')
                if selectResult:
                    logging.info('Nao tem mais processos, finalizando . . .')
            except:
                selectResult = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr")
                logging.info('Foram encontrados mais processos para realizar: ' + str(len(selectResult)))
                self.ExecuteProcesso(driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui, log_bi)
            #####################################################
            #####################################################

        except Exception as e:
            log_bi.enviar_erro(
                num_processo=self.processoExecutado,
                passo_executado="EXECUTA MINUTA EXPRESSA",
                mensagem=repr(e),
            )
            logging.info(repr(e))
            logging.info(self.listProcessos)
            logging.info('Ocorreu um erro na tela de Pre-analise')

        logging.info('Interropendo execucao')
        logging.info('Todos os processos foram assinados')

        return self.listProcessos
    def ExecuteFiltroProcesso(self, driver, logging, metodos, ):

        # #####################################################
        # Localiza frame
        # Recarrega elementos
        driver.switch_to.default_content()
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'mainFrame')))
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu uma falha ao autenticar')
            return self.listProcessos
        # alternar para o iframe selecionado
        driver.switch_to.frame(iframe)
        logging.info('Recarregando elementos')
        print('Recarregando elementos')
        # #####################################################

        # #####################################################
        # Abre menu Minutas > Para Despacho
        minutas = metodos.elemento_por_texto_em_lista_by_tag(driver, "a", "Minutas")
        minutas.click()


        despacho = metodos.elemento_por_texto_em_lista_by_tag(driver, "a", "Para Despacho")
        despacho.click()

        # #####################################################
        # #####################################################

        time.sleep(2)

        # #####################################################
        # Localiza frame
        # Recarrega elementos
        # Para deixar um iframe ou frameset
        driver.switch_to.default_content()
        # Localiza frame para o proximo processo
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'mainFrame')))

            # alternar para o iframe selecionado
            driver.switch_to.frame(iframe)
            logging.info('Recarregando elementos mainFrame')
            print('Recarregando elementos mainFrame')
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu uma falha ao localizar iframe mainFrame')
            print('Ocorreu uma falha ao localizar iframe mainFrame')
            # return self.listProcessos
        # #####################################################

        # #####################################################
        # Localiza frame
        # Recarrega elementos
        # Localiza frame para o proximo processo
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'userMainFrame')))

            # alternar para o iframe selecionado
            driver.switch_to.frame(iframe)
            logging.info('Recarregando elementos userMainFrame')
            print('Recarregando elementos userMainFrame')
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu uma falha ao localizar iframe userMainFrame')
            print('Ocorreu uma falha ao localizar iframe userMainFrame')
            # return self.listProcessos
        # #####################################################

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#tipoConclusao')))

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#idAgrupador')))

        # Seleciona Tipo de conclusao
        select = Select(driver.find_element(By.CSS_SELECTOR, '#tipoConclusao'))
        select.select_by_visible_text('TODOS OS TIPOS')
        time.sleep(1)

        # Seleciona agrupador
        select = Select(driver.find_element(By.CSS_SELECTOR, '#idAgrupador'))
        try:
            select.select_by_visible_text('Vista ao Ministério Público')  # Comentado para teste
            # select.select_by_visible_text('acordao alterar pena')
        except:
            select.select_by_visible_text('Vista ao MP')
        time.sleep(1)

        # Seleciona Sem pre-analise
        select = driver.find_element(By.XPATH, '//input[@name="preAnalisada"][2]').click()

        time.sleep(1)

        # Clica em filtrar
        select = driver.find_element(By.CSS_SELECTOR, '#searchButton').click()

        time.sleep(2)

        try:
            # Exibe 100 processos por pagina
            select = Select(driver.find_element(By.CSS_SELECTOR, 'select[name="conclusaoPageSizeOptions"i]'))
            time.sleep(1)
            select.select_by_visible_text('100 por pág.')
            time.sleep(3)
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Nao foi possivel exibir 100 por pagina... Continuando. . .')
            print('Nao foi possivel exibir 100 por pagina... Continuando. . .')

        return driver
    def ExecuteAlteraVara(self, driver, logging, metodos, vara):

        # #####################################################
        # Localiza frame
        # Recarrega elementos
        # driver.switch_to.default_content()
        # try:
        #     iframe = WebDriverWait(driver, 10).until(
        #         EC.presence_of_element_located((By.NAME, 'userMainFrame')))
        # except Exception as e:
        #     logging.info(repr(e))
        #     logging.info('Ocorreu uma falha ao localizar iframe userMainFrame')
        #     print('Ocorreu uma falha ao localizar iframe userMainFrame')
        #     # return self.listProcessos
        # # alternar para o iframe selecionado
        # driver.switch_to.frame(iframe)
        # logging.info('Recarregando elementos userMainFrame')
        # print('Recarregando elementos userMainFrame')
        # #####################################################

        # Clica em altera vara
        select = driver.find_element(By.CSS_SELECTOR, '#alterarAreaAtuacao').click()
        time.sleep(2)

        # #####################################################
        # Localiza frame
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//iframe')))
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu uma falha ao localizar iframe window_1695079211505_content')
            print('Ocorreu uma falha ao localizar iframe window_1695079211505_content')
            # return self.listProcessos
        # alternar para o iframe selecionado
        driver.switch_to.frame(iframe)
        logging.info('Recarregando elementos iframe window_1695079211505_content')
        print('Recarregando elementos iframe window_1695079211505_content')
        # #####################################################

        try:
            select = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@title="' + vara + '"]'))).click()
            logging.info('Selecionando a vara ' + vara)
            print('Selecionando a vara ' + vara)

            time.sleep(6)
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Nao foi possivel alterar a vara')
            logging.info('Finalizando robo')
            return self.listProcessos

        return driver

    def Execute(self, driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel, inicioTime, url, dataForm,log_bi):
        
        log_bi.criar_arquivo_executados(
            ["EXECUTA MINUTA EXPRESSA"]
        )

        metodos = Metodos(url)
        driver.get(url)
        logging.info('##############################')
        logging.info('Robô iniciado')
        logging.info('Acesso da Url: ' + url)
        time.sleep(5)
        autenticacao = Auth()
        autenticacao.LoginSeeu(driver, logging, dataForm, url)
        # #####################################################
        # Localiza frame
        # Recarrega elementos
        # Para deixar um iframe ou frameset
        driver.switch_to.default_content()
        # Localiza frame para o proximo processo
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'mainFrame')))
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu uma falha ao autenticar')
            return self.listProcessos
        # alternar para o iframe selecionado
        driver.switch_to.frame(iframe)
        logging.info('Recarregando elementos')
        print('Recarregando elementos')
        # #####################################################

        try:
            time.sleep(2)
            # #####################################################
            # Selecao do perfil
            # #####################################################
            try:
                select = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Analista Judiciário")]'))).click() # Teste - TJCE - Acopiara - Corregedoria de Presídios
                # Contabiliza dados

                logging.info('Clicando no perfil Analista Judiciário')
            except Exception as e:
                logging.info('Nao foi possivel selecionar o perfil')
                logging.info('Continuando . . .')

            # #####################################################
            # Selecao da vara
            vara = 'TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Semiaberto e Fechado)'
            try:
                select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@title="' + vara + '"]'))).click()
                logging.info('Selecionando a vara')
                print('Selecionando a vara')

            except Exception as e:
                logging.info(repr(e))
                print(repr(e))
                logging.info('Nao foi possivel localizar a vara')
                logging.info('Finalizando robo')
                return self.listProcessos
            # #####################################################
            time.sleep(2)

            # Abre menu e filtra processos
            driver = self.ExecuteFiltroProcesso(driver, logging, metodos,)

            try:
                selectResult = driver.find_elements(By.XPATH, '//td[contains(text(), "Nenhum registro encontrado")]')
                if selectResult:
                    logging.info('Nenhum registro encontrado em TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Semiaberto e Fechado)')
                    logging.info('Interropendo execucao . . .')
                    print('Nenhum registro encontrado em TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Semiaberto e Fechado)')
                    print('Interropendo execucao . . .')

                    vara = "TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)"

                    logging.info('Alterando para vara: TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')
                    print('Alterando para vara: TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')

                    # Altera para proxima vara
                    driver = self.ExecuteAlteraVara(driver, logging, metodos, vara,)

                    # Abre menu e filtra processos
                    driver = self.ExecuteFiltroProcesso(driver, logging, metodos, )

                    selectResult = driver.find_elements(By.XPATH,
                                                        '//td[contains(text(), "Nenhum registro encontrado")]')
                    if selectResult:
                        logging.info(
                            'Nenhum registro encontrado em TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')
                        logging.info('Interropendo execucao . . .')
                        print(
                            'Nenhum registro encontrado em TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')
                        print('Interropendo execucao . . .')

                        logging.info('Sem registros para execucao')
                        print('Sem registros para execucao')

                        return self.listProcessos

            except Exception as e:
                logging.info(repr(e))
                logging.info('Ocorreu um erro ao alterar a vara - Registros')
                print(repr(e))
                return self.listProcessos

            # Localizando processos na primeira vara, sao executados
            # Executa etapa Minuta Expressa para todos os processos
            self.ExecuteProcesso(driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui)

            # #####################################################
            # #####################################################
            # Ao finalizar a primeira vara, chamado a segunda vara para execucao
            vara = "TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)"

            logging.info('Alterando para vara: TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')
            print('Alterando para vara: TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Aberto)')

            # Abre menu e filtra processos
            driver = self.ExecuteAlteraVara(driver, logging, metodos, vara, )

            # Abre menu e filtra processos
            driver = self.ExecuteFiltroProcesso(driver, logging, metodos, )

            # Executa etapa Minuta Expressa para todos os processos
            self.ExecuteProcesso(driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui)

        except Exception as e:
            dataBaseModel['qtd_erros_robo'] = 1
            logging.info('---------------------------')
            logging.info('Atividade Erro:')
            logging.info(dataBaseModel)
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))

        # Alimenta total encaminhado
        self.listProcessos.append(self.countEncaminhados)

        ###################################
        # Calculo do tempo de execucao
        ###################################
        # Registra horario que finalizou a tarefa
        fim = time.time()
        timeTotal = fim - inicioTime
        timeTotal = float('{:.2f}'.format(timeTotal))
        if timeTotal <= 60:
            logging.info('Tempo de execucao da atividade: ' + str(timeTotal) + ' segundos')
            self.listProcessos.append(str(timeTotal) + ' segundos')
        else:
            logging.info('Tempo de execucao da atividade: ' + str(timeTotal // 60) + ' minutos')
            self.listProcessos.append(str(timeTotal // 60) + ' minutos')
        logging.info('---------------------------')
        # Alimenta total de nao encontrado
        self.listProcessos.append(len(self.listProcessos[2]))
        logging.info('---------------------------')
        driver.switch_to.default_content()
        # Registra base
        dataBaseModel['qtd_processos'] = str(len(self.listProcessos[0]))
        dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
        dataBaseModel['tempo_execucao_sec'] = str(timeTotal)
        logging.info('Total de Processos no término da execução: ' + str(len(self.listProcessos[0])))
        return self.listProcessos