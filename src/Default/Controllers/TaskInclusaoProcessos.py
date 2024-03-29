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
from selenium.webdriver.support.select import Select

from src.Default.Controllers.Print import Print


class TaskInclusaoProcessos:
    listProcessos = [[], [], [], ]
    countIncluidos = 0
    countEnviaProcesso = 0

    # Geração de dados
    qtd_clicks_all = 0
    qtd_erros_tentativa_processo_all = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml, dataBaseModel, inicioTime, arrayVarRefDados):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEnviaProcesso = 0
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml, dataBaseModel, inicioTime, arrayVarRefDados)

    def pecorreProcessoPauta(self, firefox, process, element, dayProcess, logging, caminhoImages):

        # Ordena os processos
        # select = Select(firefox.find_element(By.CSS_SELECTOR, 'table#richTabRelacaoJulgamento select'))
        # select.select_by_visible_text('Órgão julgador')
        # time.sleep(14)

        # Localiza os processos do dia e marca
        ##########################################################
        for i in range(len(process)):
            # Usado para verificar se o processo nao foi localizado
            # count = 0

            logging.info('Procurando processo: ' + str(process[i][0]))
            # logging.info('Total de linhas: ' + str(len(element)))

            try:

                # firefox.find_element(By.XPATH,
                # "//table[@id='pautaJulgamentoList']/tbody/tr/td/div/div/h6/a[contains(text(), '" + process[i][0] + "')]//ancestor::td[1]/form/center/input").click()

                firefox.find_element(By.XPATH,
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

            except Exception as e:

                #############################################
                # Caso acontece de nao existir o botao marcar
                #############################################
                logging.info('Processo nao pode ser selecionado: ' + str(process[i][0]))
                logging.info(repr(e))

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                # Processo nao incluido
                self.listProcessos[1].append(1)

                # Inclui lista de processos nao localizados
                self.listProcessos[2].append(str(process[i][0]))

                image = Print(firefox, caminhoImages)
                logging.info('---------------------------')
                logging.info('O processo nao ser localizado na sessao. Data: ' + str(dayProcess))
                logging.info('Processo nao foi localizado: ' + str(process[i][0]))
                logging.info('---------------------------')



            # for x in range(len(element)):
            #
            #     try:  # Para verificar se o processo existe na listagem
            #
            #         firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
            #             x + 1) + "]/td[2]/div/div/h6/a[contains(text(), '" + process[i][0] + "')]")
            #
            #         logging.info('Processo encontrato.')
            #         # time.sleep(3)
            #
            #         try:
            #             firefox.find_element(By.XPATH, "//table[@id='pautaJulgamentoList']/tbody/tr[" + str(
            #                 x + 1) + "]/td[1]/form/center/input").click()
            #
            #             # Inclui lista de processos localizados
            #             self.listProcessos[0].append(str(process[i][0]))
            #             logging.info('Processo selecionado: ' + str(process[i][0]))
            #
            #             # Processo incluido
            #             self.listProcessos[1].append(0)
            #
            #             self.countIncluidos += 1
            #
            #             # Processo localizado
            #             count += 1
            #
            #             # Aguarda loading do click
            #             # Verifica time de click
            #             time.sleep(4)
            #
            #             ######################################################################################
            #             # Alteracao Solicitada Karyna
            #             ######################################################################################
            #
            #             # Clica em incluir processos
            #             # Finaliza atividade
            #             ##########################################################
            #             # element2 = WebDriverWait(firefox, 20).until(
            #             #     EC.presence_of_element_located(
            #             #         (By.CSS_SELECTOR,
            #             #          'form#j_id1620 input')))
            #             # element2.click()
            #             ##########################################################
            #
            #             # logging.info('Processo incluido: ' + str(process[i][0]))
            #             # logging.info('---------------------------')
            #
            #             ##########################################################
            #             # Demora 11s a inclusao
            #             ##########################################################
            #             ##########################################################
            #             ##########################################################
            #             # time.sleep(8)
            #
            #             ######################################################################################
            #
            #         except Exception as e:
            #
            #             #############################################
            #             # Caso acontece de nao existir o botao marcar
            #             #############################################
            #             logging.info('Processo nao pode ser selecionado: ' + str(process[i][0]))
            #             logging.info(repr(e))
            #
            #             # Contabiliza dados
            #             self.qtd_erros_tentativa_processo_all += 1
            #
            #             # Processo nao incluido
            #             self.listProcessos[1].append(1)
            #
            #     except Exception as e:
            #         logging.info(repr(e))
            #         continue

            # Caso o processo nao seja localizado, incluir na lista de nao localizados
            # if count == 0:
            #     # Inclui lista de processos nao localizados
            #     self.listProcessos[2].append(str(process[i][0]))
            #
            #     image = Print(firefox, caminhoImages)
            #     logging.info('---------------------------')
            #     logging.info('O processo nao ser localizado na sessao. Data: ' + str(dayProcess))
            #     logging.info('Processo nao foi localizado: ' + str(process[i][0]))
            #     logging.info('---------------------------')

        logging.info('Atividade de incluir processos em "Aptos para Inclusao em Pauta" foi realizada com sucesso. Data: ' + str(dayProcess))
        logging.info('---------------------------')

        ##########################################################

    def pecorreProcessoMesa(self, firefox, process, dayProcess, logging, caminhoImages):

        # Localiza os processos do dia e marca
        ##########################################################

        for i in range(len(process)):

            try:  # Para verificar se o processo existe

                elementInput = WebDriverWait(firefox, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                elementInput.send_keys(process[i][0])

                # Contabiliza dados
                self.qtd_clicks_all += 1

                time.sleep(2)

                try:
                    # Aguarda a busca do processo
                    elementIn = WebDriverWait(firefox, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'div.rich-sb-common-container table.rich-sb-int-decor-table tr.richfaces_suggestionEntry')))
                    firefox.execute_script("arguments[0].click();", elementIn)
                    # Contabiliza dados
                    self.qtd_clicks_all += 1

                except Exception as e:
                    logging.info(repr(e))
                    logging.info('Nao foi possivel clicar na sugestao de processo na busca.')

                    # Contabiliza dados
                    self.qtd_erros_tentativa_processo_all += 1

                time.sleep(2)

                # Clical em incluir
                elementInn = WebDriverWait(firefox, 3).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="processoEmMesaForm:cadastrar"]')))
                elementInn.click()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                # Confirma o alerto caso exista
                # Messagem: A classe exige pauta. Deseja continuar?
                try:
                    WebDriverWait(firefox, 2).until(EC.alert_is_present())

                    alert = firefox.switch_to.alert
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
                elementInput = WebDriverWait(firefox, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                # Limpa campo
                elementInput.clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                time.sleep(2)

            except:

                # Captura novamente o elemento
                elementInput = WebDriverWait(firefox, 4).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                elementInput.clear()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                time.sleep(2)

                # Inclui lista de processos nao localizados
                self.listProcessos[2].append(process[i][0])

                self.qtd_erros_tentativa_processo_all += 1

                image = Print(firefox, caminhoImages)
                logging.info('---------------------------')
                logging.info('Processo de nao ser localizado na busca "Aptos para Inclusao em Mesa". Data: ' + str(dayProcess))
                logging.info('Processo nao foi localizado: ' + str(process[i][0]))
                logging.info('Registrando print.')
                logging.info('---------------------------')

        logging.info('Atividade de incluir processos em "Aptos para Inclusao em Mesa" foi realizada com sucesso. Data: ' + str(dayProcess))
        logging.info('---------------------------')

        ##########################################################

    def processoIncluir(self, firefox, process, dayProcess, logging, caminhoImages, countDef):

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

            # Procura dia no calendario atual
            # A Aberta
            # R Realizada
            # F Finalizada
            logging.info('Buscando o dia da sessao.')
            logging.info('---------------------------')

            try:
                element = firefox.find_element_by_xpath("//span[@class='text-center' and ./text()='" + str(
                    dayProce) + "']//following-sibling::span[@class='ml-10' and contains(text(),'- EASP')]")
            except Exception as e:
                logging.info(repr(e))
                logging.info('---------------------------')
                logging.info('Nao foi possivel abrir a sessao do dia especificado, pois a sessao nao esta como "EASP". Por favor, verificar.')
                logging.info('Ou pode ter ocorrido desde dia nao haver sessao aberta.')
                logging.info('Registrando print.')
                logging.info('---------------------------')
                image = Print(firefox, caminhoImages)

                # Contabiliza dados
                self.qtd_erros_tentativa_processo_all += 1

                # try:
                #     firefox.close()
                # except:
                #     firefox.quit()

                return self.listProcessos

            # Verifica se achou o respectivo dia no calendario
            if element:

                logging.info('Dia da sessao encontrato.')
                logging.info('---------------------------')

                element.click()

                # Contabiliza dados
                self.qtd_clicks_all += 1

                time.sleep(1)

                # Identifica se tem mais de uma sessao e qual deve entrar
                ##########################################################
                try:
                    element = firefox.find_elements_by_css_selector("table#sessaoRelacaoJulgamentoDt tr.rich-table-row")

                    for x in range(len(element)):

                        try:

                            if len(processPresencial) > 0 and countDef == 0:
                                # firefox.find_element(By.XPATH, "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[" + str(
                                #     x + 1) + "]/td[contains(text(), 'Presencial')]//ancestor::tr[" + str(
                                #     x + 1) + "]/td[1]/a").click()

                                try:
                                    e = firefox.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[contains(., 'Presencial')]").text
                                    if e:
                                        firefox.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a").click()
                                except:
                                    firefox.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a").click()

                                sessao = 'Presencial'

                                # Contabiliza dados
                                self.qtd_clicks_all += 1

                            elif len(processVirtual) > 0 and countDef == 1:

                                try:
                                    e = firefox.find_element(By.XPATH,
                                                             "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[contains(., 'Virtual')]").text
                                    if e:
                                        firefox.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a").click()
                                except:
                                    firefox.find_element(By.XPATH,
                                                         "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a").click()

                                sessao = 'Virtual'

                                # Contabiliza dados
                                self.qtd_clicks_all += 1

                            elif len(processPresencial) > 0:
                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[1]/td[1]/a").click()

                                sessao = 'Presencial'

                                # Contabiliza dados
                                self.qtd_clicks_all += 1

                            elif len(processVirtual) > 0:
                                firefox.find_element(By.XPATH,
                                                     "//table[@id='sessaoRelacaoJulgamentoDt']/tbody/tr[2]/td[1]/a").click()

                                sessao = 'Virtual'

                                # Contabiliza dados
                                self.qtd_clicks_all += 1

                        except:

                            # Contabiliza dados
                            self.qtd_erros_tentativa_processo_all += 1

                            logging.info('Houve um problema a selecionar sessao correta. Por favor verificar se os dados da planilha estao corretos.')
                            logging.info('---------------------------')
                            logging.info('Presencial:')
                            logging.info(str(processPresencial))
                            logging.info('Virtual:')
                            logging.info(str(processVirtual))
                            logging.info('---------------------------')

                            # try:
                            #     firefox.close()
                            # except:
                            #     firefox.quit()

                            return self.listProcessos

                    firefox.find_element(By.CSS_SELECTOR, "span#fecharModal").click()

                    # Contabiliza dados
                    self.qtd_clicks_all += 1

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
                    main_window_handle = firefox.current_window_handle

                signin_window_handle = None
                while not signin_window_handle:
                    for handle in firefox.window_handles:
                        if handle != main_window_handle:
                            signin_window_handle = handle
                            break
                firefox.switch_to.window(signin_window_handle)
                ##########################################################

                logging.info('Nova janela encontrada.')
                logging.info('---------------------------')

                ##########################################################
                # Aguarda o carregamento da nova janela
                ##########################################################

                time.sleep(30)

                # Seleciona "Aptos para inclusão em pauta"
                ##########################################################
                pauta = WebDriverWait(firefox, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'td#form_lbl')))

                ##########################################################

                # Seleciona "Aptos para inclusão em mesa"
                ##########################################################
                mesa = WebDriverWait(firefox, 600).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'td#processoMesaTab_lbl')))

                ##########################################################

                # Verifica se a sessao esta fechada
                ##########################################################
                try:
                    element = firefox.find_element_by_xpath(
                        "//p[@class='text-center' and contains(text(),'está fechada')]")

                    logging.info('Registrando print.')
                    image = Print(firefox, caminhoImages)

                    try:
                        firefox.close()
                    except:
                        firefox.quit()

                    # Para sair do objeto popup
                    firefox.switch_to.window(main_window_handle)

                    logging.info('Sessao deste dia esta fechada. Dia: ' + str(dayProcess))
                    logging.info('Fechando janela aberta.')

                    # Contabiliza dados
                    self.qtd_erros_tentativa_processo_all += 1

                    return self.listProcessos

                except:

                    try:

                        # Identifica o tipo da sessao
                        element = firefox.find_element(By.XPATH,
                                                   "//span[contains(text(), 'Sessão Virtual')]")

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
                            image = Print(firefox, caminhoImages)

                            try:
                                firefox.close()
                            except:
                                firefox.quit()

                            # Para sair do objeto popup
                            firefox.switch_to.window(main_window_handle)

                            # Contabiliza dados
                            self.qtd_erros_tentativa_processo_all += 1

                            return self.listProcessos

                        pauta.click()

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

                        ##########################################################
                        # Inicia a busca

                        logging.info('Selecionado menu: Aptos para inclusao em pauta.')
                        logging.info('---------------------------')

                        logging.info('Buscando processos para serem incluidos...')
                        logging.info('---------------------------')
                        logging.info(processVirtual)
                        logging.info('---------------------------')

                        time.sleep(45)

                        # Localiza processos a serem selecionados e seleciona cada um deles
                        # WebDrive usado somente para o aguardo do carregamento da pagina
                        ##########################################################

                        try:
                            element = WebDriverWait(firefox, 600).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR,
                                     'table#pautaJulgamentoList tbody tr')))
                        except:

                            # Contabiliza dados
                            self.qtd_erros_tentativa_processo_all += 1

                            logging.info('Nao existe processos para serem incluidos nessa sessao e nessa data. Data: ' + str(dayProcess))
                            logging.info('Os processos abaixos nao poderam ser localizados. A lista esta vazia.')
                            logging.info('Registrando print.')
                            image = Print(firefox, caminhoImages)

                            for i in range(len(processVirtual)):
                                logging.info('Processo: ' + str(processVirtual[i][0]))
                                # Inclui lista de processos nao localizados
                                self.listProcessos[2].append(str(processVirtual[i][0]))

                            logging.info('Fechando a janela da sessao.')
                            logging.info('Finalizando a busca na sessao do dia: ' + str(dayProcess))
                            logging.info('---------------------------')

                            try:
                                firefox.close()
                            except:
                                firefox.quit()

                            # Para sair do objeto popup
                            firefox.switch_to.window(main_window_handle)

                            return self.listProcessos

                        # Localiza tabela com listagem dos processos
                        element = firefox.find_elements_by_css_selector(
                            "table#pautaJulgamentoList tbody tr.rich-table-row")
                        ##########################################################

                        countDef += 1
                        self.pecorreProcessoPauta(firefox, processVirtual, element, dayProcess, logging, caminhoImages)

                        ######################################################################################
                        # Alteracao Solicitada Karyna
                        #####################################################################################
                        logging.info('Processos selecionados...')
                        logging.info('---------------------------')

                        # Clica em incluir processos
                        # Finaliza atividade
                        ##########################################################
                        element = WebDriverWait(firefox, 600).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 #'form#j_id1620 input')))
                                 'table#richTabRelacaoJulgamento form input[value="Incluir"i]')))
                        element.click()
                        ##########################################################

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

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
                            firefox.close()
                        except:
                            firefox.quit()

                        # Para sair do objeto popup
                        firefox.switch_to.window(main_window_handle)  # or driver.switch_to_default_content()

                        time.sleep(1)

                        # Para verificar caso haja mais de uma sessao
                        if len(processPresencial) > 0 and len(processVirtual) > 0 and countDef == 1:
                            self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages, countDef)

                        logging.info('Fechando a janela da sessao.')
                        logging.info('---------------------------')

                        return self.listProcessos

                    except:

                        # Identifica o tipo da sessao
                        element = firefox.find_element(By.XPATH,
                                                       "//span[contains(text(), 'Presencial')]")

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
                            image = Print(firefox, caminhoImages)

                            logging.info('Fechando a janela da sessao.')
                            logging.info('Finalizando a busca na sessao do dia: ' + str(dayProcess))
                            logging.info('---------------------------')

                            # Contabiliza dados
                            self.qtd_erros_tentativa_processo_all += 1

                            try:
                                firefox.close()
                            except:
                                firefox.quit()

                            # Para sair do objeto popup
                            firefox.switch_to.window(main_window_handle)

                            return self.listProcessos

                        mesa.click()

                        time.sleep(5)

                        ##########################################################
                        # Para aguardar o carregamento total da pagina
                        element = WebDriverWait(firefox, 600).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'form#processoEmMesaForm div.propertyView div.value input.suggest')))

                        countDef += 1

                        self.pecorreProcessoMesa(firefox, processPresencial, dayProcess, logging, caminhoImages)

                        # Fecha popup
                        try:
                            firefox.close()
                        except:
                            firefox.quit()

                        # Para sair do objeto popup
                        firefox.switch_to.window(main_window_handle)

                        time.sleep(1)

                        # Para verificar caso haja mais de uma sessao
                        if len(processPresencial) > 0 and len(processVirtual) > 0 and countDef == 1:
                            self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages, countDef)

                        logging.info('Fechando a janela da sessao.')
                        logging.info('---------------------------')

                        return self.listProcessos


        except Exception as e:

            # Contabiliza dados
            self.qtd_erros_tentativa_processo_all += 1

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.exception('Dia da sessao nao encontrado.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()

            # Fecha popup
            try:
                firefox.close()
            except:
                firefox.quit()

            # Para sair do objeto popup
            firefox.switch_to.window(main_window_handle)

            time.sleep(1)

            return self.listProcessos

    def localizarDataCalendarioIncluir(self, firefox, process, dayProcess, logging, caminhoImages):

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
            element = WebDriverWait(firefox, 60).until(
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
                        element = firefox.find_element(By.XPATH,
                                                       "//div[@class='rich-calendar-tool-btn' and contains(text(), '" + str(
                                                           Meses[valMes]) + "')]")
                        count += 1

                        logging.info('Encontrado o mes correto para o processo.')
                        logging.info('---------------------------')
                        break

                    except:

                        # Avança o calendário mes
                        element = WebDriverWait(firefox, 20).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "//div[./text()='>']")))
                        element.click()

                        # Contabiliza dados
                        self.qtd_clicks_all += 1

                        logging.info('Avancando para o proximo mes.')
                        logging.info('---------------------------')

                        # Aguarda mudar o mês
                        time.sleep(2)

            logging.info('---------------------------')
            logging.info('Iniciando a inclusao dos processos')
            logging.info('---------------------------')

            # Usado para chamada recursiva do metodo
            countDef = 0
            self.processoIncluir(firefox, process, dayProcess, logging, caminhoImages, countDef)

        except:

            image = Print(firefox, caminhoImages)
            logging.exception('Falha ao concluir a tarefa especificada.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml, dataBaseModel, inicioTime, arrayVarRefDados):

        try:

            time.sleep(3)

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            # Contabiliza dados
            arrayVarRefDados['qtd_clicks'] += 1

            time.sleep(1)

            # selecao last-child nao funciona
            # verificar em browser atualizado
            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#menu div.nivel-aberto ul li:nth-of-type(2) a')))
            element.click()

            # Contabiliza dados
            arrayVarRefDados['qtd_clicks'] += 1

            time.sleep(1)

            element = WebDriverWait(firefox, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#menu .nivel-overlay div.nivel-aberto ul li:first-child a')))
            element.click()

            # Contabiliza dados
            arrayVarRefDados['qtd_clicks'] += 1

            time.sleep(1)

            # {'29-10-2020': [['3000746-69.2019.8.06.0012', '29-10-2020', 'Presencial'],
            #                 ['3000074-61.2017.8.06.9964', '29-10-2020', 'Presencial'],
            #                 ['3000323-07.2017.8.06.0008', '29-10-2020', 'Presencial']],
            #  '30-10-2020': [['3000323-07.2017.8.06.0007', '30-10-2020', 'Virtual']],
            #  '15-11-2020': [['3000323-07.2017.8.06.0006', '15-11-2020', 'Presencial']],
            #  '20-11-2020': [['3000323-07.2017.8.06.0004', '20-11-2020', 'Virtual'],
            #                 ['3000323-07.2017.8.06.0005', '20-11-2020', 'Virtual']]
            #                 }
            listDataProcessos = openXls.getDataProcessInclusaoXLS(xlsData, firefox, logging, xml)

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
                self.localizarDataCalendarioIncluir(firefox, listDataProcessos[i], str(i), logging, caminhoImages)

                fimProc = time.time()
                timeTotal = fimProc - inicioTimeProc
                timeTotal = float('{:.2f}'.format(timeTotal))

                listTimeExc.append(str(timeTotal))

                # for x in range(len(listDataProcessos[i])):
                #     dataBaseModel['individual']['tempo_execucao_individual_sec'].append(str(timeTotal))

                logging.info('---------------------------')
                logging.info('---------------------------')
                logging.info('---------------------------')

            logging.info('---------------------------')
            logging.info('Dados gerados apos conclusao da super classe')
            logging.info(dataBaseModel)
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

            firefox.switch_to.default_content()

            # Registra base
            dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
            dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
            dataBaseModel['qtd_clicks'] = arrayVarRefDados['qtd_clicks'] + self.qtd_clicks_all
            dataBaseModel['qtd_erros_tentativa_processo'] = self.qtd_erros_tentativa_processo_all
            dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

            logging.info('---------------------------')
            logging.info('Final Atividade:')
            logging.info(dataBaseModel)
            logging.info('---------------------------')

            try:
                firefox.close()
            except:
                firefox.quit()

            logging.info('Lista completa para formulario:')
            logging.info(str(self.listProcessos))
            logging.info('---------------------------')

            return self.listProcessos

        except Exception as e:

            dataBaseModel['qtd_erros_robo'] = 1

            logging.info('---------------------------')
            logging.info('Atividade Erro:')
            logging.info(dataBaseModel)
            logging.info('---------------------------')

            image = Print(firefox, caminhoImages)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            # logging.shutdown()

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos