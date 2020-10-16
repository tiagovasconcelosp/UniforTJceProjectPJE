import sys
import pandas as pd

class OpenXls:

    pathXls = ""

    def __init__(self, pathXls):
        self._pathXls = pathXls

    def OpenFileXls(self, firefox, logging):

        try:
            xls = pd.ExcelFile(self._pathXls)
            logging.debug("Arquivo XLS carregado com sucesso.")
            return xls
        except:
            logging.exception('Falha ao carregar o arquivo XLS.')
            logging.info('Finalizando o robo')
            logging.shutdown()

            try:
                firefox.close()
            except:
                firefox.quit()

            sys.exit(0)

    def getDataXls(self, data, firefox, logging, xml):

        try:
            # Ler o arquivo
            df = pd.read_excel(data)

            # Filtra pelo dado X
            # Captura a coluna 0 do xml -> robo
            getX = df.loc[df[df.columns[int([i.text for i in xml.iter('columnRobo')][0])]].str.upper() == str([i.text for i in xml.iter('filterXLS')][0]).upper()]

            # Captura os valores do filtro
            # Captura a coluna 1 do xml -> cod processo
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnProcess')][0])]]

            # Armazena os valores
            listDataProcessos = getXdata.values.tolist()

            if len(listDataProcessos) > 0:
                # ['3002930-23.2018.8.06.0112', '3000885-35.2019.8.06.0072',
                return listDataProcessos
            else:
                logging.info('Planilha esta vazia. Finalizando o robo')
                logging.shutdown()

                try:
                    firefox.close()
                except:
                    firefox.quit()

                sys.exit(0)

        except:
            logging.exception('Falha ao ler dados da planilha.')
            logging.info('Finalizando o robo.')
            logging.shutdown()

            try:
                firefox.close()
            except:
                firefox.quit()

            sys.exit(0)