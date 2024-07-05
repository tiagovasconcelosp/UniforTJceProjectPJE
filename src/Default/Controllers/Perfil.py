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

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class Perfil:

    def __init__(self, driver, logging, desPerfil):
        self.Perfil(driver, logging, desPerfil)

    def Perfil(self, driver, logging, desPerfil):

        try:

            codP = str(self.codigoPerfil(desPerfil))

            logging.info('Codigo do perfil selecionado: ' + codP)
            print('Codigo do perfil selecionado: ' + codP)

            if codP == '999':
                print('Perfil nao identificado . . .')
                logging.info('Perfil nao identificado . . .')
                logging.info('Encerrando robo . . .')
                logging.shutdown()

                try:
                    driver.close()
                except:
                    driver.quit()

            logging.info('Aguardando autenticação . . .')
            print('Aguardando autenticação . . .')

            # foi alterado para 300s, antes estava 20s
            # aguarda para que seja feita a autenticacao manual
            element = WebDriverWait(driver, 300).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     '.menu-usuario a')))
            element.click()

            select = Select(driver.find_element(By.CSS_SELECTOR, "form#papeisUsuarioForm select"))
            select.select_by_visible_text(desPerfil)

            logging.info('Perfil selecionado com sucesso! Selecionado: ' + str(desPerfil))
            print('Perfil selecionado com sucesso! Selecionado: ' + str(desPerfil))

        except Exception as e:
            logging.exception('Falha ao autenticar ou selecionar perfil')
            logging.exception('Falha em selecionar o perfil indicado com codigo ' + str(self.codigoPerfil(desPerfil)))
            logging.info('Perfil "' + str(desPerfil) + '" nao identificado.')
            logging.info('Finalizando o robo.')
            logging.info(repr(e))
            logging.shutdown()

            try:
                driver.close()
            except:
                driver.quit()

    def codigoPerfil(self, desPerfil):

        # ##############################################
        # Codigo fica especificado de acordo com codigo atribuido no sistema - PJE
        # Não apagar, pode servir de consulta para futuros robôs
        # ##############################################

        # if desPerfil == '5ª Turma Recursal / Presidência da 5ª Turma Recursal / Juiz de Direito' \
        #         or desPerfil == 'Gab. 3 - 5ª Juizado Especial Cível e Criminal de Iguatu / Juiz de Direito' \
        #         or desPerfil == '1ª Turma Recursal / Gab. 1 - 1ª Turma Recursal / Juiz Titular' \
        #         or desPerfil == '2ª Turma Recursal / Gab. 1 - 2ª Turma Recursal / Juiz Titular' \
        #         or desPerfil == '1ª Turma Recursal / Gab. 3 - 1ª Turma Recursal / Juiz Substituto' \
        #         or desPerfil == '2ª Turma Recursal / Gab. 3 - 2ª Turma Recursal / Juiz Titular' \
        #         or desPerfil == '5ª Turma Recursal Provisória / Gab. 2 - 5ª Turma Recursal Provisória / Juiz Titular':
        #     codPerfil = 0
        # elif desPerfil == '5ª Turma Recursal Provisória / Gab. 1 - 5ª Turma Recursal Provisória / Juiz Titular' \
        #         or desPerfil == '6ª Turma Recursal Provisória / Gab. 2 - 6ª Turma Recursal Provisória / Juiz Titular' \
        #         or desPerfil == 'Gab. 3 - 5ª Juizado Especial Cível e Criminal do Crato / Juiz Substituto':
        #     codPerfil = 1
        # elif desPerfil == '5ª Turma Recursal Provisória / Secretaria de Colegiado / Diretor de Secretaria' \
        #         or desPerfil == '2ª Turma Recursal / Gab.da Presidência da 2ª Turma Recursal / Juiz de Direito' \
        #         or desPerfil == '2ª Turma Recursal / Secretaria de Colegiado / Servidor Geral' \
        #         or desPerfil == '6ª Turma Recursal Provisória / Gab. 1 - 6ª Turma Recursal Provisória / Juiz Titular':
        #     codPerfil = 2
        # elif desPerfil == '5ª Turma Recursal Provisória / Secretaria de Colegiado / Secretário da Sessão' \
        #         or desPerfil == '6ª Turma Recursal Provisória / Gab. da Presidência da 6ª Turma Recursal / Juiz Titular' \
        #         or desPerfil == '5ª Turma Recursal Provisória / Secretaria de Colegiado / Servidor Geral':
        #     codPerfil = 3
        # elif desPerfil == '6ª Turma Recursal Provisória / Secretaria de Colegiado / Diretor de Secretaria' \
        #         or desPerfil == '2ª Turma Recursal / Secretaria de Colegiado / Diretor de Secretaria':
        #     codPerfil = 4
        # elif desPerfil == '6ª Turma Recursal Provisória / Secretaria de Colegiado / Secretário da Sessão' \
        #         or desPerfil == '2ª Turma Recursal / Secretaria de Colegiado / Secretário da Sessão' \
        #         or desPerfil == '6ª Turma Recursal Provisória / Secretaria de Colegiado / Servidor Geral':
        #     codPerfil = 5
        # elif desPerfil == '4ª Turma Recursal / Gab. 1 - 4ª Turma Recursal / Juiz Substituto' \
        #         or desPerfil == '2ª Turma Recursal / Gab. 2 - 2ª Turma Recursal / Juiz Titular':
        #     codPerfil = 3
        # else:
        #     codPerfil = '999'

        if desPerfil == '5ª Turma Recursal Provisória / Secretaria de Colegiado / Secretário da Sessão' \
                or desPerfil == '5ª Turma Recursal Provisória / Secretaria de Colegiado / Servidor Geral':
            codPerfil = 3

        elif desPerfil == '6ª Turma Recursal Provisória / Secretaria de Colegiado / Secretário da Sessão' \
                or desPerfil == '6ª Turma Recursal Provisória / Secretaria de Colegiado / Servidor Geral':
            codPerfil = 5

        else:
            codPerfil = '999'

        return codPerfil