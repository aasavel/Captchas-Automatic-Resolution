# Pipeline: page loading => captcha detection on visible area => scrolling => consent handling => iframe checking => saving

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from datetime import datetime, time
import pandas as pd

from consent_selectors import consent_selectors

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
        # Search for CAPTCHA images among given images
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
    
    def consent_cookies_buttons(self):
        # Try to find and consent or cookies buttons using selectors
        print("\nSearching for consent buttons...Wait a second please.")
        
        # Scroll down to load potential buttons for JS
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Use imported selectors
        print(f"{len(consent_selectors)} selectors to try")
        for consent_selector in consent_selectors:
            try:
                button = self.driver.find_element(By.XPATH, consent_selector)
                # Check if button is not hidden
                if button.is_displayed():
                    button.click()
                    print(f"Consent button was found & clicked! Yay!")
                    time.sleep(3)
                    return True
            except:
                continue
        print("No consent or cookie button found")
        return False
    
    def get_captcha(self, url):
        # Scrape captcha 
        try:
            self.driver.get(url)
            time.sleep(2)

            page_info = {
                "title": self.driver.title,
                "url": url,
                "date_extraction": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "cookies": len(self.driver.get_cookies()),
                "taille_page": len(self.driver.page_source)
            }
            
            print(f"Page loaded: {page_info['title']}")
            
        except Exception as error:
            print(f"Error: {error}")
        
        captcha_element = None
        
        # Search in visible area (top of the page)
        print("\n1. Searching for CAPTCHA on visible area...")
        try:
            elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
            print(f"   Found {len(elements)} visual elements")
            captcha_element = self.find_captcha_in_elements(elements, "on main page")
        except:
            pass
        
        # If not found yet, try scrolling down
        if not captcha_element:
            print("\n2. Scrolling down and searching...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            try:
                elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                captcha_element = self.find_captcha_in_elements(elements, "after scroll")
            except:
                pass
        
        # If still not found, try to consent buttons first
        if not captcha_element:
            print("\n3. No CAPTCHA yet, trying consent buttons...")
            consent_clicked = self.try_click_consent_buttons()
            
            if consent_clicked:
                print("\n3.1 Searching for CAPTCHA after consent...")
                time.sleep(2)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                try:
                    elements = self.driver.find_elements(By.XPATH, "//img | //canvas")
                    captcha_element = self.find_captcha_in_elements(elements, "after consent")
                except:
                    pass
        
        # If still not found, check iframes
        if not captcha_element:
            print("\n4. Checking iframes...")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                print(f"Found {len(iframes)} iframe(s)")
                
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
                print("No iframes found")
        
        # Save CAPTCHA if found
        if captcha_element:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captcha_{timestamp}.png"
                path = f"data/raw/{filename}"
                
                captcha_element.screenshot(path)
                print(f"\n✓ CAPTCHA SAVED: {path}")
                
                self.save_metadata(filename, url)
                
                self.driver.switch_to.default_content()
                return True
            except Exception as e:
                print(f"\n✗ Error saving CAPTCHA: {e}")
                self.driver.switch_to.default_content()
                return False
        else:
            print("\n⚠ NO CAPTCHA FOUND on this page")
            self.driver.switch_to.default_content()
            return False
    
    def close(self):
        """Ferme le navigateur"""
        self.driver.quit()


def main():
    """Fonction principale"""
    print("""
╔══════════════════════════════════════════════════════════╗
║   CAPTCHA Scraper - Projet M2 MoSEF 2025-2026          ║
║   Université Paris 1 Panthéon-Sorbonne                  ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print("1. Setup WebDriver")
    # Initialiser le scraper
    scraper = CaptchaScraper()
    print("2. WebDriver ready")

    # URLs à tester
    urls = [
        "https://solvecaptcha.com/demo/image-captcha",
        "https://2captcha.com/demo/normal",
        "https://rutracker.org/forum/profile.php?mode=register",
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