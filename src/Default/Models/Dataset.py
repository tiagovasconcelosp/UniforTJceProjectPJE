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
    tableName = ''
    columns = ''
    listData = ''
    log = ''

    hostname = 'kuringacomunicacao.com.br'
    username = 'domcow36_pontes_app'
    password = 'pontesKK1#'
    database = 'domcow36_db_pontes_app'

    def __init__(self, tableName, columns, listData, log):
        self._tableName = tableName
        self._columns = columns
        self._listData = listData
        self._log = log

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
            self.log.info('Valores inseridos com sucesso.')

        except mysql.connector.Error as error:
            self.log.info('Falha ao inserir valores na tabela: ' + str(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.log.info('Conexao fechada.')

    def setDataIndividual(self):
        try:
            connection = mysql.connector.connect(host=self.hostname,
                                                 database=self.database,
                                                 user=self.username,
                                                 password=self.password)
            cursor = connection.cursor()

            for linha in self.listData:
                mySql_insert_query = """INSERT INTO log_database_execucao
                                            VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

                record = tuple(linha)
                cursor.execute(mySql_insert_query, record)
                connection.commit()

            self.log.info('Valores inseridos com sucesso.')

        except mysql.connector.Error as error:
            self.log.info('Falha ao inserir valores na tabela: ' + str(error))

        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                self.log.info('Conexao fechada.')