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
    def __init__(self, driver_path: str = 'selenium_utils/driver/chromedriver.exe', headless: bool = True):
        """Create a Chrome driver that works reliably in head-less mode.

        When *headless* is True we enable the modern head-less mode and
        apply a few common *stealth* flags so that web sites do not hide
        dynamic content (price, image, etc.) from automation scripts.
        """
        options = webdriver.ChromeOptions()

        # Modern head-less mode (only when requested)
        if headless:
            options.add_argument('--headless=new')

        # General browser tweaks
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Stealth flags
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/125.0.0.0 Safari/537.36'
        )

        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)

        # Remove the easy "webdriver" fingerprint
        self.driver.execute_cdp_cmd(
            'Page.addScriptToEvaluateOnNewDocument',
            {
                'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'
            },
        )

    def get_product_details(self, link):
        raise NotImplementedError

    def quit(self):
        self.driver.quit()

class HepsiBuradaScraper(BaseScraper):
    def _download_image(self, url: str) -> io.BytesIO:
        """Fetch *url* with the same cookies / headers Selenium is using."""
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie["name"], cookie["value"])

        headers = {
            "User-Agent": self.driver.execute_script("return navigator.userAgent;"),
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Referer": self.driver.current_url,
        }
        response = session.get(url, headers=headers, stream=True, timeout=15)
        response.raise_for_status()
        return io.BytesIO(response.content)

    def get_product_details(self, link):
        self.driver.get(link)
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        html = self.driver.page_source

        wait = WebDriverWait(self.driver, 10)
        details = {'Link': link, 'Image': None}

        name_match = re.search(r'<title>\s*(.*?)\s*</title>', html, re.DOTALL)
        if name_match:
            details['Product Name'] = name_match.group(1).strip()
        else:
            details['Product Name'] = "Unknown"

        try:
            price_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'meta[itemprop="price"]'))
            )
            price_raw = price_elem.get_attribute('content') or price_elem.text
            details['Price'] = convert_price_str_to_float(price_raw)
        except Exception:
            price_match = re.search(r'"product_unit_prices":\s*\[\s*"([^"]+)"\s*\]', self.driver.page_source)
            if price_match:
                details['Price'] = convert_price_str_to_float(price_match.group(1))
            else:
                details['Price'] = 0.0

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
            image_url = None
            cdn_matches = re.findall(
                r'https://productimages\.hepsiburada\.net[^"\' >]+\.(?:jpg|jpeg|png)(?:/format:webp)?',
                html,
                re.IGNORECASE,
            )
            print(f"CDN matches: {cdn_matches}")
            if cdn_matches:
                image_url = cdn_matches[0]
            if image_url:
                print(f"Image URL found: {image_url}")
                img_bytes = self._download_image(image_url)
                processed = ImageProcessor.prepare_image_for_db(img_bytes)
                if processed:
                    details['Image'] = processed

        except requests.exceptions.RequestException as req_e:
            print(f"Error downloading image: {req_e}")

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

 
