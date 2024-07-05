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
import sys
class Logging:
    pathLogExecucao = ""
    def __init__(self, pathLogExecucao):
        self._pathLogExecucao = pathLogExecucao
    def createLogExecucao(self, fileName):
        file_handler = logging.FileHandler(filename= self._pathLogExecucao + fileName + '.log')
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]
        logging.basicConfig(handlers=handlers,
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        return logging