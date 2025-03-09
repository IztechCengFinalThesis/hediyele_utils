from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class BaseScraper:
    def __init__(self, driver_path='selenium_utils/driver/chromedriver.exe'):
        self.driver = webdriver.Chrome(service=Service(driver_path))
        self.driver.maximize_window()

    def get_product_details(self, link):
        raise NotImplementedError

    def quit(self):
        self.driver.quit()

class HepsiBuradaScraper(BaseScraper):
    def get_product_details(self, link):
        self.driver.get(link)
        wait = WebDriverWait(self.driver, 10)

        try:
            product_name_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-test-id="title"]'))
            )
            product_name = product_name_elem.text
        except:
            product_name = "Unknown"

        try:
            price_div = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="price-current-price"]'))
            )
            price = convert_price_str_to_float(price_div.text)
        except:
            price = "0"

        try:
            description_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="ProductDescription"]'))
            )
            description_text = description_elem.text
        except:
            description_text = "Unknown"

        try:
            rating_elem = self.driver.find_element(By.CSS_SELECTOR, 'span.JYHIcZ8Z_Gz7VXzxFB96')
            rating = rating_elem.text
        except:
            rating = "Not yet evaluated"

        html = self.driver.page_source
        match = re.search(r'content_category:\[?"([^"\]]+)"?\]', html)
        if match:
            category = match.group(1).replace(r'\x3e', '>')
            category = category.split('>')[-1].strip()
        else:
            category = "Unknown"

        return {
            'Link': link,
            'Product Name': product_name,
            'Price': price,
            'Description': description_text,
            'Rating': rating,
            'Category': category
        }

class AmazonScraper(BaseScraper):
    def get_product_details(self, link):
        self.driver.get(link)
        wait = WebDriverWait(self.driver, 10)

        try:
            product_name_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span#productTitle'))
            )
            product_name = product_name_elem.text.strip()
        except:
            product_name = "Unknown"

        try:
            price_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'span.a-price span.a-offscreen'))
            )
            price = price_elem.text.strip()
        except:
            price = "Unknown"

        try:
            description_elem = self.driver.find_element(By.CSS_SELECTOR, 'div#productDescription')
            description_text = description_elem.text.strip()
        except:
            description_text = "Unknown"

        try:
            rating_elem = self.driver.find_element(By.CSS_SELECTOR, 'span.a-icon-alt')
            rating = rating_elem.text.strip()
        except:
            rating = "Not yet evaluated"

        return {
            'Link': link,
            'Product Name': product_name,
            'Price': price,
        }


import re

def convert_price_str_to_float(price_str: str) -> float:
    numeric_str = re.sub(r"[^\d,\.]", "", price_str)
    if "," in numeric_str:
        numeric_str = numeric_str.replace(".", "")
        numeric_str = numeric_str.replace(",", ".")
    try:
        return float(numeric_str)
    except ValueError:
        return 0.0

 
