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

import re

class HepsiBuradaScraper(BaseScraper):
    def get_product_details(self, link):
        self.driver.get(link)
        html = self.driver.page_source
        wait = WebDriverWait(self.driver, 10)
        details = {'Link': link}

        name_match = re.search(r'<title>\s*(.*?)\s*</title>', html, re.DOTALL)
        if name_match:
            details['Product Name'] = name_match.group(1).strip()
        else:
            details['Product Name'] = "Unknown"

        price_match = re.search(r'"product_unit_prices":\s*\[\s*"([^"]+)"\s*\]', html)
        if price_match:
            price_str = price_match.group(1).strip()
            try:
                details['Price'] = float(price_str.replace(',', ''))
            except Exception as e:
                details['Price'] = price_str
        else:
            details['Price'] = "0"

        try:
            desc_elem = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="ProductDescription"]'))
            )
            details['Description'] = desc_elem.text.strip()
        except Exception as e:
            details['Description'] = "Unknown"

        try:
            rating_match = re.search(
                r'data-test-id=["\']has-review["\'][^>]*>.*?<span[^>]*>(.*?)</span>',
                html, re.DOTALL
            )
            if rating_match:
                details['Rating'] = rating_match.group(1).strip()
        except Exception as e:
            details['Rating'] = "Not yet evaluated"

        cat_match = re.search(r'content_category:\[?"([^"\]]+)"?\]', html)
        if cat_match:
            cat_text = cat_match.group(1).replace(r'\x3e', '>').split('>')[-1].strip()
            details['Category'] = cat_text
        else:
            details['Category'] = "Unknown"

        return details

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

 
