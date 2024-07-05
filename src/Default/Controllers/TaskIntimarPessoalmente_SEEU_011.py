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
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Controllers.Auth import Auth

from .Metodos import Metodos
import time

import os
import pyautogui as pag
import pandas as pd
from pathlib import Path

import glob
from datetime import datetime

import xml.etree.ElementTree as ET

class TaskIntimarPessoalmente_SEEU_011:
    
    def __init__(self, driver, caminhoImages, logging, atividade, dataBaseModel, 
                 inicioTime, url, dataform, acaoEmErro, xml, log_bi):
        # self.modelo = self.get_modelo_by_element(xml, "intimarPessoalmente")
        self.modelo = Metodos.load_child_tags_as_dict(xml=xml, father_element_name='intimarPessoalmente')
        self.log_bi = log_bi
        self.Execute(driver, caminhoImages, logging, atividade, dataBaseModel, 
                     inicioTime, url, dataform, acaoEmErro, xml)
    
    def adicionar_linha_pandas(self, df, dados):         
        df.loc[0] = dados         
        df.index = df.index + 1         
        #df.append(pd.Series(dados, index=df.columns[:len(dados)]), ignore_index=True)
        return df

    def atualizar_status_processo(self, df, processo, coluna, status):         
        indice = df[df["Processo"]==processo].index.values.astype(int)         
        df.at[indice[0], coluna] = status         
        return df

    def pagina_1(self, driver, methods, main_frame):
        # TROCA PARA O FRAME PRINCIPAL
        driver.switch_to.default_content()
        driver.switch_to.frame(main_frame)

        # TROCA FRAME
        user_main_frame = methods.get_element(driver, '//*[@name="userMainFrame"]') # '/html/body/div[2]/iframe'
        driver.switch_to.frame(user_main_frame)

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Mesa do(a) Analista Judiciário") is None:
            print("Espera Página de Mesa do Analista Judiciário")
            time.sleep(0.5)

        # ACESSA ABA OUTROS CUMPRIMENTOS
        tab = methods.get_element(driver, '//*[@name="tabOutrosCumprimentos"]')
        tab.click()

        # Clicar no número do Mandado
        table = methods.buscar_tabela_por_texto(driver, "Para Expedir", nao_incluso="Outros Cumprimentos")
        tr = methods.elemento_por_texto_em_lista_by_tag(table, "tr", "Mandado")
        td = tr.find_elements(by=By.TAG_NAME, value="td")
        tag_a = td[2].find_elements(by=By.TAG_NAME, value="a")
        tag_a = tag_a[0]
        quantidade = int(tag_a.text)
        if quantidade > 0:
            tag_a.click()
        return quantidade
        

    def pagina_2(self, driver, methods):

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Mandados") is None:
            print("Espera Página de Mandados")
            time.sleep(0.5)

        table = methods.get_element(driver, '//*[@id="cumprimentoCartorioMandadoForm"]/table[4]/tbody')
        tr = table.find_elements(by=By.TAG_NAME, value="tr")
        td = tr[0].find_elements(by=By.TAG_NAME, value="td")
        processo = td[4].text
        td[15].click()
        return processo
        

    def pagina_3(self, driver, methods):

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h4", "Arquivos") is None:
            print("Espera Página de Arquivos")
            time.sleep(0.5)

        file_type_select = methods.get_element(driver, '//*[@id="codTipoArquivo"]')
        file_type_select.send_keys('mandado')
        
        methods.get_element(driver, '//*[@id="content"]').click()
        time.sleep(0.5)
        
        model_select = methods.get_element(driver, '//*[@id="codModelo"]')
        while model_select.get_attribute('disabled'):
            print("Espera Select ficar habilitado")
            time.sleep(0.5)
        time.sleep(0.5)

        while methods.elemento_por_texto_em_lista_by_tag(model_select, "option", self.modelo['modelo']) is None:
            print("Espera Elemento do Modelo no Select")
            time.sleep(0.5)

        time.sleep(0.5)
        model_select.send_keys(self.modelo['modelo'])
        time.sleep(0.5)
        
        print("Clique no Digitar Texto")
        type_text = methods.get_element(driver, '//*[@id="digitarButton"]')
        type_text.click()
        print("Fim clique no Digitar Texto")

    def pagina_4(self, driver, methods):

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Digitar Documento") is None:
            print("Espera Página de Digitar Documento")
            time.sleep(0.5)

        continue_button = methods.get_element(driver, '//*[@id="submitButton"]')
        continue_button.click()

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Documento") is None:
            print("Espera Página de Documento")
            time.sleep(0.5)

        save_button = methods.get_element(driver, '//*[@id="submitButton"]')
        save_button.click()

    def pagina_5(self, driver, methods):

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h4", "Arquivos") is None:
            print("Espera Página de Arquivos")
            time.sleep(0.5)
        
        save_and_conclude_button = methods.get_element(driver, '//*[@id="finishButton"]')
        save_and_conclude_button.click()

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h4", "Arquivos") is None:
            print("Espera Página de Arquivos")
            time.sleep(0.5)

        alter_button = methods.get_element(driver, '//input[@id="editButton" and @value="Alterar"]')
        alter_button.click()

        time.sleep(1) # wait elements to prefill

    def pagina_6(self, driver, methods):
        warrant_classification = methods.get_element(driver, '//*[@id="cumprimentoCartorioMandadoForm"]/fieldset/table[1]/tbody/tr[10]/td[2]/input[1]') # Gratuito
        warrant_classification.click()

        warrant_cost_select = methods.get_element(driver, '//*[@id="codCustasMandado"]') # Citação, intimação e notificação
        warrant_cost_select.send_keys('c')

        linked_fullfilment = methods.get_element(driver, '//*[@id="cumprimentoCartorioMandadoForm"]/fieldset/table[1]/tbody/tr[12]/td[2]/input[2]') # não
        linked_fullfilment.click()

        digitaly_signed_by_judge = methods.get_element(driver, '//*[@id="rowAssinadoPorJuiz"]/td[2]/input[2]') # não
        digitaly_signed_by_judge.click()

        probation_officer_term = methods.get_element(driver, '//*[@id="prazoOficialJustica"]')
        for i in range(10): 
            probation_officer_term.send_keys(Keys.BACK_SPACE)
        probation_officer_term.send_keys('15')

        time.sleep(0.5)

        save_button = methods.get_element(driver, '//*[@id="saveButton"]')
        save_button.click()

    def pagina_7(self, driver, methods):

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h4", "Arquivos") is None:
            print("Espera Página de Arquivos")
            time.sleep(0.5)
        
        add_button = methods.get_element(driver, '//input[@id="editButton" and @value="Adicionar"]')
        add_button.click()

        time.sleep(2)

    def selecionar_anexo(self, trs, methods):
        despachos = ["Assistência Judiciária Gratuita",
                     "Conflito de Competência", 
                     "Exceção da Verdade", 
                     "Exceção de Incompetência, suspeição ou Impedimento",
                     "Incidente de Insanidade Mental", 
                     "Expedição de alvará de levantamento",
                     "Julgamento em Diligência",
                     "Mero expediente",
                     "Ordenação de entrega de autos",
                     "Requisição de Informações"]
        
        decisoes = ["A depender do julgamento de outra causa, de outro juízo ou declaração incidente",
                    "Força maior",
                    "Livramento Condicional", 
                    "Morte ou perda da capacidade", 
                    "Por decisão judicial", 
                    "Réu revel citado por edital", 
                    "Suspensão Condicional do Processo",
                    "Antecipação de tutela", 
                    "Comutação da pena", 
                    "Detração/Remição da Pena", 
                    "Direito de visita", 
                    "Indulto", 
                    "Liberdade provisória", 
                    "Liminar", 
                    "Livramento Condicional", 
                    "Medida protetiva", 
                    "Permissão de saída", 
                    "Prisão Domiciliar", 
                    "Progressão de regime", 
                    "Suspensão Condicional da Pena",
                    "Arquivamento", 
                    "Bloqueio/penhora on line", 
                    "Demonstração de existência de repercussão geral e manifestação sobre a questão constitucional", 
                    "Determinação de arquivamento de procedimentos investigatórios", 
                    "Devolução da carta rogatória ao juízo rogante", 
                    "Devolução dos autos à origem", 
                    "Distribuição", 
                    "Juízo provisório para medidas urgentes", 
                    "Quebra de sigilo bancário", 
                    "Quebra de sigilo fiscal", 
                    "Quebra de sigilo telemático",
                    "Regressão de Medida Sócio-Educativa",
                    "Regressão de Regime",
                    "Assistência judiciária gratuita", 
                    "Liberdade Provisória", 
                    "Liminar", 
                    "Medida protetiva",
                    "Assistência Judiciária Gratuita", 
                    "Decisão anterior", 
                    "Detração/Remição", 
                    "Liminar", 
                    "Livramento Condicional", 
                    "Medida protetiva", 
                    "Medida protetiva determinada por autoridade policia", 
                    "Prisão", 
                    "Revogação da Suspensão do Processo", 
                    "Suspensão Condicional da Pena", 
                    "Cancelamento da distribuição",
                    "Com efeito suspensivo", 
                    "Sem efeito suspensivo", 
                    "Decisão de Saneamento e de Organização", 
                    "Decisão Interlocutória de Mérito", 
                    "deferimento",
                    "Denúncia", 
                    "Exceção de Impedimento ou Suspeição", 
                    "Exceção de incompetência",
                    "Desistência de Recurso", 
                    "Medida protetiva determinada por autoridade policial", 
                    "Domiciliar", 
                    "Embargos", 
                    "Reclamação", 
                    "Impedimento", 
                    "Incompetência", 
                    "Remição", 
                    "Suspeição", 
                    "Impedimento ou Suspeição", 
                    "Incompetência",  
                    "Inclusão em Regime Disciplinar Diferenciado", 
                    "pagamento", 
                    "Recambiamento de Preso", 
                    "Saída Temporária", 
                    "Trabalho Externo", 
                    "Transferência da Execução da Pena", 
                    "Transferência para outro Estabelecimento Penal", 
                    "Indeferimento", 
                    "Liminar", 
                    "Medida protetiva", 
                    "Liminar Prejudicada", 
                    "Outras Decisões", 
                    "Pena / Medida", 
                    "Preventiva", 
                    "Temporária", 
                    "Prorrogação de cumprimento de pena/medida de segurança", 
                    "Provisória",
                    "Recurso", "Reforma de decisão anterior", 
                    "Relaxamento do Flagrante", 
                    "Suscitação de Conflito de Competência", 
                    "Unificação e Soma de Penas"]
        
        despachos = [x.upper() for x in despachos]
        decisoes = [x.upper() for x in decisoes]

        funcionou = False
        opcao = None
        indice = 0
        for indice, tr in enumerate(trs):
            tag_b = tr.find_elements(by=By.TAG_NAME, value="b")
            if len(tag_b)>0:
                tag_b = tag_b[0]
                for despacho in despachos:
                    if despacho in tag_b.text.upper():
                        funcionou = True
                        opcao = despacho
                        if methods.get_elements_by_tag(trs[indice+2], "input") is not None:
                            return funcionou, "Despacho: "+opcao, indice
                for decisao in decisoes:
                    if decisao in tag_b.text.upper():
                        funcionou = True    
                        opcao = decisao
                        if methods.get_elements_by_tag(trs[indice+2], "input") is not None:
                            return funcionou, "Decisão: "+opcao, indice
        return funcionou, "Não Encontrado", indice

    def pagina_8(self, driver, methods, logging):
        
        pop_up_frame = methods.get_element(driver, '//iframe[@frameborder="0"]')

        pop_up_name = pop_up_frame.get_attribute('name')
        pop_up_name = "_".join(pop_up_name.split("_")[:-1])

        driver.switch_to.frame(pop_up_frame)

        table = methods.get_element(driver, '//*[@id="cumprimentoCartorioMandadoForm"]/table[1]/tbody')
        trs = methods.get_elements_by_tag(table, "tr")
        
        funcionou, opcao, indice = self.selecionar_anexo(trs, methods)

        if(funcionou):
            input_check = methods.get_elements_by_tag(trs[indice+2], "input")
            input_check[0].click() 
            time.sleep(0.5)
            select = methods.get_element(driver, '//*[@id="selectButton"]')
            select.click()
        else:
            mensagem = "Não foi possível encontrar checkbox de um documento válido. Realize o procedimento adequado para esse caso."
            self.mensagem(logging, "Não foi possível encontrar checkbox de um documento válido. Aguardando o usuário realizar procedimento adequado.")
            pag.alert(mensagem)

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Seleção de Documentos") is not None:
            print("Espera Sair de Seleção de Documentos")
            time.sleep(0.5)

        return opcao

    def pagina_9(self, driver, methods, main_frame):
        driver.switch_to.default_content()
        driver.switch_to.frame(main_frame)
        user_main_frame = methods.get_element(driver, '//*[@name="userMainFrame"]') # '/html/body/div[2]/iframe'
        driver.switch_to.frame(user_main_frame)

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h4", "Arquivos") is None:
            print("Espera Página de Arquivos")
            time.sleep(0.5)

        time.sleep(1)

        sing_and_ship_button = methods.get_element(driver, '//*[@id="postergarButton" and @value="Postergar Assinatura"]')
        sing_and_ship_button.click()


    def retorno_processos(self, driver, methods, main_frame):
        # area_atuacao = methods.get_element(driver, '//*[@id="areaatuacao"]')
        driver.switch_to.default_content()
        driver.switch_to.frame(main_frame)
        area_atuacao = methods.elemento_por_texto_em_lista_by_tag(driver, "a", "Início")
        area_atuacao.click()
    

    def get_download_path(self):
        """Returns the default downloads path for linux or windows"""
        if os.name == 'nt':
            import winreg
            sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
            downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                location = winreg.QueryValueEx(key, downloads_guid)[0]
            return location
        return os.path.join(os.path.expanduser('~'), 'downloads')


    def identifica_ultimo_crdownload(self, folder_path, timestamp, logging):
        file_type = '\*crdownload' # se nao quiser filtrar por extenção deixe apenas *
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
        jnlp = "assinador-"+str(data_arq.tm_mday)\
                           +"-"+str(data_arq.tm_mon)\
                           +"-"+str(data_arq.tm_year)\
                           +"_" +str(data_arq.tm_hour)\
                           +"-"+str(data_arq.tm_min)+".jnlp"
        path_jnlp = f"{path_jnlp}"+jnlp
        os.rename(f"{crdownload}", path_jnlp)
        return path_jnlp


    def executando_assinador(self, path_jnlp):
        if " " in path_jnlp:
            partes = path_jnlp.split("\\")
            path_jnlp = ""
            for parte in partes:
                if " " in parte:
                    parte = '"'+parte+'"'
                path_jnlp = os.path.join(path_jnlp, parte)
        path_jnlp = path_jnlp.replace(":", ":\\")
        os.system('start '+path_jnlp)


    def realizar_assinatura_lote(self, driver, methods, main_frame, caminhoImages, logging):
        driver.switch_to.default_content()
        driver.switch_to.frame(main_frame)
        cumprimentos = methods.elemento_por_texto_em_lista_by_tag(driver, "a", "Cumprimentos")
        cumprimentos.click()
        ul_mandados = methods.elemento_por_texto_em_lista_by_tag(driver, "ul", "Mandados")
        mandados = methods.elemento_por_texto_em_lista_by_tag(ul_mandados, "a", "Mandados")
        mandados.click()
        para_assinar = methods.elemento_por_texto_em_lista_by_tag(ul_mandados, "a", "Para Assinar (Minhas Pendências)")
        para_assinar.click()
        user_main_frame = methods.get_element(driver, '//*[@name="userMainFrame"]') # '/html/body/div[2]/iframe'
        driver.switch_to.frame(user_main_frame)
        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Mandados com Assinatura Pendente - Minhas Pendências") is None:
            print("Espera Página de Assinatura Pendente")
            time.sleep(0.5)
        # quantidade = 1
        # while quantidade > 0:
        # IDENTIFICA SE HÁ ALGO PARA ASSINAR
        if methods.elemento_por_texto_em_lista_by_tag(driver, "td", "Nenhum registro encontrado") is None:

            # Validando com Luciano
            try:
                # Exibe 100 processos por pagina
                select = Select(driver.find_element(By.CSS_SELECTOR, 'select[name="cumprimentoCartorioMandadoPageSizeOptions"i]'))
                select.select_by_visible_text('100 por pág.')
                time.sleep(3)
            except Exception as e:
                logging.info(repr(e))
                print(repr(e))
                logging.info('Nao foi possivel exibir 100 por pagina... Continuando. . .')
                print('Nao foi possivel exibir 100 por pagina... Continuando. . .')
                self.log_bi.enviar_erro(num_processo="Lote",
                                        passo_executado="Selecionar 100 por página",
                                        mensagem=repr(e))


            check_todos = methods.buscar_componente_por_value(driver, 'checker')
            check_todos.click()
            timestamp = time.time()
            assinar = methods.buscar_componente_por_value(driver, 'Assinar')
            assinar.click()
            time.sleep(3)
            folder_path = self.get_download_path()
            crdownload = self.identifica_ultimo_crdownload(folder_path, timestamp, logging)
            path_jnlp = self.renomear_arquivo(crdownload)
            self.executando_assinador(path_jnlp)
            self.mensagem(logging, "Início processo de assinatura no assinador - Outra Tecnologia")
            while not self.present(caminhoImages + "deseja_executar.png"):
                print("Espera Carregar Confirmação de Execução")
                time.sleep(0.5)
            self.click(caminhoImages + "executar.png")
            while not self.present(caminhoImages + "assinador_tipo.png"):
                print("Espera Carregar Escolha de Certificado")
                time.sleep(0.5)
                if self.present(caminhoImages + "deseja_continuar.png"):
                    self.click(caminhoImages + "continuar.png")        
            self.click(caminhoImages + "token_a3.png")
            self.click(caminhoImages + "assinar.png")
            time.sleep(7)
            while self.present(caminhoImages + "aguarda_assinatura.png"):
                print("Espera Terminar de Assinar")
                time.sleep(0.5)
            print("assinou")
            print("Terminou Espera")
            # quantidade = methods.texto_by_xpath(driver, '//*[@id="navigator"]/div[2]')
            # quantidade = quantidade.split(" registro")[0]
            # quantidade = int(quantidade)
            # if quantidade < 1:
            return True
        else:
            return False

        

    def present(self, imagem, confianca=0.80):
        return bool(pag.locateOnScreen(imagem, confidence=confianca))
    
    def click(self, imagem, confianca=0.82):
        pag.click(pag.locateOnScreen(imagem, confidence=confianca))

    def mensagem(self, logging, mensagem):
        logging.info(mensagem)
        print(mensagem)


    def Execute(self, driver, caminhoImages, logging, atividade, dataBaseModel, 
                inicioTime, url, dataform, acaoEmErro, xml):
        methods = Metodos(url)
        autenticacao = Auth()

        # GERA PASTA e NOME DO ARQUIVO DE EXECUTADOS
        self.log_bi.criar_arquivo_executados(['Selecionar Processo para Analisar', 'Selecionar Modelo', 
                                              'Confirmar Conteúdo', 'Salvar e Concluir', 'Editar Informações', 
                                              'Adicionar', 'Selecionar Documento', 'Postergar Assinatura'])

        self.mensagem(logging, "Gerou planilha de processos")

        # ACESSA PÁGINA DO SEEU
        driver.get(url)

        # TEMPO PARA FINALIZAR CARREGAMENTO
        time.sleep(1.5)

        # TROCA PARA O FRAME PRINCIPAL
        main_frame = methods.get_element(driver, '//*[@id="mainFrame"]')
        driver.switch_to.frame(main_frame)

        # REALIZA A AUTENTICAÇÃO PELO USUÁRIO
        # primeira = True
        # if primeira:
        #     mensagem = 'Realize o login com o Login com usuário e senha, resolva o captcha e em seguida clique em OK para prosseguir.'
        #     self.mensagem(logging, "Aguardando Login com usuário e senha no Portal SEEU")
        #     pag.alert(mensagem)
        #     primeira = False
        
        autenticacao.LoginSeeu(driver, logging, dataform, url)

        self.mensagem(logging, "Acessou SEEU")

        while methods.elemento_por_texto_em_lista_by_tag(driver, "h3", "Selecione a Área de Atuação:") is None:
            print("Espera Página de Área de Atuação")
            time.sleep(0.5)

        # ACESSA AS MESAS DOS ANALISTAS JUDICIÁRIOS 
        mesas = [i.text for i in xml.iter('mesa')]

        for indice, mesa in enumerate(mesas):
            # ACESSA A MESA
            if indice > 0:
                driver.switch_to.default_content()
                driver.switch_to.frame(main_frame)
                # TROCA FRAME
                user_main_frame = methods.get_element(driver, '//*[@name="userMainFrame"]') # '/html/body/div[2]/iframe'
                driver.switch_to.frame(user_main_frame)
                # CLICA PARA ALTERAR A ÁREA DE ATUAÇÃO
                altera_mesa = methods.get_element(driver, '//*[@id="alterarAreaAtuacao"]')
                altera_mesa.click()
                # ACESSA FRAME DO POP UP
                pop_up_frame = methods.get_element(driver, '//iframe[@frameborder="0"]')
                pop_up_name = pop_up_frame.get_attribute('name')
                pop_up_name = "_".join(pop_up_name.split("_")[:-1])
                driver.switch_to.frame(pop_up_frame)

            court = methods.get_element(driver, f'//*[@title="{mesa}"]')
            court.click()
            self.mensagem(logging, "Acessou a mesa do analista: "+mesa)
            continuacao = True
            while continuacao:
                continuacao = False
                # PÁGINA 1
                quantidade = self.pagina_1(driver, methods, main_frame)
                self.mensagem(logging, "Finalizou Página 1")
                # quantidade = 0
                if quantidade > 0:
                    continuacao = True
                    # PÁGINA 2
                    processo = self.pagina_2(driver, methods)
                    self.log_bi.adicionar_processo(processo=processo)
                    self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Selecionar Processo para Analisar",
                                                         atualizacao='Realizado')
                    # PÁGINA 3
                    try:
                        self.pagina_3(driver, methods)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Selecionar Modelo",
                                                         atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 3")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Selecionar Modelo",
                                                mensagem=repr(e))

                    # PÁGINA 4
                    try:
                        self.pagina_4(driver, methods)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                             etapa="Confirmar Conteúdo",
                                                             atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 4")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Confirmar Conteúdo",
                                                mensagem=repr(e))
                    # PÁGINA 5
                    try:
                        self.pagina_5(driver, methods)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                             etapa="Salvar e Concluir",
                                                             atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 5")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Salvar e Concluir",
                                                mensagem=repr(e))
                    # PÁGINA 6
                    try:
                        self.pagina_6(driver, methods)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Editar Informações",
                                                         atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 6")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Editar Informações",
                                                mensagem=repr(e))
                    # PÁGINA 7
                    try:
                        self.pagina_7(driver, methods)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Adicionar",
                                                         atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 7")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Adicionar",
                                                mensagem=repr(e))
                    # PÁGINA 8
                    try:
                        documento = self.pagina_8(driver, methods, logging)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Selecionar Documento",
                                                         atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 8")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Selecionar Documento",
                                                mensagem=repr(e))
                    # PÁGINA 9
                    try:
                        self.pagina_9(driver, methods, main_frame)
                        self.log_bi.atualizar_etapa_processo(processo=processo,
                                                         etapa="Postergar Assinatura",
                                                         atualizacao='Realizado')
                        self.mensagem(logging, "Finalizou Página 9")
                    except Exception as e:
                        self.log_bi.enviar_erro(num_processo=processo,
                                                passo_executado="Postergar Assinatura",
                                                mensagem=repr(e))
                    
                    # Retornar para Mesa do Analista Judiciário 
                    self.retorno_processos(driver, methods, main_frame)
                    self.mensagem(logging, "Retorna para Mesa do Analista Judiciário")
                else:
                    self.log_bi.realizar_requisicao("Lote", "Início Assinatura", "Busca Assinar em Lote")
                    retorno = self.realizar_assinatura_lote(driver, methods, main_frame, caminhoImages, logging)
                    self.retorno_processos(driver, methods, main_frame)
                    if retorno:
                        self.mensagem(logging, "Realizou assinatura em Lote")
                        self.log_bi.realizar_requisicao("Lote", "Fim Assinatura", "Realizou assinatura em Lote")
                    else: 
                        self.mensagem(logging, "Sem processos para assinar")
                        self.log_bi.realizar_requisicao("Lote", "Fim Assinatura", "Sem processos para assinar")
            print("Fim de um ciclo")
        self.mensagem(logging, "Finalizou Execução")
