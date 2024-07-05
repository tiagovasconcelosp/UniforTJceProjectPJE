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
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Print import Print

class TaskIncidentesCitacao_SEEU_020:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], 0, ] # Adicionado uma nova posicao de lista para somar total de processos
    countEncaminhados = 0
    
    def __init__(self, driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                 inicioTime, url, dataForm, xml, log_unificado):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], 0, ] # Adicionado uma nova posicao de lista para somar total de processos
        self.countEncaminhados = 0
        self.modelo = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='incidentesVencerCitacao')
        self.Execute(driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel,
                     inicioTime, url, dataForm, log_unificado)

    def fecharAba(self, driver, logging, main_window_handle):
        # ##################################################### - ATT
        # Fechando nova aba
        try:
            try:
                driver.close()
            except:
                driver.quit()
            driver.switch_to.window(main_window_handle)
            logging.info('Fechando nova aba')
            time.sleep(1)
            # Recarrega elementos
            driver.switch_to.default_content()
            logging.info('Recarrega elementos - Fecha Aba')
            time.sleep(1)
            # #####################################################
            logging.info('Localizando os iframes - Fecha Aba')
            # Localiza frame para o proximo processo
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'mainFrame')))
            # alternar para o iframe selecionado
            driver.switch_to.frame(iframe)
            logging.info('Recarregando elementos - Fecha Aba - mainFrame')
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'userMainFrame')))
            driver.switch_to.frame(iframe)
            logging.info('Recarregando elementos - Fecha Aba - userMainFrame')
            # #####################################################
        except Exception as e:
            logging.info(repr(e))
            logging.info('Erro ao fechar aba')
            print('Erro ao fechar aba')
    def get_download_path(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        return os.path.join(os.path.expanduser('~'), 'downloads')
    def identifica_ultimo_crdownload(self, folder_path, timestamp, logging):
        file_type = '\*crdownload'  # se nao quiser filtrar por extenção deixe apenas *
        repete = True
        while repete:
            files = glob.glob(folder_path + file_type)
            max_file = max(files, key=os.path.getctime)
            ti_c = os.path.getctime(max_file)
            if ti_c > timestamp:
                return max_file
            else:
                self.mensagem(logging, "Aguardando o download do assinador")
                time.sleep(1)
    def renomear_arquivo(self, crdownload):
        path_jnlp = crdownload.split("Não confirmado")[0]
        data_arq = time.localtime()
        jnlp = "assinador-" + str(data_arq.tm_mday) \
     \
               + "-" + str(data_arq.tm_mon) \
     \
               + "-" + str(data_arq.tm_year) \
     \
               + "_" + str(data_arq.tm_hour) \
     \
               + "-" + str(data_arq.tm_min) + ".jnlp"
        path_jnlp = f"{path_jnlp}" + jnlp
        os.rename(f"{crdownload}", path_jnlp)
        return path_jnlp
    def executando_assinador(self, path_jnlp):
        if " " in path_jnlp:
            partes = path_jnlp.split("\\")
            path_jnlp = ""
            for parte in partes:
                if " " in parte:
                    parte = '"' + parte + '"'
                path_jnlp = os.path.join(path_jnlp, parte)
        path_jnlp = path_jnlp.replace(":", ":\\")
        os.system('start ' + path_jnlp)
    def ExecuteProgressaoAberto(self, driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui, log_unificado):
        return self.ExecuteProcesso(driver, logging, metodos, 'Progressão para Aberto', caminhoImagesPrint, caminhoImagesGui, log_unificado)
    def ExecuteProcesso(self, driver, logging, metodos, tipoIncidente, caminhoImagesPrint, caminhoImagesGui, log_unificado):
        try:
            selectResult = driver.find_elements(By.XPATH, '//td[contains(text(), "Nenhum registro encontrado")]')
            if selectResult:
                logging.info('Nenhum registro encontrado em ' + str(tipoIncidente))
                logging.info('Interropendo execucao de ' + str(tipoIncidente))
                return self.listProcessos
        except Exception as e:
            logging.info(repr(e))
            logging.info('Ocorreu um erro na tela de Pendencias de Incidentes - Registros')
            print(repr(e))
            return self.listProcessos
        try:
            # Verifica se é a primeira vez que está executando
            if self.countEncaminhados == 0:
                time.sleep(5)
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
            selectResult = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr")
            for x in range(len(selectResult)):

                # Captura numero do processo
                try:
                    numeroProcesso = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(
                        x + 1) + "]/td[4]/a[1]/em")[0].text
                except:
                    logging.info('Falha ao localizar o numero do processo')
                    continue

                # Valida se o processo possui reu preso
                try:
                    select = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(
                        x + 1) + "]/td[4]/span[@class='class_flag_REU_PRESO']/img")[0].get_attribute('title')

                    logging.info('Processo ' + str(numeroProcesso) + ' possui reu preso')
                    continue

                except:
                    logging.info('Processo ' + str(numeroProcesso) + ' nao possui reu preso')
                    print('Processo ' + str(numeroProcesso) + ' nao possui reu preso')


                logging.info('Abrindo processo: ' + numeroProcesso)
                print('Abrindo processo: ' + numeroProcesso)
                log_unificado.adicionar_processo(str(numeroProcesso))
                # Alimentando resultando
                self.listProcessos[0].append(str(numeroProcesso))
                self.listProcessos[1].append(1) # Valor 1 para nao concluido
                try:
                    new_tab_link = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(x + 1) + "]/td[4]/a[1]")[0]
                except:
                    logging.info('Falha ao localizar elemento para nova aba')
                    continue
                try:
                    # Abre processo em nova aba
                    actions = ActionChains(driver)
                    actions.key_down(Keys.CONTROL).click(new_tab_link).key_up(Keys.CONTROL).perform()
                    logging.info('Abrindo nova aba')
                    time.sleep(1)
                    # Localiza a nova aba aberta
                    driver = metodos.buscar_nova_aba(driver, logging)
                    main_window_handle = driver[1]
                    driver = driver[0]
                    time.sleep(3)
                    # Recarrega elementos
                    driver.switch_to.default_content()
                except Exception as e:
                    logging.info('Nao foi possivel abrir nova aba')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                # Captura data
                logging.info('Capturando data')
                try:
                    data = driver.find_elements(By.CSS_SELECTOR,
                                                "fieldset#quadroPendencias em")
                    data = data[0].text
                    logging.info('Data Localizada: ' + data)
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel capturar a data')
                    logging.info('Tentando novamente . . .')
                    try:
                        data = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,  "fieldset#quadroPendencias em")))
                        data = driver.find_elements(By.CSS_SELECTOR,
                                                    "fieldset#quadroPendencias em")
                        for value in data:
                            data = value.text
                        logging.info('Data Localizada: ' + data)
                    except Exception as e:
                        logging.info('Nao foi possivel capturar a data novamente - 2x')
                        logging.info('Registrando print')
                        # data = '01/01/2000'
                        image = Print(driver, caminhoImagesPrint)
                        # Fechando nova aba
                        self.fecharAba(driver, logging, main_window_handle)
                        continue
                # Clica em Incidentes Pendentes
                select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="tabItemprefix9"]')))
                select = metodos.get_element(driver,
                                             '//*[@id="tabItemprefix9"]').click()
                logging.info('Clicando em Incidentes Pendentes')

                time.sleep(1)
                # Clica em Adicionar
                select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="addButton"]'))).click()
                logging.info('Clicando em Adicionar')

                # #####################################################
                # Localiza frame
                # Recarrega elementos
                driver.switch_to.default_content()
                # Localiza frame para o proximo processo
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//iframe')))
                driver.switch_to.frame(iframe)
                logging.info('Novo iframe localizado')
                # #####################################################
                # Define formulario
                text = 'FIXAÇÃO/ALTERAÇÃO DE REGIME'

                select = metodos.get_element(driver,
                                             '//td[contains(text(), "' + text + '")]//ancestor::tr/td[1]/input').click()
                logging.info('Selecionando fluxo: ' + text)

                # #####################################################
                # Clica em novo incidente
                try:
                    select = metodos.get_element(driver,
                                                '//*[@id="addButton"]').click()
                    logging.info('Clicando em Novo Incidente')

                    # Preenche o formulário
                    # Seleciona novo regime
                    select = Select(driver.find_element(By.XPATH, '//*[@id="codTipoRegimeNovo"]'))
                    select.select_by_visible_text('Aberto')
                    logging.info('Selecionando regime: Aberto')
                    print('Selecionando regime: Aberto')
                    # Insere data
                    # ATUALIZAR PROCESSO PARA PEGAR DATA CORRETA
                    metodos.get_element(driver,
                                        '//*[@id="dataInicio"]').send_keys(str(data))
                    logging.info('Insere data: ' + str(data))
                    print('Insere data: ' + str(data))
                    # Seleciona motivo
                    select = Select(driver.find_element(By.XPATH, '//*[@id="codMotivo"]'))
                    select.select_by_visible_text('Progressão de Regime')
                    logging.info('Selecionando motivo: Progressao de Regime')
                    print('Selecionando motivo: Progressao de Regime')
                    # Clica em salvar
                    metodos.get_element(driver,
                                        '//*[@id="saveButton"]').click()
                    logging.info('Clicando em salvar')
                    print('Clicando em salvar')
                    log_unificado.atualizar_etapa_processo(
                        processo=str(numeroProcesso),
                        etapa="ADICIONAR INCIDENTE",
                        atualizacao="Realizado",
                    )

                    time.sleep(2)
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu um erro na etapa de adicionar incidente')
                    log_unificado.enviar_erro(
                        num_processo=str(numeroProcesso),
                        passo_executado="ADICIONAR INCIDENTE",
                        mensagem=repr(e),
                    )
                    return self.listProcessos

                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarrega elementos - 01')
                print('Recarrega elementos - 01')
                
                try:
                    try:
                        # Clica em juntar documentos
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@id="movimentarButton"]'))).click()
                        logging.info('Clicando em juntar documentos')

                    except Exception as e:
                        logging.info('Nao foi possivel clicar em juntar documentos')
                        logging.info('Registrando print')
                        image = Print(driver, caminhoImagesPrint)
                        # Fechando nova aba
                        self.fecharAba(driver, logging, main_window_handle)
                        continue

                    # #####################################################
                    # #####################################################
                    # #####################################################
                    # #####################################################
                    # Filtra documento
                    # Clica no icone da lupa
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[@title="Seleção de Tipo de Documento"]'))).click()
                    logging.info('Clica no icone da lupa')
                    time.sleep(1)
                    # #####################################################
                    # Localiza frame
                    # Recarrega elementos
                    driver.switch_to.default_content()
                    # Localiza frame para o proximo processo
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))
                    driver.switch_to.frame(iframe)
                    logging.info('Novo iframe localizado')

                    # Realiza a busca
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="descricaoPesquisa"]'))).send_keys(self.modelo['modeloBusca'])

                    time.sleep(1)
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="searchButton"]'))).click()
                    logging.info('Clica em buscar')
                    time.sleep(1)
                    # #####################################################
                    # Localiza frame
                    # Recarrega elementos
                    driver.switch_to.default_content()
                    # Localiza frame para o proximo processo
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))
                    driver.switch_to.frame(iframe)
                    logging.info('Novo iframe localizado')
                    # #####################################################
                    # Seleciona a busca
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//input[@name="idTipoDocumentoSelecionado"]'))).click()
                    logging.info('Seleciona opcao')
                    time.sleep(2)
                    try:
                        element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '#selectButton')))
                        actions = ActionChains(driver)
                        actions.click(element).perform()
                        logging.info('Clica em confirmar')
                    except Exception as e:
                        logging.info('Nao foi possivel clicar em confirmar')
                        logging.info('Registrando print')
                        # data = '01/01/2000'
                        image = Print(driver, caminhoImagesPrint)
                        # Fechando nova aba
                        self.fecharAba(driver, logging, main_window_handle)
                        continue

                    time.sleep(2)
                    driver.switch_to.default_content()
                    time.sleep(1)
                    # Clica em adicionar
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="editButton"]')))
                    actions = ActionChains(driver)
                    actions.click(element).perform()
                    logging.info('Adicionar documentos')

                    time.sleep(2)
                    # #####################################################
                    # Localiza frame
                    # Recarrega elementos
                    driver.switch_to.default_content()
                    # Localiza frame para o proximo processo
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))
                    driver.switch_to.frame(iframe)
                    logging.info('Novo iframe localizado')
                    # Seleciona documento
                    try:
                        select = Select(driver.find_element(By.XPATH, '//*[@id="codDescricao"]'))

                        # select.select_by_visible_text('Ato Ordinatório')
                        select.select_by_visible_text(self.modelo['modelo'])

                        logging.info('Selecionando tipo arquivo')
                    except Exception as e:
                        logging.info(repr(e))
                        logging.info('Nao foi possivel localizar o modelo')
                        logging.info('Registrando print')
                        image = Print(driver, caminhoImagesPrint)
                        # Fechando nova aba
                        self.fecharAba(driver, logging, main_window_handle)
                        continue
                    time.sleep(2)
                    try:
                        select = Select(driver.find_element(By.CSS_SELECTOR, '#codModelo'))
                        # select.select_by_visible_text('Documento em Branco (com cabeçalho)')

                        # select.select_by_visible_text('3ª VEP ROBO RELATORIO DE MONITORAMENTO')
                        select.select_by_visible_text(self.modelo['modeloAssinar'])

                        logging.info('Selecionando tipo modelo')
                        time.sleep(2)
                    except Exception as e:
                        logging.info(repr(e))
                        logging.info('Nao foi possivel selecionar o modelo')
                        logging.info('Registrando print')
                        image = Print(driver, caminhoImagesPrint)
                        # Fechando nova aba
                        self.fecharAba(driver, logging, main_window_handle)
                        continue
                    # #####################################################
                    # DEFINIR MODELO DOCUMENTO A SER SELECIONADO - SOLICITAR PADRAO DE DOCUMENTO - ATT
                    # Clica em digitar texto
                    select = driver.find_element(By.CSS_SELECTOR, '#digitarButton')
                    driver.execute_script("javascript:enviar(1);", select)
                    logging.info('Clica em digitar texto')
                    time.sleep(2)
                    # Clica em continuar
                    select = metodos.get_element(driver,
                                                '//*[@id="submitButton"]').click()
                    logging.info('Clica em continuar')

                    time.sleep(2)
                    # Clica em concluir
                    select = metodos.get_element(driver,
                                                '//*[@id="editButton"]').click()
                    logging.info('Clica em concluir')
                    time.sleep(2)
                    log_unificado.atualizar_etapa_processo(
                        processo=str(numeroProcesso),
                        etapa="JUNTAR DOCUMENTOS",
                        atualizacao="Realizado",
                    )
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Ocorreu um erro na etapa de juntar documentos')
                    log_unificado.enviar_erro(
                        num_processo=str(numeroProcesso),
                        passo_executado="JUNTAR DOCUMENTOS",
                        mensagem=repr(e),
                    )
                    return self.listProcessos
                # #####################################################
                # #####################################################
                # #####################################################
                # Clica em assinar
                select = metodos.get_element(driver,
                                             '//*[@id="assinarButton"]').click()
                logging.info('Clica em assinar')
    
                # #####################################################
                # RESOLVER PROCESSO DE ASSINATURA - ATT
                logging.info('Arquivo baixado')
                time.sleep(3)
                # V1
                # #####################################################
                # #####################################################
                # Tratando download
                # #####################################################
                # #####################################################
                # Capturando caminho da pasta download
                folder_path = self.get_download_path()
                logging.info('Capturando caminho da pasta download')
                # Identificando ultimo download
                crdownload = self.identifica_ultimo_crdownload(folder_path, 2, logging)
                logging.info('Identificando ultimo download')
                # Renomeando arquivo
                path_jnlp = self.renomear_arquivo(crdownload)
                logging.info('Renomeando arquivo')
                # Executando assinador
                self.executando_assinador(path_jnlp)
                logging.info('Executando assinador')
                time.sleep(7)

                # Executa java
                image = pyautogui.locateOnScreen(caminhoImagesGui + 'executa-java.png')
                if image:
                    logging.info('Botao java localizado - primeira tentativa')
                    pyautogui.press('enter')
                else:
                    time.sleep(3)
                    image = pyautogui.locateOnScreen(caminhoImagesGui + 'executa-java.png')
                    if image:
                        logging.info('Botao java localizado - segunda tentativa')
                        pyautogui.press('enter')
                    else:

                        time.sleep(5)
                        image = pyautogui.locateOnScreen(caminhoImagesGui + 'executa-java.png')
                        if image:
                            logging.info('Botao java localizado - terceira tentativa')
                            pyautogui.press('enter')
                        else:
                            time.sleep(10)
                            image = pyautogui.locateOnScreen(caminhoImagesGui + 'executa-java.png')
                            if image:
                                logging.info('Botao java localizado - quarta tentativa')
                                pyautogui.press('enter')
                            else:
                                time.sleep(5)
                                pyautogui.press('enter')


                time.sleep(8)

                pyautogui.press('enter')
                logging.info('Teclando Enter')
                logging.info('Confirma assinatura')
                time.sleep(1)
                image = pyautogui.locateOnScreen(caminhoImagesGui + 'erro-certificado-1.png')
                if image:
                    logging.info('Ocorreu um erro ao assinar processo')
                    logging.info('Nao foi possivel concluir')
                    logging.info('Selecionado opcao errada')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                image = pyautogui.locateOnScreen(caminhoImagesGui + 'erro-certificado-2.png')
                if image:
                    logging.info('Ocorreu um erro ao assinar processo')
                    logging.info('Nao foi possivel concluir')
                    logging.info('Certificado nao localizado')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                time.sleep(2)
                image = pyautogui.locateOnScreen(caminhoImagesGui + 'Ok.png')
                if image:
                    pyautogui.press('tab')
                    logging.info('Teclando Tab')
                    time.sleep(1)
                    pyautogui.press('enter')
                    logging.info('Teclando Enter')
                    logging.info('Confirma Certificado')
                time.sleep(5)
                logging.info('Processo assinado com sucesso')
                # #####################################################
                # #####################################################
                # Tratando download
                # #####################################################
                # #####################################################
                # #####################################################
                # #####################################################
                # #####################################################
                # #####################################################
                # Localiza frame
                # Recarrega elementos
                try:
                    driver.switch_to.default_content()
                    time.sleep(1)
                    # Localiza frame para o proximo processo
                    iframe = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//iframe')))
                    driver.switch_to.frame(iframe)
                    logging.info('Novo iframe localizado')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel elemento iframe apos conclusao')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # Clica em confirmar inclusao
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="closeButton"]')))#.click()
                    actions = ActionChains(driver)
                    actions.click(element).perform()
                    logging.info('Clica em confirmar inclusao')

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em confirmar inclusao')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                # #####################################################
                # #####################################################
                time.sleep(3)
                # #####################################################
                # Localiza frame
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarregando elementos')
                # #####################################################
                # Clica em concluir movimento
                try:
                    element = WebDriverWait(driver, 10).until(
                        # EC.presence_of_element_located((By.XPATH, '//*[@id="editButton"]')))#.click()
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'div#content table.buttonBar input[value="Concluir Movimento"i]')))  # .click()
                    actions = ActionChains(driver)
                    actions.click(element).perform()
                    logging.info('Clica em concluir movimento')
                    log_unificado.atualizar_etapa_processo(
                        processo=str(numeroProcesso),
                        etapa="ASSINAR DOCUMENTO",
                        atualizacao="Realizado",
                    )

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em concluir movimento')
                    logging.info('Registrando print')
                    log_unificado.enviar_erro(
                        num_processo = str(numeroProcesso),
                        passo_executado = "ASSINAR DOCUMENTO",
                        mensagem = repr(e)
                    )
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                time.sleep(1)
                # Recarregando elementos
                driver.switch_to.default_content()
                logging.info('Recarregando elementos')
                # #####################################################
                # Clica em realizar remessa
                try:
                    select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Realizar Remessa")]'))).click()
                    logging.info('Clica em Realizar Remessa')
                    log_unificado.atualizar_etapa_processo(
                        processo=str(numeroProcesso),
                        etapa="REALIZAR REMESSA",
                        atualizacao="Realizado",
                    )

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em Realizar Remessa')
                    logging.info('Registrando print')
                    log_unificado.enviar_erro(
                        num_processo = str(numeroProcesso),
                        passo_executado = "REALIZAR REMESSA",
                        mensagem = repr(e)
                    )
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                time.sleep(1)
                # #####################################################
                # Localiza frame
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarregando elementos')
                logging.info('Recarregando elementos')
                # Localiza frame para o proximo processo
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//iframe')))
                driver.switch_to.frame(iframe)
                logging.info('Novo iframe localizado')
                # #####################################################
                # Clica em outras remessas
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'table.form input[value="entidadeRemessa"i]'))).click()
                    logging.info('Clica em Outras Remessas')

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em Outras Remessas')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue

                # #####################################################
                # #####################################################
                # Clica em destino
                try:
                    select = Select(driver.find_element(By.CSS_SELECTOR, '#codEntidadeRemessa'))
                    select.select_by_visible_text('TJCE - SAP - 0029 - Central de Monitoramento Eletrônico de Pessoas - CMEP (online)')
                    logging.info('Clica em destino')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em destino')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                # #####################################################

                # #####################################################
                # #####################################################
                # Clica em finalidade
                try:
                    select = Select(driver.find_element(By.CSS_SELECTOR, '#codFinalidadeRemessaEntidade'))
                    select.select_by_visible_text('REQUISIÇÃO AO DIRETOR DA UNIDADE')
                    logging.info('Clica em manisfetacao')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em manisfetacao')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue

                # #####################################################
                # #####################################################
                # Clica em prazo
                try:
                    select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'input#prazoEntidadeRemessa')))
                    select.clear()

                    # select.send_keys('5')
                    select.send_keys(self.modelo['dias'])

                    logging.info('Clica em prazo')
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em prazo')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue

                # #####################################################
                # #####################################################
                # Clica em enviar remessa - salvar
                try:
                    select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'input#remessaButton'))).click()
                    logging.info('Clica em enviar remessa')
                    

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em enviar remessa')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                # Recarrega elementos
                driver.switch_to.default_content()
                logging.info('Recarregando elementos')
                # #####################################################
                # Clica em voltar para o processo
                try:
                    select = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'input#backButton'))).click()
                    logging.info('Clica em voltar para o processo')

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar em voltar para o processo')
                    logging.info('Registrando print')
                    image = Print(driver, caminhoImagesPrint)
                    # Fechando nova aba
                    self.fecharAba(driver, logging, main_window_handle)
                    continue
                # #####################################################
                # Total finalizado
                self.countEncaminhados += 1
                # Altera o status para finalizado
                # Deleta o ultimo registro
                del(self.listProcessos[1][-1])
                # Finaliza com status de sucesso
                self.listProcessos[1].append(0)
                time.sleep(1)
                self.fecharAba(driver, logging, main_window_handle)
                # Recarrega elementos
                driver.switch_to.default_content()
                time.sleep(1)
                # #####################################################
                logging.info('Localizando os iframes para retornar busca')
                # Localiza frame para o proximo processo
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'mainFrame')))
                # alternar para o iframe selecionado
                driver.switch_to.frame(iframe)
                logging.info('Recarregando elementos - Final For - mainFrame')
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, 'userMainFrame')))
                driver.switch_to.frame(iframe)
                logging.info('Recarregando elementos - Final For - userMainFrame')
                # #####################################################
            # #####################################################
            # Clica em pesquisar - para carregar novos processos
            try:
                element = driver.find_elements(By.XPATH,
                                             '//*[@id="searchButton"]')#.click()
                actions = ActionChains(driver)
                actions.click(element).perform()
                logging.info('Clica em Pesquisar')

                time.sleep(4)
            except Exception as e:
                logging.info(repr(e))
                logging.info('Ocorreu um erro ao clicar em pesquisar')
                return self.listProcessos
            #####################################################

            # #####################################################
            # Validando se ainda existem processos com reu para finalizacao do robo
            selectResult = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr")
            totaldeProcessos = len(selectResult)
            contadorReu = 0
            for x in range(len(selectResult)):
                # Valida se o processo nao possui reu preso
                try:
                    select = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr[" + str(
                        x + 1) + "]/td[4]/span[@class='class_flag_REU_PRESO']/img")[0].get_attribute('title')

                    contadorReu = 0
                    logging.info('Validando, contagem de processos com reu . . .')
                    print('Validando, contagem de processos com reu . . .')
                    continue

                except:
                    contadorReu += 1
                    logging.info('Finalizando validacao, contagem de processos com reu . . .')
                    print('Finalizando validacao, contagem de processos com reu . . .')

            if contadorReu == totaldeProcessos:
                logging.info('Finalizando execucao do robo, sem processos com reu . . .')
                print('Finalizando execucao do robo, sem processos com reu . . .')
                return self.listProcessos

            # Verifica e executa novamente a fila de processos
            try:
                selectResult = driver.find_elements(By.XPATH, "//table[@class='resultTable']/tbody/tr")
                logging.info('Checando se existe mais processos . . .')
                if len(selectResult) > 0:
                    logging.info('Foram encontrados mais processos para realizar: ' + str(len(selectResult)))
                    self.ExecuteProcesso(driver, logging, metodos, tipoIncidente, caminhoImagesPrint, caminhoImagesGui, log_unificado)
                logging.info('Nao tem mais processos, finalizando . . .')
            except Exception as e:
                logging.info(repr(e))
                logging.info('Ocorreu um erro na etapa de executar novamente a fila')
        except Exception as e:
            logging.info(repr(e))
            logging.info(self.listProcessos)
            logging.info('Ocorreu um erro na tela de incidentes')
        logging.info('Interropendo execucao de ' + str(tipoIncidente))
        logging.info('Todos os processos foram assinados')
        return self.listProcessos

    def Execute(self, driver, caminhoImagesPrint, caminhoImagesGui, logging, atividade, dataBaseModel, inicioTime, url, dataForm, log_unificado):
        log_unificado.criar_arquivo_executados(
            ["ADICIONAR INCIDENTE", "JUNTAR DOCUMENTO", "ASSINAR DOCUMENTO", "REALIZAR REMESSA"]
        )
        metodos = Metodos(url)
        driver.get(url)
        logging.info('##############################')
        logging.info('Robô iniciado')
        logging.info('Acesso da Url: ' + url)
        time.sleep(5)
        autenticacao = Auth()
        autenticacao.LoginSeeu(driver, logging, dataForm, url)
        # Usado para aguardar validacao do recaptcha
        # logging.info('Aguardando resolucao de recaptcha - 120s')
        logging.info('Aguardando resolucao de recaptcha - 10s')
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
        # #####################################################

        try:
            time.sleep(2)
            # autenticacao.LoginSeeu(driver, logging, dataform, url)
            # #####################################################
            # Selecao do perfil
            # #####################################################
            try:
                select = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "Analista Judiciário")]'))).click() # Teste - TJCE - Acopiara - Corregedoria de Presídios
                # Contabiliza dados
                arrayVarRefDados['qtd_clicks'] += 1
                logging.info('Clicando no perfil Analista Judiciário')
            except Exception as e:
                logging.info('Nao foi possivel selecionar o perfil')
                logging.info('Continuando . . .')
            # #####################################################
            # Selecao da vara
            vara = 'TJCE - Fortaleza - 3ª Vara de Execução Penal (Regime Semiaberto e Fechado)'
            # TESTE
            # vara = 'TJCE - Fortaleza - Auditoria Militar do Estado do Ceará (Regime Aberto)'
            try:
                select = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@title="' + vara + '"]'))).click()
                logging.info('Selecionando a vara')

            except Exception as e:
                logging.info(repr(e))
                logging.info('Nao foi possivel localizar a vara')
                logging.info('Finalizando robo')
                return self.listProcessos
            # #####################################################
            time.sleep(2)
            # #####################################################
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'userMainFrame')))
            driver.switch_to.frame(iframe)
            logging.info('Recarregando elementos')
            # #####################################################
            # #####################################################
            # Selecao de pendencias
            try:
                select = metodos.get_element(driver,
                                              '//*[@id="tabItemprefix1"]').click()
                logging.info('Clicando em pendencias')

            except Exception as e:
                logging.info(repr(e))
                logging.info('Nao foi possivel clicar aba pendencias')
                return self.listProcessos
            # #####################################################
            # #####################################################
            # Abre Selecao progressos Abertos
            try:
                select = metodos.get_element(driver,
                                                 '//h4[contains(text(), "A vencer")]//ancestor::td/table/tbody/tr[2]/td[2]/a').click()
                logging.info('Clicando em: Progressao para Aberto')

            except Exception as e:
                logging.info(repr(e))
                logging.info('Nao foi possivel clicar em: Progressao para Aberto')
                return self.listProcessos


            # Verifica registros
            try:

                # #####################################################
                # #####################################################
                # Usado para trazer processos para teste
                # Remover em produção
                # Inclui data incial

                # element = WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located(
                #         (By.ID, 'dataInicio')))
                # element.clear()
                #
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, '//*[@id="dataInicio"]'))).send_keys('01082022')
                #
                # time.sleep(1)
                #
                # metodos.get_element(driver,
                #                     '//*[@id="searchButton"]').click()

                # #####################################################


                # print('ok')
                # time.sleep(999)

                # #####################################################
                # Verifica se existem registros
                time.sleep(1)
                select = driver.find_elements(By.XPATH,
                                             "*//td[contains(text(), 'Nenhum registro encontrado')]")
                if select:
                    logging.info('Nenhum registro encontrado em Progressao para Aberto')
                    return self.listProcessos

                else:
                    self.ExecuteProgressaoAberto(driver, logging, metodos, caminhoImagesPrint, caminhoImagesGui, log_unificado)
                # #####################################################

            except Exception as e:
                logging.info(repr(e))
                logging.info('Ocorreu um erro interno na execucao')

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
            # Retorna valor caso haja algum erro durante a execucao
            # return self.listProcessos

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