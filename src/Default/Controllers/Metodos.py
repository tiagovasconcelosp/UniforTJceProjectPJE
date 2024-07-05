# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Augusto Lima dos Santos 
# ## Email: augusto.santos@tjce.jus.br 
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################

import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import xml.etree.ElementTree as ET
from selenium.webdriver.common.keys import Keys

class Metodos():

    def __init__(self, url):
        self.tempo_espera = 0
        self.url = url
        
    @classmethod
    def load_child_tags_as_dict(self, xml, father_element_name):
        try:
            tree = ET.ElementTree(xml)
            father_element = tree.find(father_element_name)
            
            if father_element is not None:
                child_tags_dict = {}
                for child in father_element:
                    child_tags_dict[child.tag] = child.text
                return child_tags_dict
            
            return None
        except ET.ParseError as e:
            print(f"Error parsing XML file: {e}")
            return None
    def check_exists_by_xpath(self, driver, xpath):
        try:
            driver.find_element(by=By.XPATH, value=xpath)
        except NoSuchElementException:
            return False
        return True

    def check_exists_element_inside(self, tag_element, tag, position=0):
        try:
            tag_element.find_elements(by=By.XPATH, value=tag)[position]
        except:
            return False
        return True

    def identificacao_erros(self, driver):
        if self.check_exists_by_xpath(driver, '//*[@id="pageBody"]/ul/li'):
            if 'Erro inesperado, por favor tente novamente' in \
                driver.find_element(by=By.XPATH, value='//*[@id="pageBody"]/ul/li').text:
                driver.get(self.url)
                print("Retornando ao ponto inicial devido a erros")
                raise Exception("Retornando ao ponto inicial devido a erros")

    def get_element(self, driver, xpath, max=60):
        self.controlar_tempo_espera(True)
        while not self.check_exists_by_xpath(driver, xpath):
            time.sleep(1)
            print("searching... " + xpath)
            self.identificacao_erros(driver)
            self.controlar_tempo_espera(max=max)
        return driver.find_element(by=By.XPATH, value=xpath)

    def get_element_check_page(self, driver, xpath, pagina):
        self.controlar_tempo_espera(True)
        while not self.check_exists_by_xpath(driver, xpath):
            time.sleep(1)
            print("get_element_check_page", xpath)
            self.identificacao_erros(driver)
            if driver.title != pagina:
                return None
            self.controlar_tempo_espera()
        return driver.find_element(by=By.XPATH, value=xpath)
    
    def get_elements_by_tag(self, driver, tag, repete=False):
        print("get_elements_by_tag -", tag)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elements = driver.find_elements(by=By.TAG_NAME, value=tag)
            if elements is not None:
                return elements
        return None

    def elemento_por_texto_em_lista_by_xpath_e_tag(self, driver, xpath, tag, texto):
        
        while True:
            print("elemento_por_texto_em_lista_by_xpath_e_tag -", texto)
            elementos = self.get_element(driver, xpath)
            elementos = elementos.find_elements(by=By.TAG_NAME, value=tag) 
            if len(elementos)>0:
                for elemento in elementos:
                    if texto == elemento.get_attribute('title'):
                        return elemento
                return None
            time.sleep(0.3)

    def elemento_por_texto_em_lista_by_tag(self, driver, tag, texto, repete=False, nao_incluso=None):
        print("elemento_por_texto_em_lista_by_tag -", texto)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                continua = True
                if nao_incluso is not None: 
                    continua = False 
                    if nao_incluso not in elemento.text:
                        continua = True
                if texto in elemento.text and continua \
                    and "Traceback (most recent call last)" not in elemento.text:
                    return elemento
        return None
    
    def elementos_por_texto_em_lista_by_tag(self, driver, tag, texto, repete=False, nao_incluso=None):
        print("elemento_por_texto_em_lista_by_tag -", texto)
        repete_interno = True
        elementos_lista = []
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                continua = True
                if nao_incluso is not None: 
                    continua = False 
                    if nao_incluso not in elemento.text:
                        continua = True
                if texto in elemento.text and continua \
                    and "Traceback (most recent call last)" not in elemento.text:
                    elementos_lista.append(elemento)
        return elementos_lista
    
    def get_elements_by_classe(self, driver, classe):
        return driver.find_elements(by=By.CLASS_NAME, value=classe)

    def elemento_por_texto_em_lista_by_classe(self, driver, classe, texto):
        print("elemento_por_texto_em_lista_by_classe -", texto)
        elementos = driver.find_elements(by=By.CLASS_NAME, value=classe)
        for elemento in elementos:
            if texto in elemento.text:
                return elemento
        return None

    def texto_by_xpath(self, driver, xpath):
        return driver.find_element(by= By.XPATH, value=xpath).text

    def check_by_xpath(self, driver, xpath):
        check = driver.find_element(by= By.XPATH, value=xpath)
        return check.is_selected()

    def check_by_tag(self, driver, tag):
        check = driver.find_element(by= By.TAG_NAME, value=tag)
        return check.is_selected()

    def controlar_tempo_espera(self, inicio=False, max=600):
        if inicio:
            self.tempo_espera = 0
        else:
            self.tempo_espera += 1
            if self.tempo_espera % 60 == 0:
                print("Mais 60", self.tempo_espera)
        if self.tempo_espera >= max:
            print("Excedeu o tempo")
            raise Exception("Excedeu o tempo")

    def identifica_frames(self, driver):
        frames = driver.find_elements(by=By.TAG_NAME, value="iframe")
        return frames

    def verifica_presenca_no_frame(self, driver, frames, xpath):
        print("verifica_presenca_no_frame")
        for frame in frames:
            driver.switch_to.frame(frame)
            if self.check_exists_by_xpath(driver, xpath):
                driver.switch_to.parent_frame()
                return frame
            driver.switch_to.parent_frame()
        return None

    def buscar_componentes_por_css_selector(self, driver,value):
        list_of_elements = driver.find_elements(by=By.CSS_SELECTOR,value=value)                            
        return list_of_elements
    
    def buscar_componente_por_value(self, driver, value, repete=False):
        print("buscar_componente_por_value -", value)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            inputs = driver.find_elements(by=By.TAG_NAME, value="input")
            for input in inputs:
                if value in input.get_attribute("value"):
                    return input
        return None

    def selecionar_option_select(self, selects, texto, identico=False):
        print("selecionar_option_select -", texto)
        for select in selects:
            if texto in select.text:
                select.click()
                for option in select.find_elements(by=By.TAG_NAME, value='option'):
                    if not identico and texto in option.text:
                        option.click()
                    if identico and texto == option.text:
                        option.click()
                return select

    def elemento_por_titulo_em_lista_by_tag(self, driver, tag, titulo, repete=False):
        print("elemento_por_titulo_em_lista_by_tag -", titulo)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                if titulo in elemento.get_attribute('title'):
                    return elemento
        return None

    def elemento_por_atributo_em_lista_by_tag(self, driver, tag, atributo, valor, repete=False):
        print("elemento_por_atributo_em_lista_by_tag -", atributo, valor)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                atri = elemento.get_attribute(atributo)
                if atri is not None:
                    if valor in atri:
                        return elemento
        return None

    def buscar_tabela_por_texto(self, driver, texto, id=False, repete=False, completo=False, nao_incluso=None):
        print("buscar_tabela_por_texto -", texto)
        self.controlar_tempo_espera(True)
        repete_interno = True
        while repete_interno:
            time.sleep(0.1)
            self.identificacao_erros(driver)
            self.controlar_tempo_espera(max=300)
            repete_interno = repete
            tabelas = driver.find_elements(by=By.TAG_NAME, value='table')
            for index, tabela in enumerate(tabelas):
                if "Traceback (most recent call last)" not in tabela.text:
                    continua = True
                    if nao_incluso is not None: 
                        continua = False 
                        if nao_incluso not in tabela.text:
                            continua = True
                    if texto in tabela.text and continua:
                        if completo:
                            return index, tabela, tabelas
                        if id:
                            return index
                        return tabela
        return None
    
    def elemento_por_placeholder_em_lista_by_tag(self, driver, tag, placeholder, repete=False):
        print("elemento_por_placeholder_em_lista_by_tag -", placeholder)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                if placeholder in elemento.get_attribute('placeholder'):
                    return elemento
        return None
    
    def elemento_por_classe_em_lista_by_tag(self, driver, tag, classe, repete=False):
        print("elemento_por_classe_em_lista_by_tag -", classe)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                if classe in elemento.get_attribute('class'):
                    return elemento
        return None
    
    def elemento_por_type_em_lista_by_tag(self, driver, tag, type, repete=False):
        print("elemento_por_type_em_lista_by_tag -", type)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                if type in elemento.get_attribute('type') \
                    and "Traceback (most recent call last)" not in elemento.text:
                    return elemento
        return None

    def get_element_css(self, driver, css_selector, max=60):

        self.controlar_tempo_espera(True)
        while not self.check_exists_by_xpath(driver, css_selector):
            time.sleep(1)
            print("searching... " + css_selector)
            self.identificacao_erros(driver)
            self.controlar_tempo_espera(max=max)
        return driver.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def buscar_nova_aba(self, driver, logging):
        try:
            main_window_handle = None
            while not main_window_handle:
                main_window_handle = driver.current_window_handle

            signin_window_handle = None
            while not signin_window_handle:
                for handle in driver.window_handles:
                    if handle != main_window_handle:
                        signin_window_handle = handle
                        break
            driver.switch_to.window(signin_window_handle)
            logging.info('Nova aba localizada')
            return [driver, main_window_handle]
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))

    def fechar_nova_aba(self, driver, logging, main_window_handle):
        try:
            try:
                driver.close()
            except:
                driver.quit()

            driver.switch_to.window(main_window_handle)
            logging.info('Fechando aba')
            return driver
        except Exception as e:
            logging.info(repr(e))
            print(repr(e))

    def subir_etiqueta(self, driver, elemento):
        div_barra = self.get_element(driver, '//*[@id="processosEtiqueta"]')
        print("Size:", div_barra.size, "Location:", div_barra.location)
        print("Size:", elemento.size, "Location:", elemento.location)
        passo = 36
        deslocamento = int((elemento.location['y']-div_barra.location['y'])/passo)-4
        if deslocamento < 0:
            deslocamento = 0
        html = self.get_element(driver, 'html')
        for i in range(deslocamento):
            html.send_keys(Keys.DOWN)

