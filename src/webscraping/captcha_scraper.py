"""
CAPTCHA Scraper : goal is to detect captcha on the page (visible area & scroll down), 
 - if there are consent buttons - handle them, 
 - if there is an iframe - handle it 
 - save the image in data/raw.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime
import time
from utils.consent_selectors import css_selectors, xpath_selectors

class CaptchaScraper:
    def __init__(self, chrome_driver_path=None):
        # Configuration of Chrome WebDriver options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # self.options.add_argument('--headless')

        # Initialize driver
        if chrome_driver_path:
            self.driver = webdriver.Chrome(
                service=Service(chrome_driver_path), options=self.options)
        else:
            # Search chrome driver in PATH
            try:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()), options=self.options
                )
            except Exception as e:
                raise Exception(
                    "ChromeDriver not found in system PATH. "
                    "Specify the path or add it to the system PATH.\n"
                    f"Error: {str(e)}"
                )

        self.wait = WebDriverWait(self.driver, 10)
        

    def find_captcha_in_elements(self, images, context=""):
        # Search for CAPTCHA-like elements among given images
        for image in images:
            try:
                width = image.size['width']
                height = image.size['height']
                # src attribute from HTML - treatement for demo sites, canvas are treated as empty src
                src = (image.get_attribute('src') or '').lower()
                 
                if 100<width<400 and 40<height< 150:
                    # Logo and banner filtering
                    if "logo" in src or "banner" in src:
                        continue
                    
                    print(f"CAPTCHA found {context} ({width} x {height})")
                    return image
            except:
                continue
        return None

       
    def click_consent_buttons(self):
        # Consent buttons handling with prepared selectors
        # Scroll to load JS consent buttons
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # Trying CSS selectors firstly
        for index, css_selector in enumerate(css_selectors, 1):
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))                
                button.click()
                print(f"Consent clicked (CSS #{index})")
                return True
            
            except TimeoutException:
                continue

            except Exception:
                continue

        # Trying manually entered XPath selectors if not
        for index, xpath_selector in enumerate(xpath_selectors, 1):
            try:
                button = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_selector)))
                button.click()
                print(f"Consent clicked (XPath #{index})")
                return True
            except TimeoutException:
                continue

            except Exception:
                continue

        print("No consent button found")
        return False
    

    def extract_captcha(self):
        # Detecting captcha on visible area/scrolling/consent/iframes
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"Found {len(elements)} Captcha-like elements IN VISIBLE AREA")

            captcha = self.find_captcha_in_elements(elements, "on main page")
            
        except TimeoutException:
            print("No images found in visible area")
        
        if not captcha:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            try:
                time.sleep(1) 
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
                elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                print(f"Found {len(elements)} Captcha-like elements AFTER SCROLLING")
                captcha = self.find_captcha_in_elements(elements, "after scroll")
                
            except TimeoutException:
                pass

        if not captcha:
            print(f"Loaded {len(css_selectors)+len(xpath_selectors)} consent selectors")
            consent_clicked = self.try_click_consent_buttons()
            
            if consent_clicked:
                try:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, "//img | //canvas")))
                    
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    print(f"Found {len(elements)} Captcha-like elements AFTER CONSENT")
                    captcha = self.find_captcha_in_elements(elements, "after consent")
                    
                except TimeoutException:
                    pass
        
        if not captcha:
            try:
                self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
                elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                print(f"Found {len(elements)} Captcha-like elements IN IFRAME")
                captcha = self.find_captcha_in_elements(elements, "in iframe")
                
                if not captcha:
                    self.driver.switch_to.default_content()
                
            except TimeoutException:
                self.driver.switch_to.default_content()
        
        self.captcha_element = captcha
        
        if captcha:
            print(f"YAY! Captcha detected")
            return True
        else:
            print(f"SOS! NO CAPTCHA FOUND")
            return False

    
    def save_captcha_image(self):
        """Save CAPTCHA image to file"""
        if not self.captcha_element:
            print("   ✗ No CAPTCHA element to save")
            return None
        
        try:
            os.makedirs("data/raw", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_{timestamp}.png"
            path = f"data/raw/{filename}"
            
            self.captcha_element.screenshot(path)
            print(f"   ✓ CAPTCHA saved: {path}")
            return path
            
        except Exception as e:
            print(f"   ✗ Error saving: {e}")
            return None
    

    def save_metadata(self, filename, url, solution=None, success=None):
        metadata_path = "data/processed/captcha_metadata.json"
        
        try:
            with open(metadata_path, 'r') as f:
                all_metadata = json.load(f)
        except:
            all_metadata = []
        
        metadata_entry = {
            'filename': filename,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'page_title': self.driver.title
        }
        
        # Add solver-specific fields if provided
        if solution is not None:
            metadata_entry['solution'] = solution
        if success is not None:
            metadata_entry['success'] = success
        
        all_metadata.append(metadata_entry)
        
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)
    
    def scrape_url(self, url):
        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print(f"Page loaded: {self.driver.title}")
            
            # Extract CAPTCHA
            if self.extract_captcha():
                # Save image
                captcha_path = self.save_captcha_image()
                
                if captcha_path:
                    # Save metadata
                    self.save_metadata(captcha_path, url)
                    return True
            
            return False
            
        except TimeoutException:
            return False
        
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        finally:
            self.driver.switch_to.default_content()
    
    def close(self):
        self.driver.quit()


def main():
    print("1. Setup WebDriver")
    scraper = CaptchaScraper()
    print("2. WebDriver ready")

    # URLs test
    urls = [
        "https://rutracker.org/forum/profile.php?mode=register"
    ]

    print("3. Starting CAPTCHA scraping")
    
    success_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"\n{'#'*60}")
        print(f"[{idx}/{len(urls)}] Processing URL")
        print(f"{'#'*60}")
        
        if scraper.find_captcha_in_elements(url):
            success_count += 1
        
        time.sleep(1) 

    print(f"URLs processed: {len(urls)}")
    print(f"CAPTCHAs found: {success_count}")
    print(f"Success rate: {success_count}/{len(urls)}")
    print(f"Images saved in: data/raw/")
    print(f"Metadata saved in: data/processed/")

    print("4. Closing browser")
    scraper.close()
    print("Browser closed")


if __name__ == "__main__":
    main()