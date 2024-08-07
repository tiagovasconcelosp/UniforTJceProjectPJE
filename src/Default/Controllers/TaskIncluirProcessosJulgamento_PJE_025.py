# ###################################################
# ###################################################
# ## Projeto MPCE - Unifor - Universidade de Fortaleza
# ## Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
# ## Laboratório M02
# ## Cientista-Chefe: Prof. Carlos Caminha
# ## Bolsista Desenvolvedor do Projeto:
# ## Tiago Vasconcelos
# ## Email: tiagovasconcelosp@gmail.com
# ###################################################
# ###################################################

import time

from unicodedata import normalize
from datetime import date
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select

from src.Default.Controllers.Print import Print
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Perfil import Perfil

class TaskIncluirProcessosJulgamento_PJE_025:
    listProcessos = [[], [], [], ]
    countIncluidos = 0

    def __init__(self, driver, caminhoImagesPrint, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, 
                 url, dataForm, xml, log_bi):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.Execute(driver, caminhoImagesPrint, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, 
                 url, dataForm, xml, log_bi)

    def pecorreProcessoPauta(self, driver, process, element, dayProcess, logging, caminhoImages, log_bi):

        # Localiza os processos do dia e marca
        ##########################################################
        for i in range(len(process)):
            # Usado para verificar se o processo nao foi localizado
            # count = 0

            logging.info('Procurando processo: ' + str(process[i][0]))
            # logging.info('Total de linhas: ' + str(len(element)))

            try:

                # driver.find_element(By.XPATH,
                # "//table[@id='pautaJulgamentoList']/tbody/tr/td/div/div/h6/a[contains(text(), '" + process[i][0] + "')]//ancestor::td[1]/form/center/input").click()

                driver.find_element(By.XPATH,
                                     "//a[contains(text(), '" +
                                     process[i][0] + "')]//ancestor::tr/td[1]/form/center/input").click()

                # Inclui lista de processos localizados
                self.listProcessos[0].append(str(process[i][0]))
                logging.info('Processo selecionado: ' + str(process[i][0]))

                # Processo incluido
                self.listProcessos[1].append(0)

                self.countIncluidos += 1

                # Processo localizado
                # count += 1

                # Aguarda loading do click
                # Verifica time de click
                time.sleep(4)
                log_bi.atualizar_etapa_processo(
                    processo= str(process[i][0]),
                    etapa="INCLUÍDO EM PAUTA",
                    atualizacao="Realizado",
                )
            except Exception as e:

                #############################################
                # Caso acontece de nao existir o botao marcar
                #############################################
                logging.info('Processo nao pode ser selecionado: ' + str(process[i][0]))
                logging.info(repr(e))

                # Processo nao incluido
                self.listProcessos[1].append(1)

                # Inclui lista de processos nao localizados
                self.listProcessos[2].append(str(process[i][0]))

                image = Print(driver, caminhoImages)
                logging.info('---------------------------')
                logging.info('O processo nao ser localizado na sessao. Data: ' + str(dayProcess))
                logging.info('Processo nao foi localizado: ' + str(process[i][0]))
                logging.info('---------------------------')
                log_bi.enviar_erro(
                    num_processo=str(process[i][0]),
                    passo_executado="INCLUÍDO EM PAUTA",
                    mensagem=repr(e),
                )

        logging.info('Atividade de incluir processos em "Aptos para Inclusao em Pauta" foi realizada com sucesso. Data: ' + str(dayProcess))
        logging.info('---------------------------')

        ##########################################################

    def pecorreProcessoMesa(self, driver, process, dayProcess, logging, caminhoImages, log_bi):


        # Localiza os processos do dia e marca
        ##########################################################

        for i in range(len(process)):

            try:  # Para verificar se o processo existe

                elementInput = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                elementInput.send_keys(process[i][0])

                time.sleep(2)

                try:
                    # Aguarda a busca do processo
                    elementIn = WebDriverWait(driver, 600).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.rich-sb-common-container table.rich-sb-int-decor-table tr.richfaces_suggestionEntry')))
                    driver.execute_script("arguments[0].click();", elementIn)

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar na sugestao de processo na busca.')

                time.sleep(2)

                # Clical em incluir
                elementInn = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="processoEmMesaForm:cadastrar"]')))
                elementInn.click()

                # Confirma o alerto caso exista
                # Messagem: A classe exige pauta. Deseja continuar?
                try:
                    WebDriverWait(driver, 600).until(EC.alert_is_present())

                    alert = driver.switch_to.alert
                    alert.accept()
                    logging.info('Confirmando o alerta: A classe exige pauta. Deseja continuar?')
                    logging.info('Processo: ' + str(process[i][0]))


                except Exception as e:

                    logging.info(repr(e))
                    continue

                logging.info('Processo incluido com sucesso: ' + str(process[i][0]))

                # Inclui lista de processos localizados
                self.listProcessos[0].append(str(process[i][0]))

                # Processo incluido
                self.listProcessos[1].append(0)

                #Captura novamente o elemento
                elementInput = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                # Limpa campo
                elementInput.clear()

                time.sleep(2)
                log_bi.atualizar_etapa_processo(
                    processo= str(process[i][0]),
                    etapa="INCLUÍDO EM MESA",
                    atualizacao="Realizado",
                )

            except:

                # Captura novamente o elemento
                elementInput = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                elementInput.clear()

                time.sleep(2)

                # Inclui lista de processos nao localizados
                self.listProcessos[2].append(process[i][0])

                self.qtd_erros_tentativa_processo_all += 1

                image = Print(driver, caminhoImages)
                log_bi.enviar_erro(
                    num_processo=str(process[i][0]),
                    passo_executado="INCLUÍDO EM MESA",
                    mensagem=repr(e),
                )

                logging.info('---------------------------')
                logging.info('Processo de nao ser localizado na busca "Aptos para Inclusao em Mesa". Data: ' + str(dayProcess))
                logging.info('Processo nao foi localizado: ' + str(process[i][0]))
                logging.info('Registrando print.')
                logging.info('---------------------------')

        logging.info('Atividade de incluir processos em "Aptos para Inclusao em Mesa" foi realizada com sucesso. Data: ' + str(dayProcess))
        logging.info('---------------------------')

        ##########################################################

    def processoIncluir(self, driver, process, dayProcess, logging, caminhoImages, countDef, log_bi):

        try:
            # Mapeamento dos dados da planilha
            # Numero do processo, dia, mes, ano e sessao
            dayProce = int(dayProcess[0:2])
            monthProcess = dayProcess[3:5]
            yearProcess = dayProcess[6:10]

            sessao = ''

            processVirtual = []
            processPresencial = []

            for x in range(len(process)):

                source = str(process[x][2])
                target = normalize('NFKD', source).encode('ASCII', 'ignore').decode('ASCII')

                if (str(target).upper()).strip() == (str('Virtual').upper()).strip():
                    processVirtual.append([process[x][0]])                    
                elif (str(target).upper()).strip() == (str('Presencial').upper()).strip() or (str(target).upper()).strip() == (str('Videoconferencia').upper()).strip():
                    processPresencial.append([process[x][0]])
                else:
                    logging.info('---------------------------')
                    logging.info('A coluna da sessao por um dado incorreto. O valor deve ser Virtual ou Presencial')
                    logging.info('O valor da coluna atual: ' + str(process[x][2]))
                    logging.info('Numero do processo: ' + str(process[x][0]))
                    logging.info('---------------------------')

                log_bi.adicionar_processo(processo=str([process[x][0]]))
            # Procura dia no calendario atual
            # A Aberta
            # R Realizada
            # F Finalizada
            logging.info('Buscando o dia da sessao.')
            logging.info('---------------------------')

            try:
                element = driver.find_elements(By.XPATH, "//span[@class='text-center' and ./text()='" + str(
                    dayProce) + "']//following-sibling::span[@class='ml-10' and contains(text(),'- EASP')]")[0]
            except Exception as e:
                logging.info(repr(e))
                logging.info('---------------------------')
                logging.info('Nao foi possivel abrir a sessao do dia especificado, pois a sessao nao esta como "EASP". Por favor, verificar.')
                logging.info('Ou pode ter ocorrido desde dia nao haver sessao aberta.')
                logging.info('Registrando print.')
                logging.info('---------------------------')
                image = Print(driver, caminhoImages)

                # try:
                #     driver.close()
                # except:
                #     driver.quit()

                return self.listProcessos

            # Verifica se achou o respectivo dia no calendario
            if element:

                logging.info('Dia da sessao encontrato.')
                logging.info('---------------------------')

                element.click()

                time.sleep(1)

                # Identifica se tem mais de uma sessao e qual deve entrar
                ##########################################################
                try:
                    element = driver.find_elements(By.CSS_SELECTOR, "table#sessaoRelacaoJulgamentoDt tr.rich-table-row")

                    for x in range(len(element)):

                        try:

                            if len(processPresencial) > 0 and countDef == 0:
                                # driver.find_element(By.XPATH, "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[" + str(
                                #     x + 1) + "]/td[contains(text(), 'Presencial')]//ancestor::tr[" + str(
                                #     x + 1) + "]/td[1]/a").click()

                                try:
                                    e = driver.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[contains(., 'Presencial')]")[0].text
                                    if e:
                                        driver.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a")[0].click()
                                except:
                                    driver.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a")[0].click()

                                sessao = 'Presencial'

                            elif len(processVirtual) > 0 and countDef == 1:

                                try:
                                    e = driver.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[contains(., 'Virtual')]")[0].text
                                    if e:
                                        driver.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a")[0].click()
                                except:
                                    driver.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a")[0].click()

                                sessao = 'Virtual'

                            elif len(processPresencial) > 0:
                                driver.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a")[0].click()

                                sessao = 'Presencial'

                            elif len(processVirtual) > 0:
                                driver.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a")[0].click()

                                sessao = 'Virtual'

                        except:

                            logging.info('Houve um problema a selecionar sessao correta. Por favor verificar se os dados da planilha estao corretos.')
                            logging.info('---------------------------')
                            logging.info('Presencial:')
                            logging.info(str(processPresencial))
                            logging.info('Virtual:')
                            logging.info(str(processVirtual))
                            logging.info('---------------------------')

                            # try:
                            #     driver.close()
                            # except:
                            #     driver.quit()

                            return self.listProcessos

                    driver.find_element(By.CSS_SELECTOR, "span#fecharModal").click()

                except:

                    logging.info('Entrando na sessao...')
                ##########################################################

                time.sleep(2)

                logging.info('Aguardando a nova janela ser aberta.')
                logging.info('---------------------------')

                # Localiza a nova janela aberta
                ##########################################################
                main_window_handle = None
                while not main_window_handle:
                    main_window_handle = driver.current_window_handle

                signin_window_handle = None
                while not signin_window_handle:
                    for handle in driver.window_handles:
                        if handle != main_window_handle:
                            signin_window_handle = handle
                            break
                driver.switch_to.window(signin_window_handle)
                ##########################################################

                logging.info('Nova janela encontrada.')
                logging.info('---------------------------')

                ##########################################################
                # Aguarda o carregamento da nova janela
                ##########################################################

                time.sleep(3)

                # Seleciona "Aptos para inclusão em pauta"
                ##########################################################
                pauta = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'td#form_lbl')))

                ##########################################################

                # Seleciona "Aptos para inclusão em mesa"
                ##########################################################
                mesa = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'td#processoMesaTab_lbl')))

                ##########################################################

                # Verifica se a sessao esta fechada
                ##########################################################
                try:
                    # element = driver.find_elements(By.XPATH,
                    #     "//p[@class='text-center' and contains(text(),'sessão já está fechada')]")

                    element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located(
                            (By.XPATH,
                             "//p[@class='text-center' and contains(text(),'sessão já está fechada')]")))

                    logging.info('Registrando print.')
                    image = Print(driver, caminhoImages)

                    try:
                        driver.close()
                    except:
                        driver.quit()

                    # Para sair do objeto popup
                    driver.switch_to.window(main_window_handle)

                    logging.info('Sessao deste dia esta fechada. Dia: ' + str(dayProcess))
                    logging.info('Fechando janela aberta.')

                    return self.listProcessos

                except:

                    try:

                        # Identifica o tipo da sessao
                        # element = driver.find_element(By.XPATH,
                        #                            "//span[contains(text(), 'Sessão Virtual')]")

                        element = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//span[contains(text(), 'Sessão Virtual')]")))

                        if len(processPresencial) > 0 and len(processVirtual) == 0 and sessao == '':
                            logging.info('---------------------------')
                            logging.info('Houve uma divergencia entre os dados. O(s) processo(s) abaixo nao serao '
                                         'buscados pois pertencem a tipo Presencial e a sessao aberta e do tipo Virtual.')

                            for i in range(len(processPresencial)):
                                logging.info('Processo: ' + str(processPresencial[i][0]))
                                # Inclui lista de processos nao localizados
                                self.listProcessos[2].append(str(processPresencial[i][0]))
                            logging.info(
                                'O(s) processo(s) pode(m) esta com a informacao divergente na planilha. Foi tentado realizar a'
                                ' busca do processo no menu "Aptos para inclusao em pauta", porem na planilha informa '
                                'como Presencial ou Videoconferencia')
                            logging.info('---------------------------')
                            logging.info('Registrando print.')
                            image = Print(driver, caminhoImages)

                            try:
                                driver.close()
                            except:
                                driver.quit()

                            # Para sair do objeto popup
                            driver.switch_to.window(main_window_handle)

                            return self.listProcessos

                        pauta.click()

                        ##########################################################
                        # Inicia a busca

                        logging.info('Selecionado menu: Aptos para inclusao em pauta.')
                        logging.info('---------------------------')

                        logging.info('Buscando processos para serem incluidos...')
                        logging.info('---------------------------')
                        logging.info(processVirtual)
                        logging.info('---------------------------')

                        time.sleep(10)

                        # Localiza processos a serem selecionados e seleciona cada um deles
                        # WebDrive usado somente para o aguardo do carregamento da pagina
                        ##########################################################

                        try:
                            element = WebDriverWait(driver, 3600).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR,
                                     'table#pautaJulgamentoList tbody tr')))
                        except:

                            logging.info('Nao existe processos para serem incluidos nessa sessao e nessa data. Data: ' + str(dayProcess))
                            logging.info('Os processos abaixos nao poderam ser localizados. A lista esta vazia.')
                            logging.info('Registrando print.')
                            image = Print(driver, caminhoImages)

                            for i in range(len(processVirtual)):
                                logging.info('Processo: ' + str(processVirtual[i][0]))
                                # Inclui lista de processos nao localizados
                                self.listProcessos[2].append(str(processVirtual[i][0]))

                            logging.info('Fechando a janela da sessao.')
                            logging.info('Finalizando a busca na sessao do dia: ' + str(dayProcess))
                            logging.info('---------------------------')

                            try:
                                driver.close()
                            except:
                                driver.quit()

                            # Para sair do objeto popup
                            driver.switch_to.window(main_window_handle)

                            return self.listProcessos

                        # Localiza tabela com listagem dos processos
                        element = driver.find_elements(By.CSS_SELECTOR, 
                            "table#pautaJulgamentoList tbody tr.rich-table-row")
                        ##########################################################

                        countDef += 1

                        self.pecorreProcessoPauta(driver, processVirtual, element, dayProcess, logging, caminhoImages, log_bi)

                        ######################################################################################
                        # Alteracao Solicitada Karyna
                        #####################################################################################
                        logging.info('Processos selecionados...')
                        logging.info('---------------------------')

                        # Clica em incluir processos
                        # Finaliza atividade
                        ##########################################################
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 #'form#j_id1620 input')))
                                 'table#richTabRelacaoJulgamento form input[value="Incluir"i]')))
                        element.click()
                        ##########################################################

                        logging.info('Incluindo os processos...')
                        logging.info('---------------------------')

                        ##########################################################
                        # Demora 11s a inclusao
                        ##########################################################
                        ##########################################################
                        ##########################################################
                        time.sleep(20)

                        # Fecha popup
                        try:
                            driver.close()
                        except:
                            driver.quit()

                        # Para sair do objeto popup
                        driver.switch_to.window(main_window_handle)  # or driver.switch_to_default_content()

                        time.sleep(1)

                        # Para verificar caso haja mais de uma sessao
                        if len(processPresencial) > 0 and len(processVirtual) > 0 and countDef == 1:
                            self.processoIncluir(driver, process, dayProcess, logging, caminhoImages, countDef, log_bi)

                        logging.info('Fechando a janela da sessao.')
                        logging.info('---------------------------')
                        
                        return self.listProcessos

                    except:

                        # Identifica o tipo da sessao
                        # element = driver.find_element(By.XPATH,
                        #                                "//span[contains(text(), 'Presencial')]")

                        element = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//span[contains(text(), 'Presencial')]")))

                        if len(processVirtual) > 0 and len(processPresencial) == 0 and sessao == '':
                            logging.info('---------------------------')
                            logging.info('Houve uma divergencia entre os dados. O(s) processo(s) abaixo nao serao '
                                         'buscados pois pertencem a tipo Virtual e a sessao aberta e do tipo Presencial.')

                            for i in range(len(processVirtual)):
                                logging.info('Processo: ' + str(processVirtual[i][0]))
                                # Inclui lista de processos nao localizados
                                self.listProcessos[2].append(str(processVirtual[i][0]))
                            logging.info(
                                'O(s) processo(s) pode(m) esta com a informacao divergente na planilha. Foi tentado realizar a'
                                ' busca do processo no menu "Aptos para inclusao em mesa", porem na planilha informa '
                                'como Virtual')
                            logging.info('---------------------------')
                            logging.info('Registrando print.')
                            image = Print(driver, caminhoImages)

                            logging.info('Fechando a janela da sessao.')
                            logging.info('Finalizando a busca na sessao do dia: ' + str(dayProcess))
                            logging.info('---------------------------')

                            try:
                                driver.close()
                            except:
                                driver.quit()

                            # Para sair do objeto popup
                            driver.switch_to.window(main_window_handle)

                            return self.listProcessos

                        mesa.click()

                        time.sleep(5)

                        ##########################################################
                        # Para aguardar o carregamento total da pagina
                        element = WebDriverWait(driver, 3600).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                        countDef += 1

                        self.pecorreProcessoMesa(driver, processPresencial, dayProcess, logging, caminhoImages, log_bi)

                        # Fecha popup
                        try:
                            driver.close()
                        except:
                            driver.quit()

                        # Para sair do objeto popup
                        driver.switch_to.window(main_window_handle)

                        time.sleep(1)

                        # Para verificar caso haja mais de uma sessao
                        if len(processPresencial) > 0 and len(processVirtual) > 0 and countDef == 1:
                            self.processoIncluir(driver, process, dayProcess, logging, caminhoImages, countDef, log_bi)

                        logging.info('Fechando a janela da sessao.')
                        logging.info('---------------------------')

                        return self.listProcessos


        except Exception as e:

            image = Print(driver, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.exception('Dia da sessao nao encontrado.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()

            # Fecha popup
            try:
                driver.close()
            except:
                driver.quit()

            # Para sair do objeto popup
            driver.switch_to.window(main_window_handle)

            time.sleep(1)

            return self.listProcessos

    def localizarDataCalendarioIncluir(self, driver, process, dayProcess, logging, caminhoImages, log_bi):

        try:
            # Mapeamento dos dados da planilha
            monthProcess = dayProcess[3:5]

            data = date.today()

            # Salva a data atual
            dataAtual = data.strftime('%d-%m-%Y')

            # Usado para capturar a descricao no mes atual
            valMes = int(monthProcess) - 1

            Meses = ('Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro')

            ##########################################################
            # Para aguardar o carregamento total da pagina - calendario
            element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '.calendario')))

            logging.info('---------------------------')
            logging.info('Iniciando uma nova busca pela sessao dos processos. Data procurada: ' + str(dayProcess))
            logging.info('---------------------------')

            if dataAtual[3:5] != monthProcess:

                logging.info('Selecionado o proximo mes para buscar a sessao.')
                logging.info('---------------------------')

                logging.info('A busca atual nao encontrou os processos no mes selecionado no calendario.')
                logging.info('Buscando a sessao no proximo mes: ' + str(Meses[valMes]))
                logging.info('---------------------------')

                # Contador usado para parar o loop somente quando o mes for encontrado
                count = 0
                while count == 0:
                    try:
                        # element = driver.find_element(By.XPATH,
                        #                                "//div[@class='rich-calendar-tool-btn' and contains(text(), '" + str(
                        #                                    Meses[valMes]) + "')]")

                        element = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//div[@class='rich-calendar-tool-btn' and contains(text(), '" + str(
                                                           Meses[valMes]) + "')]")))

                        count += 1

                        logging.info('Encontrado o mes correto para o processo.')
                        logging.info('---------------------------')
                        break

                    except:

                        # Avança o calendário mes
                        element = WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//div[./text()='>']")))
                        element.click()

                        logging.info('Avancando para o proximo mes.')
                        logging.info('---------------------------')

                        # Aguarda mudar o mês
                        time.sleep(2)

            logging.info('---------------------------')
            logging.info('Iniciando a inclusao dos processos')
            logging.info('---------------------------')

            # Usado para chamada recursiva do metodo
            countDef = 0
            self.processoIncluir(driver, process, dayProcess, logging, caminhoImages, countDef, log_bi)

        except:

            image = Print(driver, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

    def Execute(self, driver, caminhoImages, logging, openXls, xlsData, atividade, dataBaseModel, inicioTime, url, dataForm, xml, log_bi):

        metodos = Metodos(url)

        waitButtonLogin = WebDriverWait(driver, 10)

        # Tratamento para inicialização do Mozilla Firefox
        try:
            driver.maximize_window()
            driver.delete_all_cookies()
            driver.set_page_load_timeout(120)

            logging.info('Abrindo url')
            print('Abrindo url')

            # self.url = [i.text for i in xml.iter('url')][0]
            driver.get(url)

        except:

            # Interrompe o carregamento da página após error de time out, se passar de 5s
            waitButtonLogin.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#kc-login')))
            driver.execute_script('window.stop();')

            logging.info('Tempo de carregamento da pagina ultrapassou 5s.')
            logging.info('Executar parada de carregamento da pagina.')
            print('Executar parada de carregamento da pagina.')


        logging.info('Navegador iniciado com sucesso.')
        print('Navegador iniciado com sucesso.')

        logging.info('##############################')
        logging.info('Robô iniciado')
        logging.info('Acesso da Url: ' + url)
        print('Robô iniciado')
        print('Acesso da Url: ' + url)
        time.sleep(5)
        autenticacao = Auth()
        autenticacao.LoginPje2g(driver, logging, dataForm, url)

        # Seleciona o perfil
        selecionarPerfil = Perfil(driver, logging, dataForm['perfil'])

        log_bi.criar_arquivo_executados(
            ["INCLUÍDO EM PAUTA", "INCLUÍDO EM MESA"]
        )

        try:

            time.sleep(3)

            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            time.sleep(1)

            # try:
            # selecao last-child nao funciona
            # verificar em browser atualizado
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#menu div.nivel-aberto ul li:nth-of-type(2) a')))
            # element.click()

            actions = ActionChains(driver)
            actions.click(element).perform()

            # except Exception as e:
            #     logging.info('Falha ao clicar em Audiencias e Sessoes')
            #     logging.info(repr(e))

            time.sleep(1)

            try:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         '#menu .nivel-overlay div.nivel-aberto ul li:nth-of-type(3) a')))
                # element.click()

                actions = ActionChains(driver)
                actions.click(element).perform()

            except Exception as e:
                element = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         '#menu .nivel-overlay div.nivel-aberto ul li:nth-of-type(2) a')))
                # element.click()

                actions = ActionChains(driver)
                actions.click(element).perform()

            time.sleep(1)

            # {'29-10-2020': [['3000746-69.2019.8.06.0012', '29-10-2020', 'Presencial'],
            #                 ['3000074-61.2017.8.06.9964', '29-10-2020', 'Presencial'],
            #                 ['3000323-07.2017.8.06.0008', '29-10-2020', 'Presencial']],
            #  '30-10-2020': [['3000323-07.2017.8.06.0007', '30-10-2020', 'Virtual']],
            #  '15-11-2020': [['3000323-07.2017.8.06.0006', '15-11-2020', 'Presencial']],
            #  '20-11-2020': [['3000323-07.2017.8.06.0004', '20-11-2020', 'Virtual'],
            #                 ['3000323-07.2017.8.06.0005', '20-11-2020', 'Virtual']]
            #                 }
            listDataProcessos = openXls.getDataProcessInclusaoXLS(xlsData, driver, logging, xml)

            listTimeExc = []

            # Chama metodo que localiza os processos
            for i in listDataProcessos:

                # Registra horario que iniciou o processo
                inicioTimeProc = time.time()

                logging.info('---------------------------')
                logging.info('Iniciando uma nova busca...')
                logging.info('Incluindo processos na sessao do dia: ' + str(i))
                logging.info('Abrindo a sessao...')
                logging.info('---------------------------')
                self.localizarDataCalendarioIncluir(driver, listDataProcessos[i], str(i), logging, caminhoImages, log_bi)

                fimProc = time.time()
                timeTotal = fimProc - inicioTimeProc
                timeTotal = float('{:.2f}'.format(timeTotal))

                listTimeExc.append(str(timeTotal))

                # for x in range(len(listDataProcessos[i])):
                #     dataBaseModel['individual']['tempo_execucao_individual_sec'].append(str(timeTotal))

                logging.info('---------------------------')
                logging.info('---------------------------')
                logging.info('---------------------------')

            try:
                for i in range(len(self.listProcessos[0])):
                    dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[0][i]))
                    dataBaseModel['individual']['processo_realizado'].append(str(self.listProcessos[1][i]))
                    dataBaseModel['individual']['processo_nao_encontrado'].append(0)
            except:
                logging.info('Falha ao registrar os dados individual.')

            try:
                x = 0
                for i in listDataProcessos:

                    tamanhoListaPrincipal = len(listDataProcessos[i])
                    tamanhoListaFinal = len(self.listProcessos[0])

                    while tamanhoListaPrincipal > 0 and tamanhoListaFinal > 0:
                        dataBaseModel['individual']['tempo_execucao_individual_sec'].append(listTimeExc[x])
                        tamanhoListaPrincipal -= 1
                        tamanhoListaFinal -= 1

                    x += 1
            except:
                logging.info('Falha ao registrar os dados individual de tempo.')

            try:
                if self.listProcessos[2]:
                    for i in range(len(self.listProcessos[2])):
                        dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[2][i]))
                        dataBaseModel['individual']['processo_realizado'].append(1)
                        dataBaseModel['individual']['processo_nao_encontrado'].append(1)
                        dataBaseModel['individual']['tempo_execucao_individual_sec'].append(0)

            except:
                logging.info('Falha ao registrar os dados individual.')

            logging.info('---------------------------')
            logging.info('Dados gerados apos conclusao da super classe - individual')
            logging.info(dataBaseModel)
            logging.info('---------------------------')

            ###################################
            # Verificacao dos processos localizado e incluidos
            ###################################

            if len(self.listProcessos[0]) > 0:
                logging.info('Lista de processos encontrados:')
                for i in range(len(self.listProcessos[0])):
                    logging.info('Processo: ' + str(self.listProcessos[0][i]))

                logging.info("Total de processos encontrados: " + str(len(self.listProcessos[0])))
                logging.info("Total de processos incluidos: " + str(self.countIncluidos))
            else:
                logging.info('Nenhum processo foi encontrado.')

            self.listProcessos.append(len(self.listProcessos[0]))
            self.listProcessos.append(self.countIncluidos)

            logging.info('---------------------------')

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

            ###################################
            # Vericacao dos processos nao localizados
            ###################################

            if len(self.listProcessos[2]) > 0:
                logging.info('Lista de processos nao foram encontrados:')
                for i in range(len(self.listProcessos[2])):
                    logging.info('Processo: ' + str(self.listProcessos[2][i]))
                logging.info("Total de processos que nao foram encontrados: " + str(len(self.listProcessos[2])))
            else:
                logging.info('Todos os processos foram encontrados corretamente.')

            self.listProcessos.append(len(self.listProcessos[2]))

            logging.info('---------------------------')

            driver.switch_to.default_content()

            # Registra base
            dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
            dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
            dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

            try:
                driver.close()
            except:
                driver.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

            return self.listProcessos

        except Exception as e:

            logging.info('---------------------------')
            logging.info('Atividade Erro:')
            logging.info(dataBaseModel)
            logging.info('---------------------------')

            image = Print(driver, caminhoImages)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            # logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos