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


class CSV:
    pathCsvExecucao = ""

    pathDatabaseGeral = "database-geral.csv"
    pathDatabaseIndividual = "database-individual.csv"

    columnsGeral = ['data_aplicacao', 'qtd_processos', 'qtd_processos_nao_localizados', 'tempo_execucao_min',
                    'qtd_clicks',
                    'qtd_erros_tentativa_processo', 'endereco_mac', 'qtd_erros_robo', 'cod_atividade',
                    'tempo_uso_aplicacao_min', 'qtd_trafeco_baixado_kb', 'qtd_requisicao']

    columnsIndividual = ['data_aplicacao', 'cod_processo', 'processo_localizado', 'tempo_execucao_individual_min',
                         'qtd_clicks',
                         'qtd_erros_tentativa_processo', 'endereco_mac', 'qtd_erros_robo', 'cod_atividade',
                         'tempo_uso_aplicacao_min', 'qtd_trafeco_baixado_kb', 'data_execucao_individual', ]

    def __init__(self, pathCsvExecucao):
        self._pathCsvExecucao = pathCsvExecucao

    def registraCsvTraffic(self, fileName, listaDadosGerarCsv):
        arquivoOutput = self._pathCsvExecucao + fileName + '.csv'

        fieldnames = ['url', 'milissegundos', 'kbytes']

        with open(arquivoOutput, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=';', fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)

            # Escreve Cabecalho
            writer.writeheader()
            # Escreve os dados
            for linha in listaDadosGerarCsv:
                writer.writerow(linha)

    def registraCsvDatabase(self, listaDadosGerarCsv):
        arquivoOutput = self._pathCsvExecucao

        del listaDadosGerarCsv['individual']

        with open(arquivoOutput, mode='a+', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter=';', fieldnames=self.columnsGeral, quoting=csv.QUOTE_MINIMAL)

            # Ex data {'data_aplicacao': '01/01/2000 00:00:00', 'qtd_clicks': '10', 'qtd_erros_tentativa_processo': '1'}
            writer.writerow(listaDadosGerarCsv)
