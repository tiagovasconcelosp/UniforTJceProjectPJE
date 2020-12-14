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

from src.Default.Controllers.Print import Print


class Auth:

    def __init__(self, firefox, logging, caminhoImages):
        self.Login(firefox, logging, caminhoImages)

    def Login(self, firefox, logging, caminhoImages):

        try:
            # Aumenta o tempo de time out para 120s
            # Linhas comentadas para interroper preenchimento do login e senha

            firefox.set_page_load_timeout(120)

            # firefox.find_element(By.ID, "username").send_keys('60013884310')
            # firefox.find_element(By.ID, "password").send_keys('12345')

            logging.info("Realizando autenticacao.")
        except:

            image = Print(firefox, caminhoImages)

            logging.exception('Falha realizar autenticacao.')
            logging.info('Finalizando o robo.')
            logging.shutdown()
            # firefox.quit()
            sys.exit(0)
