import logging
from datetime import datetime


class Logging:

    pathLogExecucao = ""
    fileName = ""

    def __init__(self, pathLogExecucao):
        self._pathLogExecucao = pathLogExecucao
        self._fileName = datetime.now().strftime("%d_%m_%Y__%H_%M_%S")

    def createLogExecucao(self):
        logging.basicConfig(filename=self._pathLogExecucao + self._fileName + '.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        return logging