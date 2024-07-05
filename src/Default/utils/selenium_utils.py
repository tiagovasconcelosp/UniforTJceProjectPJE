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

class Selenium_utils():
    def __init__(self, driver, logging):
        self.driver = driver
        self.logging = logging
    def is_element_present(self, locator):
        """
        Check if an element exists on the page using the provided locator.

        :param locator: A tuple (By, value) identifying the element.
        :return: True if the element exists, False otherwise.
        """
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_frame_present(self, frame_locator, timeout=3):
        """
        Check if a frame identified by the given locator is present.

        :param frame_locator: A tuple (By, value) identifying the frame.
        :param timeout: Maximum time to wait for the frame to be present (default is 3 seconds).
        :return: True if the frame is present, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.frame_to_be_available_and_switch_to_it(frame_locator))
            return True
        except TimeoutException:
            return False

    def get_element(self, locator, timeout=10):
            """
            Get the element identified by the provided locator.

            :param locator: A tuple (By, value) identifying the element.
            :param timeout: Maximum time to wait for the element to be present (default is 10 seconds).
            :return: The element if found, None otherwise.
            """
            try:
                element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
                return element
            except TimeoutException:
                return None
    
    def find_element_by_text(self, text, timeout=10):
        """
        Find an element containing the specified text.

        :param text: The text to search for within the element.
        :param timeout: Maximum time to wait for the element to be found (default is 10 seconds).
        :return: WebElement if found, None if not found within the timeout.
        """
        try:
            xpath = f"//*[contains(text(), '{text}')]"
            
            # Wait for the element to be present in the DOM
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            
            return element
        except Exception as e:
            print(f"Error finding element with text '{text}': {e}")
            return None
  
    def elemento_por_texto_em_lista_by_xpath_e_tag(self, xpath, tag, texto):
        #refatorar, muitos argumentos.
        elementos = self.get_element(self.driver, xpath)
        elementos = elementos.find_elements(by=By.TAG_NAME, value=tag) 
        if len(elementos)>0:
            for elemento in elementos:
                if texto == elemento.get_attribute('title'):
                    return elemento
            return None
        time.sleep(0.3)
        
    def elemento_por_texto_em_lista_by_tag(self, driver, tag, texto, repete=False, nao_incluso=None):
        #refatorar, muitos argumentos, muito uso de booleans
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

    def get_frames(self):
        """
        Get a list of iframe elements in the current page.

        Returns:
            list: A list of iframe elements.
        """
        try:
            frames = self.driver.find_elements(by=By.TAG_NAME, value="iframe")
            if frames:
                self.logging.info(f"Found {len(frames)} iframe(s) on the page.")
            else:
                self.logging.warning("No iframes found on the page.")
            return frames
        except NoSuchElementException as e:
            self.logging.error(f"Error while finding iframes: {e}")
            return []

    def select_option_in_dropdown(self, dropdown, option_text):
        """
        Selects an option in a dropdown by its visible text.

        Args:
            dropdown (WebElement): Selenium WebElement representing the dropdown element.
            option_text (str): The text of the option to be selected.

        Returns:
            WebElement: The selected dropdown element.

        Example:
            select_option_in_dropdown(dropdown, "Option 1")
        """
        self.logging.info("select_option_in_dropdown -", option_text)

        select_element = Select(dropdown)

        for option in select_element.options:
            if option_text in option.text:
                select_element.select_by_visible_text(option.text)
                return dropdown
    
    def elemento_por_titulo_em_lista_by_tag(self, driver, tag, titulo, repete=False):
        ## Refatorar
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
        ## Refatorar
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
        #Refatorar
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
    
    def elemento_por_placeholder_em_lista_by_tag(self, tag, placeholder, repete=False):
        # Refatorar
        print("elemento_por_placeholder_em_lista_by_tag -", placeholder)
        repete_interno = True
        while repete_interno:
            repete_interno = repete
            elementos = self.driver.find_elements(by=By.TAG_NAME, value=tag)
            for elemento in elementos:
                if placeholder in elemento.get_attribute('placeholder'):
                    return elemento
        return None
    

    def switch_to_new_tab(self):
        """
        Switch to the new tab in the browser.

        This method searches for the identifier of the new tab and switches to it,
        while maintaining a reference to the main tab.

        Returns:
            list: A list containing the identifiers of the new tab and the main tab.
                [new_tab_handle, main_tab_handle]

        Raises:
            Exception: If an error occurs during the process, it will be caught
                    and logged, but it won't halt the program's execution.
        """
        try:
            main_tab_handle = None
            while not main_tab_handle:
                main_tab_handle = self.driver.current_window_handle
            new_tab_handle = None
            while not new_tab_handle:
                for handle in self.driver.window_handles:
                    if handle != main_tab_handle:
                        new_tab_handle = handle
                        break

            self.driver.switch_to.window(new_tab_handle)


            self.logging.info('Switched to the new tab')

            return [new_tab_handle, main_tab_handle]

        except Exception as e:
            self.logging.error(repr(e))
            print(repr(e))
    def close_new_tab(self, main_tab_handle):
        """
        Close the new tab in the browser.

        This method attempts to close the new tab and switch back to the main tab.
        If closing the tab fails, it will attempt to quit the entire browser.

        Args:
            main_tab_handle (str): The identifier of the main tab.

        Returns:
            WebDriver: The WebDriver instance after closing the tab.

        Raises:
            Exception: If an error occurs during the process, it will be caught
                    and logged, but it won't halt the program's execution.
        """
        try:
            try:
                self.driver.close()
            except:
                self.driver.quit()
            self.driver.switch_to.window(main_tab_handle)

            self.logging.info('Closed the new tab')
            return self.driver

        except Exception as e:
            # Log the exception in case of an error
            self.logging.error(repr(e))
            print(repr(e))

    def subir_etiqueta(self, driver, elemento):
        #Mover para Clovis
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
    
    def wait_web_element_until_clickable(self, element_locator, wait_time=10):
        """
        Wait for a web element to be clickable.

        This method uses WebDriverWait to wait for the specified web element to become clickable.
        
        Args:
            element_locator (tuple): A tuple representing the locator strategy and value, e.g., (By.XPATH, "//button[@id='submit_button']").
            wait_time (int, optional): The maximum time to wait for the element to be clickable, in seconds. Default is 10 seconds.

        Raises:
            TimeoutException: If the specified web element is not clickable within the specified time, a TimeoutException is raised.

        Returns:
            WebElement: The web element that became clickable within the specified time.

        Note:
            The WebDriverWait is used in conjunction with the ExpectedCondition `element_to_be_clickable` from Selenium's ExpectedConditions module.

        Example:
            clickable_element = wait_web_element_until_clickable((By.XPATH, "//button[@id='submit_button']"), wait_time=15)
            clickable_element.click()
        """
        try:
            return WebDriverWait(self.driver, wait_time).until(EC.element_to_be_clickable(element_locator))
        except TimeoutException:
            self.logging.info("Timeout occurred while waiting for the web element to be clickable.")

    def switch_frame(self, frame_locator):
        """
        Switch the focus of the WebDriver to a specified iframe.

        This method locates the iframe element using the provided locator,
        switches the focus to the identified iframe, and logs the action.

        Args:
            frame_locator (tuple): A tuple representing the locator strategy and value, e.g., (By.XPATH, "//iframe[@id='frame_id']").

        Returns:
            None

        Raises:
            Exception: If an error occurs during the process, it will be caught
                    and logged, but it won't halt the program's execution.

        Example:
            switch_frame((By.XPATH, "//iframe[@id='frame_id']"))
        """
        try:
            iframe = self.get_element(frame_locator)
            self.driver.switch_to.frame(iframe)
            self.logging.info('Switched focus to internal frame: ' + str(frame_locator))
        except Exception as e:
            self.logging.error(repr(e))
            print("Error: ", repr(e))

 
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
    def is_element_visible(self, element_locator, timeout=10):
        """
        Check if a specific element is visible on the page.

        Args:
            element_locator (tuple): Selector strategy and value, e.g., (By.XPATH, '//xpath').
            timeout (int, optional): Maximum time to wait for the element to be visible (default is 10 seconds).

        Returns:
            bool: True if the element is visible, False otherwise.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(element_locator) and EC.visibility_of_element_located(element_locator)
            )
            return True

        except Exception as e:
            print(f"Exception: {e}")
            return False
  
    def find_element_by_text(self, text):
        """
        Find a web element by searching for the given text within its content.

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

    def is_web_element_invisible(self, web_element_locator):
        """
        Check if a specific web element identified by its locator is currently invisible on the page.

        Args:
            web_element_locator (tuple): The locator strategy and value, e.g., (By.ID, 'exampleElement').

        Returns:
            bool: True if the web element is currently invisible, False otherwise.

        Example:
            is_web_element_invisible((By.ID, 'exampleElement'))
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(web_element_locator))
            return True
        except TimeoutException:
            return False
