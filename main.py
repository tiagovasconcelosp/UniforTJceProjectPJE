import os
import xml.etree.ElementTree as ET

from src.Default.Control.Logging import Logging
from src.Default.Forms.formMain import Form

if __name__ == "__main__":

    xmlFile = os.path.dirname(os.path.realpath(__file__)) + "\\config.xml"
    xmlFile = ET.parse(xmlFile)
    root = xmlFile.getroot()  # recupera a tag principal

    caminhoLogExecucao = os.path.dirname(os.path.realpath(__file__)) + "\\" + [i.text for i in root.iter('directoryLog')][0] + "\\"

    # Iniciando Logs
    logging = Logging(caminhoLogExecucao)
    log = logging.createLogExecucao()

    log.info("Iniciando o robo.")

    form = Form(log, root)