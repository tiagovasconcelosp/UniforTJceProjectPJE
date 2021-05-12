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

import sys
import pandas as pd


class DataCsv:
    pathDatabaseGeral = "\database-geral.csv"
    pathDatabaseIndividual = "\database-individual.csv"
    pathDatabase = ''

    columnsGeral = ['data_aplicacao', 'qtd_processos', 'qtd_processos_nao_localizados', 'tempo_execucao_min',
                    'qtd_clicks',
                    'qtd_erros_tentativa_processo', 'endereco_mac', 'qtd_erros_robo', 'cod_atividade',
                    'tempo_uso_aplicacao_min', 'qtd_trafeco_baixado_kb', ]

    columnsIndividual = ['data_aplicacao', 'cod_processo', 'processo_localizado', 'tempo_execucao_individual_min',
                         'qtd_clicks',
                         'qtd_erros_tentativa_processo', 'endereco_mac', 'qtd_erros_robo', 'cod_atividade',
                         'tempo_uso_aplicacao_min', 'qtd_trafeco_baixado_kb', 'data_execucao_individual', ]

    def __init__(self, pathDatabase):
        self._pathDatabase = pathDatabase

    def OpenFileGeralCsv(self, logging):
        csv = pd.read_csv(self._pathDatabase + self.pathDatabaseGeral, header=None, names=self.columnsGeral,
                          index_col=0, sep=';')

        return csv

    def OpenFileIndividualCsv(self, logging):
        csv = pd.read_csv(self._pathDatabase + self.pathDatabaseIndividual, header=None, names=self.columnsIndividual,
                          index_col=0, sep=';')

        return csv

    def getDataGeral(self, logging):
        return False

    def setDataGeral(self, dados, logging):
        return False

    def setDataIndividual(self, dados, logging):
        return False

    def getDataFull(self, logging):
        return False
