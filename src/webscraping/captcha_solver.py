"""
CAPTCHA RESOLUTION
- detect an input field
- input solution
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from datetime import datetime
import time
from utils.consent_selectors import css_selectors, xpath_selectors
from captcha_scraper import CaptchaScraper

class CaptchaSolver(CaptchaScraper):
    # Calling parent's class
    def __init__(self, chrome_driver_path=None):
        super().__init__(chrome_driver_path)
        
    def detect_captcha_input_field(self):
        # Detect input field
        # Input selectors with By types
        input_selectors = [
            (By.ID, "captcha"),
            (By.ID, "captcha_code"),
            (By.ID, "captchaInput"),
            (By.ID, "code"),
            (By.ID, "verification_code"),
            (By.NAME, "captcha"),
            (By.NAME, "code"),
            (By.XPATH, "//input[contains(@placeholder, 'captcha')]"),
            (By.XPATH, "//input[contains(@placeholder, 'code')]"),
            (By.XPATH, "//input[contains(@class, 'captcha')]"),
            (By.XPATH, "//input[@type='text']"),
        ]
        
        # Try each selector with EC
        for (sel_type, selector) in enumerate(input_selectors, 1):
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((sel_type, selector))
                )
                
                if element.is_displayed() and element.is_enabled():
                    self.input_field = element
                    
                    # Highlight
                    self.driver.execute_script(
                        "arguments[0].style.border='3px solid red'", element
                    )
                    return element
                    
            except TimeoutException:
                continue
            except Exception:
                continue
        
        # Try near CAPTCHA 
        if self.captcha_element:
            print("Trying near CAPTCHA...")
            try:
                parent = self.captcha_element.find_element(By.XPATH, "..")
                inputs = parent.find_elements(By.TAG_NAME, "input")
                
                for inp in inputs:
                    if inp.get_attribute('type') in ['text', ''] and inp.is_displayed():
                        self.input_field = inp
                        return inp
            except:
                pass
        
        print("No input field found")
        return None
    

    def fill_captcha_solution(self, solution):
        # Fill the solution in the input field
        if not self.input_field:
            print("No input field available")
            return False
        
        try:
            self.wait.until(EC.element_to_be_clickable(self.input_field))
            
            # Clear and fill
            self.input_field.clear()
            
            for char in solution:
                self.input_field.send_keys(char)
                time.sleep(0.1)
            
            print(f"Solution entered: '{solution}'")
            return True
            
        except TimeoutException:
            print(f"Timeout: Input not ready")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    

    def submit_captcha(self):
        # Submit
        print("\n[SUBMIT] Submitting...")
        
        # Submit button selectors
        submit_selectors = [
            "//button[contains(text(), 'Submit')]",
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Check')]",
            "//button[contains(text(), 'Valider')]",
            "//button[contains(text(), 'Send')]",
            "//button[@type='submit']",
            "//input[@type='submit']",
        ]
        
        # Try to find button with EC
        for selector in submit_selectors:
            try:
                button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                print(f"Submit button clicked")
                time.sleep(1)
                return True
            
            except TimeoutException:
                continue

            except Exception:
                continue
        
        # Fallback: Enter key
        if self.input_field:
            try:
                self.input_field.send_keys(Keys.RETURN)
                print(f"Submitted via Enter")
                time.sleep(1)
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        print("No submit method found")
        return False
    

    def check_captcha_success(self):
        # Success check
        # Success/error indicators
        success_indicators = [
            (By.XPATH, "//*[contains(text(), 'Success')]"),
            (By.XPATH, "//*[contains(text(), 'Correct')]"),
            (By.XPATH, "//*[contains(text(), 'Valid')]"),
            (By.XPATH, "//*[contains(text(), 'Succès')]"),
        ]
        
        error_indicators = [
            (By.XPATH, "//*[contains(text(), 'Error')]"),
            (By.XPATH, "//*[contains(text(), 'Incorrect')]"),
            (By.XPATH, "//*[contains(text(), 'Invalid')]"),
            (By.XPATH, "//*[contains(text(), 'Erreur')]"),
        ]
        
        # Short wait for indicators
        short_wait = WebDriverWait(self.driver, 3)
        
        # Check success with EC
        for sel_type, selector in success_indicators:
            try:
                short_wait.until(
                    EC.presence_of_element_located((sel_type, selector))
                )
                print(f"SUCCESS!")
                return True
            except TimeoutException:
                continue
        
        # Check errors with EC
        for sel_type, selector in error_indicators:
            try:
                short_wait.until(
                    EC.presence_of_element_located((sel_type, selector))
                )
                print(f"ERROR: Failed")
                return False
            except TimeoutException:
                continue
        
        # Fallback: page source
        page_source = self.driver.page_source.lower()
        
        if any(w in page_source for w in ["success", "correct", "valid", "succès"]):
            print(f"SUCCESS (in source)")
            return True
        
        if any(w in page_source for w in ["error", "incorrect", "invalid", "erreur"]):
            print(f"ERROR (in source)")
            return False
        
        print(f"UNCERTAIN")
        return None
    

    def save_screenshot(self, label="screenshot"):
        # SAve a screenshot for demo
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"data/solved/{label}_{timestamp}.png"
            self.driver.save_screenshot(path)
            return path
        except Exception as e:
            return None
    

    def solve_captcha_complete(self, url, solution=None):
        """
        COMPLETE WORKFLOW
        
        Uses from parent (CaptchaScraper):
            - extract_captcha()
            - click_consent_buttons()
            - save_captcha_image()
            - save_metadata()
        
        Adds solver-specific:
            - find_captcha_input_field()
            - fill_captcha_solution()
            - submit_captcha()
            - check_captcha_success()
        """
        result = {
            'url': url,
            'captcha_found': False,
            'input_found': False,
            'solution_filled': False,
            'submitted': False,
            'success': None,
            'screenshot': None
        }
        
        try:
            # Step 1: Load page with EC
            print(f"Loading page...")
            self.driver.get(url)
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print(f"Page loaded: {self.driver.title}")
            except TimeoutException:
                return result
            
            # Step 2: Extract CAPTCHA
            print(f"Extracting CAPTCHA...")
            result['captcha_found'] = self.extract_captcha()
            
            if not result['captcha_found']:
                print("No CAPTCHA found")
                return result
            
            # Save CAPTCHA image 
            captcha_path = self.save_captcha_image()
            
            # Step 3: Find input (solver method)
            print(f"Finding input...")
            input_found = self.find_captcha_input_field()
            
            if input_found:
                result['input_found'] = True
            else:
                return result
            
            # Step 4: Fill solution 
            print(f"Filling...")
            
            if solution is None:
                return result
            
            if self.fill_captcha_solution(solution):
                result['solution_filled'] = True
                result['screenshot'] = self.save_screenshot("before_submit")
            else:
                return result
            
            # Step 5: Submit (solver method)
            print(f"\nSubmitting...")
            if self.submit_captcha():
                result['submitted'] = True
                result['screenshot'] = self.save_screenshot("after_submit")
            else:
                return result
            
            # Step 6: Verify (solver method)
            print(f"\nChecking...")
            success = self.check_captcha_success()
            result['success'] = success
            
            # Save metadata
            if captcha_path:
                self.save_metadata(captcha_path, url, solution=solution, success=success)
            
            self.driver.switch_to.default_content()
            
            # Summary
            print(f"CAPTCHA found: {result['captcha_found']}")
            print(f"Input found: {result['input_found']}")
            print(f"Solution filled: {result['solution_filled']}")
            print(f"Submitted: {result['submitted']}")
            print(f"Success: {result['success']}")
            return result
            
        except Exception as e:
            print(f"Error: {e}")
            return result


def main():
    solver = CaptchaSolver()
    
    # Test complete workflow
    result = solver.solve_captcha_complete(
        url="https://2captcha.com/demo/normal",
        solution="TEST123"
    )
    
    print("RESULT:")
    print(json.dumps(result, indent=2))
    print("="*70)
    
    # Close browser 
    solver.close()

if __name__ == "__main__":
    main()

