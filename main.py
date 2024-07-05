####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
### Laboratório M02
### Cientista-Chefe: Prof. Carlos Caminha
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

from src.Default.Controllers.Logging import Logging
# from src.Default.Models.Dataset import Dataset
from src.Default.Views.FormMain import Form

def resource_path(relative_path):
    """ Obtenha o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":

    xmlFile = resource_path("config\\config.xml")
    xmlFile = ET.parse(xmlFile)
    root = xmlFile.getroot()  # recupera a tag principal

    timeRegistre = datetime.now().strftime("%d_%m_%Y__%H_%M_%S")

    caminhoLogExecucao = [i.text for i in root.iter('directoryLog')][0] + "\\"

    # Iniciando Logs
    logging = Logging(caminhoLogExecucao)
    log = logging.createLogExecucao(timeRegistre)

    log.info("Iniciando o robo.")

    form = Form(log, root, timeRegistre)