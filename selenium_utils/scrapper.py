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
        details = {'Link': link, 'Image': None}
        wait = WebDriverWait(self.driver, 2)

        # Find the script tag containing product data
        script_match = re.search(r'const utagData = ({.*?});', html, re.DOTALL)
        if script_match:
            script_content = script_match.group(1)
            
            # Extract product name
            name_match = re.search(r'"product_name_array":"([^"]+)"', script_content)
            if name_match:
                details['Product Name'] = name_match.group(1)
            else:
                details['Product Name'] = "Unknown"

            # Extract price
            price_match = re.search(r'"product_prices":\["([^"]+)"\]', script_content)
            if price_match:
                details['Price'] = convert_price_str_to_float(price_match.group(1))
            else:
                details['Price'] = 0.0

            # Extract category (last value in hierarchy)
            category_match = re.search(r'"category_name_hierarchy":"([^"]+)"', script_content)
            if category_match:
                category_hierarchy = category_match.group(1)
                category = category_hierarchy.split(' > ')[-1]
                details['Category'] = category
            else:
                details['Category'] = "Unknown"

            # Extract rating
            rating_match = re.search(r'"review_rate":"([^"]+)"', script_content)
            if rating_match:
                details['Rating'] = rating_match.group(1)
            else:
                details['Rating'] = "Not yet evaluated"

            # Extract description
            try:
                desc_elem = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-test-id="ProductDescription"]'))
                )
                details['Description'] = desc_elem.text.strip()
            except Exception as e:
                details['Description'] = "Unknown"

        # Keep existing image extraction logic
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

 
