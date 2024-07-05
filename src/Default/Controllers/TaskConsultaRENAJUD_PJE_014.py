# ###################################################
# ###################################################
# ## Desenvolvido por:
# ## Tiago Vasconcelos
# ## E-mail: tiago.ponte@tjce.jus.br
# ## Núcleo de Inovações SETIN
# ###################################################
# ###################################################

import time
import re
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from src.Default.Controllers.Print import Print
from src.Default.Controllers.Auth import Auth
from src.Default.Controllers.Metodos import Metodos
from src.Default.Controllers.Perfil import Perfil

class TaskConsultaRENAJUD_PJE_014:
    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countEncaminhados = 0
    countTotalEncontrato = 0

    def __init__(self, driver, caminhoImagesPrint, logging, atividade, dataBaseModel, inicioTime,
                 url, dataForm, xml, log_unificado):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countTotalEncontrato = 0
        self.urlRENAJUD = [i.text for i in xml.iter('urlRenajud')][0]
        self.etiqueta = [i.text for i in xml.iter('etiquetaConsultaRenajud')][0]
        self.Execute(driver, caminhoImagesPrint, logging, atividade, dataBaseModel, inicioTime,
                 url, dataForm, xml, log_unificado)

    def mais_detalhes(self, driver, logging, metodos):

        # Usado para garantia de carregamento da pagina
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.TAG_NAME, 'a')))

        # ABRE MAIS DETALHES
        mais_detalhes = metodos.elemento_por_titulo_em_lista_by_tag(driver, 'a', 'Mais detalhes')
        mais_detalhes.click()

        logging.info("Abrirndo mais detalhes ...")
        print("Abrirndo mais detalhes ...")

        # IDENTIFICA VALOR DA CAUSA
        lista_dt = driver.find_elements(by=By.TAG_NAME, value='dt')
        posicao_titulo = 0

        for indice, dt in enumerate(lista_dt):
            if 'Valor da causa' in dt.text:
                posicao_titulo = indice

        lista_dd = driver.find_elements(by=By.TAG_NAME, value='dd')
        dd = lista_dd[posicao_titulo]
        valor = dd.text

        # IDENTIFICA POLO ATIVO
        polo_ativo = metodos.get_element(driver, '//*[@id="poloAtivo"]')
        municipio = polo_ativo.text.split('\n')
        municipio = municipio[1].split('-')[0]

        # IDENTIFICA POLO PASSIVO
        polo_passivo = metodos.get_element(driver, '//*[@id="poloPassivo"]')
        spans = metodos.get_elements_by_tag(polo_passivo, 'span')
        identificacao = ""

        for span in spans:
            if "EXECUTADO" in span.text:
                if "CNPJ:" in span.text:
                    cnpj = span.text.split('\n')
                    cnpj_tratado = re.search(r'\d{2}.\d{3}.\d{3}/\d{4}-\d{2}', span.text)
                    identificacao = cnpj_tratado.group().replace("-", "").replace(".", "").replace("/", "")
                    break
                elif "CPF:" in span.text:
                    cpf_tratado = re.search(r'\d{3}.\d{3}.\d{3}-\d{2}', span.text)
                    identificacao = cpf_tratado.group().replace("-", "").replace(".", "")
                    break
                else:
                    identificacao = "Sem Identificação"

        dados_coletados = {'valor': valor, 'municipio': municipio, 'cpf': identificacao}

        for indice, valor in dados_coletados.items():
            if len(valor) == 0:
                raise ("Faltando dados")

        if dados_coletados["cpf"] == "Sem Identificação":
            return False

        logging.info("Informações coletadas")
        print("Informações coletadas")

        return dados_coletados

    def localizarProcesso(self, driver, logging, caminhoImagesPrint, metodos, abas, dataBaseModel, log_unificado, pula):

        if pula == 0:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.ID, 'inputPesquisaTarefas')))
            element.clear()

            # Filtrar etiqueta
            logging.info('---------------------------')
            logging.info('Filtrando os processos pela etiqueta: Renajud consultar')

            time.sleep(1)

            # Abre filtro da pesquisa para etiquetas
            element = driver.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
            driver.execute_script("arguments[0].click();", element)

            element = driver.find_element(By.ID, 'porEtiqueta')
            element.clear()

            driver.find_element(By.ID, "porEtiqueta").send_keys(self.etiqueta)

            time.sleep(1)

            # Clica em pesquisar
            element = driver.find_element(By.CSS_SELECTOR, '.col-sm-12 button.btn-pesquisar-filtro')
            driver.execute_script("arguments[0].click();", element)

            time.sleep(5)

            # Fecha filtro da pesquisa
            element = driver.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
            driver.execute_script("arguments[0].click();", element)

            print('Concluiu Filtro da Etiqueta')

        try:
            element = driver.find_element(By.CSS_SELECTOR, 'div.ui-datalist-emptymessage').text

            if element == 'Nenhum processo encontrado':
                print('Nenhum processo encontrato')
                logging.info('Nenhum processo encontrato')

                # Fecha Janela PJe
                driver.close()

                logging.info('Abrindo aba RENAJUD')
                print('Abrindo aba RENAJUD')
                driver.switch_to.window(abas['RENAJUD'])

                # Fecha Janela RENAJUD
                driver.close()

                logging.info('Finalizando execuxao . . .')
                print('Finalizando execuxao . . .')

                return self.listProcessos

        except:
            time.sleep(1)

        # Aguarda carregamento completo dos processos
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'div.ui-datalist-content ul.ui-datalist-data li')))

        print('Consultando total de atividades . . .')

        # Consultando total de atividades
        try:
            selectResult = driver.find_element(By.CSS_SELECTOR, 'span[title="Quantidade de processos na tarefa"i]').text
            logging.info('Quantidade de processo(s) encontrado(s): ' + str(selectResult))
            print('Quantidade de processo(s) encontrado(s): ' + str(selectResult))
            # Total encontrado
            self.countTotalEncontrato = self.countTotalEncontrato + int(selectResult)

            if int(selectResult) == 0:

                logging.info('Nao tem mais processos, finalizando . . .')
                print('Nao tem mais processos, finalizando . . .')

                # Altera para Janela RENAJUD
                logging.info('Fechando aba RENAJUD')
                print('Fechando aba RENAJUD')
                driver.switch_to.window(abas['RENAJUD'])

                driver.close()

                # Retorna ao PJe
                driver.switch_to.window(abas['PJe'])
                logging.info('Fechando aba PJe')
                print('Fechando aba PJe')

                driver.close()

                return self.listProcessos

        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Ocorreu um erro ao capturar o total de processos')
            print('Ocorreu um erro ao capturar o total de processos')

        # Captura todos os elementos da lista
        selectResult = driver.find_elements(By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li')

        # for x in range(len(selectResult)):

        # Inicia for
        # Registra horario que iniciou o processo
        inicioTimeProc = time.time()

        driver.switch_to.default_content()

        iframe = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        driver.switch_to.frame(iframe)

        # Captura numero do processo
        # Invertando execucao, do ultimo para o mais recente
        try:
            # numeroProcesso = driver.find_element(By.CSS_SELECTOR, 'div.ui-datalist-content ul.ui-datalist-data li:nth-child(' + str(
            #     x + 1) + ') div.col-sm-11 a span.tarefa-numero-processo.process').text
            numeroProcesso = driver.find_element(By.CSS_SELECTOR,
                                                 'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) div.col-sm-11 a span.tarefa-numero-processo.process').text
            numeroProcesso = numeroProcesso.split()
            numeroProcesso = numeroProcesso[1]
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Falha ao localizar o numero do processo')
            print('Falha ao localizar o numero do processo')
            numeroProcesso = "Falha Numero Processo"

            # continue

        log_unificado.adicionar_processo(str(numeroProcesso))

        logging.info('Abrindo processo: ' + numeroProcesso)
        print('Abrindo processo: ' + numeroProcesso)

        # Alimentando resultando
        self.listProcessos[0].append(str(numeroProcesso))
        self.listProcessos[1].append(1)  # Valor 1 para nao concluido

        # Abre processo
        try:
            # element = WebDriverWait(driver, 5).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR,
            #          'div.ui-datalist-content ul.ui-datalist-data li:nth-child(' + str(
            #             x + 1) + ') a.selecionarProcesso')))
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) a.selecionarProcesso')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(1)
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Falha ao abrir processo')
            print('Falha ao abrir processo')
            image = Print(driver, caminhoImagesPrint)

            return self.listProcessos

        # Aguarda carregamento do elemento: encaminhar para ...
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#btnTransicoesTarefa')))

        # Clica no botao Autos
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.header-wrapper div.toolbar-processo button[tooltip="Autos"i]')))
        driver.execute_script("arguments[0].click();", element)

        time.sleep(1)

        # Identificando a aba de Autos e coletando os detalhes
        abas['PJe - Autos'] = driver.window_handles[2]
        driver.switch_to.window(abas['PJe - Autos'])

        try:
            resultDestalhes = self.mais_detalhes(driver, logging, metodos)

            print('Dados Coletados:')
            print(resultDestalhes)

            log_unificado.atualizar_etapa_processo(
                processo = str(numeroProcesso),
                etapa = "COLETAR INFORMACOES DO PROCESSO",
                atualizacao = "Realizado"
            )

        except Exception as e:
            log_unificado.enviar_erro(
                num_processo = str(numeroProcesso),
                passo_Executado = "COLETAR INFORMACOES DO PROCESSO",
                mensagem=repr(e)
            )

        # Altera para Janela RENAJUD
        logging.info('Abrindo aba RENAJUD')
        print('Abrindo aba RENAJUD')
        driver.switch_to.window(abas['RENAJUD'])

        time.sleep(1)

        # #######################################################
        # #######################################################

        # Etapa - realiza processo RENAJUD

        # Remover ponto e traco do processo
        try:
            numeroProcessoRE = re.sub(r'[.-]', '', numeroProcesso)

            print('Realizando processo no RENAJUD')
            logging.info('Realizando processo no RENAJUD')

            # Clica no botao Restrições
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#main_nav ul.navbar-nav li:nth-child(2) a.dropdown-toggle'))).click()

            print('Abre Restricoes')
            logging.info('Abre Restricoes')

            time.sleep(1)

            # Clica no botao Retirar
            element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#main_nav ul.navbar-nav li:nth-child(2) ul.dropdown-menu li:nth-child(1) a.dropdown-item')))
            driver.execute_script("arguments[0].click();", element)

            print('Abre Inserir')
            logging.info('Abre Inserir')

            time.sleep(1)

            # Clica no botao Veiculo
            element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div#main_nav ul.navbar-nav li:nth-child(2) ul.dropdown-menu li:nth-child(1) ul.submenu li:nth-child(2) a')))
            driver.execute_script("arguments[0].click();", element)

            print('Abre Veiculo')
            logging.info('Abre Veiculo')

            time.sleep(1)

            # Informa o Processo
            elementPro = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '#numeroProcesso')))
            elementPro.send_keys(numeroProcessoRE)

            print('Inseriu processo: ' + numeroProcesso)
            logging.info('Inseriu processo: ' + numeroProcesso)

            time.sleep(1)

            # Clica em Pesquisar
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'form.ng-valid'))).submit()

            print('Realiza pesquisa')
            logging.info('Realiza pesquisa')

            # Verificar tempo de pesquisa RENAJUD
            time.sleep(6)

            driver.switch_to.default_content()

            # #######################################################
            # #######################################################
            # Aguarda carregamento
            try:
                resultadoPesquisa = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,
                         'div.shadow-lg div.alert')))

                print('Nenhum veiculo encontrado')
                logging.info('Nenhum veiculo encontrado')
            except:

                try:
                    resultadoPesquisa = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR,
                             'table.table-hover')))

                    print('Veiculo encontrado')
                    logging.info('Veiculo encontrado')
                except:

                    try:
                        resultadoPesquisa = WebDriverWait(driver, 4).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR,
                                 'div.shadow-lg div.alert')))

                        print('Nenhum veiculo encontrado')
                        logging.info('Nenhum veiculo encontrado')
                    except:

                        try:
                            resultadoPesquisa = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located(
                                    (By.CSS_SELECTOR,
                                     'table.table-hover')))

                            print('Veiculo encontrado')
                            logging.info('Veiculo encontrado')
                        except:
                            print('Erro inesperado na pesquisa')
                            logging.info('Erro inesperado na pesquisa')

            log_unificado.atualizar_etapa_processo(
                processo = str(numeroProcesso),
                etapa = "CONSULTA PROCESSO NO RENAJUD",
                atualizacao = "Realizado"
            )

        except Exception as e:
            log_unificado.enviar_erro(
                num_processo = str(numeroProcesso),
                passo_Executado = "CONSULTA PROCESSO NO RENAJUD",
                mensagem=repr(e)
            )

        # #######################################################
        # #######################################################

        retornoCaminhoPDF = Print(driver, caminhoImagesPrint, pdf=True, descricao=numeroProcesso + '_RENAJUD')
        caminhoRegistroPDF = retornoCaminhoPDF.caminhoPDF
        caminhoRegistroPDF = os.getcwd() + '\\' + caminhoRegistroPDF

        print('PDF gerado: ' + str(caminhoRegistroPDF))
        logging.info('PDF gerado: ' + str(caminhoRegistroPDF))

        elementPro.clear()

        # Clica no botao Logo RENAJUD
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div#main_nav ul.navbar-nav li:nth-child(1) a.nav-link')))
        driver.execute_script("arguments[0].click();", element)

        print('Volta inicio RENAJUD')
        logging.info('Volta inicio RENAJUD')

        # FIM - RENAJUD

        # #######################################################
        # #######################################################

        logging.info('Voltando para aba AUTOS')
        print('Voltando para aba AUTOS')
        driver.switch_to.window(abas['PJe - Autos'])

        time.sleep(1)

        # Clica em juntar documentos
        button_juntar_documentos = metodos.elemento_por_titulo_em_lista_by_tag(driver, 'a', 'Juntar documentos')
        button_juntar_documentos.click()

        print('Clica em juntar documentos')
        logging.info('Clica em juntar documentos')

        # Aguarda carregamento - tela
        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//*[@id="cbTDDecoration:cbTD"]')))

        try:
            # Seleciona certidao
            select = Select(
                driver.find_element(By.XPATH, '//*[@id="cbTDDecoration:cbTD"]'))
            select.select_by_visible_text('Certidão')

            print('Seleciona certidao')
            logging.info('Seleciona certidao')

            time.sleep(2)
        except Exception as e:
            logging.info('Houve um problema na etapa de selecionar a certidao')
            logging.info(repr(e))
            print(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)

            return self.listProcessos

        try:
            select = Select(driver.find_element(By.XPATH, '//*[@id="modTDDecoration:modTD"]'))
            select.select_by_visible_text('CERTIDÃO - RENAJUD')

            print('Seleciona certidao RENAJUD')
            logging.info('Seleciona certidao RENAJUD')

            time.sleep(2)
        except Exception as e:
            logging.info('Houve um problema na etapa de selecionar a certidao')
            logging.info(repr(e))
            print(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)

            return self.listProcessos

        # Clica em editar texto
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'table#raTipoDocPrincipal input[value="HTML"i]')))
        driver.execute_script("arguments[0].click();", element)

        print('Clica em editar texto')
        logging.info('Clica em editar texto')

        # Clica no botao Salvar
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[value="Salvar"i]')))
        driver.execute_script("arguments[0].click();", element)

        print('Clica em salvar')
        logging.info('Clica em salvar')

        time.sleep(1)

        # Aguarda carregamento - botao assinar documentos
        element = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 '//input[@id="btn-assinador" and @value="Assinar documento(s)"]')))

        try:
            # Adiciona anexo na pagina de juntar documentos
            # Espera se o elemento Adicionar esta clicável
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="commandLinkAdicionar"]')))

            time.sleep(1)

            # Envia arquivo - upload
            input_file = metodos.elemento_por_type_em_lista_by_tag(driver, 'input', 'file', repete=True)
            input_file.send_keys(caminhoRegistroPDF)

            print('Realizando upload do arquivo')
            logging.info('Realizando upload do arquivo')

            # Aguarda carregamento - botao Aguardando a classificação dos documentos
            element = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     '//input[@id="btn-assinador" and @value="Aguardando a classificação dos documentos"]')))

            # Seleciona o tipo de documento
            painel_anexo = metodos.get_element(driver, '//*[@id="dz-tabela-upload"]')
            painel_anexo_select = painel_anexo.find_elements(by=By.TAG_NAME, value='select')
            painel_anexo_select = painel_anexo_select[0]
            painel_anexo_select.send_keys('Outros Documentos')

            print('Seleciona outros documentos')
            logging.info('Seleciona outros documentos')

            time.sleep(5)
        except Exception as e:
            logging.info('Houve um problema na etapa de upload do arquivo')
            logging.info(repr(e))
            print(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)

            driver.close()

            # continue

        time.sleep(2)

        # Aguarda carregamento - botao assinar documentos
        try:
            element = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located(
                    (By.XPATH,
                     '//input[@id="btn-assinador" and @value="Assinar documento(s)"]'))).click()

            log_unificado.atualizar_etapa_processo(
                processo = str(numeroProcesso),
                etapa = "ASSINAR DOCUMENTO",
                atualizacao = "Realizado"
            )

        except Exception as e:
            log_unificado.enviar_erro(
                num_processo = str(numeroProcesso),
                passo_Executado = "ASSINAR DOCUMENTO",
                mensagem = repr(e)
            )

        print('Clica em assinar documentos')
        logging.info('Clica em assinar documentos')

        # Time pre-defindo - recomendado identificar conclusao de carregamento da pagina
        time.sleep(8)

        # Apaga PDF
        if os.path.isfile(caminhoRegistroPDF):
            os.remove(caminhoRegistroPDF)
            print('Remove PDF')
            logging.info('Remove PDF')

        # Fecha Janela de Autos
        driver.close()
        logging.info('Fecha Janela de Autos')
        print('Fecha Janela de Autos')

        # Retorna ao PJe
        driver.switch_to.window(abas['PJe'])
        logging.info('Voltando para aba PJe')
        print('Voltando para aba PJe')

        driver.switch_to.default_content()

        iframe = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        driver.switch_to.frame(iframe)

        # #######################################################
        # #######################################################
        # Remove etiqueta
        try:
            # etiquetas = driver.find_elements(By.CSS_SELECTOR,
            #                                  'div.ui-datalist-content ul.ui-datalist-data li:nth-child(' + str(
            #                                      x + 1) + ') div.col-sm-11 div.label-info.label-etiqueta')
            etiquetas = driver.find_elements(By.CSS_SELECTOR,
                                             'div.ui-datalist-content ul.ui-datalist-data li:nth-child(1) div.col-sm-11 div.label-info.label-etiqueta')

            logging.info('Quantidade de etiquetas encontradas: ' + str(len(etiquetas)))
            print('Quantidade de etiquetas encontradas: ' + str(len(etiquetas)))

            for y in range(len(etiquetas)):

                # nomeEtiquetas = driver.find_element(By.XPATH,
                #                                     '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[' + str(
                #                                         x + 1) + ']/processo-datalist-card/div/div[3]/div[' + str(
                #                                         y + 1) + ']/span[1]')
                nomeEtiquetas = driver.find_element(By.XPATH,
                                                    '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[1]/processo-datalist-card/div/div[3]/div[' + str(
                                                        y + 1) + ']/span[1]')

                # Tratamento para remover espaços no início e no final do texto, bem como espaços duplicados
                nomeEtiquetasText = nomeEtiquetas.text.strip()
                nomeEtiquetasText = ' '.join(nomeEtiquetasText.split())

                nomeEtiquetasTextConfig = self.etiqueta.strip()
                nomeEtiquetasTextConfig = ' '.join(nomeEtiquetasTextConfig.split())

                logging.info('Verificando etiqueta: ' + nomeEtiquetasText + '===' + nomeEtiquetasTextConfig)
                print('Verificando etiqueta: ' + nomeEtiquetasText + '===' + nomeEtiquetasTextConfig)

                if nomeEtiquetasText == nomeEtiquetasTextConfig:
                    logging.info('Etiqueta encontrada')
                    print('Etiqueta encontrada')

                    # nomeEtiquetasIn = driver.find_element(By.XPATH,
                    #                                       '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[' + str(
                    #                                           x + 1) + ']/processo-datalist-card/div/div[3]/div[' + str(
                    #                                           y + 1) + ']/span[2]')
                    nomeEtiquetasIn = driver.find_element(By.XPATH,
                                                          '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[1]/processo-datalist-card/div/div[3]/div[' + str(
                                                              y + 1) + ']/span[2]')

                    driver.execute_script("arguments[0].click();", nomeEtiquetasIn)

                    time.sleep(1)

                    logging.info('Etiqueta removida')
                    print('Etiqueta removida')

                    # break
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Falha ao remover etiqueta')
            print('Falha ao remover etiqueta')
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)


        # #######################################################
        # #######################################################

        # #######################################################
        # #######################################################
        # Encaminha processo
        try:
            # Clica no botao Encaminhar para (ABRE AS OPCOES)
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.dropdown button#btnTransicoesTarefa')))
            driver.execute_script("arguments[0].click();", element)

            logging.info('Clica em Emcaminhar para')
            print('Clica em Emcaminhar para')

            time.sleep(1)

            # Clica em Prosseguir
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.dropdown ul.dropdown-menu li a[title="Encaminhar para Prosseguir"i]')))
            driver.execute_script("arguments[0].click();", element)

            time.sleep(8)

            logging.info('Clica em Prosseguir')
            print('Clica em Prosseguir')

            log_unificado.atualizar_etapa_processo(
                processo = str(numeroProcesso),
                etapa = "ENCAMINHAR PARA PROSSEGUIR",
                atualizacao = "Realizado"
            )

        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)
            log_unificado.enviar_erro(
                num_processo = str(numeroProcesso),
                passo_Executado = "ENCAMINHAR PARA PROSSEGUIR",
                mensagem = repr(e)
            )

            # continue
        # #######################################################
        # #######################################################

        self.countEncaminhados += 1

        # Deleta o ultimo registro
        del (self.listProcessos[1][(len(self.listProcessos[1]) - 1)])
        # Inclui novo registro
        self.listProcessos[1].append(0)

        fimProc = time.time()
        timeTotal = fimProc - inicioTimeProc
        timeTotal = float('{:.2f}'.format(timeTotal))

        # Inclui processo na lista dataset
        dataBaseModel['individual']['cod_processo'].append(numeroProcesso)
        dataBaseModel['individual']['processo_realizado'].append(1)
        dataBaseModel['individual']['tempo_execucao_individual_sec'].append(str(timeTotal))

        #####################################################
        #####################################################
        logging.info('Checando se existe mais processos . . .')
        print('Checando se existe mais processos . . .')

        # Filtrar etiqueta
        logging.info('---------------------------')
        logging.info('Filtrando os processos pela etiqueta: Renajud consultar')

        time.sleep(1)

        # Abre filtro da pesquisa para etiquetas
        element = driver.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
        driver.execute_script("arguments[0].click();", element)

        element = driver.find_element(By.ID, 'porEtiqueta')
        element.clear()

        driver.find_element(By.ID, "porEtiqueta").send_keys(self.etiqueta)

        time.sleep(1)

        # Clica em pesquisar
        element = driver.find_element(By.CSS_SELECTOR, '.col-sm-12 button.btn-pesquisar-filtro')
        driver.execute_script("arguments[0].click();", element)

        time.sleep(5)

        # Fecha filtro da pesquisa
        element = driver.find_element(By.CSS_SELECTOR, 'button#dropdown-filtro-tarefas')
        driver.execute_script("arguments[0].click();", element)

        print('Concluiu Filtro da Etiqueta')
        #####################################################
        #####################################################

        # Consultando total de tarefas
        try:
            selectResult = driver.find_elements(By.CSS_SELECTOR, 'span[title="Quantidade de processos na tarefa"i]')[0].text
            logging.info('Quantidade de processo(s) encontrado(s): ' + str(selectResult))
            print('Quantidade de processo(s) encontrado(s): ' + str(selectResult))
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))
            logging.info('Ocorreu um erro ao capturar o total de processos')
            print('Ocorreu um erro ao capturar o total de processos')
            logging.info('---------------------------')
            image = Print(driver, caminhoImagesPrint)

        if int(selectResult) > 0:
            logging.info('Foram encontrados mais processos para realizar')
            print('Foram encontrados mais processos para realizar')

            self.localizarProcesso(driver, logging, caminhoImagesPrint, metodos, abas, dataBaseModel, log_unificado, pula=1)
        else:

            logging.info('Nao tem mais processos, finalizando . . .')
            print('Nao tem mais processos, finalizando . . .')

            # Altera para Janela RENAJUD
            logging.info('Fechando aba RENAJUD')
            print('Fechando aba RENAJUD')
            driver.switch_to.window(abas['RENAJUD'])

            driver.close()

            # Retorna ao PJe
            driver.switch_to.window(abas['PJe'])
            logging.info('Fechando aba PJe')
            print('Fechando aba PJe')

            driver.close()

        return self.listProcessos

    def Execute(self, driver, caminhoImagesPrint, logging, atividade, dataBaseModel, inicioTime,
         url, dataForm, xml, log_unificado):

        self.countEncaminhados = 0

        log_unificado.criar_arquivo_executados(
            ["COLETAR INFORMACOES DO PROCESSO", "CONSULTA PROCESSO NO RENAJUD", "ASSINAR DOCUMENTO", "ENCAMINHAR PARA PROSSEGUIR",]
        )

        # Controle de Abas
        abas = {}

        metodos = Metodos(url)
        driver.get(url)
        logging.info('##############################')
        logging.info('Robô iniciado')
        logging.info('Acesso da Url: ' + url)
        # time.sleep(5)

        driver.implicitly_wait(15)
        driver.set_page_load_timeout(420)

        autenticacao = Auth()
        autenticacao.Login(driver, logging, dataForm, url)

        # if dataForm['perfil'] != '':
        #     # Seleciona o perfil
        #     selecionarPerfil = Perfil(driver, logging, dataForm['perfil'])
        # else:
        # Aguarda para que seja feita a autenticacao manual
        element = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '.menu-usuario a')))

        abas['PJe'] = driver.window_handles[0]

        try:

            # Abre uma nova aba para RENAJUD
            logging.info('Abrindo aba RENAJUD')
            print('Abrindo aba RENAJUD')
            driver.execute_script("window.open('', '_blank');")

            try:
                abas['RENAJUD'] = driver.window_handles[1]
            except Exception as e:
                logging.info(repr(e))
                logging.info('erro window_handles')
                print('erro window_handles')
                print(repr(e))

            try:
                driver.switch_to.window(abas['RENAJUD'])
            except Exception as e:
                logging.info('erro switch_to window')
                print('erro switch_to window')
                logging.info(repr(e))
                print(repr(e))

            time.sleep(3)

            try:
                driver.get(self.urlRENAJUD)
            except Exception as e:
                logging.info('erro get')
                print('erro get')
                logging.info(repr(e))
                print(repr(e))

            time.sleep(5)

        except Exception as e:

            logging.info(repr(e))
            print(repr(e))
            logging.info('---------------------------')

            driver.close()

            try:

                # Abre uma nova aba para RENAJUD
                logging.info('Abrindo aba RENAJUD')
                print('Abrindo aba RENAJUD')
                driver.execute_script("window.open('', '_blank');")
                # actions = ActionChains(driver)
                # element = driver.find_element("tag name", "body")
                # actions.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

                # Abre o endereço e armazena
                try:
                    abas['RENAJUD'] = driver.window_handles[1]
                except Exception as e:
                    logging.info(repr(e))
                    logging.info('erro window_handles')
                    print('erro window_handles')
                    print(repr(e))

                try:
                    driver.switch_to.window(abas['RENAJUD'])
                except Exception as e:
                    logging.info('erro switch_to window')
                    print('erro switch_to window')
                    logging.info(repr(e))
                    print(repr(e))

                time.sleep(6)

                try:
                    driver.get(self.urlRENAJUD)
                except Exception as e:
                    logging.info('erro get')
                    print('erro get')
                    logging.info(repr(e))
                    print(repr(e))

                time.sleep(8)

            except Exception as e:

                logging.info(repr(e))
                print(repr(e))
                logging.info('---------------------------')

                # driver.close()

                # Retorna ao PJe
                logging.info('Voltando para aba PJe')
                print('Voltando para aba PJe')
                driver.switch_to.window(abas['PJe'])

                driver.close()

                return self.listProcessos

        # Retorna ao PJe
        logging.info('Voltando para aba PJe')
        print('Voltando para aba PJe')
        driver.switch_to.window(abas['PJe'])

        time.sleep(1)

        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     'a[title="Abrir menu"i]')))
            element.click()

            time.sleep(1)

            driver.find_element(By.CSS_SELECTOR, "#menu div.nivel-aberto ul li:first-child a").click()

            time.sleep(1)

            driver.find_element(By.CSS_SELECTOR, "#menu .nivel-overlay div.nivel-aberto ul li:first-child a").click()

            iframe = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, 'ngFrame')))

            driver.switch_to.frame(iframe)

            element = WebDriverWait(driver, 600).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.col-md-4:nth-child(3) #divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
            driver.execute_script("arguments[0].click();", element)

            logging.info('---------------------------')
            logging.info('Tarefa localizada: ' + str(atividade))
            logging.info('---------------------------')

            time.sleep(2)

            logging.info('Iniciando a busca pelo os processos...')

            self.localizarProcesso(driver, logging, caminhoImagesPrint, metodos, abas, dataBaseModel, log_unificado, pula=0)

            logging.info('---------------------------')
            logging.info('---------------------------')
            logging.info('---------------------------')

            # logging.info('---------------------------')
            # logging.info('Dados gerados apos conclusao da super classe')
            # logging.info(dataBaseModel)
            # logging.info('---------------------------')

            try:
                if self.listProcessos[2]:
                    for i in range(len(self.listProcessos[2])):
                        dataBaseModel['individual']['cod_processo'].append(str(self.listProcessos[2][i]))
                        dataBaseModel['individual']['processo_realizado'].append(1)
                        dataBaseModel['individual']['processo_nao_encontrado'].append(1)
                        dataBaseModel['individual']['tempo_execucao_individual_sec'].append(0)
            except:
                logging.info('Falha ao registrar os dados individual.')

            # logging.info('---------------------------')
            # logging.info('Dados gerados apos conclusao da super classe - individual')
            # logging.info(dataBaseModel)
            # logging.info('---------------------------')

            ###################################
            # Verificacao dos processos localizado e encaminhados
            ###################################

            if len(self.listProcessos[0]) > 0:
                logging.info('Lista de processos encontrados:')
                for i in range(len(self.listProcessos[0])):
                    logging.info('Processo: ' + str(self.listProcessos[0][i]))

                logging.info("Total de processos encontrados: " + str(len(self.listProcessos[0])))
                logging.info("Total de processos encaminhados: " + str(self.countEncaminhados))
            else:
                logging.info('Nenhum processo foi encontrado.')

            self.listProcessos.append(len(self.listProcessos[0]))
            self.listProcessos.append(self.countEncaminhados)

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

            # Registra base
            dataBaseModel['qtd_processos'] = (str(len(self.listProcessos[0])))
            dataBaseModel['qtd_processos_nao_localizados'] = str(len(self.listProcessos[2]))
            dataBaseModel['tempo_execucao_sec'] = str(timeTotal)

            logging.info('---------------------------')
            logging.info('Final Atividade:')
            logging.info(dataBaseModel)
            logging.info('---------------------------')

            # try:
            #     driver.close()
            # except:
            #     driver.quit()

            # logging.info('Lista completa para formulario:')
            # logging.info(str(self.listProcessos))
            # logging.info('---------------------------')

            return self.listProcessos

        except Exception as e:

            logging.info('---------------------------')
            logging.info('Atividade Erro:')
            logging.info(dataBaseModel)

            image = Print(driver, caminhoImagesPrint)
            logging.info('Falha ao concluir a tarefa especificada. - ' + str(atividade))
            logging.info('Finalizando o robo.')
            logging.info(repr(e))

            # Retorna valor caso haja algum erro durante a execucao
            return self.listProcessos