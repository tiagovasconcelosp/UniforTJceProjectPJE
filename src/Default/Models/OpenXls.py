####################################################
####################################################
### Projeto MPCE - Unifor - Universidade de Fortaleza
### Programa Cientista-Chefe, da Fundação Cearense de Apoio ao Desenvolvimento Científico e Tecnológico (Funcap)
### Laboratório M02
### Cientista-Chefe: Prof. Carlos Caminha
### Co-coordenador: Daniel Sullivan
### Bolsista Desenvolvedor do Projeto:
### Tiago Vasconcelos
### Email: tiagovasconcelosp@gmail.com
####################################################
####################################################

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

    def getDataProcessAguardandoSessaoXLS(self, data, firefox, logging, xml):

        try:
            # Ler o arquivo
            df = pd.read_excel(data)

            logging.info('Calculando os dados para execucao do robo...')

            # Filtra pelo dado X
            # Captura a coluna 0 do xml -> robo
            getX = df.loc[df[df.columns[int([i.text for i in xml.iter('columnRobo')][0])]].str.upper() == str([i.text for i in xml.iter('filterXLS')][0]).upper()]

            # Captura os valores do filtro
            # Captura a coluna 1 do xml -> cod processo
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnProcess')][0])]]

            # Armazena os valores
            listDataProcessos = getXdata.values.tolist()

            if len(listDataProcessos) > 0:

                logging.info('Elaboracao dos dados realizada com sucesso.')

                # ['3002930-23.2018.8.06.0112', '3000885-35.2019.8.06.0072',
                return listDataProcessos
            else:
                logging.info('Planilha esta vazia. Finalizando o robo.')
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

            logging.info('Calculando os dados para execucao do robo.')

            # Filtra pelo dado X
            # Captura a coluna 0 do xml -> robo
            getX = df.loc[df[df.columns[int([i.text for i in xml.iter('columnRobo')][0])]].str.upper() == str([i.text for i in xml.iter('filterXLS')][0]).upper()]

            ######################################################################################
            # Alteracao Solicitada Karyna
            ######################################################################################
            # Ordena os processos por DATA e em seguida por Sessao
            # getX = getX.sort_values([df.columns[int([i.text for i in xml.iter('columnData')][0])],
            #                          df.columns[int([i.text for i in xml.iter('columnSession')][0])],
            #                          df.columns[int([i.text for i in xml.iter('columnProcess')][0])]])

            ########################################
            # Processos
            # Captura os valores do filtro
            # Captura a coluna 1 do xml -> cod processo
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnProcess')][0])]]

            # Armazena os valores
            listProcessos = getXdata.values.tolist()
            ########################################

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
            # Captura o Sessao
            getXdata = getX[df.columns[int([i.text for i in xml.iter('columnSession')][0])]]

            # Formatada hora
            # listSessionProcessos = getXdata.apply(lambda h: '{}'.format(h))

            # Armazena os valores
            listSessionProcessos = getXdata.values.tolist()

            ########################################

            if len(listProcessos) > 0:
                if len(listProcessos) == len(listDateProcessos):
                    if len(listProcessos) == len(listSessionProcessos):

                        # ['3000323-07.2017.8.06.0004', '3000746-69.2019.8.06.0012']
                        # ['13-11-2020', '14-11-2020']
                        # ['Presencial', 'Virtual']
                        listAllProcess = [listProcessos, listDateProcessos, listSessionProcessos]
                        dictAllProcess = {}

                        for x in range(len(getCalendar)):

                            dictAllProcess[getCalendar[x]] = []

                            for i in range(len(listAllProcess[0])):
                                if (listAllProcess[1][i] == getCalendar[x]):
                                    # {'29-10-2020': [['3000746-69.2019.8.06.0012', '29-10-2020', 'Presencial'],
                                    #                 ['3000074-61.2017.8.06.9964', '29-10-2020', 'Presencial'],
                                    #                 ['3000323-07.2017.8.06.0008', '29-10-2020', 'Presencial']],
                                    #  '30-10-2020': [['3000323-07.2017.8.06.0007', '30-10-2020', 'Virtual']],
                                    #  '15-11-2020': [['3000323-07.2017.8.06.0006', '15-11-2020', 'Presencial']],
                                    #  '20-11-2020': [['3000323-07.2017.8.06.0004', '20-11-2020', 'Virtual'],
                                    #                 ['3000323-07.2017.8.06.0005', '20-11-2020', 'Virtual']]
                                    #                 }
                                    dictAllProcess[getCalendar[x]].append([listAllProcess[0][i], listAllProcess[1][i], listAllProcess[2][i]])

                        logging.info('Elaboracao dos dados realizada com sucesso.')

                        return dictAllProcess
                    else:
                        logging.info('Planilha esta com coluna Sessao faltando. Finalizando o robo.')
                        logging.shutdown()

                        try:
                            firefox.close()
                        except:
                            firefox.quit()

                        sys.exit(0)
                else:
                    logging.info('Planilha esta com coluna Data faltando. Finalizando o robo.')
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

    def getDataProcessTrasidarJulgadoXLS(self, data, firefox, logging, xml):

        try:
            # Ler o arquivo
            df = pd.read_excel(data)

            logging.info('Calculando os dados para execucao do robo...')

            # Filtra pelo dado X
            # Captura a coluna 0 do xml -> robo
            getX = df.loc[df[df.columns[int([i.text for i in xml.iter('columnRobo')][0])]].str.upper() == str(
                [i.text for i in xml.iter('filterXLS')][0]).upper()]

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

            # Armazena os valores convertendo em list
            listDateProcessos = listDateProcessos.tolist()

            if len(listDataProcessos) > 0:
                if len(listDataProcessos) == len(listDateProcessos):

                    # [['3000323-07.2017.8.06.0004', '13-11-2020'], ['3000746-69.2019.8.06.0012', '14-11-2020']]
                    listAllProcess = []

                    for x in range(len(listDataProcessos)):
                        listAllProcess.append([listDataProcessos[x], listDateProcessos[x]])

                    logging.info('Elaboracao dos dados realizada com sucesso.')

                    # [['3000323-07.2017.8.06.0004', '13-11-2020'], ['3000746-69.2019.8.06.0012', '14-11-2020']]
                    return listAllProcess

                else:
                    logging.info('Planilha esta com coluna Data faltando. Finalizando o robo.')
                    logging.shutdown()

                    try:
                        firefox.close()
                    except:
                        firefox.quit()

                    sys.exit(0)
            else:
                logging.info('Planilha esta vazia. Finalizando o robo.')
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