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

import logging


class Logging:

    pathLogExecucao = ""

    def __init__(self, pathLogExecucao):
        self._pathLogExecucao = pathLogExecucao

    def createLogExecucao(self, fileName):
        logging.basicConfig(filename=self._pathLogExecucao + fileName + '.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        return logging