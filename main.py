import unittest
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from openpyxl import Workbook
from selenium.webdriver.support.ui import Select

class WebScraper(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def execute_actions(self, actions):
        driver = self.driver
        elements = None
        columns = []
        for action in actions:
            if action['action'] == 'click':
                element = driver.find_element(getattr(By, action['by']), action['value'])
                element.click()
            elif action['action'] == 'input':
                element = driver.find_element(getattr(By, action['by']), action['value'])
                element.clear()
                element.send_keys(action['input_value'])
            elif action['action'] == 'select':
                select_element = driver.find_element(getattr(By, action['by']), action['value'])
                select = Select(select_element)
                select.select_by_visible_text(action['option_value'])
            elif action['action'] == 'radio':
                radio_element = driver.find_element(getattr(By, action['by']), action['value'])
                radio_element.click()
            elif action['action'] == 'checkbox':
                checkbox_element = driver.find_element(getattr(By, action['by']), action['value'])
                if action.get('check', True):
                    if not checkbox_element.is_selected():
                        checkbox_element.click()
                else:
                    if checkbox_element.is_selected():
                        checkbox_element.click()
            elif action['action'] == 'find_elements':
                elements = driver.find_elements(getattr(By, action['by']), action['value'])
                columns = action['columns']
            if 'wait' in action:
                time.sleep(action['wait'])
        return elements, columns

    def test_web_scraper(self):
        with open('config1.json') as f:
            config = json.load(f)

        driver = self.driver
        driver.get(config['start_url'])
        time.sleep(2)

        elements, columns = self.execute_actions(config['actions'])

        # Crea un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Data Extracted"

        # Escribe la cabecera del archivo Excel
        headers = [column['header'] for column in columns]
        ws.append(headers)

        for x, element in enumerate(elements, start=1):
            row = []
            for column in columns:
                try:
                    selector = column['selector_pattern'].format(x=x)
                    cell_data = element.find_element(By.CSS_SELECTOR, selector).text
                    row.append(cell_data)
                except Exception as e:
                    print(f"Error al procesar elemento: {e}")
                    print(element.get_attribute('outerHTML'))
                    row.append("")  # Añadir una celda vacía en caso de error
            ws.append(row)

        # Guarda el archivo Excel
        wb.save(config['output']['filename'])

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
