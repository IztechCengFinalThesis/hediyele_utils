from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import requests
import io
from utils.image_utils import ImageProcessor

class BaseScraper:
    def __init__(self, driver_path='selenium_utils/driver/chromedriver.exe'):
        options = webdriver.ChromeOptions()  
        options.add_argument('--disable-gpu')  
        options.add_argument('--window-size=1920,1080') 
        
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)

    def get_product_details(self, link):
        raise NotImplementedError

    def quit(self):
        self.driver.quit()

class HepsiBuradaScraper(BaseScraper):
    def get_product_details(self, link):
        self.driver.get(link)
        html = self.driver.page_source
        wait = WebDriverWait(self.driver, 10)
        details = {'Link': link, 'Image': None}

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

        try:
            image_match = re.search(r'"image":\s*\[\s*"([^"]+)"', html)
            if image_match:
                image_url = image_match.group(1)
                
                response = requests.get(image_url, stream=True)
                response.raise_for_status()
                
                img_bytes = io.BytesIO(response.content)
                processed_image_bytes = ImageProcessor.prepare_image_for_db(img_bytes)
                if processed_image_bytes:
                    details['Image'] = processed_image_bytes

        except requests.exceptions.RequestException as req_e:
            print(f"Error downloading image: {req_e}")
        except Exception as e:
            print(f"Error processing image for {link}: {e}")
            details['Image'] = None

        return details

class AmazonScraper(BaseScraper):
    def get_product_details(self, link):
        return None


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

 
