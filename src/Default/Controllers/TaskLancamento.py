####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
### Laboratório M02
### Cientista-Chefe: Prof. Carlos Caminha
### Co-coordenador: Daniel Sullivan
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Controllers.Print import Print


class TaskLancamento:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countEncaminhados = 0

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.countEncaminhados = 0
        self.countEnviaProcesso = 0
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def localizarProcesso(self, firefox, numProcesso, codRecorrente, logging, caminhoImages):

       return False

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

        self.countEncaminhados = 0

        # try:

        time.sleep(3)

        element = WebDriverWait(firefox, 200).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 'a[title="Abrir menu"i]')))
        element.click()

        time.sleep(1)

        firefox.find_element(By.CSS_SELECTOR, "#menu div.nivel-aberto ul li:first-child a").click()

        time.sleep(1)

        firefox.find_element(By.CSS_SELECTOR, "#menu .nivel-overlay div.nivel-aberto ul li:first-child a").click()

        iframe = WebDriverWait(firefox, 60).until(
            EC.presence_of_element_located((By.ID, 'ngFrame')))

        firefox.switch_to.frame(iframe)

        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
        firefox.execute_script("arguments[0].click();", element)

        # Registra horario que iniciou a tarefa
        inicio = time.time()

        logging.info('---------------------------')
        logging.info('Tarefa localizada: ' + str(atividade))
        logging.info('---------------------------')

        time.sleep(2)

        logging.info('Iniciando a busca pelo os processos...')

        listDataProcessos = openXls.getDataProcessLancamentoXLS(xlsData, firefox, logging, xml)

        for i in range(len(listDataProcessos)):
            logging.info('Buscando o processo: ' + str(listDataProcessos[i][0]))
            self.localizarProcesso(firefox, listDataProcessos[i][0], listDataProcessos[i][1], logging,
                                   caminhoImages)

        logging.info('---------------------------')

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

        timeTotal = fim - inicio

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

        # print(self.listProcessos)

        try:
            firefox.close()
        except:
            firefox.quit()

        logging.info('Lista completa para formulario:')
        logging.info(str(self.listProcessos))
        logging.info('---------------------------')

        return self.listProcessos

        # except:
        #
        #     image = Print(firefox, caminhoImages)
        #     logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
        #     logging.info('Finalizando o robo.')
        #     logging.shutdown()
        #
        #     # Retorna valor caso haja algum erro durante a execucao
        #     return self.listProcessos