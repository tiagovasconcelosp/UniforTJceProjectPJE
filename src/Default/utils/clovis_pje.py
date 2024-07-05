# ################################################### 
# ################################################### 
# ## Desenvolvido por: 
# ## Lucas Pacheco
# ## Email: lucas.pacheco@tjce.jus.br 
# ## Núcleo de Inovações SETIN
# ################################################### 
# ###################################################
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import xml.etree.ElementTree as ET
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import pyautogui
import selenium_utils as selu
class Clovis_pje():
    def __init__(self, task):
        self.tempo_espera = 0
        self.driver = task.driver
        self.url = task.url
        self.run_arguments = task.run_arguments
        self.logging = task.logging
        self.selu = selu.Selenium_utils(self.driver,self.logging)

    def subir_etiqueta(self, elemento):
        div_barra = self.selu.get_element('//*[@id="processosEtiqueta"]')
        print("Size:", div_barra.size, "Location:", div_barra.location)
        print("Size:", elemento.size, "Location:", elemento.location)
        passo = 36
        deslocamento = int((elemento.location['y']-div_barra.location['y'])/passo)-4
        if deslocamento < 0:
            deslocamento = 0
        html = self.selu.get_element( 'html')
        for i in range(deslocamento):
            html.send_keys(Keys.DOWN)
    

    def does_profile_selection_differ_from_run_arguments(self):
        # Clovis
        self.logging.info('Identificação do Perfil')
        return self._get_profile_web_element().get_attribute('data-original-title') != self.run_arguments['perfil']
    
    def _get_profile_web_element(self):
        #clovis
        profile_xpath = '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]'
            
        perfil_web_element = self.get_element(self.driver,profile_xpath)
        return perfil_web_element
    def select_profile(self):
        #clovis
        self._get_profile_web_element.click()
        select_xpath = '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]'
        select_web_element = self.get_element(select_xpath)
        options = select_web_element.find_elements(by=By.TAG_NAME, value='option')
        select = Select(select_web_element)
        select.select_by_visible_text(self.run_arguments['perfil'])  
        for option in options:
            if option.text == self.run_arguments['perfil']:
                option.click()
                time.sleep(2)
                perfil = self.get_element(self.driver, '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]')
                self.controlar_tempo_espera(True)
                while perfil.get_attribute('data-original-title') != self.run_arguments['perfil']:
                    time.sleep(0.5)
                    self.controlar_tempo_espera(max=1200)
                break

    def show_login_certificate_alert(self):
        #clovis
        mensagem = 'Realize o login com o CERTIFICADO DIGITAL e em seguida clique em OK para prosseguir.'
        
        self.logging.info("Aguardando Login com CERTIFICADO DIGITAL")
        pyautogui.alert(mensagem)
    def redirect_to_user_painel(self):
        #clovis
        url2 = self.url.replace('login.seam', 'ng2/dev.seam#/painel-usuario-interno')
        self.driver.get(url2)
        self.logging.info('Acesso da Url: '+ url2)    
    
    def wait_util_selected_precess_is_shown(self, texto_anterior):
        #Clovis
        texto_carregado = self.texto_by_xpath(self.driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
        while texto_carregado.split(' - ')[0] == texto_anterior: 
            time.sleep(0.1)
            self.logging.info("Aguardando recarregar o texto")
            texto_carregado = self.texto_by_xpath(self.driver, '//*[@id="frameTarefas"]/div/div[1]/div[1]/div/div[1]/a')
        texto_anterior = texto_carregado.split(' - ')[0]
    def get_first_process(self, ordem_li):
        #Clovis
        processo = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li['+str(ordem_li)+']/processo-datalist-card/div/div[3]/a/div/span[2]'
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, processo)))
        processo_web_element = self.get_element(self.driver, processo)
        return processo_web_element
    def find_element_by_text(self, text):
        """
        Find a web element by searching for the given text within its content.

        This method constructs an XPath expression that searches for elements containing
        the specified text, attempts to find the element using the XPath, and returns it.

        Args:
            text (str): The text to search for within the elements.

        Returns:
            WebElement or None: The web element containing the specified text, or None if not found.

        Example:
            find_element_by_text("Example Text")
        """
        try:
            element_xpath = f"//*[contains(text(), '{text}')]"
            element = self.driver.find_element(By.XPATH, element_xpath)
            return element
        except NoSuchElementException:
            return None

    def select_task(self, task_text):
        #clovis
        self.logging.info('Selecionando Tarefa: '+ task_text)
        try:
            task_web_element = self.elemento_por_texto_em_lista_by_xpath_e_tag('//*[@id="rightPanel"]/div/div[3]', 'a', task_text)
            if task_web_element is None:
                mensagem = 'Não foi encontrada a fila: ' + task_text
                self.logging.info(mensagem)
                pyautogui.alert(mensagem)
                raise Exception(mensagem)
            task_web_element.click()
            return task_web_element
        except Exception as e:
            self.logging.error(f"Page load timed out. {e}")
            self.logging.error("Você pode estar tentando interagir com elementos no frame '{frame_name}', mas o foco do WebDriver não está nesse frame. Certifique-se de usar switch_to.frame('{frame_name}') antes de realizar a interação.") 
    def wait_locate_tasks(self):
        #clovis
        self.logging.info('Aguardando lista de Tarefas carregar')
        task_queue_xpath = '//*[@id="divTarefasPendentes"]/div[3]/div[1]/div/a/div/span[1]'
        self.wait_locate_web_element(task_queue_xpath, wait_time=30)
    def wait_login(self):
        #clovis
        self.wait_locate_profile_element()
    def wait_locate_profile_element(self):
        #clovis
        profile_xpath = '//*[@id="barraSuperiorPrincipal"]/div/div[2]/ul/li/a/span[1]'
        self.wait_locate_web_element(profile_xpath,wait_time=60)

    def wait_locate_web_element(self, element_xpath, wait_time=10):
        """
        Wait for a web element to be present in the DOM by using its XPath.

        This method utilizes WebDriverWait to wait for the specified web element to be present.
        
        Args:
            element_xpath (str): The XPath of the web element to wait for.
            wait_time (int, optional): The maximum time to wait for the element to be present, in seconds. Default is 10 seconds.

        Returns:
            WebElement: The located web element.

        Raises:
            TimeoutException: If the specified web element is not present within the specified time, a TimeoutException is raised.

        Example:
            wait_locate_web_element("//button[@id='submit_button']", wait_time=15)
        """
        try:
            wait = WebDriverWait(self.driver, wait_time)
            element = wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
            return element
        except TimeoutException as e:
            self.logging.info(f"Element load timed out. {e}")
            raise

    def check_for_unexpected_err(self):
        #clovis
        erro_locator = (By.XPATH, '//*[@id="pageBody"]/ul/li')
        erro_text = "	Erro inesperado, por favor tente novamente. "
        self.is_element_visible_with_text(element_selecto=erro_locator,expected_text=erro_text,timeout=5)
    def wait_active_processes_page(self):
        #clovis
        self.logging.info('Aguardando Página de Processos Ativos')
        generic_chosen_web_element_locator = '//*[@id="processosTarefa"]/p-datalist/div/div/ul/li[1]/processo-datalist-card/div/div[3]/a/div/span[2]'    
        self.wait_locate_web_element(generic_chosen_web_element_locator)


