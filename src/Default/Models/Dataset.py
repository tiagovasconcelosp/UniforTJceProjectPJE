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

import mysql.connector

class Dataset:
    listData = ''
    log = ''

    hostname = 'kuringacomunicacao.com.br'
    username = 'domcow36_pontes_app'
    password = 'pontesKK1#'
    database = 'domcow36_db_pontes_app'

    def __init__(self, listData, log):
        self.listData = listData
        self.log = log
        # self.log.info(listData)

    def setDataGeral(self):
        try:
            connection = mysql.connector.connect(host=self.hostname,
                                                 database=self.database,
                                                 user=self.username,
                                                 password=self.password)
            cursor = connection.cursor()

            mySql_insert_query = """INSERT INTO log_database_execucao
                                                VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

            record = tuple(self.listData)
            cursor.execute(mySql_insert_query, record)
            connection.commit()
            self.log.info('Dados SQL inserido com sucesso - Geral.')

        except mysql.connector.Error as error:
            self.log.info('Falha ao inserir valores na tabela: ' + str(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.log.info('Conexao SQL finalizada - Geral.')

    def setDataIndividual(self):
        try:
            connection = mysql.connector.connect(host=self.hostname,
                                                 database=self.database,
                                                 user=self.username,
                                                 password=self.password)
            cursor = connection.cursor()

            for linha in self.listData:

                linha2 = linha.values()

                linha2 = list(linha2)

                # linha2[13] = linha2[13][0]
                # linha2[14] = linha2[14][0]
                # linha2[15] = linha2[15][0]
                # linha2[16] = linha2[16][0]

                mySql_insert_query = """INSERT INTO log_database_processo
                                                    VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

                record = tuple(linha2)
                cursor.execute(mySql_insert_query, record)
                connection.commit()

            self.log.info('Dados SQL inserido com sucesso - Individual.')

        except mysql.connector.Error as error:
            self.log.info('Falha ao inserir valores na tabela: ' + str(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.log.info('Conexao SQL finalizada - Individual.')