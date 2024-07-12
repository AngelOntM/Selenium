import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from openpyxl import Workbook


class CyberpuertaPromociones(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_promociones(self):
        driver = self.driver
        driver.get("https://www.cyberpuerta.mx")
        time.sleep(5)

        # Navega a la sección de promociones
        promociones_link = driver.find_element(By.LINK_TEXT, 'Promociones')
        promociones_link.click()

        # Espera a que la página de promociones cargue completamente
        time.sleep(10)

        # Encuentra el contenedor de la lista de productos
        lista_productos = driver.find_element(By.CSS_SELECTOR, '#productList')

        # Inicializa un contador para iterar sobre los productos
        x = 1

        # Crea un nuevo libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Promociones Cyberpuerta"

        # Escribe la cabecera del archivo Excel
        ws.append(["Producto", "Precio"])

        while True:
            try:
                # Selector dinámico para cada producto
                producto_selector = f'#productList-{x}'
                producto = lista_productos.find_element(By.CSS_SELECTOR, producto_selector)

                # Selector para el precio
                precio_selector = '#productList > li:nth-child(1) > div > form > div.emproduct_right > div.clear.emproduct_left_attribute_price > div.emproduct_right_price > div:nth-child(2) > div.emproduct_right_price_left > label'
                nombre = producto.text  # Obtén el texto del nombre del producto
                precio = driver.find_element(By.CSS_SELECTOR, precio_selector).text  # Obtén el texto del precio

                print(f'Producto: {nombre} - Precio: {precio}')
                # Agrega los datos al archivo Excel
                ws.append([nombre, precio])

                x += 1  # Incrementa el contador para el siguiente producto
            except:
                # Si no se encuentra más productos, rompe el bucle
                break

        # Guarda el archivo Excel
        wb.save("Promociones_Cyberpuerta.xlsx")

    def tearDown(self):
        self.driver.close()


if __name__ == "__main__":
    unittest.main()
