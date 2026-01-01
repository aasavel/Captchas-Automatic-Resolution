# CAPTCHA Web Scraper - Universal Version with Class
# Projet M2 MoSEF 2025-2026 - Université Paris 1 Panthéon-Sorbonne
# Pipeline: page loading => captcha detection on visible area => scrolling => consent handling => iframe checking => saving

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime
import time
import pandas as pd

# ============================================
# IMPORT DES SELECTORS (depuis notre parser!)
# ============================================
try:
    from consent_selectors import CONSENT_SELECTORS
    print(f"✓ Loaded {len(CONSENT_SELECTORS)} consent selectors from file")
except ImportError:
    print("⚠ Warning: consent_selectors.py not found, using minimal selectors")
    # Fallback minimal selectors
    CONSENT_SELECTORS = [
        "//button[contains(text(), 'Accept')]",
        "//button[contains(text(), 'Agree')]",
        "//input[@value='Я согласен с этими правилами']",
    ]


class CaptchaScraper:
    def __init__(self, chrome_driver_path=None):
        # Configuration of Chrome WebDriver options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        
        # Using specified ChromeDriver path if provided else try to find it in system PATH
        if chrome_driver_path:
            self.driver = webdriver.Chrome(
                service=Service(chrome_driver_path), options=self.options
            )
        else:
            # Search chrome driver in PATH
            try:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),options=self.options
                )
            except Exception as error:
                raise Exception(
                    "ChromeDriver not found in system PATH. "
                    "Specify the path or add it to the system PATH.\n"
                    f"Error: {str(error)}"
                )
        # 20 seconds wait time
        self.wait = WebDriverWait(self.driver, 20)
        

    def find_captcha_in_elements(self, images, context=""):
        # Search for CAPTCHA-like elements among given images
        for image in images:
            try:
                width = image.size['width']
                height = image.size['height']
                # src attribute from HTML - treatement for demo sites, canvas are treated as empty src
                src = (image.get_attribute('src') or '').lower()
                 
                if 100 < width < 400 and 40 < height < 150:
                    # Logo and banner filtering
                    if "logo" in src or "banner" in src:
                        continue
                    
                    print(f"CAPTCHA found {context}: {width} x {height}")
                    return image
            except:
                continue
        return None
    
    def try_click_consent_buttons(self):
        """
        Try to find and click consent/cookies buttons
        Uses selectors imported from consent_selectors.py
        """
        print("\nSearching for consent buttons...Wait a second please.")
        
        # Scroll down to load potential buttons for JS
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Use imported selectors (from our parser!)
        print(f"   Trying {len(CONSENT_SELECTORS)} different selectors...")
        
        for idx, consent_selector in enumerate(CONSENT_SELECTORS, 1):
            try:
                button = self.driver.find_element(By.XPATH, consent_selector)
                # Check if button is not hidden in CSS
                if button.is_displayed():
                    self.driver.execute_script('arguments[0].scrollIntoView();', button)
                    time.sleep(1)
                    button.click()
                    print(f"✓ Consent button found & clicked! (Selector #{idx})")
                    time.sleep(2)
                    return True
            except:
                continue
        
        print("   No consent or cookie button found")
        return False
    
    def save_metadata(self, filename, url):
        """Save CAPTCHA metadata to JSON"""
        metadata_path = "data/processed/captcha_metadata.json"
        
        # Load existing metadata
        try:
            with open(metadata_path, 'r') as f:
                all_metadata = json.load(f)
        except:
            all_metadata = []
        
        # Add new entry
        all_metadata.append({
            'filename': filename,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'page_title': self.driver.title
        })
        
        # Save
        with open(metadata_path, 'w') as f:
            json.dump(all_metadata, f, indent=2)
        
        print(f"✓ Metadata saved to: {metadata_path}")
    
    def scrape_captcha_from_url(self, url):
        """Fonction principale qui orchestre le scraping"""
        print(f"\n{'='*60}")
        print(f"Opening: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(2)
            print(f"Title: {self.driver.title}")
        except Exception as e:
            print(f"✗ Error loading page: {e}")
            return False
        
        captcha_element = None
        
        # Visible wone searching
        print("\n[Step 1] Searching for CAPTCHA on visible area...")
        try:
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"   Found {len(elements)} visual elements")
            captcha_element = self.find_captcha_in_elements(elements, "on main page")
        except:
            pass
        
        # Search
        if not captcha_element:
            print("\n[Step 2] Scrolling down and searching again...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            try:
                elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                captcha_element = self.find_captcha_in_elements(elements, "after scroll")
            except:
                pass
        
        # Consentement
        if not captcha_element:
            print("\n[Step 3] No CAPTCHA yet, trying consent buttons...")
            consent_clicked = self.try_click_consent_buttons()
            
            if consent_clicked:
                print("\n[Step 3.1] Searching for CAPTCHA after consent...")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                try:
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    captcha_element = self.find_captcha_in_elements(elements, "after consent")
                except:
                    pass
        
        # Iframe
        if not captcha_element:
            print("\n[Step 4] Checking iframes...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                print(f"   Found {len(iframes)} iframe(s)")
                
                for idx, iframe in enumerate(iframes):
                    try:
                        self.driver.switch_to.frame(iframe)
                        time.sleep(1)
                        
                        elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                        captcha_element = self.find_captcha_in_elements(elements, f"in iframe {idx+1}")
                        
                        if captcha_element:
                            break
                        
                        self.driver.switch_to.default_content()
                    except:
                        self.driver.switch_to.default_content()
                        continue
            else:
                print("   No iframes found")
        
        # Save captcha
        if captcha_element:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                path = f"data/raw/{filename}"
                
                captcha_element.screenshot(path)
                print(f"CAPTCHA SAVED: {path}")
                
                self.save_metadata(filename, url)
                
                self.driver.switch_to.default_content()
                return True
            except Exception as e:
                print(f"Error saving CAPTCHA: {e}")
                self.driver.switch_to.default_content()
                return False
        else:
            print("NO CAPTCHA FOUND on this page")
            self.driver.switch_to.default_content()
            return False
    
    def close(self):
        """Ferme le navigateur"""
        self.driver.quit()


def main():
    """Fonction principale"""
    print("1. Setup WebDriver")
    # Initialiser le scraper
    scraper = CaptchaScraper()
    print("2. WebDriver ready")

    # URLs à tester
    urls = [
        "https://www.mtcaptcha.com/test-multiple-captcha",
    ]

    print("\n3. Starting CAPTCHA scraping")
    
    success_count = 0
    for idx, url in enumerate(urls, 1):
        print(f"\n{'#'*60}")
        print(f"[{idx}/{len(urls)}] Processing URL")
        print(f"{'#'*60}")
        
        if scraper.scrape_captcha_from_url(url):
            success_count += 1
        
        time.sleep(1)  # Pause entre les URLs

    print(f"\n{'='*60}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"URLs processed: {len(urls)}")
    print(f"CAPTCHAs found: {success_count}")
    print(f"Success rate: {success_count}/{len(urls)}")
    print(f"Images saved in: data/raw/")
    print(f"Metadata saved in: data/processed/")
    print(f"{'='*60}")

    print("\n4. Closing browser")
    scraper.close()
    print("✓ Browser closed")


if __name__ == "__main__":
    main()