import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import WebDriverException, StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

driver = None
logging = None
def efetuar_click(tupla_elemento:tuple, rotulo_elemento: str , tentativas = 5):
    '''
        """efetua um click de um elemento

    Args:
        xpath_elemento (tuple): Tuple do elemento presente na pagina há ser clicado.
        rotulo_elemento (str): alias para elemento ao ser exbido em log ou para Usuário.
        tentativas (int): Numero de vezes que o metodo ira tentar repetir o click atravez das execoes esperadas.
    Returns:
    '''
    espera = 0.3
    logging.info(f'Clicar em {rotulo_elemento}')
    print(f'Clicar em {rotulo_elemento}')
    for _ in range(tentativas):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(tupla_elemento)).click()
            logging.info(f'Clicando {rotulo_elemento}.')
            return True
        except StaleElementReferenceException:
            time.sleep(espera)
            continue
        except ElementClickInterceptedException:
            time.sleep(espera)
            logging.info(f'Nao foi possivel clicar em {rotulo_elemento}. Click interceptado')
            print(f'Nao foi possivel clicar em {rotulo_elemento}. Click interceptado')
            continue
        except Exception as e:
            logging.info(repr(e))
            print("Erro: ", repr(e))
            logging.info(f'Nao foi possivel clicar em {rotulo_elemento}.')
            print(f'Nao foi possivel clicar em {rotulo_elemento}.')
            raise e