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
from selenium.webdriver.support.wait import WebDriverWait

from src.Default.Controllers.Print import Print


class TaskAssinaturaProcessos:

    # [processoLocalizado][encaminhados][processoNaoLocalizado] ~+ [totalEncontrado][totalEncaminhado][timeExecucao][totalProcessosNaoLocalizado]
    listProcessos = [[], [], [], ]
    countAssinados = 0

    listAtividades = [
        '(TR) Assinar decisão de emb. declaração',
        '(TR) Assinar inteiro teor',
        '(TR) Assinar decisão sobre recurso',
        '(TR) Sentença', # Corrigir e verificar os nomes das atividades
    ]

    def __init__(self, firefox, caminhoImages, logging, xls, book, atividade, xml):
        # Feito para zerar lista de processos
        self.listProcessos = [[], [], [], ]
        self.Execute(firefox, caminhoImages, logging, xls, book, atividade, xml)

    def checkQtdProcessosAtividade(self, firefox, atividade):
        element = firefox.find_element(By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i] span.quantidadeTarefa').text

        if int(element) > 0:
            return True
        else:
            return False

    def assinaAtividadeEmbDeclaracao(self, firefox, logging, caminhoImages):
        print(0)

    def assinaAtividadeInteiroTeor(self, firefox, atividade, logging, caminhoImages):

        element = WebDriverWait(firefox, 120).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#divTarefasPendentes .menuItem a[title="' + str(atividade) + '"i]')))
        firefox.execute_script("arguments[0].click();", element)


        print(0)

    def assinaAtividadeDecisaoSobreRecurso(self, firefox, logging, caminhoImages):
        print(0)

    def assinaAtividadeSentenca(self, firefox, logging, caminhoImages):
        print(0)

    def Execute(self, firefox, caminhoImages, logging, openXls, xlsData, atividade, xml):

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

        # Registra horario que iniciou a tarefa
        inicio = time.time()

        # Tarefa inteiro teor
        if self.checkQtdProcessosAtividade(firefox, self.listAtividades[1]):
            logging.info('---------------------------')
            logging.info('Tarefa localizada: ' + str(self.listAtividades[1]))
            logging.info('---------------------------')
            self.assinaAtividadeInteiroTeor(firefox, self.listAtividades[1], logging, caminhoImages)

        time.sleep(2)

        logging.info('Iniciando a busca pelo os processos...')




        ###################################
        # Verificacao dos processos localizado e encaminhados
        ###################################

        # if len(self.listProcessos[0]) > 0:
        #     logging.info('Lista de processos encontrados:')
        #     for i in range(len(self.listProcessos[0])):
        #         logging.info('Processo: ' + str(self.listProcessos[0][i]))
        #
        #     logging.info("Total de processos encontrados para assinatura: " + str(len(self.listProcessos[0])))
        #     logging.info("Total de processos assinados: " + str(self.countEncaminhados))
        # else:
        #     logging.info('Nenhum processo foi encontrado.')
        #
        # self.listProcessos.append(len(self.listProcessos[0]))
        # self.listProcessos.append(self.countEncaminhados)
        #
        # logging.info('---------------------------')

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

        # if len(self.listProcessos[2]) > 0:
        #     logging.info('Lista de processos nao foram assinados:')
        #     for i in range(len(self.listProcessos[2])):
        #         logging.info('Processo: ' + str(self.listProcessos[2][i]))
        #     logging.info("Total de processos que nao foram assinados: " + str(len(self.listProcessos[2])))
        # else:
        #     logging.info('Todos os processos foram assinados corretamente.')
        #
        # self.listProcessos.append(len(self.listProcessos[2]))
        #
        # logging.info('---------------------------')

        firefox.switch_to.default_content()

        # try:
        #     firefox.close()
        # except:
        #     firefox.quit()

        # logging.info('Lista completa para formulario:')
        # logging.info(str(self.listProcessos))
        # logging.info('---------------------------')
        #
        # return self.listProcessos

        # except:
        #
        #     image = Print(firefox, caminhoImages)
        #     logging.exception('Falha ao concluir a tarefa especificada. - ' + str(atividade))
        #     logging.info('Finalizando o robo.')
        #     logging.shutdown()
        #
        #     # Retorna valor caso haja algum erro durante a execucao
        #     return self.listProcessos










