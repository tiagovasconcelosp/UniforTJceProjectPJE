import sys
import time

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

    def getDataProcessAguardandoSessaoXLS(self, data, firefox, logging, xml):

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

    def getDataProcessInclusaoXLS(self, data, firefox, logging, xml):

        try:
            # Ler o arquivo
            df = pd.read_excel(data)

            # Filtra pelo dado X
            # Captura a coluna 0 do xml -> robo
            getX = df.loc[df[df.columns[int([i.text for i in xml.iter('columnRobo')][0])]].str.upper() == str([i.text for i in xml.iter('filterXLS')][0]).upper()]

            # Ordena os processos por DATA e em seguida por HORA
            getX = getX.sort_values([df.columns[int([i.text for i in xml.iter('columnData')][0])], df.columns[int([i.text for i in xml.iter('columnHour')][0])]])

            # Captura os valores do filtro
            # Captura a coluna 1 do xml -> cod processo
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnProcess')][0])]]

            # Armazena os valores
            listDataProcessos = getXdata.values.tolist()

            ########################################
            # Captura a Data
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnData')][0])]]

            # Armazena os valores
            listDateProcessos = getXdata.dt.strftime('%d-%m-%Y')

            # Captura todas as dadas da planilha sem repeticao
            getCalendar = listDateProcessos.unique().tolist()

            # Armazena os valores convertendo em list
            listDateProcessos = listDateProcessos.tolist()

            ########################################

            ########################################
            # Captura o horario
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnHour')][0])]]

            # Armazena os valores
            listHourProcessos = getXdata.apply(lambda h: '{}'.format(h))
            listHourProcessos = listHourProcessos.tolist()

            ########################################

            if len(listDataProcessos) > 0:
                if len(listDateProcessos) == len(listDataProcessos):
                    if len(listHourProcessos) == len(listDataProcessos):

                        # ['3000323-07.2017.8.06.0004', '3000746-69.2019.8.06.0012']
                        # ['13-11-2020', '14-11-2020']
                        # ['13:30:00', '17:30:00']
                        listAllProcess = [listDataProcessos, listDateProcessos, listHourProcessos]
                        dictAllProcess = {}


                        for x in range(len(getCalendar)):

                            dictAllProcess[getCalendar[x]] = []

                            for i in range(len(listAllProcess[0])):
                                if (listAllProcess[1][i] == getCalendar[x]):
                                    # {'29-10-2020': [['3000746-69.2019.8.06.0012', '29-10-2020', '10:00:00'],
                                    #                 ['3000074-61.2017.8.06.9964', '29-10-2020', '11:00:00'],
                                    #                 ['3000323-07.2017.8.06.0008', '29-10-2020', '13:30:00']],
                                    #  '30-10-2020': [['3000323-07.2017.8.06.0007', '30-10-2020', '17:30:00']],
                                    #  '15-11-2020': [['3000323-07.2017.8.06.0006', '15-11-2020', '11:30:00']],
                                    #  '20-11-2020': [['3000323-07.2017.8.06.0004', '20-11-2020', '09:30:00'],
                                    #                 ['3000323-07.2017.8.06.0005', '20-11-2020', '10:30:00']]
                                    #                 }
                                    dictAllProcess[getCalendar[x]].append([listAllProcess[0][i], listAllProcess[1][i], listAllProcess[2][i]])

                        return dictAllProcess
                    else:
                        logging.info('Planilha esta com coluna Hora faltando registro. Finalizando o robo')
                        logging.shutdown()

                        try:
                            firefox.close()
                        except:
                            firefox.quit()

                        sys.exit(0)
                else:
                    logging.info('Planilha esta com coluna Data faltando registro. Finalizando o robo')
                    logging.shutdown()

                    try:
                        firefox.close()
                    except:
                        firefox.quit()

                    sys.exit(0)
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