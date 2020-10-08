import os
import sys
import xml.etree.ElementTree as ET

from src.Default.Control.Logging import Logging
from src.Default.Forms.formMain import Form

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

    caminhoLogExecucao = [i.text for i in root.iter('directoryLog')][0] + "\\"

    # Iniciando Logs
    logging = Logging(caminhoLogExecucao)
    log = logging.createLogExecucao()

    log.info("Iniciando o robo.")

    form = Form(log, root)