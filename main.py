import unittest
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from openpyxl import Workbook
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
import os
from dotenv import load_dotenv

class WebScraper(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def execute_actions(self, actions, ws, headers_written):
        driver = self.driver
        for action in actions:
            if action['action'] == 'click':
                element = driver.find_element(getattr(By, action['by']), action['value'])
                element.click()
            elif action['action'] == 'input':
                element = driver.find_element(getattr(By, action['by']), action['value'])
                element.clear()
                if action.get('hidden', False):
                    input_value = os.getenv(action['input_value'])
                else:
                    input_value = action['input_value']
                element.send_keys(input_value)
            elif action['action'] == 'select':
                select_element = driver.find_element(getattr(By, action['by']), action['value'])
                select = Select(select_element)
                select.select_by_visible_text(action['input_value'])
            elif action['action'] == 'checkbox':
                checkbox_element = driver.find_element(getattr(By, action['by']), action['value'])
                if checkbox_element.is_selected() != action.get('selected', action['input_value']):
                    checkbox_element.click()
            elif action['action'] == 'keyboard':
                if 'element' in action:
                    element = driver.find_element(getattr(By, action['by']), action['value'])
                    element.send_keys(getattr(Keys, action['input_value'].upper()))
                else:
                    action_chain = ActionChains(driver)
                    action_chain.send_keys(getattr(Keys, action['input_value'].upper())).perform()
            elif action['action'] == 'find_elements':
                elements = driver.find_elements(getattr(By, action['by']), action['value'])
                columns = action['columns']
                headers = [column['header'] for column in columns]

                if not headers_written:
                    ws.append(headers)
                    headers_written = True

                for x, element in enumerate(elements, start=1):
                    row = []
                    for column in columns:
                        try:
                            selector = column['selector_pattern'].format(x=x)
                            cell_data = element.find_element(By.CSS_SELECTOR, selector).text
                            row.append(cell_data)
                        except StaleElementReferenceException:
                            print(f"Error al procesar elemento: el elemento se ha vuelto obsoleto.")
                            row.append("")  # Añadir una celda vacía en caso de error
                        except Exception as e:
                            print(f"Error al procesar elemento: {e}")
                            row.append("")  # Añadir una celda vacía en caso de error
                    ws.append(row)

            if 'wait' in action:
                time.sleep(action['wait'])
        return headers_written

    def test_web_scraper(self):
        load_dotenv(dotenv_path='config.env')
        with open('config.json', encoding='utf-8') as f:
            config = json.load(f)

        driver = self.driver
        driver.get(config['start_url'])
        time.sleep(5)

        # Crea un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Data Extracted"
        headers_written = False

        try:
            headers_written = self.execute_actions(config['actions'], ws, headers_written)
        except Exception as e:
            print(f"Error general al ejecutar acciones: {e}")

        # Guarda el archivo Excel
        wb.save(config['output']['filename'])

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
