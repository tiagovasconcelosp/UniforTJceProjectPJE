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

import csv

from src.Default.Models.Dataset import Dataset


class CSV:

    pathCsvExecucao = ""

    arquivoOutput = ""

    columnsGeral = ['id', 'data_aplicacao', 'qtd_processos', 'qtd_processos_nao_localizados', 'tempo_execucao_sec',
                    'qtd_clicks',
                    'qtd_erros_tentativa_processo', 'endereco_mac',
                    'qtd_erros_robo',
                    'cod_atividade',
                    # 'tempo_uso_aplicacao_sec',
                    'atividade_concluida',
                    'qtd_trafego_baixado_kb', 'qtd_requisicao',
                ]

    columnsIndividual = ['id', 'data_aplicacao', 'qtd_processos', 'qtd_processos_nao_localizados', 'tempo_execucao_sec',
                         'qtd_clicks',
                         'qtd_erros_tentativa_processo', 'endereco_mac',
                         'qtd_erros_robo',
                         'cod_atividade',
                         'atividade_concluida',
                         # 'tempo_uso_aplicacao_sec',
                         'qtd_trafeco_baixado_kb', 'qtd_requisicao',
                         # Dados Individual
                         'cod_processo', 'processo_realizado',
                         'processo_nao_encontrado',
                         'tempo_execucao_individual_sec',]

    def __init__(self, pathCsvExecucao):
        self.pathCsvExecucao = pathCsvExecucao

    def registraCsvTraffic(self, fileName, listaDadosGerarCsv, log):

        try:
            self.arquivoOutput = self.pathCsvExecucao + fileName + '.csv'

            fieldnames = ['url', 'milissegundos', 'kbytes']

            file = open(self.arquivoOutput, 'w', newline='')

            with file as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

                # Escreve Cabecalho
                writer.writeheader()
                # Escreve os dados
                for linha in listaDadosGerarCsv:
                    writer.writerow(linha)

            file.close()

        except Exception as e:
            log.info('Houve uma falha gravar o arquivo traffic.')
            log.info(repr(e))

    def registraCsvDatabase(self, listaDadosGerarCsv, log):

        try:
            self.arquivoOutput = self.pathCsvExecucao

            file = open(self.arquivoOutput, mode='a+', newline='')

            with file as csv_file:
                writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=self.columnsGeral, quoting=csv.QUOTE_MINIMAL)

                # Ex data {'data_aplicacao': '01/01/2000 00:00:00', 'qtd_clicks': '10', 'qtd_erros_tentativa_processo': '1'}
                writer.writerow(listaDadosGerarCsv)

            file.close()

        except Exception as e:
            log.info('Houve uma falha gravar o arquivo geral.')
            log.info(repr(e))

        try:

            listaDadosGerarCsv = listaDadosGerarCsv.values()

            dataset = Dataset(list(listaDadosGerarCsv), log)
            dataset.setDataGeral()
        except Exception as e:
            log.info('Nao foi possivel registrar os dados via banco.')
            log.info(repr(e))

    def registraCsvDatabaseIndividual(self, listaDadosIndividualGerarCsv, dadosIndividual, log):

        try:
            self.arquivoOutput = self.pathCsvExecucao

            list = []

            for x in range(len(dadosIndividual['cod_processo'])):

                file = open(self.arquivoOutput, mode='a+', newline='')

                listaDadosIndividualGerarCsv['cod_processo'] = dadosIndividual['cod_processo'][x]
                listaDadosIndividualGerarCsv['processo_realizado'] = dadosIndividual['processo_realizado'][x]
                listaDadosIndividualGerarCsv['processo_nao_encontrado'] = dadosIndividual['processo_nao_encontrado'][x]
                listaDadosIndividualGerarCsv['tempo_execucao_individual_sec'] = dadosIndividual['tempo_execucao_individual_sec'][x]

                with file as csv_file:
                    writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=self.columnsIndividual, quoting=csv.QUOTE_MINIMAL)

                    # Ex data {'data_aplicacao': '01/01/2000 00:00:00', 'qtd_clicks': '10', 'qtd_erros_tentativa_processo': '1'}
                    writer.writerow(listaDadosIndividualGerarCsv)

                list.append(listaDadosIndividualGerarCsv)

                file.close()

        except Exception as e:
            log.info('Houve uma falha gravar o arquivo individual.')
            log.info(repr(e))

        try:
            dataset = Dataset(list, log)
            dataset.setDataIndividual()
        except Exception as e:
            log.info('Nao foi possivel registrar os dados via banco.')
            log.info(repr(e))